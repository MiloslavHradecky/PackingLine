"""
📦 Module: login_services.py

Provides shared services for login logic, including decryption and BarTender process control.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser

# 🧠 First-party (project-specific)
from utils.bartender_utils import BartenderUtils
from utils.messenger import Messenger

from models.user_model import SzvDecrypt


class LoginServices:
    """
    Container for login-related services.

    Attributes:
        decrypter (SzvDecrypt): Handles password decryption.
        bartender (BartenderUtils): Manages BarTender process control.
    """

    def __init__(self, config: configparser.ConfigParser, messenger: Messenger):
        """
        Initializes login services with config and messenger.

        Args:
            config (ConfigParser): Loaded configuration file.
            messenger (Messenger): Messenger instance for user feedback.
        """
        self.decrypter = SzvDecrypt()
        self.bartender = BartenderUtils(messenger=messenger, config=config)
