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
from utils.bartender_utils import BartenderUtils


class LoginController:
    """
    Controller responsible for handling login logic and post-authentication navigation.

    Attributes:
        login_window (LoginWindow): Reference to the login window UI.
        window_stack (WindowStackManager): Manages window transitions.
        config (ConfigParser): Parsed configuration file.
        decrypter (SzvDecrypt): Handles password decryption.
        messenger (Messenger): Displays messages to the user.
        logger (Logger): Logs messages and errors.
    """

    def __init__(self, login_window, window_stack):
        """
        Initializes the LoginController and connects UI event handlers.

        Args:
            login_window (LoginWindow): The login window instance.
            window_stack (WindowStackManager): Stack manager for window navigation.
        """

        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Saving references to application windows
        self.login_window = login_window
        self.window_stack = window_stack
        self.work_order_controller = None

        # 📌 Initializing the 'SzvDecrypt' class to decrypt logins
        self.decrypter = models.user_model.SzvDecrypt()
        self.value_prefix = None

        # 📌 Logger initialization
        self.logger = get_logger("LoginController")

        # 📌 Messenger initialization
        self.messenger = Messenger(self.login_window)

        # 📌 Bartender initialization
        self.bartender = BartenderUtils(messenger=self.messenger)

        # 📌 Linking the button to the method
        self.login_window.login_button.clicked.connect(self.handle_login)
        self.login_window.exit_button.clicked.connect(self.handle_exit)

    def handle_login(self):
        """
        Validates user credentials and navigates to the next window if successful.

        Workflow:
            - Retrieves password from input field
            - Verifies password using SzvDecrypt
            - Terminates BarTender processes
            - Opens WorkOrderWindow on success
            - Shows warning on failure
        """
        password = self.login_window.password_input.text().strip()
        self.login_window.password_input.clear()

        try:
            if self.decrypter.check_login(password):
                self.value_prefix = models.user_model.get_value_prefix()
                self.bartender.kill_processes()
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
        Opens the WorkOrderWindow upon successful login.
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
