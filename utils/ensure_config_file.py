# utils/ensure_config_file.py
from configparser import ConfigParser
from utils.resources import get_config_path
from utils.logger import get_logger


def ensure_config_file(path: str = "config.ini"):
    """
    Ensures that the configuration file exists. If not, creates it with default values.
        :param path: Path to the config file (default: 'config.ini')
    """
    logger = get_logger("EnsureConfig")
    config_path = get_config_path(path)

    if not config_path.exists():
        config = ConfigParser()
        config.optionxform = str  # ✅ preserves the size of the letters

        # 📌 Default sections and values
        config["Paths"] = {
            "szv_input_file": "T:/Prikazy/DataTPV/SZV.dat",
            "csv_input_file": "T:/Prikazy/DataTPV/ManualLabelPrint/Databaze/MLP.csv",
            "csv_output_file": "T:/Prikazy/DataTPV/ManualLabelPrint/Etikety/label.csv",
            "bartender_path": "C:/Program Files (x86)/Seagull/BarTender Suite/bartend.exe",
            "label_folder": "T:/Prikazy/DataTPV/ManualLabelPrint/Etikety/",
            "orders_folder": "T:/Prikazy/",
            "archiv_file_path": "T:/Prikazy/DataTPV/ManualLabelPrint/Archiv/"
        }

        try:
            with config_path.open("w", encoding="utf-8") as config_file:
                config.write(config_file)
            logger.info(f"Konfigurační soubor vytvořen: {config_path}")
        except Exception as e:
            logger.error(f"Chyba při vytváření konfiguračního souboru: {str(e)}")
    else:
        logger.info(f"Konfigurační soubor již existuje: {config_path}")
