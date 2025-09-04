# utils/system_info.py

"""
Utility for logging basic system information at application startup.

Captures and logs the current version, computer name, and IP address.
"""

# 🧱 Standard library
import socket
import platform

# 🧠 First-party
from utils.logger import get_logger


def log_system_info(version: str):
    """
    Logs system information including application version, computer name, and IP address.

    Args:
        version (str): Current version of the application.
    """
    logger = get_logger("SystemInfo")

    # 📌 IP address
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        ip_address = "Neznámá"

    # 📌 PC Name
    try:
        computer_name = platform.node()
    except OSError:
        computer_name = "Neznámý"

    logger.info("Aplikace v%s spuštěna | PC: %s | IP: %s", version, computer_name, ip_address)
