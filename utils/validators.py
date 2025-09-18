"""
📦 Module: validators.py

Validates input formats, extracts values from .lbl files, and injects data into records.
Provides error logging and user messaging. Used during the print workflow.

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
    Validates serial formats and extracts structured data from .lbl files.
    Handles missing fields, injection logic, and user feedback.
    """

    def __init__(self, print_window):
        """
        Initializes validator with UI window, messenger, and logger.
        """
        # 📌 Initialization
        self.print_window = print_window
        self.messenger = Messenger(self.print_window)
        self.logger = get_logger("Validators")

    def validate_serial_format(self, serial_number: str) -> bool:
        """
        Checks if serial number matches expected format "00-0000-0000".
        Shows message and resets focus on failure.
        """
        pattern = r"^\d{2}-\d{4}-\d{4}$"
        if not re.fullmatch(pattern, serial_number):
            self.messenger.info("Serial number must be in format 00-0000-0000.", "Validators")
            self.print_window.reset_input_focus()
            return False
        return True

    def validate_input_exists_for_product(self, lbl_lines: list[str], serial: str) -> bool:
        """
        Checks if B=, D=, and E= lines exist for the given serial number.
        Logs and alerts if any are missing.
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
        Injects value prefix into 'P Znacka balice' field in the record.
        Returns modified record or None on failure.
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
        Extracts D= and E= lines for the given serial number.
        Returns header and record tuple or None if missing.
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
        Extracts values from B= line for the given serial number.
        Returns list of values or None if line is missing.
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
        Returns header and record tuple or None if missing.
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
        Returns list of values or None if line is missing.
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
        Checks if I=, J=, and K= lines exist for Control4 serial number.
        Logs and alerts if any are missing.
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
        Extracts My2N token from report file based on serial number.

        Searches for 'my2n token:' line and returns extracted value.
        Returns None if file is missing or token not found.
        """
        def abort_token_extraction(message: str) -> None:
            self.logger.error(message)
            self.messenger.error(message, "Validators")
            self.print_window.reset_input_focus()

        sn_parts = serial_number.split("-")
        if len(sn_parts) != 3:
            return abort_token_extraction("Neplatný formát serial number.")

        base_code = sn_parts[1] + sn_parts[2]
        source_file = reports_path / f"20{sn_parts[0]}" / sn_parts[1] / f"{base_code}.{sn_parts[0]}"

        if not source_file.exists():
            return abort_token_extraction(f"Report soubor {source_file} neexistuje.")

        try:
            lines = source_file.read_text().splitlines()
            token_line = next((line for line in reversed(lines) if "my2n token:" in line.lower()), None)
            if not token_line:
                return abort_token_extraction("V souboru nebyl nalezen žádný My2N token.")

            # 🧠 Find the position of the token in the line (case-insensitive search, but case-sensitive extraction)
            prefix_index = token_line.lower().find("my2n token:")
            if prefix_index == -1:
                return abort_token_extraction("Chyba při zpracování řádku s tokenem.")

            # ✂️ Extract the token from the original line
            token_value = token_line[prefix_index + len("my2n token:"):].strip()
            if not token_value:
                return abort_token_extraction("My2N token byl nalezen, ale neobsahuje žádnou hodnotu.")

            return token_value

        except Exception as e:
            return abort_token_extraction(f"Chyba čtení nebo extrakce: {str(e)}")
