"""
Utility for ensuring the existence of the application's configuration file.

If the config file is missing, this module creates it with default sections and values
required for the PackingLine system to operate correctly.
"""

# 🧱 Standard library
import sys

# 🧠 First-party (project-specific)
from utils.resources import get_config_path
from utils.logger import get_logger
from utils.messenger import Messenger


class ConfigFileChecker:
    def __init__(self, filename="config.ini"):
        self.config_path = get_config_path(filename)
        self.logger = get_logger("ConfigFileChecker")
        self.messenger = Messenger("ConfigFileChecker")

    def check_exists_or_exit(self):
        if not self.config_path.exists():
            self.logger.error("Konfigurační soubor chybí: %s", self.config_path)
            self.messenger.error("Konfigurační soubor nebyl nalezen. Aplikace bude ukončena.", "ConfigFileChecker")
            sys.exit(1)
        else:
            self.logger.info("Konfigurační soubor nalezen: %s", self.config_path)
