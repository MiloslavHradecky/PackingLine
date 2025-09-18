"""
📦 Module: resources.py

Utility functions for resolving file paths in both development and bundled (.exe) environments.

Responsibilities:
- Locate resource files regardless of runtime context
- Resolve paths from config.ini (absolute or relative)
- Provide writable paths for logs and outputs
- Ensure consistent file access across platforms

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Resolves absolute path to a resource file.
    Supports both standard execution and PyInstaller-packed (.exe) environments.
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
    Resolves config-defined path to an absolute path.
    Handles both absolute and relative inputs.
    """
    path = Path(config_value)
    if path.is_absolute():
        return path
    return resource_path(config_value)


def get_writable_path(relative_path: str) -> Path:
    """
    Returns writable path relative to the script or executable location.
    Used for logs, outputs, or temp files.
    """
    return Path(sys.argv[0]).resolve().parent / relative_path


def get_config_path(filename: str = "config.ini") -> Path:
    """
    Returns absolute path to the configuration file.
    Defaults to 'config.ini' in the current executable directory.
    """
    return Path(sys.argv[0]).resolve().parent / filename
