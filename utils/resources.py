# utils/resources.py

"""
Utility functions for resolving file and directory paths.

Handles both standard Python execution and PyInstaller-packed environments,
ensuring correct access to bundled resources and writable locations.
"""

# 🧱 Standard library
import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Resolves the absolute path to a bundled resource file.

    Supports both standard Python execution and PyInstaller-packed (.exe) environments.

    Args:
        relative_path (str): Relative path to the resource (e.g. 'views/assets/icon.png').

    Returns:
        Path: Absolute path to the resource file.
    """
    try:
        base_path = Path(sys._MEIPASS)  # type: ignore
    except AttributeError:
        base_path = Path(__file__).resolve().parent
        if not (base_path / relative_path).exists():
            base_path = Path.cwd()
    return base_path / relative_path


def resolve_path(config_value: str) -> Path:
    """
    Resolves a path from config.ini. Returns absolute path.

    If the path is already absolute, returns it directly.
    If it's relative, resolves it using resource_path().

    Args:
        config_value (str): Path from config.ini (absolute or relative).

    Returns:
        Path: Absolute path to the resource.
    """
    path = Path(config_value)
    if path.is_absolute():
        return path
    return resource_path(config_value)


def get_writable_path(relative_path: str) -> Path:
    """
    Returns a writable path relative to the executable or script location.

    Typically used for logs, outputs, or temporary files.

    Args:
        relative_path (str): Relative path to the writable file or folder.

    Returns:
        Path: Absolute writable path.
    """
    return Path(sys.argv[0]).resolve().parent / relative_path


def get_config_path(filename: str = "config.ini") -> Path:
    """
    Returns the path to the configuration file.

    Args:
        filename (str): Name of the config file (default: "config.ini").

    Returns:
        Path: Absolute path to the config file.
    """
    return Path(sys.argv[0]).resolve().parent / filename
