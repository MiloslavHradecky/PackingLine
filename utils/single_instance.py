from PyQt6.QtCore import QSharedMemory


class SingleInstanceChecker:
    def __init__(self, key="MlpUniqueAppKey"):
        self.key = key
        self.shared_memory = QSharedMemory(self.key)

    def is_running(self):
        if self.shared_memory.attach():
            return True
        if not self.shared_memory.create(1):
            return True
        return False
