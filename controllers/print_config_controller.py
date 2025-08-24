# 🧩 PrintConfigController – handles config-based logic for trigger group resolution

# 🧠 First-party (project-specific)
from utils.logger import get_logger


class PrintConfigController:
    """
    Controller responsible for resolving trigger groups based on product name.

    Attributes:
        config (ConfigParser): Loaded configuration object.
        messenger (Messenger): UI messenger for displaying alerts.
        logger (Logger): Logger instance for diagnostics.
    """
    def __init__(self, config, messenger):
        """
        Initializes the PrintConfigController.

        Args:
            config (ConfigParser): Parsed configuration file.
            messenger (Messenger): Messenger instance for user feedback.
        """
        self.config = config
        self.messenger = messenger
        self.logger = get_logger("PrintConfigController")

    def get_trigger_groups_for_product(self, product_name: str) -> list[str]:
        """
        Retrieves all trigger groups that include the specified product name.

        The method checks the 'ProductTriggerMapping' section in the config file
        and returns all group names where the product is listed.

        Args:
            product_name (str): Product name to search for.

        Returns:
            list[str]: List of matching trigger group names.
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
