from pathlib import Path
import logging
import json
from logging.handlers import RotatingFileHandler
from utils.resources import get_writable_path


# --- Custom JSON formatter ---
class JsonFormatter(logging.Formatter):

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage()
        }
        return json.dumps(log_record, ensure_ascii=False)


# --- Logger initialization ---
def get_logger(name: str) -> logging.Logger:
    log_file_txt = get_writable_path("logs/app.txt")
    log_file_json = get_writable_path("logs/app.json")

    # 🛡️ Ensure the existence of a folder
    Path(log_file_txt).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # TXT log with rotation
    txt_handler = RotatingFileHandler(log_file_txt, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    txt_formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)-23s | %(message)s")
    txt_handler.setFormatter(txt_formatter)
    logger.addHandler(txt_handler)

    # JSON log with rotation
    json_handler = RotatingFileHandler(log_file_json, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    json_handler.setFormatter(JsonFormatter())
    logger.addHandler(json_handler)

    return logger
