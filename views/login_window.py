"""
📦 Module: login_window.py

Defines the application's login window using PyQt6.

Responsibilities:
- Display password input field (ID card scan)
- Show login and exit buttons
- Apply custom styling, icons, and fade-in effects
- Connect input to controller logic

Used by ControllerApp to initiate authentication.

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QPalette, QColor, QPixmap, QIcon

# 🧠 First-party (project-specific)
from utils.window_effects_manager import WindowEffectsManager
from utils.resources import resource_path


class LoginWindow(QWidget):
    """
    Login window for user authentication.

    Displays password input, logo, and navigation buttons.
    Applies fade-in effect and connects input to controller logic.
    """

    def __init__(self, controller=None):
        """
        Initializes LoginWindow and sets up visual components.
        Configures layout, styling, input field, buttons, and fade-in animation.
        """
        super().__init__()

        self.controller = controller
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # 📌 Setting the window name and size
        self.setWindowTitle("Přihlášení")
        self.setFixedSize(400, 500)

        self.effects = WindowEffectsManager()
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        # 📌 Window icon settings
        icon_path = resource_path("views/assets/main.ico")
        self.setWindowIcon(QIcon(str(icon_path)))

        # 📌 Setting the window background colour
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#D8E9F3"))
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
        self.password_input.setPlaceholderText("Naskenujte svoji ID kartu")

        # 📌 Set text color for placeholder
        self.palette = self.password_input.palette()
        self.placeholder_color = QColor("#757575")
        self.palette.setColor(QPalette.ColorRole.PlaceholderText, self.placeholder_color)
        self.password_input.setPalette(self.palette)

        # 📌 Login button
        self.login_button: QPushButton = QPushButton("Přihlásit se")

        # 📌 "Exit" selection button
        self.exit_button: QPushButton = QPushButton("Ukončit")

        # 📌 Linking the button to the login action
        self.password_input.returnPressed.connect(self.login_button.click)

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
