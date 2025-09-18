"""
📦 Module: user_model.py

Handles login verification by decrypting credentials stored in an encrypted file.

Provides functionality to:
- Decode login data using XOR-based decryption
- Verify user passwords against SHA-256 hashes
- Extract user metadata upon successful login

Used by LoginController during authentication.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import configparser
import hashlib
from pathlib import Path

# 🧠 First-party (project-specific)
from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import get_config_path, resolve_path

# 📌 Global variable holding the value prefix
VALUE_PREFIX = None


def get_value_prefix():
    """
    Returns the current global value prefix after successful login.
    """
    return VALUE_PREFIX


class SzvDecrypt:
    """
    Decrypts login credentials and verifies user authentication.
    Uses XOR decoding and SHA-256 matching to validate passwords and extract user metadata.
    """

    def __init__(self, config_file='config.ini'):
        """
        Initializes decryption logic, loads config, and prepares messenger and logger.
        """
        # 📌 Loading the configuration file
        config_path = get_config_path(config_file)
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Initialization
        raw_path = self.config.get('Paths', 'szv_input_file')
        self.szv_input_file = resolve_path(raw_path)
        self.logger = get_logger("SzvDecrypt")
        self.messenger = Messenger()
        self.value_surname = None
        self.value_name = None
        self.value_prefix = None

    @staticmethod
    def decoding_line(encoded_data):
        """
        Decodes a single encrypted line using XOR logic.

        Returns decoded segments split by delimiter.
        """
        int_xor = len(encoded_data) % 32
        decoded_data = bytearray(len(encoded_data))

        for i, byte in enumerate(encoded_data):
            decoded_data[i] = byte ^ (int_xor ^ 0x6)
            int_xor = (int_xor + 5) % 32

        return decoded_data.decode('windows-1250').split('\x15')

    def check_login(self, password):
        """
        Verifies input password against stored credentials.
        Updates global prefix and user metadata on success.
        """
        # pylint: disable=global-statement
        global VALUE_PREFIX  # ✅ Allows you to modify a global variable
        try:
            decoded_data = self.decoding_file()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            for decoded_line in decoded_data:  # type: ignore
                if hashed_password == decoded_line[0]:
                    if len(decoded_line) > 1:
                        parts = decoded_line[1].split(',')
                        if len(parts) >= 4:
                            self.value_surname = parts[2].strip()
                            self.value_name = parts[3].strip()
                            self.value_prefix = parts[4].strip()
                            # pylint: disable=global-statement
                            global VALUE_PREFIX
                            VALUE_PREFIX = self.value_prefix  # ✅ Updating a global variable
                            self.logger.info("Logged: %s %s %s", self.value_surname, self.value_name, self.value_prefix)
                            return True
                        self.logger.warning("Řádek neobsahuje dostatek částí: %s", decoded_line[1])
                        return False
                    self.logger.warning("Řádek neobsahuje další části: %s", decoded_line)
                    return False
            self.logger.warning("Zadané heslo (%s) nebylo nalezeno v souboru (%s).", password, self.szv_input_file)
            return False

        except (FileNotFoundError, ValueError, IndexError, AttributeError) as e:
            self.logger.error("Neočekávaná chyba při ověřování hesla: %s", str(e))
            self.messenger.error(f"{str(e)}", "Přihlášení")
            return False

    def decoding_file(self):
        """
        Reads and decodes all lines from the encrypted login file.

        Returns list of decoded entries or False on error.
        """
        decoded_lines = []
        try:
            with Path(self.szv_input_file).open('r') as infile:
                for line in infile:
                    byte_array = bytearray.fromhex(line.strip())
                    decoded_line = self.decoding_line(byte_array)
                    decoded_lines.append([hashlib.sha256(decoded_line[0].encode()).hexdigest(), ','.join(decoded_line)])
        except (FileNotFoundError, ValueError, OSError, IndexError, AttributeError) as e:
            self.logger.error("Při čtení souboru došlo k chybě: %s", str(e))
            self.messenger.error(f"{str(e)}", "Přihlášení")
            return False

        return decoded_lines
