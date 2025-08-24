# 🔐 SzvDecrypt – handles login verification by decrypting credentials stored in an encrypted file

"""
Handles login verification by decrypting credentials stored in an encrypted file.

Provides functionality to:
- Read and decode login data using XOR-based decryption
- Verify user passwords against SHA-256 hashes
- Extract user metadata (name, surname, prefix) upon successful login

Used primarily by the LoginController during authentication.
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
value_prefix = None


def get_value_prefix():
    """
    Returns the current value of the global 'value_prefix'.

    Returns:
        str | None: The current value of 'value_prefix'.
    """
    return value_prefix


class SzvDecrypt:
    """
    Decrypts login credentials and verifies user authentication using SHA-256.

    Responsibilities:
        - Load encrypted login file from config
        - Decode file contents using XOR-based logic
        - Match input password against stored hashes
        - Extract user metadata upon successful login
    """

    def __init__(self, config_file='config.ini'):
        """
        Initializes the SzvDecrypt instance and loads configuration.

        Args:
            config_file (str): Path to the configuration file.
        """

        # 📌 Loading the configuration file
        config_path = get_config_path(config_file)
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 💡 Ensures letter size is maintained
        self.config.read(config_path)

        # 📌 Load path to encrypted login file
        raw_path = self.config.get('Paths', 'szv_input_file')
        self.szv_input_file = resolve_path(raw_path)

        # 📌 Inicializace loggeru
        self.logger = get_logger("SzvDecrypt")

        # 📌 Uchovávání dekódovaných hodnot
        self.value_surname = None
        self.value_name = None
        self.value_prefix = None

    def log_decoded_file(self):
        """
        Logs each decoded line from the encrypted input file.
        """
        try:
            with Path(self.szv_input_file).open('r') as infile:
                for line in infile:
                    byte_array = bytearray.fromhex(line.strip())
                    decoded_line = self.decoding_line(byte_array)
                    self.logger.info(f"Dekódovaný řádek: {decoded_line}")
        except Exception as e:
            self.logger.error(f"Při čtení souboru došlo k chybě: {str(e)}")

    @staticmethod
    def decoding_line(encoded_data):
        """
        Decodes a single line of encrypted data using XOR logic.

        Args:
            encoded_data (bytearray): Encrypted byte data.

        Returns:
            list[str]: Decoded string segments.
        """
        int_xor = len(encoded_data) % 32
        decoded_data = bytearray(len(encoded_data))

        for i in range(len(encoded_data)):
            decoded_data[i] = encoded_data[i] ^ (int_xor ^ 0x6)
            int_xor = (int_xor + 5) % 32

        return decoded_data.decode('windows-1250').split('\x15')

    def check_login(self, password):
        """
        Verifies the given password against stored credentials.

        Args:
            password (str): Password entered by the user.

        Returns:
            bool: True if password matches, False otherwise.
        """
        global value_prefix  # ✅ Umožňuje upravit globální proměnnou
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
                            global value_prefix
                            value_prefix = self.value_prefix  # ✅ Aktualizace globální proměnné
                            self.logger.info(f"Logged: {self.value_surname} {self.value_name} {self.value_prefix}")
                            return True
                        else:
                            self.logger.warning(f"Řádek neobsahuje dostatek částí: {decoded_line[1]}")
                            return False
                    else:
                        self.logger.warning(f"Řádek neobsahuje další části: {decoded_line}")
                        return False

            self.logger.warning(f"Zadané heslo ({password}) nebylo nalezeno v souboru ({self.szv_input_file}).")

            return False

        except Exception as e:
            self.logger.error(f"Neočekávaná chyba při ověřování hesla: {str(e)}")
            Messenger.error(str(e), "Přihlášení")
            return False

    def decoding_file(self):
        """
        Reads and decodes all lines from the encrypted input file.

        Returns:
            list[list[str]] | bool: List of decoded lines or False on error.
        """
        decoded_lines = []
        try:
            with Path(self.szv_input_file).open('r') as infile:
                for line in infile:
                    byte_array = bytearray.fromhex(line.strip())
                    decoded_line = self.decoding_line(byte_array)
                    decoded_lines.append([hashlib.sha256(decoded_line[0].encode()).hexdigest(), ','.join(decoded_line)])
        except Exception as e:
            self.logger.error(f"Při čtení souboru došlo k chybě: {str(e)}")
            Messenger.error(str(e), "Přihlášení")
            return False

        return decoded_lines
