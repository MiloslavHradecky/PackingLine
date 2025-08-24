# utils/single_instance.py

"""
Utility for enforcing single-instance execution of the application.

Uses QSharedMemory to detect if another instance is already running.
"""

# 🎨 PyQt6
from PyQt6.QtCore import QSharedMemory


class SingleInstanceChecker:
    """
    Checks whether another instance of the application is already running.
    """

    def __init__(self, key="LinebUniqueAppKey"):
        """
        Initializes the shared memory block with a unique key.

        Args:
            key (str): Unique identifier for the shared memory segment.
        """
        self.key = key
        self.shared_memory = QSharedMemory(self.key)

    def is_running(self):
        """
        Determines if another instance of the application is already running.

        Returns:
            bool: True if another instance is detected, False otherwise.
        """
        if self.shared_memory.attach():
            return True
        if not self.shared_memory.create(1):
            return True
        return False
