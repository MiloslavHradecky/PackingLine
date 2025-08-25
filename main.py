#!/usr/bin/env python3
"""
Main application launcher for the PackingLine system.

Handles initialization of the Qt application, configuration validation,
single-instance enforcement, global styling, and startup sequence including
splash screen and login window.

Version:
    3.0.0.0
"""

__version__ = '3.0.0.0'

# 🧱 Standard library
import sys
from configparser import ConfigParser

# 🧩 Third-party libraries
from PyQt6.QtWidgets import QApplication  # pylint: disable=no-name-in-module

# 🧠 First-party (project-specific)
from views.login_window import LoginWindow
from views.splash_screen import SplashScreen
from controllers.login_controller import LoginController

from utils.window_stack import WindowStackManager
from utils.ensure_logs_dir import ensure_logs_dir
from utils.resources import resource_path, get_writable_path
from utils.system_info import log_system_info
from utils.ensure_config_file import ensure_config_file
from utils.single_instance import SingleInstanceChecker
from utils.messenger import Messenger
from utils.path_validation import PathValidator
from utils.logger import get_logger

ensure_logs_dir()
window_stack = WindowStackManager()  # ✅ Window stack manager for navigation between UI windows


def main():
    """
    Initializes and launches the PackingLine desktop application.

    Performs the following steps:
        - Ensures only one instance of the app is running
        - Applies global stylesheet if available
        - Logs system information and verifies configuration file
        - Validates paths from the config file
        - Displays splash screen and launches login window
        - Starts the Qt event loop
    """
    # 🔒 Single launch check
    checker = SingleInstanceChecker("LinebUniqueAppKey")
    if checker.is_running():
        app = QApplication([])
        messenger = Messenger(None)
        messenger.error("Upozornění - Aplikace už běží!", "Main")
        sys.exit(0)

    app = QApplication([])

    # 🌈 Global style
    style_path = resource_path("views/themes/style.qss")
    if style_path.exists():
        with open(style_path, encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # 📝 Writing system information to the log
    log_system_info(__version__)

    # 💾 Check the config file
    ensure_config_file()

    # 📁 Load and validate config paths
    config = ConfigParser()
    config.read("settings/config.ini")

    validator = PathValidator()
    if not validator.validate():
        messenger = Messenger(None)
        messenger.error("Konfigurace obsahuje neplatné cesty. Aplikace bude ukončena.", "Main")

        # 📌 Logger initialization
        logger = get_logger("Main")

        # 📌 Adding a blank line to the TXT log
        try:
            log_file_txt = get_writable_path("logs/app.txt")
            with open(log_file_txt, "a", encoding="utf-8") as f:
                f.write("\n")
        except (OSError, IOError) as e:
            logger.warning("Nepodařilo se zapsat prázdný řádek do logu: %s", e)

        sys.exit(1)

    # 📌 Show splash screen
    splash = SplashScreen()

    # 📌 Creating a Messenger with the splash parent
    messenger = Messenger(splash)

    def launch_login():
        login_window = LoginWindow()
        login_controller = LoginController(login_window, window_stack)
        login_window.controller = login_controller
        window_stack.push(login_window)
        login_window.effects.fade_in(login_window, duration=2000)

    # 📌 Launch login window
    splash.start(launch_login)

    app.exec()


if __name__ == "__main__":
    main()
