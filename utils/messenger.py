from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget
from PyQt6.QtGui import QIcon
from utils.resources import resource_path


class Messenger:
    icon_path = resource_path("view/assets/message.ico")

    def __init__(self, parent=None):
        if isinstance(parent, QWidget):
            self.parent = parent
        else:
            self.parent = None
        self.progress_box = None

    @staticmethod
    def error(message: str, title: str = "Error"):
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.exec()

    @staticmethod
    def info(message: str, title: str = "Information"):
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.exec()

    @staticmethod
    def warning(message: str, title: str = "Warning"):
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.exec()

    def show_progress_box(self, text='Příprava tisku...'):
        """Displays a progress box with text."""
        if not self.progress_box:
            self.progress_box = QMessageBox(self.parent or None)
            self.progress_box.setIcon(QMessageBox.Icon.Information)
            self.progress_box.setWindowIcon(QIcon(str(Messenger.icon_path)))
            self.progress_box.setWindowTitle('Probíhá tisk...')
            self.progress_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
            self.progress_box.setFixedSize(400, 200)

        self.progress_box.setText(text)
        self.progress_box.show()
        QApplication.instance().processEvents()

    def update_progress_text(self, text):
        """Updates the text of the progress box."""
        if self.progress_box:
            self.progress_box.setText(text)
            self.progress_box.repaint()

    def set_progress_no_buttons(self):
        """Removes the buttons in the progress box."""
        if self.progress_box:
            self.progress_box.setStandardButtons(QMessageBox.StandardButton.NoButton)

    def close_progress_box(self):
        """Closes the progress box and frees the memory."""
        if self.progress_box:
            self.progress_box.close()
            self.progress_box.deleteLater()
            self.progress_box = None
