# 🧭 WorkOrderController – Manages scanning logic and transitions to printing

"""
Controller responsible for handling work order input, validating associated files,
and transitioning to the print phase. Also manages launching BarTender Commander
and terminating related processes.
"""

# 🧱 Standard library
import subprocess
import configparser
from pathlib import Path

# 🧠 First-party (project-specific)
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path
from views.work_order_window import WorkOrderWindow


class WorkOrderController:
    """
    Handles scanning logic, file validation, and transition to PrintController.

    Attributes:
        config (ConfigParser): Loaded configuration file.
        window_stack (WindowStackManager): Navigation stack for UI windows.
        work_order_window (WorkOrderWindow): UI window for work order input.
        messenger (Messenger): Displays messages and errors to the user.
        logger (Logger): Logs events and errors.
        orders_dir (Path): Directory containing .lbl and .nor files.
        lbl_file (Path): Path to the .lbl file.
        nor_file (Path): Path to the .nor file.
        lines (list[str]): Parsed lines from .lbl file.
    """

    def __init__(self, window_stack):
        """
        Initializes controller logic, event binding, and config loading.

        Args:
            window_stack (WindowStackManager): UI navigation stack.
        """
        # 📌 Loading the configuration file
        config_path = get_config_path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Saving references to application windows
        self.window_stack = window_stack
        self.work_order_window = WorkOrderWindow(controller=self)
        self.print_controller = None
        self.print_window = None

        # 🔔 User feedback system
        self.messenger = Messenger(self.work_order_window)

        # 📂 Paths and file references
        self.orders_dir = None
        self.lbl_file = None
        self.nor_file = None

        # 📄 Parsed data
        self.lines = None

        # 📌 Logger initialization
        self.logger = get_logger("WorkOrderController")

        # 📌 Linking the button to the method
        self.work_order_window.next_button.clicked.connect(self.work_order_button_click)
        self.work_order_window.exit_button.clicked.connect(self.handle_exit)

    def run_bartender_commander(self) -> None:
        """
        Launches BarTender Commander via system process.
        """
        commander_path = self.config.get("Paths", "commander_path")
        tl_file_path = self.config.get("Paths", "tl_file_path")

        if not commander_path or not tl_file_path:
            self.logger.error("Cesty k BarTender Commanderu nejsou dostupné v config.ini")
            self.messenger.error("Cesty k BarTender Commanderu nejsou dostupné v config.ini", "Work Order Ctrl")
            return

        try:
            # pylint: disable=consider-using-with
            process = subprocess.Popen([str(commander_path), "/START", "/MIN=SystemTray", "/NOSPLASH", str(tl_file_path)], shell=True)

            self.logger.info(f"BarTender Commander spuštěn: {process.pid}")

        except Exception as e:
            self.logger.error(f"Chyba při spuštění BarTender Commanderu: {str(e)}")
            self.messenger.error(f"Chyba při spuštění BarTender Commanderu: {str(e)}", "Work Order Ctrl")

    def work_order_button_click(self):
        """
        Triggered on 'Continue' click.

            - Validates input
            - Checks .lbl and .nor file existence
            - Parses .nor file and validates order
            - Loads label content and launches PrintController
        """

        # 📌 Processing of input
        value_input = self.work_order_window.work_order_input.text().strip().upper()
        if not value_input:
            self.messenger.warning("Zadejte prosím výrobní příkaz!", "Work Order Ctrl")
            self.reset_input_focus()
            return

        # 📁 Construct paths
        self.orders_dir = Path("T:/Prikazy")
        self.lbl_file = self.orders_dir / f"{value_input}.lbl"
        self.nor_file = self.orders_dir / f"{value_input}.nor"

        # ❌ If file not found
        if not self.lbl_file.exists() or not self.nor_file.exists():
            self.lines = []
            self.logger.warning(f"Soubor {self.lbl_file} nebo {self.nor_file} nebyl nalezen!")
            self.messenger.warning(f"Soubor {self.lbl_file} nebo {self.nor_file} nebyl nalezen!", "Work Order Ctrl")
            self.reset_input_focus()
            return

        try:
            with self.nor_file.open('r') as file:
                first_line = file.readline().strip()
                parts = first_line.split(';')

                if len(parts) >= 2:
                    nor_order_code = parts[0].lstrip('$').upper()
                    product_name = parts[1].strip()

                    if nor_order_code != value_input:
                        self.logger.warning(f"Výrobní příkaz v souboru .NOR ({nor_order_code}) neodpovídá zadanému vstupu ({value_input})!")
                        self.messenger.warning(f"Výrobní příkaz v souboru .NOR ({nor_order_code}) neodpovídá zadanému vstupu ({value_input})!", "Work Order Ctrl")
                        self.reset_input_focus()
                        return

                    self.lines = self.load_file(self.lbl_file)

                    self.run_bartender_commander()
                    self.open_app_window(order_code=value_input, product_name=product_name)
                    self.logger.info(f"Příkaz: {value_input}")
                    self.reset_input_focus()

                else:
                    self.logger.warning(f"Řádek v souboru {self.nor_file} nemá očekávaný formát.")
                    self.messenger.warning(f"Řádek v souboru {self.nor_file} nemá očekávaný formát.", "Work Order Ctrl")
                    self.reset_input_focus()
                    return
        except Exception as e:
            self.logger.error(f"Neočekávaná chyba při zpracování .NOR souboru: {e}")
            self.messenger.error(f"Neočekávaná chyba při zpracování .NOR souboru: {e}", "Work Order Ctrl")
            self.reset_input_focus()
            return

    def load_file(self, file_path: Path) -> list[str]:
        """
        Loads text content from file.

        Args:
            file_path (Path): Path to the file.

        Returns:
            list[str]: Lines from the file or empty list on error.
        """
        try:
            return file_path.read_text().splitlines()
        except Exception as e:
            self.logger.error(f"Soubor {file_path} se nepodařilo načíst: {e}")
            self.messenger.error(f"Soubor {file_path} se nepodařilo načíst: {e}", "Work Order Ctrl")
            return []

    def open_app_window(self, order_code, product_name):
        """
        Instantiates PrintController and launches next window.

        Args:
            order_code (str): Order code for the print job.
            product_name (str): Product name extracted from .nor file.
        """
        from controllers.print_controller import PrintController
        self.print_controller = PrintController(self.window_stack, order_code, product_name)
        self.window_stack.push(self.print_controller.print_window)

    def reset_input_focus(self):
        """
        Clears the input field and sets focus back to it.
        """
        self.work_order_window.work_order_input.clear()
        self.work_order_window.work_order_input.setFocus()

    def kill_bartender_processes(self):
        """
        Terminates all running BarTender instances (Cmdr.exe and bartend.exe).
        """
        try:
            subprocess.run('taskkill /f /im cmdr.exe 1>nul 2>nul', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run('taskkill /f /im bartend.exe 1>nul 2>nul', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Chyba při ukončování BarTender procesů: {str(e)}")
            self.messenger.error(f"Chyba při ukončování BarTender procesů: {str(e)}", "Work Order Ctrl")

    def handle_exit(self):
        """
        Closes the current window with fade-out effect.
        """
        self.kill_bartender_processes()
        self.work_order_window.effects.fade_out(self.work_order_window, duration=500)
