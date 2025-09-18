"""
📦 Module: print_config_controller.py

Resolves trigger groups based on product names.

Used during the printing workflow to determine which trigger groups apply to a given product,
based on configuration mappings defined in 'ProductTriggerMapping'.

Author: Miloslav Hradecky
"""

# 🧠 First-party (project-specific)
from utils.logger import get_logger


class PrintConfigController:
    """
    Resolves trigger groups for a given product using configuration mappings.
    """
    def __init__(self, config, messenger):
        """
        Initializes config access, messenger, and logger for trigger resolution.
        """
        self.config = config
        self.messenger = messenger
        self.logger = get_logger("PrintConfigController")

    def get_trigger_groups_for_product(self, product_name: str) -> list[str] | None:
        """
        Returns trigger groups that include the given product name.

        Logs and alerts if no match is found.
        """
        if not self.config.has_section("ProductTriggerMapping"):
            self.logger.warning("Sekce 'ProductTriggerMapping' nebyla nalezena v configu.")
            self.messenger.warning("Sekce 'ProductTriggerMapping' nebyla nalezena v configu.", "Print Config Ctrl")
            return None

        matching = []

        for group_name in self.config.options("ProductTriggerMapping"):
            raw_list = self.config.get("ProductTriggerMapping", group_name)
            items = [item.strip() for item in raw_list.split(",") if item.strip()]
            if product_name in items:
                matching.append(group_name)

        if not matching:
            self.logger.error("Produkt '%s' není mapován na žádnou skupinu v configu.", product_name)
            self.messenger.error(f"Produkt '{product_name}' není mapován na žádnou skupinu v configu!", "Print Config Ctrl")
            return None

        return matching
