"""
📦 Module: print_controller.py

Manages print operations in the PackingLine application.

Handles serial validation, .lbl parsing, and dynamic printing logic
based on configuration mappings. Supports multiple product types and protocols
(product, control4, my2n), and interacts with the PrintWindow UI.

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
    Coordinates print logic, UI interaction, and trigger-based workflows.
    """

    def __init__(self, window_stack, order_code: str, product_name: str):
        """
        Initializes print controller, services, and connects UI signals.
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
        Returns trimmed, uppercase serial number from input field.
        """
        return self.print_window.serial_number_input.text().strip().upper()

    @property
    def product_name(self) -> str:
        """
        Returns trimmed, uppercase product name from the print window.
        """
        return self.print_window.product_name.strip().upper()

    def handle_product_print(self, lbl_lines: list[str]):
        """
        Executes product-type save-and-print workflow.

        Validates input lines, extracts header and record, injects prefix,
        retrieves trigger values, and performs the print operation.
        """
        if not self.validator.validate_input_exists_for_product(lbl_lines, self.serial_input):
            self.delayed_restore_ui()
            return

        result = self.validator.extract_header_and_record(lbl_lines, self.serial_input)
        if not result:
            self.delayed_restore_ui()
            return
        header, record = result

        new_record = self.validator.validate_and_inject_balice(header, record)
        if new_record is None:
            self.delayed_restore_ui()
            return

        trigger_values = self.validator.extract_trigger_values(lbl_lines, self.serial_input)
        if not trigger_values:
            self.delayed_restore_ui()
            return

        self.logic.product_save_and_print(header, new_record, trigger_values)
        self.logger.info("%s %s", self.product_name, self.serial_input)

    def handle_control4_print(self, lbl_lines: list[str]):
        """
        Executes Control4 save-and-print workflow.

        Validates input lines, extracts header and record, retrieves trigger values,
        and performs the print operation.
        """
        if not self.validator.validate_input_exists_for_control4(lbl_lines, self.serial_input):
            self.delayed_restore_ui()
            return

        result = self.validator.extract_header_and_record_c4(lbl_lines, self.serial_input)
        if not result:
            self.delayed_restore_ui()
            return
        header, record = result

        trigger_values = self.validator.extract_trigger_values_c4(lbl_lines, self.serial_input)
        if not trigger_values:
            self.delayed_restore_ui()
            return

        self.logic.control4_save_and_print(header, record, trigger_values)
        self.logger.info("Control4 %s", self.serial_input)

    def handle_my2n_print(self):
        """
        Executes My2N save-and-print workflow.

        Validates config paths, extracts token, and performs the print operation.
        """
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

    def print_button_click(self):
        """
        Main print workflow triggered by user.
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
            self.handle_product_print(lbl_lines)

        # 📌 Execute control4-save-and-print functions as needed
        if "control4" in triggers and lbl_lines:
            self.handle_control4_print(lbl_lines)

        # 📌 Execute my2n-save-and-print functions as needed
        if "my2n" in triggers:
            self.handle_my2n_print()

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
        Restores UI controls after a short delay (default 500 ms).
        """
        QTimer.singleShot(delay_ms,  self.print_window.restore_inputs)

    def restore_ui(self, delay_ms=3000):
        """
        Restores UI controls after a longer delay (default 3000 ms).
        """
        QTimer.singleShot(delay_ms,  self.print_window.restore_inputs)
