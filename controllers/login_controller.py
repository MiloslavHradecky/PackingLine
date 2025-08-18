import configparser
import model.user_model
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path, resolve_path, get_writable_path


class LoginController:
    """
    The main control class of the application.
    """

    def __init__(self, login_window, window_stack):
        """
        Initializes the 'LoginController' and sets its main attributes.
            :param login_window: Reference to the login window ('LoginWindow')
        """

        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Saving references to application windows
        self.login_window = login_window
        self.window_stack = window_stack
        self.main_window = None
        self.product_window = None
        self.option_controller = None

        # 📌 Initializing the 'SzvDecrypt' class to decrypt logins
        self.decrypter = model.user_model.SzvDecrypt()
        self.selection_value_product = None
        self.value_prefix = None

        # 📌 Logger initialization
        self.logger = get_logger("LoginController")

        # 📌 Messenger initialization
        self.progress_box = None

        # 📌 Linking the button to the method
        self.login_window.login_button.clicked.connect(self.handle_login)
        self.login_window.exit_button.clicked.connect(self.handle_exit)

    def handle_login(self):
        """
        Verifies the login password and authenticates the user.
            - Retrieves the entered password from the 'LoginWindow'
            - Verifies the password is correct using 'SzvDecrypt'
            - On successful login, opens the 'ProductWindow'
            - If an error occurs, displays a warning to the user
        """
        password = self.login_window.input_password.text().strip()
        self.login_window.input_password.clear()

        try:
            if self.decrypter.check_login(password):
                self.value_prefix = model.user_model.get_value_prefix()
                self.open_option_window()
            else:
                self.logger.warning(f'Zadané heslo "{password}" není správné!')
                Messenger.warning("Zadané heslo není správné!", "Login Ctrl")
                self.login_window.input_password.clear()
                self.login_window.input_password.setFocus()
        except Exception as e:
            self.logger.error(f'Neočekávaný problém: {str(e)}')
            Messenger.error(str(e), "Login Ctrl")
            self.login_window.input_password.clear()
            self.login_window.input_password.setFocus()

    def open_option_window(self):
        """
        Opens the 'OptionWindow' for product selection.

            - After successful login, the 'LoginWindow' will close
            - 'OptionWindow' stores a reference to 'ControllerApp'
        """

        # 📌 Loading paths to files
        raw_path = self.config.get('Paths', 'archiv_file_path')
        archiv_path = resolve_path(raw_path)

        # 📌 Check for the existence of the folder and create it if it does not exist
        if not archiv_path.exists():
            archiv_path.mkdir(parents=True, exist_ok=True)

        from controller.option_controller import OptionController
        self.option_controller = OptionController(self.window_stack)
        self.window_stack.push(self.option_controller.option_window)

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
