"""
📦 Module: login_controller.py

Controller for managing user login in the PackingLine application.

Handles password validation, post-authentication transitions, and process cleanup.
Interacts with the LoginWindow UI and launches the WorkOrderController upon successful login.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser

# 🧠 First-party (project-specific)
import models.user_model

from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path
from utils.login_services import LoginServices


class LoginController:
    """
    Handles login validation and transitions to the work order phase.
    """

    def __init__(self, login_window, window_stack):
        """
        Initializes login logic, UI bindings, and supporting services.
        """
        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Initialization
        self.login_window = login_window
        self.window_stack = window_stack
        self.work_order_controller = None
        self.value_prefix = None
        self.logger = get_logger("LoginController")
        self.messenger = Messenger(self.login_window)
        self.services = LoginServices(config=self.config, messenger=self.messenger)

        # 📌 Linking the button to the method
        self.login_window.login_button.clicked.connect(self.handle_login)
        self.login_window.exit_button.clicked.connect(self.handle_exit)

    def handle_login(self):
        """
        Processes login input and opens the next window if credentials are valid.
        """
        password = self.login_window.password_input.text().strip()
        self.login_window.password_input.clear()

        try:
            if self.services.decrypter.check_login(password):
                self.value_prefix = models.user_model.get_value_prefix()
                self.services.bartender.kill_processes()
                self.open_work_order_window()
            else:
                self.logger.warning("Zadané heslo '%s' není správné!", password)
                self.messenger.warning("Zadané heslo není správné!", "Login Ctrl")
                self.login_window.password_input.clear()
                self.login_window.password_input.setFocus()
        except Exception as e:
            self.logger.error("Neočekávaný problém: %s", str(e))
            self.messenger.error(str(e), "Login Ctrl")
            self.login_window.password_input.clear()
            self.login_window.password_input.setFocus()

    def open_work_order_window(self):
        """
        Instantiates and opens the WorkOrderController window.
        """
        from controllers.work_order_controller import WorkOrderController
        self.work_order_controller = WorkOrderController(self.window_stack)
        self.window_stack.push(self.work_order_controller.work_order_window)

    def handle_exit(self):
        """
        Closes the LoginWindow and exits the application.
        """
        self.logger.info("Aplikace byla ukončena uživatelem.")
        self.login_window.effects.fade_out(self.login_window, duration=1000)
