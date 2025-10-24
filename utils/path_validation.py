"""
📦 Module: path_validation.py

Utility for validating file and directory paths defined in the configuration file.

Responsibilities:
    - Load paths from the [Paths] section of config.ini
    - Check existence of each path or file
    - Log missing or invalid entries
    - Notify user via Messenger dialogs

Used during startup or diagnostics to ensure environment integrity.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser

# 🧠 First-party
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path


class PathValidator:
    """
    🧭 Validates critical paths defined in the configuration file.

    Checks whether required files and directories exist, logs issues,
    and displays warnings to the user via Messenger.
    """

    def __init__(self):
        """
        Initializes the PathValidator by loading config and preparing logger/messenger.
        """

        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        self.logger = get_logger("PathValidator")
        self.messenger = Messenger()
        self.keys = [
            "reports_path",
            "orders_path",
            "trigger_path",
            "szv_input_file",
            "bartender_path",
            "commander_path",
            "guardian_path"
        ]
        self.missing = []

    def validate(self) -> bool:
        """
        Validates the existence of all required paths from the config.

        Returns:
            bool: True if all paths are valid, False otherwise.
        """
        for key in self.keys:
            try:
                raw = self.config.get("Paths", key)
                path = get_config_path(raw)
                if not path.exists():
                    self.logger.warning("Cesta nebo soubor neexistuje: %s → %s", key, path)
                    self.messenger.warning(f"Cesta nebo soubor neexistuje:\n{path}", "Path Validation")
                    self.missing.append((key, path))
            except Exception as e:
                self.logger.error("Chyba při čtení %s: %s", key, str(e))
                self.messenger.error(f"Chyba při čtení '{key}': {e}", "Path Validation")
                self.missing.append((key, "chyba v configu"))

        if self.missing:
            self.messenger.error("Následující cesty jsou neplatné nebo chybí soubor:", "Path Validation")
            for key, path in self.missing:
                self.messenger.error(f"\n{key}\n{path}", "Path Validation")
            return False

        self.logger.info("Všechny cesty v configu jsou validní.")
        return True
