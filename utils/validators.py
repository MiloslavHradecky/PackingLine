# 🔑 Validator - Validates all inputs

import re
from pathlib import Path
from utils.logger import get_logger
from utils.messenger import Messenger
from models.user_model import get_value_prefix


class Validator:
    def __init__(self, print_window):
        self.print_window = print_window

        # 📌 Messenger initialization
        self.messenger = Messenger(self.print_window)

        # 📌 Logger initialization
        self.logger = get_logger("Validators")

    def validate_serial_format(self, serial_number: str) -> bool:
        """
        Validates the serial number format 00-0000-0000.
        """
        pattern = r'^\d{2}-\d{4}-\d{4}$'
        if not re.fullmatch(pattern, serial_number):
            self.messenger.info(f"Serial number must be in format 00-0000-0000.", "Validators")
            self.print_window.reset_input_focus()
            return False
        return True

    def validate_input_exists_for_product(self, lbl_lines: list[str], serial: str) -> bool:
        """
        Validates that all key lines for a given serial number exist in lbl_lines.
        Checks that the lines SERIAL+B=, D=, E= exist for the given serial number.

            :param lbl_lines: List of lines from the .lbl file
            :param serial: Specified serial number
            :return: True if all exist, otherwise False + displays a warning
        """
        keys = [f'{serial}B=', f'{serial}D=', f'{serial}E=']
        missing_keys = [key for key in keys if not any(line.startswith(key) for line in lbl_lines)]

        if missing_keys:
            joined = ', '.join(missing_keys)
            self.logger.error(f"Nebyly nalezeny všechny klíčové řádky: {joined}")
            self.messenger.show_error('Error', f'Některé klíčové řádky v souboru .lbl chybí!', 'VALIDATOR001', False)
            self.print_window.reset_input_focus()
            return False

        return True

    def validate_and_inject_balice(self, header: str, record: str) -> str | None:
        """
        Validates and injects prefix to 'P Znacka balice' field.
        Zkontroluje správnost, provede injekci do record, nebo vrátí None při chybě.
        """
        header_fields = header.split('","')
        record_fields = record.split('","')

        try:
            index = header_fields.index('P Znacka balice')
            if index >= len(record_fields):
                self.logger.error(f"Neplatný index pole 'P Znacka balice'")
                self.messenger.show_error('Error', 'Neplatný index pole v record.', 'VALIDATOR002', False)
                self.print_window.reset_input_focus()
                return None

            prefix = get_value_prefix()
            record_fields[index] = prefix
            return '","'.join(record_fields)

        except ValueError:
            self.logger.error("Pole 'P Znacka balice' chybí.")
            self.messenger.show_error('Error', 'Pole v header nebylo nalezeno.', 'VALIDATOR003', False)
            self.print_window.reset_input_focus()
            return None

    def extract_header_and_record(self, lbl_lines: list[str], serial: str) -> tuple[str, str] | None:
        """
        Extracts D= and E= lines from lbl_lines.
        Extrahuje řádky D= a E= z lbl souboru.
        """
        key_d = f'{serial}D='
        key_e = f'{serial}E='
        header = None
        record = None

        for line in lbl_lines:
            if line.startswith(key_d):
                header = line.split('D=')[1].strip()
            elif line.startswith(key_e):
                record = line.split('E=')[1].strip()

        if not header or not record:
            self.logger.error(f"Nebyly nalezeny hlavička nebo záznam pro '{serial}'.")
            self.messenger.show_error('Error', f'Nebyly nalezeny hlavička nebo záznam pro "{serial}".', 'VALIDATOR004', False)
            self.print_window.reset_input_focus()
            return None

        return header, record

    def extract_trigger_values(self, lbl_lines: list[str], serial: str) -> list[str] | None:
        """
        Extracts values from B= line.
        Extrahuje hodnoty ze řádku B=.
        """
        key_b = f'{serial}B='
        for line in lbl_lines:
            if line.startswith(key_b):
                raw_value = line.split('B=')[1]
                values = [val.strip() for val in raw_value.split(';') if val.strip()]
                return values

        self.logger.error(f"Řádek \'{key_b}\' nebyl nalezen.")
        self.messenger.show_error('Error', f'Řádek \"{key_b}\" nebyl nalezen.', 'VALIDATOR005', False)
        self.print_window.reset_input_focus()
        return None

    def extract_header_and_record_c4(self, lbl_lines: list[str], serial: str) -> tuple[str, str] | None:
        """
        Extracts J= and K= lines for Control4.
        Extrahuje řádky J= a K= pro Control4.
        """
        key_j = f'{serial}J='
        key_k = f'{serial}K='
        header = None
        record = None

        for line in lbl_lines:
            if line.startswith(key_j):
                header = line.split('J=')[1].strip()
            elif line.startswith(key_k):
                record = line.split('K=')[1].strip()

        if not header or not record:
            self.logger.error(f"Nebyly nalezeny J/K řádky pro serial '{serial}'.")
            self.messenger.show_error('Error', f'Nebyly nalezeny J/K řádky pro serial "{serial}".', 'VALIDATOR006', False)
            self.print_window.reset_input_focus()
            return None

        return header, record

    def extract_trigger_values_c4(self, lbl_lines: list[str], serial: str) -> list[str] | None:
        """
        Extracts values from I= line for Control4.
        Extrahuje hodnoty z řádku I= pro Control4.
        """
        key_i = f'{serial}I='
        for line in lbl_lines:
            if line.startswith(key_i):
                raw_value = line.split('I=')[1]
                return [val.strip() for val in raw_value.split(';') if val.strip()]

        self.logger.error(f"Řádek \'{key_i}\' nebyl nalezen.")
        self.messenger.show_error('Error', f'Řádek \"{key_i}\" nebyl nalezen.', 'VALIDATOR007', False)
        self.print_window.reset_input_focus()
        return None

    def validate_input_exists_for_control4(self, lbl_lines: list[str], serial: str) -> bool:
        """
        Validates that all key lines for a given serial number exist in lbl_lines.
        Ověří, že existují řádky SERIAL+I=, J=, K= pro daný serial number.

        :param lbl_lines: Seznam řádků z .lbl souboru
        :param serial: Zadaný serial number
        :return: True pokud všechny existují, jinak False + zobrazí warning
        """
        keys = [f'{serial}I=', f'{serial}J=', f'{serial}K=']
        missing_keys = [key for key in keys if not any(line.startswith(key) for line in lbl_lines)]

        if missing_keys:
            joined = ', '.join(missing_keys)
            self.logger.error(f"Nebyly nalezeny všechny klíčové řádky: {joined}")
            self.messenger.show_error('Error', f'Některé klíčové řádky v souboru .lbl chybí!', 'VALIDATOR008', False)
            self.print_window.reset_input_focus()
            return False

        return True

    def extract_my2n_token(self, serial_number: str, reports_path: Path) -> str | None:
        """
        Extracts My2N token from report file.
        Získá My2N token ze souboru s reportem.
        """
        parts = serial_number.split('-')
        if len(parts) != 3:
            self.logger.error(f"Neplatný formát serial number.")
            self.messenger.show_error('Error', f'Neplatný formát serial number.', 'VALIDATOR009', False)
            self.print_window.reset_input_focus()
            return None

        base_code = parts[1] + parts[2]
        file_name = f'{base_code}.{parts[0]}'
        subdir1 = f'20{parts[0]}'
        subdir2 = parts[1]

        source_file = reports_path / subdir1 / subdir2 / file_name
        if not source_file.exists():
            self.logger.error(f"Report soubor {source_file} neexistuje.")
            self.messenger.show_error('Error', f'Report soubor {source_file} neexistuje.', 'VALIDATOR010', False)
            self.print_window.reset_input_focus()
            return None

        try:
            lines = source_file.read_text().splitlines()
            token_line = next((line for line in reversed(lines) if 'my2n token:' in line.lower()), None)
            if not token_line:
                self.logger.error(f"V souboru nebyl nalezen žádný My2N token.")
                self.messenger.show_error('Error', 'V souboru nebyl nalezen žádný My2N token.', 'VALIDATOR011', False)
                self.print_window.reset_input_focus()
                return None

            # 🧠 Find the position of the token in the line (case-insensitive search, but case-sensitive extraction) / Najdi pozici tokenu v řádku (case-insensitive hledání, ale case-sensitive extrakce)
            token_prefix = 'my2n token:'
            lower_line = token_line.lower()
            prefix_index = lower_line.find(token_prefix)

            if prefix_index == -1:
                # Tohle by nemělo nastat, ale pro jistotu
                self.logger.error(f"Chyba při zpracování řádku s tokenem.")
                self.messenger.show_error('Error', 'Chyba při zpracování řádku s tokenem.', 'VALIDATOR012', False)
                self.print_window.reset_input_focus()
                return None

            # ✂️ Extract the token from the original line / Extrahuj token z původního řádku
            token_value = token_line[prefix_index + len(token_prefix):].strip()

            if not token_value:
                self.logger.error(f"My2N token je prázdný.")
                self.messenger.show_error('Error', 'My2N token byl nalezen, ale neobsahuje žádnou hodnotu.', 'VALIDATOR013', False)
                self.print_window.reset_input_focus()
                return None

            return token_value

        except Exception as e:
            self.logger.error(f"Chyba čtení nebo extrakce: {str(e)}")
            self.messenger.show_error('Error', f'{str(e)}', 'VALIDATOR014', False)
            self.print_window.reset_input_focus()
            return None
