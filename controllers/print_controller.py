"""
📦 Module: print_controller.py

Controller for managing print operations in the PackingLine application.

Handles serial number validation, .lbl file parsing, and dynamic printing logic
based on configuration mappings. Supports multiple product types and printing
protocols (product, control4, my2n), and interacts with the PrintWindow UI.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser
from pathlib import Path

# 🧩 Third-party libraries
from PyQt6.QtCore import QTimer, QCoreApplication

# 🧠 First-party (project-specific)
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path
from utils.validators import Validator
from utils.app_services import AppServices

from views.print_window import PrintWindow

from controllers.print_logic_controller import PrintLogicController
from controllers.print_loader_controller import PrintLoaderController


class PrintController:
    """
    Main controller for managing print-related logic and UI interactions.

    Attributes:
        window_stack (WindowStackManager): Navigation stack for UI windows.
        print_window (PrintWindow): The active print window instance.
        config (ConfigParser): Loaded configuration file.
        validator (Validator): Validates serial input and .lbl file structure.
        messenger (Messenger): Displays messages and dialogs to the user.
        loader (PrintLoaderController): Loads .lbl files from disk.
        logic (PrintLogicController): Executes save-and-print operations.
    """

    def __init__(self, window_stack, order_code: str, product_name: str):
        """
        Initializes the PrintController and connects UI signals.

        Args:
            window_stack (WindowStackManager): UI navigation stack.
            order_code (str): Order code for the current print job.
            product_name (str): Name of the product being printed.
        """
        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Initialization
        self.window_stack = window_stack
        self.print_window = PrintWindow(order_code, product_name, controller=self)
        self.validator = Validator(self.print_window)
        self.messenger = Messenger(self.print_window)
        self.loader = PrintLoaderController(self.messenger)
        self.logger = get_logger("PrintController")
        self.services = AppServices(config=self.config, messenger=self.messenger)

        # 📌 Initialization of print logic
        self.logic = PrintLogicController(
            config=self.config,
            messenger=self.messenger,
            print_window=self.print_window
        )

        # 🔗 linking the button to the method
        self.print_window.print_button.clicked.connect(self.print_button_click)
        self.print_window.back_button.clicked.connect(self.handle_back)
        self.print_window.exit_button.clicked.connect(self.handle_exit)

    @property
    def serial_input(self) -> str:
        """
        Returns the cleaned serial number from the input field.

        Returns:
            str: Uppercase, trimmed serial number.
        """
        return self.print_window.serial_number_input.text().strip().upper()

    @property
    def product_name(self) -> str:
        """
        Returns the cleaned product name from the print window.

        Returns:
            str: Uppercase, trimmed product name.
        """
        return self.print_window.product_name.strip().upper()

    def print_button_click(self):
        """
        Handles the print button click event.

        Validates input, resolves trigger groups, loads .lbl file,
        and executes appropriate save-and-print logic based on product type.
        """
        self.print_window.disable_inputs()

        # === 1️⃣ Validate serial number input
        if not self.validator.validate_serial_format(self.serial_input):
            self.delayed_restore_ui()
            return

        # === 2️⃣ Resolve product trigger groups from config
        triggers = self.services.config_controller.get_trigger_groups_for_product(self.product_name)
        if not triggers:
            self.logger.warning("Zpracování zastaveno – produkt není mapován v configu.")
            self.delayed_restore_ui()
            return

        # === 3️⃣ Load corresponding .lbl file lines
        lbl_lines = self.loader.load_lbl_file(order_code=self.print_window.order_code)
        if not lbl_lines:
            self.logger.error("Soubor .lbl nelze načíst nebo je prázdný!")
            self.messenger.error("Soubor .lbl nelze načíst nebo je prázdný!", "Print Ctrl")
            self.delayed_restore_ui()
            return

        # 📌 Execute save-and-print functions as needed
        if "product" in triggers and lbl_lines:

            # === 1️⃣ Validate presence of required lines B/D/E lines
            if not self.validator.validate_input_exists_for_product(lbl_lines, self.serial_input):
                self.delayed_restore_ui()
                return

            # === 2️⃣ Extract header and record D= a E= lines
            result = self.validator.extract_header_and_record(lbl_lines, self.serial_input)
            if not result:
                self.delayed_restore_ui()
                return

            header, record = result

            # === 3️⃣ Inject prefix to record
            new_record = self.validator.validate_and_inject_balice(header, record)
            if new_record is None:
                self.delayed_restore_ui()
                return

            # === 4️⃣ Inject prefix to record
            trigger_values = self.validator.extract_trigger_values(lbl_lines, self.serial_input)
            if not trigger_values:
                self.delayed_restore_ui()
                return

            # === 5️⃣ Save and print
            self.logic.product_save_and_print(header, new_record, trigger_values)

            # === 6️⃣ Log success
            self.logger.info("%s %s", self.product_name, self.serial_input)

        # 📌 Execute control4-save-and-print functions as needed
        if "control4" in triggers and lbl_lines:
            # === 1️⃣ Validation of input lines I/J/K
            if not self.validator.validate_input_exists_for_control4(lbl_lines, self.serial_input):
                self.delayed_restore_ui()
                return

            # === 2️⃣ Getting header and record from J= and K=
            result = self.validator.extract_header_and_record_c4(lbl_lines, self.serial_input)
            if not result:
                self.delayed_restore_ui()
                return
            header, record = result

            # === 3️⃣ Getting values from I= row
            trigger_values = self.validator.extract_trigger_values_c4(lbl_lines, self.serial_input)
            if not trigger_values:
                self.delayed_restore_ui()
                return

            # === 4️⃣ Starting enrolment for Control4
            self.logic.control4_save_and_print(header, record, trigger_values)

            # === 5️⃣ Log entry
            self.logger.info("Control4 %s", self.serial_input)

        # 📌 Execute my2n-save-and-print functions as needed
        if "my2n" in triggers:
            reports_path = Path(self.config.get("Paths", "reports_path"))
            output_path = Path(self.config.get("My2nPaths", "output_file_path_my2n"))

            if not reports_path or not output_path:
                self.logger.error("Cesty k reportu nebo výstupu nejsou definovány.")
                self.messenger.error("Chybí konfigurace cest pro My2N.", "Print Ctrl")
                self.delayed_restore_ui()
                return

            token = self.validator.extract_my2n_token(self.serial_input, reports_path)
            if not token:
                self.delayed_restore_ui()
                return

            self.logic.my2n_save_and_print(self.serial_input, token)
            self.logger.info("My2N token: %s", token)

        self.messenger.auto_info_dialog("Zpracovávám požadavek...", timeout_ms=3000)
        self.restore_ui()

    def handle_back(self):
        """
        Closes the product window and returns to the previous window in the stack.
        """
        self.print_window.effects.fade_out(self.print_window)

    def handle_exit(self):
        """
        Terminates the application and fades out the product window.
        """
        self.logger.info("Aplikace byla ukončena uživatelem.")
        bartender = self.services.bartender_cls(messenger=self.messenger, config=self.config)
        bartender.kill_processes()
        self.window_stack.mark_exiting()
        self.print_window.effects.fade_out(self.print_window, callback=QCoreApplication.instance().quit)

    def delayed_restore_ui(self, delay_ms=500):
        """
        Restores UI controls after a short delay.

        Args:
            delay_ms (int): Delay in milliseconds before restoring UI.
        """
        QTimer.singleShot(delay_ms,  self.print_window.restore_inputs)

    def restore_ui(self, delay_ms=3000):
        """
        Restores UI controls after a longer delay (default 3 seconds).

        Args:
            delay_ms (int): Delay in milliseconds before restoring UI.
        """
        QTimer.singleShot(delay_ms,  self.print_window.restore_inputs)
