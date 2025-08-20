from pathlib import Path
from utils.logger import get_logger
import time


class PrintLogicController:
    def __init__(self, config, messenger, print_window, finalize_callback):
        self.config = config
        self.logger = get_logger("PrintLogicController")
        self.messenger = messenger
        self.print_window = print_window
        self.finalize = finalize_callback  # ✅ method from the main controller

    def product_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Extracts header and record for the scanned serial number and writes them to product output file.

            :param header: extracted header line
            :param record: extracted record line
            :param trigger_values: list of trigger filenames
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

            self.messenger.show_progress_box("Zahajuji tisk etiket...", timeout_ms=5000)

            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)

            time.sleep(5)
            self.messenger.close_progress_box()
            self.finalize()

        except Exception as e:
            self.logger.error(f"Chyba zápisu: {str(e)}")
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def control4_save_and_print(self, header: str, record: str, trigger_values: list[str]) -> None:
        """
        Extracts header and record for the scanned serial number and writes them to Control4 output file.

            - Searches for lines beginning with: SERIAL+I= and SERIAL+J= and SERIAL+K=
            - If it finds both the header and the record, it writes them to the output file.

            :param header: extracted header line
            :param record: extracted record line
            :param trigger_values: list of trigger filenames
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

            self.messenger.show_progress_box("Zahajuji tisk etiket pro Control4...", timeout_ms=5000)

            for value in trigger_values:
                target_file = trigger_dir / value
                target_file.touch(exist_ok=True)

            time.sleep(5)
            self.messenger.close_progress_box()
            self.finalize()

        except Exception as e:
            self.logger.error(f"Chyba zápisu: {str(e)}")
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def my2n_save_and_print(self, serial_number: str, token: str) -> None:
        """
        Writes extracted My2N token and serial number to output file and creates trigger file.

            :param serial_number: serial number from input
            :param token: extracted My2N token
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

            self.messenger.show_progress_box("Zahajuji tisk etikety pro My2N...", timeout_ms=5000)

            trigger_file = trigger_dir / 'SF_MY2N_A'
            trigger_file.touch(exist_ok=True)

            time.sleep(5)
            self.messenger.close_progress_box()
            self.finalize()

        except Exception as e:
            self.logger.error(f"Chyba zápisu: {str(e)}")
            self.messenger.error(f"Chyba zápisu: {str(e)}", "Print Logic Ctrl")
            self.print_window.reset_input_focus()

    def _get_trigger_dir(self) -> Path | None:
        """
        Returns trigger directory path from config.
        """
        raw_path = self.config.get("Paths", "trigger_path")
        if not raw_path:
            self.logger.error("Trigger path není definován.")
            self.messenger.error("Trigger path není definován.", "Print Logic Ctrl")
            self.messenger.close_progress_box()
            self.print_window.reset_input_focus()
            return None

        path = Path(raw_path)
        if not path.exists():
            self.logger.error(f"Trigger složka neexistuje: {path}")
            self.messenger.error(f"Trigger složka neexistuje: {path}", "Print Logic Ctrl")
            self.messenger.close_progress_box()
            self.print_window.reset_input_focus()
            return None

        return path
