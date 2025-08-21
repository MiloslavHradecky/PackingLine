from utils.logger import get_logger
from utils.messenger import Messenger
from utils.resources import resolve_path


class PathValidator:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("PathValidator")
        self.messenger = Messenger()
        self.keys = [
            "reports_path",
            "orders_path",
            "trigger_path",
            "szv_input_file",
            "bartender_path",
            "commander_path",
            "tl_file_path"
        ]
        self.missing = []

    def validate(self) -> bool:
        for key in self.keys:
            try:
                raw = self.config.get("Paths", key)
                path = resolve_path(raw)
                if not path.exists():
                    self.logger.warning(f"Cesta nebo soubor neexistuje: {key} → {path}")
                    self.messenger.warning(f"Cesta nebo soubor neexistuje:\n{path}", "Path Validation")
                    self.missing.append((key, path))
            except Exception as e:
                self.logger.error(f"Chyba při čtení '{key}': {e}")
                self.messenger.error(f"Chyba při čtení '{key}': {e}", "Path Validation")
                self.missing.append((key, "chyba v configu"))

        if self.missing:
            self.messenger.error(f"Následující cesty jsou neplatné nebo chybí soubor:", "Path Validation")
            for key, path in self.missing:
                self.messenger.error(f"\n{key}\n{path}", "Path Validation")
            return False

        self.logger.info(f"Všechny cesty v configu jsou validní.")
        return True
