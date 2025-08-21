#!/usr/bin/env python3
__version__ = '3.0.0.0'

import sys
from PyQt6.QtWidgets import QApplication
from views.login_window import LoginWindow
from controllers.login_controller import LoginController
from views.splash_screen import SplashScreen
from utils.window_stack import WindowStackManager
from utils.ensure_logs_dir import ensure_logs_dir
from utils.resources import resource_path, get_writable_path
from utils.system_info import log_system_info
from utils.ensure_config_file import ensure_config_file
from utils.single_instance import SingleInstanceChecker
from utils.messenger import Messenger
from configparser import ConfigParser
from utils.path_validation import PathValidator
from utils.logger import get_logger

ensure_logs_dir()
window_stack = WindowStackManager()  # ✅ Window stack manager for navigation between UI windows


def main():
    """
    Main entry point of the application.

    - Initializes QApplication
    - Creates and displays the LoginWindow
    - Starts application event loop via app.exec()
    """
    # 🔒 Single launch check
    checker = SingleInstanceChecker("LinebUniqueAppKey")
    if checker.is_running():
        app = QApplication([])
        messenger = Messenger(None)
        messenger.error(f"Upozornění - Aplikace už běží!", "Main")
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
        messenger.error(f"Konfigurace obsahuje neplatné cesty. Aplikace bude ukončena.", "Main")

        # 📌 Logger initialization
        logger = get_logger("Main")

        # 📌 Adding a blank line to the TXT log
        try:
            log_file_txt = get_writable_path("logs/app.txt")
            with open(log_file_txt, "a", encoding="utf-8") as f:
                f.write("\n")
        except Exception as e:
            logger.warning(f"Nepodařilo se zapsat prázdný řádek do logu: {e}")

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
    """
    Checks if script is run directly (not imported).
    """
    main()
