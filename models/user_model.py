import hashlib
import configparser
from utils.logger import get_logger
from pathlib import Path
from utils.messenger import Messenger
from utils.resources import get_config_path, resolve_path

# 📌 Global variable holding the value prefix
value_prefix = None


def get_value_prefix():
    """
    Returns the value 'value_prefix' without using 'global'.
        :return: current value of 'value_prefix'
    """
    return value_prefix


class SzvDecrypt:
    """
    Class for decrypting the file and verifying the login using the SHA-256 hash.
        - Reads an encrypted file containing login credentials
        - Decodes the contents of the file using an XOR operation
        - Verifies the user password against stored values
    """

    def __init__(self, config_file='config.ini'):
        """
        Initializes the SzvDecrypt class and sets the path to the input file and logger.
            :param config_file: The path to the configuration file ('config.ini').
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
        Logs the decoded content of the input file, if any.
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
        Decodes the given encoded data by XOR operation.
            :param encoded_data: Encoded data as 'bytearray'.
            :return: Decoded data as a list of strings.
        """
        int_xor = len(encoded_data) % 32
        decoded_data = bytearray(len(encoded_data))

        for i in range(len(encoded_data)):
            decoded_data[i] = encoded_data[i] ^ (int_xor ^ 0x6)
            int_xor = (int_xor + 5) % 32

        return decoded_data.decode('windows-1250').split('\x15')

    def check_login(self, password):
        """
        Checks whether the password entered matches any of the decoded lines in the input file.
            :param password: Password to be verified.
            :return: 'True' if the password matches, otherwise 'False'.
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
        Reads and decodes the contents of the input file.
            :return: a list of decoded lines, where each line is a list containing the password hash and decoded data.
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
