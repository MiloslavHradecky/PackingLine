from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget, QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, Qt
from utils.resources import resource_path


class Messenger:
    icon_path = resource_path("views/assets/message.ico")

    def __init__(self, parent=None):
        if isinstance(parent, QWidget):
            self.parent = parent
        else:
            self.parent = None
        self.auto_info_box = None

    def center_dialog(self, dialog: QWidget):
        """Centers the dialog relative to parent or screen."""
        QApplication.instance().processEvents()
        dialog.adjustSize()
        rect = dialog.frameGeometry()

        if self.parent:
            parent_center = self.parent.geometry().center()
        else:
            screen_center = QApplication.primaryScreen().availableGeometry().center()
            parent_center = screen_center

        rect.moveCenter(parent_center)
        dialog.move(rect.topLeft())

    def error(self, message: str, title: str = "Error"):
        box = QMessageBox(self.parent)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.show()
        self.center_dialog(box)
        box.exec()

    def info(self, message: str, title: str = "Information"):
        box = QMessageBox(self.parent)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.show()
        self.center_dialog(box)
        box.exec()

    def warning(self, message: str, title: str = "Warning"):
        box = QMessageBox(self.parent)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.show()
        self.center_dialog(box)
        box.exec()

    def auto_info_dialog(self, message: str, timeout_ms: int = 1500, title: str = "Zpracování"):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(title)
        dialog.setWindowModality(Qt.WindowModality.NonModal)

        # ✅ Nastavení ikonky v záhlaví
        dialog.setWindowIcon(QIcon(str(Messenger.icon_path)))

        # ✅ WindowFlags — zobrazí záhlaví s ikonou, ale bez tlačítek
        dialog.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.CustomizeWindowHint
        )

        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        dialog.setLayout(layout)

        dialog.resize(300, 100)
        self.center_dialog(dialog)
        dialog.show()

        QTimer.singleShot(timeout_ms, dialog.close)
