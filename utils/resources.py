import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Resolves the absolute path to a resource file.

    Supports both standard Python execution and PyInstaller-packed (.exe) environments.
    Automatically detects the runtime environment and returns the correct file path
    for accessing bundled resources (e.g. icons, images, config files).

    Args:
        relative_path (str): Relative path to the desired resource (e.g. 'view/assets/main.png').

    Returns:
        Path: Absolute path to the resource file on disk.
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
    Resolves a path from config.ini. If it's absolute, returns as-is.
    If it's relative, resolves it using resource_path().

    Args:
        config_value (str): Path from config.ini (can be absolute or relative).

    Returns:
        Path: Absolute path to the resource.
    """
    path = Path(config_value)
    if path.is_absolute():
        return path
    return resource_path(config_value)


def get_writable_path(relative_path: str) -> Path:
    """Returns the path for writing (e.g. logs, outputs) next to .exe or .py."""
    return Path(sys.argv[0]).resolve().parent / relative_path


def get_config_path(filename: str = "config.ini") -> Path:
    """Returns the path to the configuration file next to .exe or .py."""
    return Path(sys.argv[0]).resolve().parent / filename
