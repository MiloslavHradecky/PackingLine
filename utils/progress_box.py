from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from utils.resources import resource_path


class ProgressBox(QDialog):
    def __init__(self, parent=None, text='Probíhá tisk...'):
        super().__init__(parent)
        self.setWindowTitle("Tisk")
        self.setWindowIcon(QIcon(str(resource_path("views/assets/message.ico"))))
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)

        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_text(self, text: str):
        self.label.setText(text)
        self.repaint()
