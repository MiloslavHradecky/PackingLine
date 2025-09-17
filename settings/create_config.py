# 🛠️ create_config.py – Generates default configuration file for the application

import configparser
from io import StringIO

config = configparser.ConfigParser()
config.optionxform = str  # ✅ Preserve key casing

# 📌 Section: Window – application title
config["Window"] = {
    "title": "2N IP Force 2.0"
}

# 📁 Section: Paths – system paths and references
config["Paths"] = {
    "reports_path": "T:/reporty/",
    "orders_path": "T:/Prikazy/",
    "trigger_path": "T:/Prikazy/DataTPV/Force2IP_X/BaliciLinka/Spoustece/",
    "szv_input_file": "T:/Prikazy/DataTPV/SZV.dat",
    "bartender_path": "C:/Program Files (x86)/Seagull/BarTender Suite/bartend.exe",
    "commander_path": "C:/Program Files (x86)/Seagull/BarTender Suite/Cmdr.exe",
    "tl_file_path": "T:/Prikazy/DataTPV/Force2IP_X/BaliciLinka/Spoustece/Force2IP.tl"
}

# 📦 Section: ProductPaths – standard product output
config["ProductPaths"] = {
    "output_file_path_product": "T:/Prikazy/DataTPV/Force2IP_X/BaliciLinka/Etikety/02 product.txt"
}

# 🎯 Section: Control4Paths – special product for Control4
config["Control4Paths"] = {
    "output_file_path_c4_product": "T:/Prikazy/DataTPV/Force2IP_X/BaliciLinka/Etikety/C4-SMART.txt"
}

# 🌐 Section: My2NPaths – product output for My2N platform
config["My2nPaths"] = {
    "output_file_path_my2n": "T:/Prikazy/DataTPV/Force2IP_X/BaliciLinka/Etikety/my2n.txt"
}

# 🔗 Section: ProductTriggerMapping – mapping codes to label templates
config["ProductTriggerMapping"] = {
    "product": "9151301, 9151301C, 9151301CK, 9151301CM, 9151301CRP, 9151301K, 9151301RP, 9151302CR, 9151302R, 9151304, 9151304C",
    "control4": "",
    "my2n": "9151301, 9151301C, 9151301CK, 9151301CM, 9151301CRP, 9151301K, 9151301RP, 9151302CR, 9151302R, 9151304, 9151304C",
}

# 🧪 For testing: preview config content
configfile = StringIO()
config.write(configfile)
print(configfile.getvalue())

# 💾 Save config to .ini file
with open("config.ini", mode="w") as file:
    file.write(configfile.getvalue())
