# 🧠 PrintLogicController – handles saving and triggering print actions for different product types

"""
Controller responsible for saving structured output files and triggering label print actions.

Supports multiple product types (Product, Control4, My2N) and uses configuration-defined paths
to write output and create trigger files. Provides logging and user feedback via Messenger.
"""

# 🧱 Standard library
from pathlib import Path

# 🧠 First-party (project-specific)
from utils.logger import get_logger


class PrintLogicController:
    """
    Handles save-and-print logic for different product types.

    Attributes:
        config (ConfigParser): Loaded configuration file.
        messenger (Messenger): Displays messages and errors to the user.
        print_window (PrintWindow): Reference to the active print window.
    """
    def __init__(self, config, messenger, print_window):
        """
        Initializes the logic controller.

        Args:
            config (ConfigParser): Configuration object.
            messenger (Messenger): Messenger instance for user feedback.
            print_window (PrintWindow): UI window reference.
        """
        self.config = config
        self.logger = get_logger("PrintLogicController")
        self.messenger = messenger
        self.print_window = print_window

    def product_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Saves product header and record to output file and creates trigger files.

        Args:
            header (str): Extracted header line.
            record (str): Extracted record line.
            trigger_values (list[str]): List of trigger filenames.
        """
        raw_output_path = self.config.get("ProductPaths", "output_file_path_product")
        if not raw_output_path:
            self.logger.warning("Cesta k výstupnímu souboru product nebyla nalezena.")
            self.messenger.warning("Cesta k výstupnímu souboru product nebyla nalezena.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return

        output_path = Path(raw_output_path)

        try:
            with output_path.open('w') as file:
                file.write(header + '\n')
                file.write(record + '\n')

            trigger_dir = self._get_trigger_dir()
            if not trigger_dir:
                return

            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)

        except Exception as e:
            self.logger.error(f"Chyba zápisu: {str(e)}")
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def control4_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Saves Control4 header and record to output file and creates trigger files.

        Args:
            header (str): Extracted header line.
            record (str): Extracted record line.
            trigger_values (list[str]): List of trigger filenames.
        """
        raw_output_path = self.config.get("Control4Paths", "output_file_path_c4_product")
        if not raw_output_path:
            self.logger.error("Cesta k výstupnímu souboru Control4 nebyla nalezena.")
            self.messenger.error("Cesta k výstupnímu souboru Control4 nebyla nalezena.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return

        output_path = Path(raw_output_path)

        try:
            with output_path.open('w') as file:
                file.write(header + '\n')
                file.write(record + '\n')

            trigger_dir = self._get_trigger_dir()
            if not trigger_dir:
                return

            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)

        except Exception as e:
            self.logger.error(f"Chyba zápisu: {str(e)}")
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def my2n_save_and_print(self, serial_number: str, token: str) -> None:
        """
        Saves My2N serial number and token to output file and creates trigger file.

        Args:
            serial_number (str): Serial number from input.
            token (str): Extracted My2N token.
        """
        raw_output_path = self.config.get("My2nPaths", "output_file_path_my2n")
        if not raw_output_path:
            self.logger.error("Cesta k výstupnímu souboru My2N nebyla nalezena.")
            self.messenger.error("Cesta k výstupnímu souboru My2N nebyla nalezena.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return

        output_path = Path(raw_output_path)

        try:
            with output_path.open('w') as file:
                file.write('"L Vyrobni cislo dlouhe","L Bezpecnostni cislo","P Vyrobni cislo","P Bezpecnostni kod"\n')
                file.write(f'"Serial number:","My2N Security Code:","{serial_number}","{token}"\n')

            trigger_dir = self._get_trigger_dir()
            if not trigger_dir:
                return

            trigger_file = trigger_dir / 'SF_MY2N_A'
            trigger_file.touch(exist_ok=True)

        except Exception as e:
            self.logger.error(f"Chyba zápisu: {str(e)}")
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def _get_trigger_dir(self) -> Path | None:
        """
        Retrieves the trigger directory path from config.

        Returns:
            Path | None: Path object if valid, otherwise None.
        """
        raw_path = self.config.get("Paths", "trigger_path")
        if not raw_path:
            self.logger.error("Trigger path není definován.")
            self.messenger.error("Trigger path není definován.", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return None

        path = Path(raw_path)
        if not path.exists():
            self.logger.error(f"Trigger složka neexistuje: {path}")
            self.messenger.error(f"Trigger složka neexistuje: {path}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()
            return None

        return path
