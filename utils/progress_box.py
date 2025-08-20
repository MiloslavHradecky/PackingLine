from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from utils.resources import resource_path  # Pokud používáš vlastní správu cest


class ProgressBox(QDialog):
    def __init__(self, parent=None, text='Probíhá tisk...', timeout_ms=3000):
        super().__init__(parent)
        self.timeout_ms = timeout_ms

        # 🖼️ Vzhled okna
        self.setWindowTitle("Tisk")
        self.setWindowIcon(QIcon(str(resource_path("views/assets/message.ico"))))
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)

        self.setModal(True)

        # 📝 Textová zpráva
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        # QTimer.singleShot(self.timeout_ms, self.close)

    def update_text(self, text: str):
        self.label.setText(text)
        QApplication.processEvents()

    def close_after(self, ms: int):
        QTimer.singleShot(ms, self.close)
