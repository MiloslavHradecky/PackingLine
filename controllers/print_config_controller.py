# 🧩 PrintConfigController – handles config-based logic for trigger group resolution

from utils.logger import get_logger


class PrintConfigController:
    def __init__(self, config, messenger):
        self.config = config
        self.messenger = messenger
        self.logger = get_logger("PrintConfigController")

    def get_trigger_groups_for_product(self, product_name: str) -> list[str]:
        """
        Returns all trigger groups (product, control4, my2n) that match product_name from config.

        :param product_name: Product name to match
        :return: List of matching group names
        """
        matching = []

        if not self.config.has_section("ProductTriggerMapping"):
            self.logger.warning("Sekce 'ProductTriggerMapping' nebyla nalezena v configu.")
            self.messenger.warning("Sekce 'ProductTriggerMapping' nebyla nalezena v configu.", "Print Config Ctrl")
            return matching

        for group_name in self.config.options("ProductTriggerMapping"):
            raw_list = self.config.get("ProductTriggerMapping", group_name)
            items = [item.strip() for item in raw_list.split(",")]
            if product_name in items:
                matching.append(group_name)

        return matching
