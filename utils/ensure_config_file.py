# utils/ensure_config_file.py
from configparser import ConfigParser
from utils.resources import get_config_path
from utils.logger import get_logger


def ensure_config_file(path: str = "config.ini"):
    """
    Ensures that the configuration file exists. If not, creates it with default values.
        :param path: Path to the config file (default: "config.ini")
    """
    logger = get_logger("EnsureConfig")
    config_path = get_config_path(path)

    if not config_path.exists():
        config = ConfigParser()
        config.optionxform = str  # ✅ preserves the size of the letters

        # 📌 Default sections and values
        config["Window"] = {
            "title": "2N IP Verso 2.0"
        }

        config["Paths"] = {
            "reports_path": "T:/reporty/",
            "orders_path": "T:/Prikazy/",
            "trigger_path": "T:/Prikazy/DataTPV/IP_Verso_HD_2/BaliciLinka/Spoustece/",
            "szv_input_file": "T:/Prikazy/DataTPV/SZV.dat",
            "bartender_path": "C:/Program Files (x86)/Seagull/BarTender Suite/bartend.exe",
            "commander_path": "C:/Program Files (x86)/Seagull/BarTender Suite/Cmdr.exe",
            "tl_file_path": "T:/Prikazy/DataTPV/IP_Verso_HD_2/BaliciLinka/Spoustece/HeliosIP.tl"
        }

        config["ProductPaths"] = {
            "output_file_path_product": "T:/Prikazy/DataTPV/IP_Verso_HD_2/BaliciLinka/Etikety/02 product.txt"
        }

        config["Control4Paths"] = {
            "output_file_path_c4_product": "T:/Prikazy/DataTPV/IP_Verso_HD_2/BaliciLinka/Etikety/C4-SMART.txt"
        }

        config["My2nPaths"] = {
            "output_file_path_my2n": "T:/Prikazy/DataTPV/IP_Verso_HD_2/BaliciLinka/Etikety/my2n.txt"
        }

        config["ProductTriggerMapping"] = {
            "product": "9155211, 9155211B, 9155211C, 9155211CB, 9155211C-C4, 9155211CB-C4, VSA-211C, VSA-211CB",
            "control4": "9155211C-C4, 9155211CB-C4",
            "my2n": "9155211, 9155211B, 9155211C, 9155211CB"
        }

        try:
            with config_path.open("w", encoding="utf-8") as config_file:
                config.write(config_file)
            logger.info(f"Konfigurační soubor vytvořen: {config_path}")
        except Exception as e:
            logger.error(f"Chyba při vytváření konfiguračního souboru: {str(e)}")
    else:
        logger.info(f"Konfigurační soubor již existuje: {config_path}")
