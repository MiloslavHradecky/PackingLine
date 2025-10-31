"""
📦 Module: bartender_utils.py

Provides utility methods for managing BarTender processes (Cmdr.exe, bartend.exe),
including termination and optional user feedback via Messenger.

Author: Miloslav Hradecky
"""

# 🧱 Standard library
import time
import subprocess

# 🧠 First-party (project-specific)
from utils.logger import get_logger


class BartenderUtils:
    """
    Utility class for managing BarTender-related processes.
    Provides methods to kill, launch, and monitor BarTender components.
    """

    def __init__(self, messenger=None, config=None):
        """
        Initializes the utility with optional Messenger for user feedback.

        Args:
            messenger (Messenger | None): Optional messenger instance.
            config (ConfigParser | None): Optional config for path resolution.
        """
        self.logger = get_logger("BartenderUtils")
        self.messenger = messenger
        self.config = config

    def kill_processes(self):
        """
        Terminates all running BarTender instances (Commander.exe, Guardian.exe and bartend.exe).
        """
        try:
            subprocess.run(
                "taskkill /f /im Commander.exe 1>nul 2>nul",
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            subprocess.run(
                "taskkill /f /im Guardian.exe 1>nul 2>nul",
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            subprocess.run(
                "taskkill /f /im bartend.exe 1>nul 2>nul",
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except subprocess.CalledProcessError as e:
            self.logger.error("Chyba při ukončování BarTender procesů: %s", str(e))
            if self.messenger:
                self.messenger.error(
                    f"Chyba při ukončování BarTender procesů: {str(e)}",
                    "Bartender Utils"
                )

    def run_commander(self):
        """
        Launches BarTender Commander using configured paths.
        """
        if not self.config:
            self.logger.error("Konfigurace není dostupná pro spuštění Commanderu.")
            if self.messenger:
                self.messenger.error(
                    "Konfigurace není dostupná pro spuštění Commanderu.",
                    "Bartender Utils"
                )
            return

        commander_path = self.config.get("Paths", "commander_path", fallback=None)
        guardian_path = self.config.get("Paths", "guardian_path", fallback=None)

        if not commander_path or not guardian_path:
            self.logger.error("Cesty k Commanderu nebo Guardianu nejsou dostupné v config.ini")
            if self.messenger:
                self.messenger.error(
                    "Cesty k Commanderu nebo Guardianu nejsou dostupné v config.ini",
                    "Bartender Utils"
                )
            return

        try:
            # pylint: disable=consider-using-with
            commander_process = subprocess.Popen(
                [str(commander_path), "/START", "/MIN=SystemTray", "/NOSPLASH"],
                shell=True
            )
            self.logger.info("Commander spuštěn: PID %s", commander_process.pid)

            time.sleep(1)

            guardian_process = subprocess.Popen(
                [str(guardian_path)],
                shell=True
            )
            self.logger.info("Guardian watchdog spuštěn: PID %s", guardian_process.pid)

        except Exception as e:
            self.logger.error("Chyba při spuštění Commanderu: %s", str(e))
            if self.messenger:
                self.messenger.error(
                    f"Chyba při spuštění Commanderu: {str(e)}",
                    "Bartender Utils"
                )
