"""
📦 Module: print_loader_controller.py

Loads .lbl files based on order code and configuration.

Provides error handling, logging, and user feedback via Messenger.
Used by PrintController to retrieve label data for further processing.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser
from pathlib import Path

# 🧠 First-party (project-specific)
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path


class PrintLoaderController:
    """
    Loads .lbl files from disk using configured paths.

    Handles missing files, read errors, and provides user feedback.
    """
    def __init__(self, messenger: Messenger):
        """
        Initializes loader with config and messenger for error reporting.
        """
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(config_path)

        self.messenger = messenger
        self.logger = get_logger("PrintLoaderController")

    def load_lbl_file(self, order_code: str, reset_focus_callback=None) -> list[str]:
        """
        Loads .lbl file for the given order code.

        Handles missing paths, file absence, and read errors.
        Returns list of lines or empty list on failure.
        """
        raw_orders_path = self.config.get("Paths", "orders_path", fallback="")

        if not raw_orders_path:
            self.logger.error("Konfigurační cesta %s nebyla nalezena!", raw_orders_path)
            self.messenger.error(f"Konfigurační cesta {raw_orders_path} nebyla nalezena!", "Print Loader Ctrl")
            if reset_focus_callback:
                reset_focus_callback()
            return []

        lbl_file = Path(raw_orders_path) / f"{order_code}.lbl"

        if not lbl_file.exists():
            self.logger.warning("Soubor %s neexistuje.", lbl_file)
            self.messenger.warning(f"Soubor {lbl_file} neexistuje.", "Print Loader Ctrl")
            if reset_focus_callback:
                reset_focus_callback()
            return []

        try:
            return lbl_file.read_text().splitlines()
        except Exception as e:
            self.logger.error("Chyba načtení souboru: %s", str(e))
            self.messenger.error(f"Chyba načtení souboru: {str(e)}", "Print Loader Ctrl")
            if reset_focus_callback:
                reset_focus_callback()
            return []
