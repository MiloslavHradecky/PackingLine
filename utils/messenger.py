"""
📦 Module: messenger.py

Utility class for displaying message dialogs in a PyQt6 application.

Responsibilities:
    - Show error, info, and warning dialogs with consistent styling
    - Center dialogs relative to parent or screen
    - Display timed non-blocking info popups

Used across controllers to provide user feedback.

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget, QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, Qt

# 🧠 First-party
from utils.resources import resource_path


class Messenger:
    """
    🎙️ Wrapper class for displaying styled message dialogs in PyQt6.

    Supports:
        - Blocking dialogs: error, info, warning
        - Non-blocking timed info popups
        - Centering dialogs on parent or screen
    """
    icon_path = resource_path("views/assets/message.ico")

    def __init__(self, parent=None):
        """
        Initializes the Messenger with an optional parent widget.

        Args:
            parent (QWidget, optional): Parent widget for dialog positioning.
        """
        if isinstance(parent, QWidget):
            self.parent = parent
        else:
            self.parent = None

    def center_dialog(self, dialog: QWidget):
        """
        Centers the dialog relative to the parent widget or screen.

        Args:
            dialog (QWidget): The dialog to center.
        """
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
        """
        Displays a blocking error dialog.

        Args:
            message (str): The error message to display.
            title (str): Dialog window title.
        """
        box = QMessageBox(self.parent)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.show()
        self.center_dialog(box)
        box.exec()

    def info(self, message: str, title: str = "Information"):
        """
        Displays a blocking informational dialog.

        Args:
            message (str): The info message to display.
            title (str): Dialog window title.
        """
        box = QMessageBox(self.parent)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.show()
        self.center_dialog(box)
        box.exec()

    def warning(self, message: str, title: str = "Warning"):
        """
        Displays a blocking warning dialog.

        Args:
            message (str): The warning message to display.
            title (str): Dialog window title.
        """
        box = QMessageBox(self.parent)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.setWindowIcon(QIcon(str(Messenger.icon_path)))
        box.show()
        self.center_dialog(box)
        box.exec()

    def auto_info_dialog(self, message: str, timeout_ms: int = 3000, title: str = "Zpracování"):
        """
        Displays a non-blocking info dialog that automatically closes after a timeout.

        Args:
            message (str): The message to display.
            timeout_ms (int): Time in milliseconds before the dialog closes.
            title (str): Dialog window title.
        """
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(title)
        dialog.setObjectName("PrintInfoDialog")
        dialog.setWindowModality(Qt.WindowModality.NonModal)

        # ✅ WindowFlags - displays a header with an icon, but no buttons
        dialog.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.CustomizeWindowHint
        )
        # ✅ Header icon settings
        dialog.setWindowIcon(QIcon(str(Messenger.icon_path)))

        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout()
        label = QLabel(message)
        label.setObjectName("PrintInfoLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        dialog.setLayout(layout)

        dialog.setMinimumSize(300, 100)
        dialog.adjustSize()
        self.center_dialog(dialog)
        dialog.show()

        QTimer.singleShot(timeout_ms, dialog.close)
