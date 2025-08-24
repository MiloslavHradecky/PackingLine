# utils/ensure_logs_dir.py

"""
Utility for ensuring the existence of the logs directory.

Creates the specified directory if it doesn't already exist, including any necessary parent folders.
"""

# 🧠 First-party (project-specific)
from utils.resources import get_writable_path


def ensure_logs_dir(path: str = "logs"):
    """
    Ensures that the logs directory exists. If not, creates it.

    Args:
        path (str): Relative or absolute path to the logs directory (default: "logs").
    """
    logs_path = get_writable_path(path)
    logs_path.mkdir(parents=True, exist_ok=True)
