from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget
from PyQt6.QtGui import QIcon
from utils.resources import resource_path


class Messenger:
    icon_path = resource_path("views/assets/message.ico")

    def __init__(self, parent=None):
        if isinstance(parent, QWidget):
            self.parent = parent
        else:
            self.parent = None
        self.progress_box = None

    def center_dialog(self, dialog: QMessageBox):
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
