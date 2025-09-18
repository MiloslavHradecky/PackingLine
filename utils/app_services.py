"""
📦 Module: app_services.py

Provides a shared service container for accessing core utilities
like PrintConfigController and BartenderUtils.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser

# 🧠 First-party (project-specific)
from utils.messenger import Messenger
from utils.bartender_utils import BartenderUtils
from controllers.print_config_controller import PrintConfigController


class AppServices:
    """
    Container for shared application services.

    Attributes:
        messenger (Messenger): Centralized messenger instance.
        config_controller (PrintConfigController): Resolves trigger groups from config.
        bartender_cls (type): Reference to BartenderUtils class for flexible instantiation.
    """

    def __init__(self, config: configparser.ConfigParser, messenger: Messenger):
        """
        Initializes shared services with provided config and messenger.

        Args:
            config (ConfigParser): Loaded configuration file.
            messenger (Messenger): Messenger instance for user feedback.
        """
        self.messenger = messenger
        self.config_controller = PrintConfigController(config=config, messenger=messenger)
        self.bartender_cls = BartenderUtils  # Use: bartender = self.bartender_cls(messenger, config)
