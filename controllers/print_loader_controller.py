# 📦 PrintLoaderController – handles loading of .lbl files based on config and order code

from pathlib import Path
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path
import configparser


class PrintLoaderController:
    def __init__(self, messenger: Messenger):
        """
        Initializes loader with config and messenger for user feedback.
        """
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(config_path)

        self.messenger = messenger
        self.logger = get_logger("PrintLoaderController")

    def load_lbl_file(self, order_code: str, reset_focus_callback=None) -> list[str]:
        """
        Loads the .lbl file based on order_code and config path.

        :param order_code: Order code to locate the file
        :param reset_focus_callback: Optional callback to reset input focus
        :return: List of lines or empty list if not found
        """
        raw_orders_path = self.config.get("Paths", "orders_path", fallback="")

        if not raw_orders_path:
            self.logger.error(f"Konfigurační cesta {raw_orders_path} nebyla nalezena!")
            self.messenger.error(f"Konfigurační cesta {raw_orders_path} nebyla nalezena!", "Print Loader Ctrl")
            if reset_focus_callback:
                reset_focus_callback()
            return []

        lbl_file = Path(raw_orders_path) / f"{order_code}.lbl"

        if not lbl_file.exists():
            self.logger.warning(f"Soubor {lbl_file} neexistuje.")
            self.messenger.warning(f"Soubor {lbl_file} neexistuje.", "Print Loader Ctrl")
            if reset_focus_callback:
                reset_focus_callback()
            return []

        try:
            return lbl_file.read_text().splitlines()
        except Exception as e:
            self.logger.error(f"Chyba načtení souboru: {str(e)}")
            self.messenger.error(f"Chyba načtení souboru: {str(e)}", "Print Loader Ctrl")
            if reset_focus_callback:
                reset_focus_callback()
            return []
