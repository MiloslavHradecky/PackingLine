# 🖨️ PrintController – handles logic for serial input, validation, and print action

import configparser
from pathlib import Path
from utils.logger import get_logger
from utils.messenger import Messenger
from views.print_window import PrintWindow
from utils.resources import get_config_path
from utils.validators import Validator
from controllers.print_logic_controller import PrintLogicController
from controllers.print_loader_controller import PrintLoaderController
from controllers.print_config_controller import PrintConfigController


class PrintController:
    """
    Main logic controller for print operations in the application.

        - Handles serial number validation, .lbl file parsing, and configuration-based output decisions
        - Manages dynamic printing for multiple product types based on config-defined mappings
        - Generates structured text files and trigger signals for label printing systems
        - Operates with PrintWindow GUI and connects button actions to appropriate processing
    """

    def __init__(self, window_stack, order_code: str, product_name: str):
        """
        Initializes the print controller and connects signals.
        """
        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Saving references to application windows
        self.window_stack = window_stack
        self.print_window = PrintWindow(order_code, product_name, controller=self)
        self.validator = Validator(self.print_window)

        # 🔔 User feedback system
        self.messenger = Messenger(self.print_window)
        self.loader = PrintLoaderController(self.messenger)

        # 📌 Logger initialization
        self.logger = get_logger("PrintController")

        # 📌 Initialization of print logic
        self.logic = PrintLogicController(
            config=self.config,
            messenger=self.messenger,
            print_window=self.print_window
        )

        # 📌 Initialization of print config
        self.config_controller = PrintConfigController(
            config=self.config,
            messenger=self.messenger
        )

        # 🔗 linking the button to the method
        self.print_window.print_button.clicked.connect(self.print_button_click)
        self.print_window.exit_button.clicked.connect(self.handle_exit)

    @property
    def serial_input(self) -> str:
        """
        Returns cleaned serial number from input field.
        """
        return self.print_window.serial_number_input.text().strip().upper()

    @property
    def product_name(self) -> str:
        """
        Returns cleaned product name from print window.
        """
        return self.print_window.product_name.strip().upper()

    def print_button_click(self):
        """
        Handles print button action by validating input and triggering appropriate save-and-print methods.
        """

        # === 1️⃣ Validate serial number input
        if not self.validator.validate_serial_format(self.serial_input):
            return

        # === 2️⃣ Resolve product trigger groups from config
        triggers = self.config_controller.get_trigger_groups_for_product(self.product_name)

        # === 3️⃣ Load corresponding .lbl file lines
        lbl_lines = self.loader.load_lbl_file(order_code=self.print_window.order_code)
        if not lbl_lines:
            self.logger.error(f"Soubor .lbl nelze načíst nebo je prázdný!")
            self.messenger.error(f"Soubor .lbl nelze načíst nebo je prázdný!", "Print Ctrl")
            return

        # 📌 Execute save-and-print functions as needed
        if 'product' in triggers and lbl_lines:

            # === 1️⃣ Validate presence of required lines B/D/E lines
            if not self.validator.validate_input_exists_for_product(lbl_lines, self.serial_input):
                return

            # === 2️⃣ Extract header and record D= a E= lines
            result = self.validator.extract_header_and_record(lbl_lines, self.serial_input)
            if not result:
                return

            header, record = result

            # === 3️⃣ Inject prefix to record
            new_record = self.validator.validate_and_inject_balice(header, record)
            if new_record is None:
                return

            # === 4️⃣ Inject prefix to record
            trigger_values = self.validator.extract_trigger_values(lbl_lines, self.serial_input)
            if not trigger_values:
                return

            # === 5️⃣ Save and print
            self.logic.product_save_and_print(header, new_record, trigger_values)

            # === 6️⃣ Log success
            self.logger.info(f"{self.product_name} {self.serial_input}")

        # 📌 Execute control4-save-and-print functions as needed
        if 'control4' in triggers and lbl_lines:
            # === 1️⃣ Validation of input lines I/J/K
            if not self.validator.validate_input_exists_for_control4(lbl_lines, self.serial_input):
                return

            # === 2️⃣ Getting header and record from J= and K=
            result = self.validator.extract_header_and_record_c4(lbl_lines, self.serial_input)
            if not result:
                return
            header, record = result

            # === 3️⃣ Getting values from I= row
            trigger_values = self.validator.extract_trigger_values_c4(lbl_lines, self.serial_input)
            if not trigger_values:
                return

            # === 4️⃣ Starting enrolment for Control4
            self.logic.control4_save_and_print(header, record, trigger_values)

            # === 5️⃣ Log entry
            self.logger.info(f"Control4 {self.serial_input}")

        # 📌 Execute my2n-save-and-print functions as needed
        if 'my2n' in triggers:
            reports_path = Path(self.config.get("Paths", "reports_path"))
            output_path = Path(self.config.get("My2nPaths", "output_file_path_my2n"))

            if not reports_path or not output_path:
                self.logger.error(f"Cesty k reportu nebo výstupu nejsou definovány.")
                self.messenger.error(f"Chybí konfigurace cest pro My2N.", "Print Ctrl")
                return

            token = self.validator.extract_my2n_token(self.serial_input, reports_path)
            if not token:
                return

            self.logic.my2n_save_and_print(self.serial_input, token)
            self.logger.info(f"My2N token: {token}")

        self.print_window.reset_input_focus()

    def handle_exit(self):
        """
        Closes PrintWindow and returns to the previous window.
        """
        self.print_window.effects.fade_out(self.print_window, duration=1000)
