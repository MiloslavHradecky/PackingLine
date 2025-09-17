"""
📦 Module: system_info_logger.py

Logs basic system information at application startup.

Responsibilities:
    - Retrieve local IP address and computer name
    - Log version, hostname, and IP for diagnostics
    - Used during initialization to trace environment context

Author: Miloslav Hradecky
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
