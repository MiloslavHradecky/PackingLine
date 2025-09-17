"""
📦 Module: print_loader_controller.py

Controller responsible for loading .lbl files based on order code and configuration.

Provides error handling, logging, and user feedback via Messenger. Used by PrintController
to retrieve label data for further processing.

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
    Loads .lbl files from disk using configuration-defined paths.

    Attributes:
        config (ConfigParser): Loaded configuration file.
        messenger (Messenger): Displays messages and warnings to the user.
        logger (Logger): Logs events and errors.
    """
    def __init__(self, messenger: Messenger):
        """
        Initializes the loader with configuration and messenger.

        Args:
            messenger (Messenger): Messenger instance for user feedback.
        """
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(config_path)

        self.messenger = messenger
        self.logger = get_logger("PrintLoaderController")

    def load_lbl_file(self, order_code: str, reset_focus_callback=None) -> list[str]:
        """
        Loads a .lbl file based on the given order code.

        Args:
            order_code (str): Order code used to locate the .lbl file.
            reset_focus_callback (Callable, optional): Callback to reset UI focus.

        Returns:
            list[str]: List of lines from the .lbl file, or empty list if not found or error occurs.
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
