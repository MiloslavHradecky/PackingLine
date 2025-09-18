"""
📦 Module: print_logic_controller.py

Handles saving structured output files and triggering label print actions.

Supports multiple product types (Product, Control4, My2N) and uses configuration-defined paths.
Provides logging and user feedback via Messenger.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
from pathlib import Path

# 🧠 First-party (project-specific)
from utils.logger import get_logger


class PrintLogicController:
    """
    Executes save-and-print operations for different product types.

    Handles file writing, trigger creation, and error reporting.
    """
    def __init__(self, config, messenger, print_window):
        """
        Initializes logic controller with config, messenger, and print window reference.
        """
        self.config = config
        self.logger = get_logger("PrintLogicController")
        self.messenger = messenger
        self.print_window = print_window

    def product_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Saves product header and record to output file and creates trigger files.

        Handles file overwrite and error reporting.
        """
        raw_output_path = self.config.get("ProductPaths", "output_file_path_product")
        if not raw_output_path:
            self.logger.warning("Cesta k výstupnímu souboru product nebyla nalezena.")
            self.messenger.warning("Cesta k výstupnímu souboru product nebyla nalezena.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return

        output_path = Path(raw_output_path)

        try:
            # 🧹 Delete the file if it exists
            if output_path.exists():
                try:
                    output_path.unlink()
                    self.logger.info("Starý soubor byl smazán: %s", output_path)
                except Exception as delete_error:
                    self.logger.warning("Nepodařilo se smazat soubor %s: %s", output_path, str(delete_error))

            with output_path.open("w") as file:
                file.write(header + "\n")
                file.write(record + "\n")

            trigger_dir = self._get_trigger_dir()
            if not trigger_dir:
                return

            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)

        except Exception as e:
            self.logger.error("Chyba zápisu: %s", str(e))
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def control4_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Saves Control4 header and record to output file and creates trigger files.

        Handles file overwrite and error reporting.
        """
        raw_output_path = self.config.get("Control4Paths", "output_file_path_c4_product")
        if not raw_output_path:
            self.logger.error("Cesta k výstupnímu souboru Control4 nebyla nalezena.")
            self.messenger.error("Cesta k výstupnímu souboru Control4 nebyla nalezena.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return

        output_path = Path(raw_output_path)

        try:
            # 🧹 Delete the file if it exists
            if output_path.exists():
                try:
                    output_path.unlink()
                    self.logger.info("Starý soubor byl smazán: %s", output_path)
                except Exception as delete_error:
                    self.logger.warning("Nepodařilo se smazat soubor %s: %s", output_path, str(delete_error))

            with output_path.open("w") as file:
                file.write(header + "\n")
                file.write(record + "\n")

            trigger_dir = self._get_trigger_dir()
            if not trigger_dir:
                return

            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)

        except Exception as e:
            self.logger.error("Chyba zápisu: %s", str(e))
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def my2n_save_and_print(self, serial_number: str, token: str) -> None:
        """
        Saves My2N serial number and token to output file and creates trigger file.

        Handles file overwrite and error reporting.
        """
        raw_output_path = self.config.get("My2nPaths", "output_file_path_my2n")
        if not raw_output_path:
            self.logger.error("Cesta k výstupnímu souboru My2N nebyla nalezena.")
            self.messenger.error("Cesta k výstupnímu souboru My2N nebyla nalezena.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return

        output_path = Path(raw_output_path)

        try:
            # 🧹 Delete the file if it exists
            if output_path.exists():
                try:
                    output_path.unlink()
                    self.logger.info("Starý soubor byl smazán: %s", output_path)
                except Exception as delete_error:
                    self.logger.warning("Nepodařilo se smazat soubor %s: %s", output_path, str(delete_error))

            with output_path.open("w") as file:
                file.write('"L Vyrobni cislo dlouhe","L Bezpecnostni cislo","P Vyrobni cislo","P Bezpecnostni kod"\n')
                file.write(f'"Serial number:","My2N Security Code:","{serial_number}","{token}"\n')

            trigger_dir = self._get_trigger_dir()
            if not trigger_dir:
                return

            trigger_file = trigger_dir / "SF_MY2N_A"
            trigger_file.touch(exist_ok=True)

        except Exception as e:
            self.logger.error("Chyba zápisu: %s", str(e))
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def _get_trigger_dir(self) -> Path | None:
        """
        Retrieves and validates trigger directory path from config.

        Returns None if path is missing or invalid.
        """
        raw_path = self.config.get("Paths", "trigger_path")
        if not raw_path:
            self.logger.error("Trigger path není definován.")
            self.messenger.error("Trigger path není definován.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return None

        path = Path(raw_path)
        if not path.exists():
            self.logger.error("Trigger složka neexistuje: %s", str(path))
            self.messenger.error(f"Trigger složka neexistuje: {path}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return None

        return path
