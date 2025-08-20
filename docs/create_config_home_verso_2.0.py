# 🛠️ create_config.py – Generates default configuration file for the application

import configparser
from io import StringIO

config = configparser.ConfigParser()
config.optionxform = str  # ✅ Preserve key casing

# 📌 Section: Window – application title
config["Window"] = {
    "title": "2N IP Verso 2.0"
}

# 📁 Section: Paths – system paths and references
config["Paths"] = {
    "reports_path": "T:/reporty/",
    "orders_path": "T:/Prikazy/",
    "trigger_path": "C:/Users/Home/Documents/Coding/Python/PyQt/Spoustece/",
    "szv_input_file": "T:/Prikazy/DataTPV/SZV.dat",
    "bartender_path": "C:/Program Files (x86)/Seagull/BarTender Suite/bartend.exe",
    "commander_path": "C:/Program Files (x86)/Seagull/BarTender Suite/Cmdr.exe",
    "tl_file_path": "C:/Users/Home/Documents/Coding/Python/PyQt/Spoustece/TestLine.tl"
}

# 📦 Section: ProductPaths – standard product output
config["ProductPaths"] = {
    "output_file_path_product": "C:/Users/Home/Documents/Coding/Python/PyQt/Etikety/02 product.txt"
}

# 🎯 Section: Control4Paths – special product for Control4
config["Control4Paths"] = {
    "output_file_path_c4_product": "C:/Users/Home/Documents/Coding/Python/PyQt/Etikety/C4-SMART.txt"
}

# 🌐 Section: My2NPaths – product output for My2N platform
config["My2nPaths"] = {
    "output_file_path_my2n": "C:/Users/Home/Documents/Coding/Python/PyQt/Etikety/my2n.txt"
}

# 🔗 Section: ProductTriggerMapping – mapping codes to label templates
config["ProductTriggerMapping"] = {
    "product": "9155211, 9155211B, 9155211C, 9155211CB, 9155211C-C4, 9155211CB-C4, VSA-211C, VSA-211CB",
    "control4": "9155211C-C4, 9155211CB-C4",
    "my2n": "9155211, 9155211B, 9155211C, 9155211CB",
}

# 🧪 For testing: preview config content
configfile = StringIO()
config.write(configfile)
print(configfile.getvalue())

# 💾 Save config to .ini file
with open("config.ini", mode="w") as file:
    file.write(configfile.getvalue())
