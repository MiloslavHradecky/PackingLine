# utils/ensure_logs_dir.py
from utils.resources import get_writable_path


def ensure_logs_dir(path: str = "logs"):
    logs_path = get_writable_path(path)
    logs_path.mkdir(parents=True, exist_ok=True)
