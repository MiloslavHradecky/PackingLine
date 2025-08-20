# 🖨️ PrintController – handles logic for serial input, validation, and print action

import configparser
from pathlib import Path
from utils.logger import get_logger
from utils.messenger import Messenger
from views.print_window import PrintWindow
from utils.resources import get_config_path
from utils.validators import Validator
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from controllers.print_logic_controller import PrintLogicController


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
        self.progress_box = QMessageBox(self.print_window or None)

        # 📌 Logger initialization
        self.logger = get_logger("PrintController")

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

    def get_trigger_dir(self) -> Path | None:
        """
        Returns trigger directory path from config.
        """
        raw_path = self.config.get("Paths", "trigger_path")
        if raw_path:
            path = Path(raw_path)
            if path.exists():
                return path
        return None

    def load_file_lbl(self):
        """
        Loads the .lbl file based on order_code and config path.

            :return: List of lines or empty list if not found
        """
        # 🎯 Getting path from config.ini
        raw_orders_path = self.config.get("Paths", "orders_path")

        if not raw_orders_path:
            self.logger.error(f"Konfigurační cesta {raw_orders_path} nebyla nalezena!")
            self.messenger.error(f"Konfigurační cesta {raw_orders_path} nebyla nalezena!", "Print Ctrl")
            self.print_window.reset_input_focus()
            return []

        orders_path = Path(raw_orders_path)

        # 🧩 Build path to .lbl file
        lbl_file = orders_path / f'{self.print_window.order_code}.lbl'

        if not lbl_file.exists():
            self.logger.warning(f"Soubor {lbl_file} neexistuje.")
            self.messenger.warning(f"Soubor {lbl_file} neexistuje.", "Print Ctrl")
            self.print_window.reset_input_focus()
            return []

        try:
            # 📄 Load the contents of a file
            return lbl_file.read_text().splitlines()
        except Exception as e:
            self.logger.error(f"Chyba načtení souboru {str(e)}")
            self.messenger.error(f"Chyba načtení souboru {str(e)}", "Print Ctrl")
            self.print_window.reset_input_focus()
            return []

    def get_trigger_groups_for_product(self) -> list[str]:
        """
        Returns all trigger groups (product, control4, my2n) that match product_name from config.

            :return: List of matching group names
        """
        product_name = self.product_name
        matching = []

        if not self.config.has_section("ProductTriggerMapping"):
            self.logger.warning("Sekce 'ProductTriggerMapping' nebyla nalezena v configu.")
            return matching

        for group_name in self.config.options("ProductTriggerMapping"):
            raw_list = self.config.get("ProductTriggerMapping", group_name)
            items = [item.strip() for item in raw_list.split(",")]
            if product_name in items:
                matching.append(group_name)

        return matching  # ✅ e.g. ['product', 'my2n']

    def finalize_print_process(self, delay=3000):
        """Completing the printing process - closing the progress box."""

        # 📌 UI updates
        self._update_ui_after_print()

        # 📌 Automatic closing of progress box after 'delay' seconds
        QTimer.singleShot(delay, lambda: self.messenger.close_progress_box())

    def _update_ui_after_print(self):
        """UI update after successful printing."""
        self.messenger.update_progress_text('✅ Tisk byl úspěšně dokončen!')
        self.messenger.set_progress_no_buttons()

    def print_button_click(self):
        """
        Handles print button action by validating input and triggering appropriate save-and-print methods.
        """

        # === 1️⃣ Validate serial number input
        if not self.validator.validate_serial_format(self.serial_input):
            return

        # === 2️⃣ Resolve product trigger groups from config
        triggers = self.get_trigger_groups_for_product()

        # === 3️⃣ Load corresponding .lbl file lines
        lbl_lines = self.load_file_lbl()
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
            self.product_save_and_print(header, new_record, trigger_values)

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
            self.control4_save_and_print(header, record, trigger_values)

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

            self.my2n_save_and_print(self.serial_input, token, output_path)
            self.logger.info(f"My2N token: {token}")

        self.print_window.reset_input_focus()

    def handle_exit(self):
        """
        Closes PrintWindow and returns to the previous window.
        """
        self.print_window.effects.fade_out(self.print_window, duration=1000)
