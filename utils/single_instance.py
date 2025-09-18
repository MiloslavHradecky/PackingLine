"""
📦 Module: single_instance_checker.py

Utility for preventing multiple instances of the application.

Responsibilities:
    - Use QSharedMemory to detect if another instance is already running
    - Block duplicate launches by checking shared memory attachment
    - Used during application startup to enforce single-instance behavior

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtCore import QSharedMemory


class SingleInstanceChecker:
    """
    Prevents multiple instances of the application using QSharedMemory.

    Checks whether a shared memory block with a unique key is already attached.
    If so, assumes another instance is running.
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
