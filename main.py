#!/usr/bin/env python3
__version__ = '3.0.0.0'

from PyQt6.QtWidgets import QApplication
from views.login_window import LoginWindow
from controllers.login_controller import LoginController
from views.splash_screen import SplashScreen
from utils.window_stack import WindowStackManager

# 📌 Window stack manager for navigation between UI windows
window_stack = WindowStackManager()


def main():
    """
    Main entry point of the application.

    - Initializes QApplication
    - Creates and displays the LoginWindow
    - Starts application event loop via app.exec()
    """
    app = QApplication([])

    def launch_login():
        login_window = LoginWindow()
        login_controller = LoginController(login_window, window_stack)
        login_window.controller = login_controller
        window_stack.push(login_window)
        login_window.effects.fade_in(login_window, duration=2000)

    # 📌 Show splash screen and then launch login window
    splash = SplashScreen()
    splash.start(launch_login)

    app.exec()


if __name__ == "__main__":
    """
    Checks if script is run directly (not imported).
    Spustí aplikaci pouze při přímém spuštění (ne importem jako modul).
    """
    main()
