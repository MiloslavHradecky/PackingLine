# 🎛️ LoginController – handles login logic and post-authentication navigation

# 🧱 Standard library
import subprocess
import configparser

# 🧩 Third-party libraries
# (none in this file)

# 🧠 First-party (project-specific)
from models.user_model import SzvDecrypt, get_value_prefix
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path, get_writable_path


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

        # 📌 Adding a blank line to the TXT log
        try:
            log_file_txt = get_writable_path("logs/app.txt")
            with open(log_file_txt, "a", encoding="utf-8") as f:
                f.write("\n")
        except Exception as e:
            self.logger.warning(f"Nepodařilo se zapsat prázdný řádek do logu: {e}")
