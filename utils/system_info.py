import socket
import platform
from utils.logger import get_logger

def log_system_info(version: str):
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

    logger.info(f"Aplikace v{version} spuštěna | PC: {computer_name} | IP: {ip_address}")
