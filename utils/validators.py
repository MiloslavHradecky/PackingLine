"""
📦 Module: validators.py

Validator module for checking input formats, extracting values from .lbl files,
and injecting data into records. Provides error logging and user messaging.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import re
from pathlib import Path

# 🧠 First-party
from utils.logger import get_logger
from utils.messenger import Messenger
from models.user_model import get_value_prefix


class Validator:
    """
    Validator class for checking input formats, extracting structured data from .lbl files,
    and injecting values into records. Provides error logging and user feedback via Messenger.

    Attributes:
        print_window: UI window reference for user interaction.
        messenger (Messenger): Handles user-facing messages.
        logger: Logger instance for internal diagnostics.
    """

    def __init__(self, print_window):
        """
        Initializes the Validator with UI window, logger, and messenger.

        Args:
            print_window: Reference to the UI window for user interaction.
        """
        self.print_window = print_window

        # 📌 Messenger initialization
        self.messenger = Messenger(self.print_window)

        # 📌 Logger initialization
        self.logger = get_logger("Validators")

    def validate_serial_format(self, serial_number: str) -> bool:
        """
        Validates the serial number format "00-0000-0000".

        Args:
            serial_number (str): Serial number to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        pattern = r"^\d{2}-\d{4}-\d{4}$"
        if not re.fullmatch(pattern, serial_number):
            self.messenger.info("Serial number must be in format 00-0000-0000.", "Validators")
            self.print_window.reset_input_focus()
            return False
        return True

    def validate_input_exists_for_product(self, lbl_lines: list[str], serial: str) -> bool:
        """
        Validates that required lines (B=, D=, E=) exist for a given serial number.

        Args:
            lbl_lines (list[str]): Lines from the .lbl file.
            serial (str): Serial number to check.

        Returns:
            bool: True if all lines exist, False otherwise.
        """
        keys = [f"{serial}B=", f"{serial}D=", f"{serial}E="]
        missing_keys = [key for key in keys if not any(line.startswith(key) for line in lbl_lines)]

        if missing_keys:
            joined = ", ".join(missing_keys)
            self.logger.error("Nebyly nalezeny všechny klíčové řádky: %s, sn nepatří k příkazu!", joined)
            self.messenger.error("Některé klíčové řádky v souboru .lbl chybí, sn nepatří k příkazu!", "Validators")
            self.print_window.reset_input_focus()
            return False

        return True

    def validate_and_inject_balice(self, header: str, record: str) -> str | None:
        """
        Injects prefix into the "P Znacka balice" field in the record.

        Args:
            header (str): Header line from .lbl file.
            record (str): Record line from .lbl file.

        Returns:
            str | None: Modified record or None if injection fails.
        """
        header_fields = header.split('","')
        record_fields = record.split('","')

        try:
            index = header_fields.index("P Znacka balice")
            if index >= len(record_fields):
                self.logger.error("Neplatný index pole 'P Znacka balice'")
                self.messenger.error("Neplatný index pole v record.", "Validators")
                self.print_window.reset_input_focus()
                return None

            prefix = get_value_prefix()
            record_fields[index] = prefix
            return '","'.join(record_fields)

        except ValueError:
            self.logger.error("Pole 'P Znacka balice' chybí.")
            self.messenger.error("Pole v header nebylo nalezeno.", "Validators")
            self.print_window.reset_input_focus()
            return None

    def extract_header_and_record(self, lbl_lines: list[str], serial: str) -> tuple[str, str] | None:
        """
        Extracts D= and E= lines for a given serial number.

        Args:
            lbl_lines (list[str]): Lines from the .lbl file.
            serial (str): Serial number to extract.

        Returns:
            tuple[str, str] | None: Header and record if found, else None.
        """
        key_d = f"{serial}D="
        key_e = f"{serial}E="
        header = None
        record = None

        for line in lbl_lines:
            if line.startswith(key_d):
                header = line.split("D=")[1].strip()
            elif line.startswith(key_e):
                record = line.split("E=")[1].strip()

        if not header or not record:
            self.logger.error("Nebyly nalezeny hlavička nebo záznam pro '%s'.", serial)
            self.messenger.error(f"Nebyly nalezeny hlavička nebo záznam pro '{serial}'.", "Validators")
            self.print_window.reset_input_focus()
            return None

        return header, record

    def extract_trigger_values(self, lbl_lines: list[str], serial: str) -> list[str] | None:
        """
        Extracts values from B= line for a given serial number.

        Args:
            lbl_lines (list[str]): Lines from the .lbl file.
            serial (str): Serial number to extract.

        Returns:
            list[str] | None: List of values or None if not found.
        """
        key_b = f"{serial}B="
        for line in lbl_lines:
            if line.startswith(key_b):
                raw_value = line.split("B=")[1]
                values = [val.strip() for val in raw_value.split(";") if val.strip()]
                return values

        self.logger.error("Řádek '%s' nebyl nalezen.", key_b)
        self.messenger.error(f"Řádek \'{key_b}\' nebyl nalezen.", "Validators")
        self.print_window.reset_input_focus()
        return None

    def extract_header_and_record_c4(self, lbl_lines: list[str], serial: str) -> tuple[str, str] | None:
        """
        Extracts J= and K= lines for Control4 serial number.

        Args:
            lbl_lines (list[str]): Lines from the .lbl file.
            serial (str): Serial number to extract.

        Returns:
            tuple[str, str] | None: Header and record if found, else None.
        """
        key_j = f"{serial}J="
        key_k = f"{serial}K="
        header = None
        record = None

        for line in lbl_lines:
            if line.startswith(key_j):
                header = line.split("J=")[1].strip()
            elif line.startswith(key_k):
                record = line.split("K=")[1].strip()

        if not header or not record:
            self.logger.error("Nebyly nalezeny J/K řádky pro serial '%s'.", serial)
            self.messenger.error(f"Nebyly nalezeny J/K řádky pro serial '{serial}'.", "Validators")
            self.print_window.reset_input_focus()
            return None

        return header, record

    def extract_trigger_values_c4(self, lbl_lines: list[str], serial: str) -> list[str] | None:
        """
        Extracts values from I= line for Control4 serial number.

        Args:
            lbl_lines (list[str]): Lines from the .lbl file.
            serial (str): Serial number to extract.

        Returns:
            list[str] | None: List of values or None if not found.
        """
        key_i = f"{serial}I="
        for line in lbl_lines:
            if line.startswith(key_i):
                raw_value = line.split("I=")[1]
                return [val.strip() for val in raw_value.split(";") if val.strip()]

        self.logger.error("Řádek '%s' nebyl nalezen.", key_i)
        self.messenger.error(f"Řádek \'{key_i}\' nebyl nalezen.", "Validators")
        self.print_window.reset_input_focus()
        return None

    def validate_input_exists_for_control4(self, lbl_lines: list[str], serial: str) -> bool:
        """
        Validates that required lines (I=, J=, K=) exist for Control4 serial number.

        Args:
            lbl_lines (list[str]): Lines from the .lbl file.
            serial (str): Serial number to check.

        Returns:
            bool: True if all lines exist, False otherwise.
        """
        keys = [f"{serial}I=", f"{serial}J=", f"{serial}K="]
        missing_keys = [key for key in keys if not any(line.startswith(key) for line in lbl_lines)]

        if missing_keys:
            joined = ", ".join(missing_keys)
            self.logger.error("Nebyly nalezeny všechny klíčové řádky: %s", joined)
            self.messenger.error("Některé klíčové řádky v souboru .lbl chybí!", "Validators")
            self.print_window.reset_input_focus()
            return False

        return True

    def extract_my2n_token(self, serial_number: str, reports_path: Path) -> str | None:
        """
        Extracts the My2N token from a report file based on the serial number.

        The method constructs the expected file path using the serial number format "00-0000-0000",
        then searches the file for a line containing "my2n token:" (case-insensitive).
        If found, it extracts and returns the token value.

        Args:
            serial_number (str): Serial number in format "00-0000-0000".
            reports_path (Path): Base path to the reports directory.

        Returns:
            str | None: Extracted token string if found, otherwise None.
        """
        parts = serial_number.split("-")
        if len(parts) != 3:
            self.logger.error("Neplatný formát serial number.")
            self.messenger.error("Neplatný formát serial number.", "Validators")
            self.print_window.reset_input_focus()
            return None

        base_code = parts[1] + parts[2]
        file_name = f"{base_code}.{parts[0]}"
        subdir1 = f"20{parts[0]}"
        subdir2 = parts[1]

        source_file = reports_path / subdir1 / subdir2 / file_name
        if not source_file.exists():
            self.logger.error("Report soubor %s neexistuje.", str(source_file))
            self.messenger.error(f"Report soubor {source_file} neexistuje.", "Validators")
            self.print_window.reset_input_focus()
            return None

        try:
            lines = source_file.read_text().splitlines()
            token_line = next((line for line in reversed(lines) if "my2n token:" in line.lower()), None)
            if not token_line:
                self.logger.error("V souboru nebyl nalezen žádný My2N token.")
                self.messenger.error("V souboru nebyl nalezen žádný My2N token.", "Validators")
                self.print_window.reset_input_focus()
                return None

            # 🧠 Find the position of the token in the line (case-insensitive search, but case-sensitive extraction)
            token_prefix = "my2n token:"
            lower_line = token_line.lower()
            prefix_index = lower_line.find(token_prefix)

            if prefix_index == -1:
                # 📌 This should not happen, but just to be sure
                self.logger.error("Chyba při zpracování řádku s tokenem.")
                self.messenger.error("Chyba při zpracování řádku s tokenem.", "Validators")
                self.print_window.reset_input_focus()
                return None

            # ✂️ Extract the token from the original line
            token_value = token_line[prefix_index + len(token_prefix):].strip()

            if not token_value:
                self.logger.error("My2N token je prázdný.")
                self.messenger.error("My2N token byl nalezen, ale neobsahuje žádnou hodnotu.", "Validators")
                self.print_window.reset_input_focus()
                return None

            return token_value

        except Exception as e:
            self.logger.error("Chyba čtení nebo extrakce: %s", str(e))
            self.messenger.error(f"{str(e)}", "Validators")
            self.print_window.reset_input_focus()
            return None
