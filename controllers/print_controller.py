# 🖨️ PrintController – handles logic for serial input, validation, and print action

import configparser
from pathlib import Path
from utils.logger import get_logger
from utils.messenger import Messenger
from views.print_window import PrintWindow
from utils.resources import get_config_path
from utils.validators import Validator
from PyQt6.QtCore import QEventLoop, QTimer


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

    def control4_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Extracts header and record for the scanned serial number and writes them to Control4 output file.
        Načte hlavičku a záznam z řádků .lbl pro naskenovaný serial number a zapíše je do výstupního souboru Control4.

        - Hledá řádky začínající na: SERIAL+I= a SERIAL+J= a SERIAL+K=
        - Pokud najde hlavičku i záznam, zapíše je do výstupního souboru

        :param header: extracted header line / extrahovaná hlavička z .lbl
        :param record: extracted record line / extrahovaný záznam z .lbl
        :param trigger_values: list of trigger filenames / seznam názvů souborů spouštěče
        """
        # 📁 Retrieve output file path from config / Získání cesty k výstupnímu souboru z konfigurace
        output_path = self.config.get_path('output_file_path_c4_product', section='Control4Paths')
        if not output_path:
            self.normal_logger.log('Error', f'Cesta k výstupnímu souboru product nebyla nalezena.', 'PRICON004')
            self.messenger.show_error('Error', f'Cesta k výstupnímu souboru product nebyla nalezena.', 'PRICON004', False)
            self.print_window.reset_input_focus()
            return

        try:
            # 💾 Write header and record to file / Zápis hlavičky a záznamu do souboru
            with output_path.open('w') as file:
                file.write(header + '\n')
                file.write(record + '\n')

            # 🗂️ Retrieve trigger directory from config / Získání složky pro spouštěče z konfigurace
            trigger_dir = self.get_trigger_dir()
            if not trigger_dir or not trigger_dir.exists():
                self.normal_logger.log('Error', f'Složka trigger_path neexistuje nebo není zadána.', 'PRICON005')
                self.messenger.show_error('Error', f'Složka trigger_path neexistuje nebo není zadána.', 'PRICON005', False)
                self.print_window.reset_input_focus()
                return

            # ✂️ Create trigger files from values / Vytvoření souborů podle hodnot I=
            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)
                # 💬 Inform the user about printing progress / Informace o průběhu tisku
                self.messenger.show_timed_info('Info', f'Prosím čekejte, tisknu etiketu: {value}', 3000)

                # 🛑 Vytvoření prodlevy bez blokace GUI
                loop = QEventLoop()
                QTimer.singleShot(3000, loop.quit)
                loop.exec()

        except Exception as e:
            # 🛑 Log and display unexpected error / Zaloguj a zobraz neočekávanou chybu
            self.normal_logger.log('Error', f'Chyba zápisu {str(e)}', 'PRICON006')
            self.messenger.show_error('Error', f'{str(e)}', 'PRICON006', False)
            self.print_window.reset_input_focus()

    def product_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Extracts header and record for the scanned serial number and writes them to product output file.
        Načte hlavičku a záznam z řádků .lbl pro naskenovaný serial number a zapíše je do výstupního souboru product.

        :param header: extracted header line / extrahovaná hlavička z .lbl
        :param record: extracted record line / extrahovaný záznam z .lbl
        :param trigger_values: list of trigger filenames / seznam názvů souborů spouštěče
        """

        # 📁 Retrieve output file path from config / Získání cesty k výstupnímu souboru z konfigurace
        output_path = self.config.get_path('output_file_path_product', section='ProductPaths')
        if not output_path:
            self.normal_logger.log('Warning', f'Cesta k výstupnímu souboru product nebyla nalezena.', 'PRICON009')
            self.messenger.show_warning('Warning', f'Cesta k výstupnímu souboru product nebyla nalezena.', 'PRICON009')
            self.print_window.reset_input_focus()
            return

        try:
            # 💾 Write header and record to file / Zápis hlavičky a záznamu do souboru
            with output_path.open('w') as file:
                file.write(header + '\n')
                file.write(record + '\n')

            # 🗂️ Retrieve trigger directory from config / Získání složky pro spouštěče z konfigurace
            trigger_dir = self.get_trigger_dir()
            if not trigger_dir or not trigger_dir.exists():
                self.normal_logger.log('Warning', f'Složka trigger_path neexistuje nebo není zadána.', 'PRICON010')
                self.messenger.show_warning('Warning', f'Složka trigger_path neexistuje nebo není zadána.', 'PRICON010')
                self.print_window.reset_input_focus()
                return

            # ✂️ Create trigger files from values / Vytvoření souborů podle hodnot B=
            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)
                # 💬 Inform the user about printing progress / Informace o průběhu tisku
                self.messenger.show_timed_info('Info', f'Prosím čekejte, tisknu etiketu: {value}', 3000)

                # 🛑 Vytvoření prodlevy bez blokace GUI
                loop = QEventLoop()
                QTimer.singleShot(3000, loop.quit)
                loop.exec()

        except Exception as e:
            # 🛑 Log and display unexpected error / Zaloguj a zobraz neočekávanou chybu
            self.normal_logger.log('Error', f'Chyba zápisu {str(e)}', 'PRICON011')
            self.messenger.show_error('Error', f'{str(e)}', 'PRICON011', False)
            self.print_window.reset_input_focus()

    def my2n_save_and_print(self, serial_number: str, token: str, output_path: Path) -> None:
        """
        Writes extracted My2N token and serial number to output file and creates trigger file.
        Zapíše získaný My2N token a serial do výstupního souboru a vytvoří trigger soubor.

        :param serial_number: serial number from input / seriové číslo z inputu
        :param token: extracted My2N token / získaný bezpečnostní kód
        :param output_path: path to output file / cesta k výstupnímu souboru
        """
        try:
            with output_path.open('w') as file:
                file.write('"L Vyrobni cislo dlouhe","L Bezpecnostni cislo","P Vyrobni cislo","P Bezpecnostni kod"\n')
                file.write(f'"Serial number:","My2N Security Code:","{serial_number}","{token}"\n')

            trigger_dir = self.get_trigger_dir()
            if trigger_dir and trigger_dir.exists():
                try:
                    trigger_file = trigger_dir / 'SF_MY2N_A'
                    trigger_file.touch(exist_ok=True)
                    # 💬 Inform the user about printing progress / Informace o průběhu tisku
                    self.messenger.show_timed_info('Info', f'Prosím čekejte, tisknu etiketu: SF_MY2N_A', 3000)

                    # 🛑 Vytvoření prodlevy bez blokace GUI
                    loop = QEventLoop()
                    QTimer.singleShot(3000, loop.quit)
                    loop.exec()
                except Exception as e:
                    self.normal_logger.log('Error', f'Chyba trigger souboru {str(e)}', 'PRICON012')
                    self.messenger.show_error('Error', f'{str(e)}', 'PRICON012', False)
            else:
                self.normal_logger.log('Error', 'Trigger složka není definována nebo neexistuje.', 'PRICON013')
                self.messenger.show_error('Error', 'Složka pro trigger není dostupná.', 'PRICON013', False)

        except Exception as e:
            self.normal_logger.log('Error', f'Chyba zápisu: {str(e)}', 'PRICON014')
            self.messenger.show_error('Error', f'{str(e)}', 'PRICON014', False)

    def get_trigger_groups_for_product(self) -> list[str]:
        """
        Returns all trigger groups (product, control4, my2n) that match product_name from config.
        Vrátí všechny skupiny (product, control4, my2n), které obsahují zadaný produkt z configu.

        :return: List of matching group names / Seznam shodných skupin
        """
        product_name = self.product_name

        matching = []
        for section_key in self.config.config.options('ProductTriggerMapping'):
            raw_list = self.config.config.get('ProductTriggerMapping', section_key)
            items = [i.strip() for i in raw_list.split(',')]
            if product_name in items:
                matching.append(section_key)

        return matching  # e.g. ['product', 'my2n']

    def print_button_click(self):
        """
        Handles print button action by validating input and triggering appropriate save-and-print methods.
        Obsluhuje kliknutí na tlačítko 'Print' validací vstupu a spuštěním příslušných metod podle konfigurace.
        """

        # === 1️⃣ Validate serial number input / Validace vstupu
        if not self.validator.validate_serial_format(self.serial_input):
            return

        # === 2️⃣ Resolve product trigger groups from config / Načtení skupin produktů podle konfigurace
        triggers = self.get_trigger_groups_for_product()

        # === 3️⃣ Load corresponding .lbl file lines / Načtení řádků ze souboru .lbl
        lbl_lines = self.load_file_lbl()
        if not lbl_lines:
            self.normal_logger.log('Error', f'Soubor .lbl nelze načíst nebo je prázdný!', 'PRICON015')
            self.messenger.show_error('Error', 'Soubor .lbl nelze načíst nebo je prázdný!', 'PRICON015', False)
            return

        # 📌 Execute save-and-print functions as needed / Spuštění odpovídajících funkcí
        if 'product' in triggers and lbl_lines:

            # === 1️⃣ Validate presence of required lines / Validace existence B/D/E řádků
            if not self.validator.validate_input_exists_for_product(lbl_lines, self.serial_input):
                return

            # === 2️⃣ Extract header and record / Získání D= a E= řádků
            result = self.validator.extract_header_and_record(lbl_lines, self.serial_input)
            if not result:
                return

            header, record = result

            # === 3️⃣ Inject prefix to record / Vložení prefixu do správného pole
            new_record = self.validator.validate_and_inject_balice(header, record)
            if new_record is None:
                return

            # === 4️⃣ Inject prefix to record / Vložení prefixu do správného pole
            trigger_values = self.validator.extract_trigger_values(lbl_lines, self.serial_input)
            if not trigger_values:
                return

            # === 5️⃣ Save and print / Spuštění zápisu výstupního souboru
            self.product_save_and_print(header, new_record, trigger_values)

            # === 6️⃣ Log success
            self.normal_logger.clear_log('Info', f'{self.product_name} {self.serial_input}')

        # 📌 Execute control4-save-and-print functions as needed / Spuštění odpovídajících funkcí
        if 'control4' in triggers and lbl_lines:
            # === 1️⃣ Validation of input lines I/J/K / Validace vstupních řádků I/J/K
            if not self.validator.validate_input_exists_for_control4(lbl_lines, self.serial_input):
                return

            # === 2️⃣ Getting header and record from J= and K= / Získání hlavičky a záznamu z J= a K=
            result = self.validator.extract_header_and_record_c4(lbl_lines, self.serial_input)
            if not result:
                return
            header, record = result

            # === 3️⃣ Getting values from I= row / Získání hodnot z I= řádku
            trigger_values = self.validator.extract_trigger_values_c4(lbl_lines, self.serial_input)
            if not trigger_values:
                return

            # === 4️⃣ Starting enrolment for Control4 / Spuštění zápisu pro Control4
            self.control4_save_and_print(header, record, trigger_values)

            # === 5️⃣ Log entry / Zápis do logu
            self.normal_logger.clear_log('Info', f'Control4 {self.serial_input}')

        # 📌 Execute my2n-save-and-print functions as needed / Spuštění odpovídajících funkcí
        if 'my2n' in triggers:
            reports_path = self.config.get_path('reports_path', section='Paths')
            output_path = self.config.get_path('output_file_path_my2n', section='My2nPaths')

            if not reports_path or not output_path:
                self.normal_logger.log('Error', 'Cesty k reportu nebo výstupu nejsou definovány.', 'PRICON016')
                self.messenger.show_error('Error', 'Chybí konfigurace cest pro My2N.', 'PRICON016', False)
                return

            token = self.validator.extract_my2n_token(self.serial_input, reports_path)
            if not token:
                return

            self.my2n_save_and_print(self.serial_input, token, output_path)
            self.normal_logger.clear_log('Info', f'My2N token: {token}')

        self.normal_logger.add_blank_line()
        self.print_window.reset_input_focus()

    def handle_exit(self):
        """
        Closes PrintWindow and returns to the previous window.
        Zavře PrintWindow a vrátí se na předchozí okno ve stacku.
        """
        self.print_window.effects.fade_out(self.print_window, duration=1000)
