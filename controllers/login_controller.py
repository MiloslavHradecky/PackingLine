# 🎛️ LoginController – handles login logic and post-authentication navigation

import subprocess
import configparser
import models.user_model
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path, get_writable_path


class LoginController:
    """
    Main controller for the login process.
    """

    def __init__(self, login_window, window_stack):
        """
        Initializes the LoginController and connects event handlers.

            :param login_window: Reference to LoginWindow
            :param window_stack: WindowStackManager for screen navigation
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
        self.selection_value_product = None
        self.value_prefix = None

        # 📌 Logger initialization
        self.logger = get_logger("LoginController")

        # 📌 Messenger initialization
        self.messenger = Messenger(self.login_window)
        self.progress_box = None

        # 📌 Linking the button to the method
        self.login_window.login_button.clicked.connect(self.handle_login)
        self.login_window.exit_button.clicked.connect(self.handle_exit)

    def kill_bartender_processes(self):
        """
        Terminates all running BarTender instances (Cmdr.exe and bartend.exe).
        """
        try:
            subprocess.run('taskkill /f /im cmdr.exe 1>nul 2>nul', shell=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run('taskkill /f /im bartend.exe 1>nul 2>nul', shell=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Chyba při ukončování BarTender procesů: {str(e)}")
            self.messenger.error(f"Chyba při ukončování BarTender procesů: {str(e)}", "Login Ctrl")

    def handle_login(self):
        """
        Handles login validation and user authentication.

            - Retrieves password from LoginWindow
            - Verifies password via SzvDecrypt
            - Opens WorkOrderWindow if successful
            - Shows warning on failure
        """
        password = self.login_window.password_input.text().strip()
        self.login_window.password_input.clear()

        try:
            if self.decrypter.check_login(password):
                self.value_prefix = models.user_model.get_value_prefix()
                self.kill_bartender_processes()
                self.open_work_order_window()
            else:
                self.logger.warning(f'Zadané heslo "{password}" není správné!')
                self.messenger.warning("Zadané heslo není správné!", "Login Ctrl")
                self.login_window.password_input.clear()
                self.login_window.password_input.setFocus()
        except Exception as e:
            self.logger.error(f'Neočekávaný problém: {str(e)}')
            self.messenger.error(str(e), "Login Ctrl")
            self.login_window.password_input.clear()
            self.login_window.password_input.setFocus()

    def open_work_order_window(self):
        """
        Opens the WorkOrderWindow upon successful login.

            - Fades out login window
            - Pushes next window to stack
        """
        from controllers.work_order_controller import WorkOrderController
        self.work_order_controller = WorkOrderController(self.window_stack)
        self.window_stack.push(self.work_order_controller.work_order_window)

    def handle_exit(self):
        """Closes the LoginWindow and exits the application."""
        self.logger.info("Aplikace byla ukončena uživatelem.")
        self.login_window.effects.fade_out(self.login_window, duration=3000)

        # 📌 Adding a blank line to the TXT log
        try:
            log_file_txt = get_writable_path("logs/app.txt")
            with open(log_file_txt, "a", encoding="utf-8") as f:
                f.write("\n")
        except Exception as e:
            self.logger.warning(f"Nepodařilo se zapsat prázdný řádek do logu: {e}")
