# 🔐 LoginWindow – GUI login screen with password entry for ID card systems

"""
This module defines the LoginWindow class, which provides a graphical interface
for user authentication via ID card scanning. It includes:
- A password input field with hidden text
- A login confirmation button
- An exit button
- Visual enhancements via WindowEffectsManager

Used in conjunction with ControllerApp to handle login logic.
"""

# 🧱 Standard library (žádný zde)

# 🎨 Third-party (PyQt6)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QPalette, QColor, QPixmap, QIcon

# 🧠 First-party (project-specific)
from utils.window_effects_manager import WindowEffectsManager
from utils.resources import resource_path


class LoginWindow(QWidget):
    """
    GUI window for user login via ID card.

    Responsibilities:
        - Display a password input field with hidden characters
        - Show application logo and window icon
        - Provide login and exit buttons
        - Trigger login logic via ControllerApp
        - Apply visual effects (fade-in, background color)

    Args:
        controller (object, optional): Reference to the controller managing login logic.
    """

    def __init__(self, controller=None):
        """
        Initializes the LoginWindow and sets up its visual components.

    Steps:
        - Sets window title, size, and icon
        - Applies background color and fade-in effect
        - Loads and displays application logo
        - Creates password input field with placeholder
        - Adds login and exit buttons
        - Connects Enter key to login action
        - Applies layout and focuses input field

    Args:
        controller (object, optional): Controller instance for handling login logic.
        """
        super().__init__()

        self.controller = controller
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # 📌 Setting the window name and size
        self.setWindowTitle('Přihlášení')
        self.setFixedSize(400, 500)

        self.effects = WindowEffectsManager()
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        # 📌 Window icon settings
        icon_path = resource_path("views/assets/main.ico")
        self.setWindowIcon(QIcon(str(icon_path)))

        # 📌 Setting the window background colour
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#D8E9F3'))
        self.setPalette(palette)

        # 📌 Main window layout
        layout = QVBoxLayout()

        # 📌 Application logo
        login_logo = resource_path("views/assets/login.tiff")
        self.logo = QLabel(self)
        pixmap = QPixmap(str(login_logo)).scaled(self.width() - 20, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo)

        # 📌 Password field (ID card)
        self.password_input: QLineEdit = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Naskenujte svoji ID kartu')

        # 📌 Set text color for placeholder
        self.palette = self.password_input.palette()
        self.placeholder_color = QColor('#757575')
        self.palette.setColor(QPalette.ColorRole.PlaceholderText, self.placeholder_color)
        self.password_input.setPalette(self.palette)

        # 📌 Login button
        self.login_button: QPushButton = QPushButton('Přihlásit se')

        # 📌 'Exit' selection button
        self.exit_button: QPushButton = QPushButton('Ukončit')

        # 📌 Linking the button to the login action
        self.password_input.returnPressed.connect(self.login_button.click)  # 💡 Enter activates the button

        # 📌 Přidání prvků do hlavního layoutu
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.exit_button)

        # 📌 Setting the window layout
        self.setLayout(layout)

        self.activateWindow()
        self.raise_()

        self.password_input.setFocus()
        self.effects.fade_in(self)
