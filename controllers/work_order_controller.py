"""
📦 Module: work_order_controller.py

Controller responsible for handling work order input, validating associated files,
and transitioning to the print phase. Also manages launching BarTender Commander
and terminating related processes.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser
from pathlib import Path

# 🧩 Third-party libraries
from PyQt6.QtCore import QCoreApplication

# 🧠 First-party (project-specific)
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path
from utils.order_data import OrderData
from utils.app_services import AppServices

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

        # 📌 Initialization
        self.window_stack = window_stack
        self.work_order_window = WorkOrderWindow(controller=self)
        self.print_controller = None
        self.print_window = None
        self.messenger = Messenger(self.work_order_window)
        self.order_data = OrderData()
        self.logger = get_logger("WorkOrderController")
        self.services = AppServices(config=self.config, messenger=self.messenger)

        # 📌 Linking the button to the method
        self.work_order_window.next_button.clicked.connect(self.work_order_button_click)
        self.work_order_window.back_button.clicked.connect(self.handle_back)
        self.work_order_window.exit_button.clicked.connect(self.handle_exit)

    def work_order_button_click(self):
        """
        Triggered on "Continue" click.

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
        self.order_data.set_files(value_input)

        # ❌ If file not found
        if not self.order_data.lbl_file.exists() or not self.order_data.nor_file.exists():
            self.order_data.lines = []
            self.logger.warning("Soubor %s nebo %s nebyl nalezen!", self.order_data.lbl_file, self.order_data.nor_file)
            self.messenger.warning(f"Soubor {self.order_data.lbl_file} nebo {self.order_data.nor_file} nebyl nalezen!", "Work Order Ctrl")
            self.reset_input_focus()
            return

        try:
            with self.order_data.nor_file.open("r") as file:
                first_line = file.readline().strip()
                parts = first_line.split(";")

                if len(parts) >= 2:
                    nor_order_code = parts[0].lstrip("$").upper()
                    product_name = parts[1].strip()

                    if nor_order_code != value_input:
                        self.logger.warning("Výrobní příkaz v souboru .NOR (%s) neodpovídá zadanému vstupu (%s)!", nor_order_code, value_input)
                        self.messenger.warning(f"Výrobní příkaz v souboru .NOR ({nor_order_code}) neodpovídá zadanému vstupu ({value_input})!", "Work Order Ctrl")
                        self.reset_input_focus()
                        return

                    groups = self.services.config_controller.get_trigger_groups_for_product(product_name)
                    if not groups:
                        self.logger.info("Zpracování zastaveno – produkt není mapován v configu.")
                        self.reset_input_focus()
                        return

                    self.order_data.lines = self.load_file(self.order_data.lbl_file)

                    bartender = self.services.bartender_cls(messenger=self.messenger, config=self.config)
                    bartender.run_commander()

                    self.open_app_window(order_code=value_input, product_name=product_name)
                    self.logger.info("Příkaz: %s", value_input)
                    self.reset_input_focus()

                else:
                    self.logger.warning("Řádek v souboru %s nemá očekávaný formát.", self.order_data.nor_file)
                    self.messenger.warning(f"Řádek v souboru {self.order_data.nor_file} nemá očekávaný formát.", "Work Order Ctrl")
                    self.reset_input_focus()
                    return
        except Exception as e:
            self.logger.error("Neočekávaná chyba při zpracování .NOR souboru: %s", str(e))
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
            self.logger.error("Soubor %s se nepodařilo načíst: %s", file_path, str(e))
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

    def handle_back(self):
        """
        Closes the product window and returns to the previous window in the stack.
        """
        bartender = self.services.bartender_cls(messenger=self.messenger, config=self.config)
        bartender.kill_processes()
        self.work_order_window.effects.fade_out(self.work_order_window)

    def handle_exit(self):
        """
        Terminates the application and fades out the product window.
        """
        self.logger.info("Aplikace byla ukončena uživatelem.")
        bartender = self.services.bartender_cls(messenger=self.messenger, config=self.config)
        bartender.kill_processes()
        self.window_stack.mark_exiting()
        self.work_order_window.effects.fade_out(self.work_order_window, callback=QCoreApplication.instance().quit)
