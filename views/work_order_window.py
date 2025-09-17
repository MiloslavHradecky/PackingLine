"""
📦 Module: work_order_window.py

This module defines the WorkOrderWindow class, which provides a graphical interface
for entering or scanning a work order code (e.g., barcode or ID). It includes:
- A styled input field
- Buttons for continuing or exiting
- Application logo and visual effects

Used during the initial phase of the workflow to identify the active work order.

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QPalette, QColor, QPixmap, QIcon

# 🧠 First-party (project-specific)
from utils.window_effects_manager import WindowEffectsManager
from utils.resources import resource_path


class WorkOrderWindow(QWidget):
    """
    GUI window for scanning or entering a work order code.

    Responsibilities:
        - Display application logo and styled background
        - Provide input field for scanning work order
        - Include buttons to continue or exit
        - Trigger controller logic via Enter key
        - Apply fade-in visual effect

    Args:
        controller (object, optional): Controller instance for handling workflow logic.
    """

    def __init__(self, controller=None):
        """
        Initializes the WorkOrderWindow and sets up its visual components.

        Steps:
            - Sets window title, size, and icon
            - Loads and displays logo
            - Creates input field with placeholder styling
            - Adds continue and exit buttons
            - Connects Enter key to continue action
            - Applies layout and fade-in animation

        Args:
            controller (object, optional): Controller instance for handling workflow logic.
        """
        super().__init__()

        self.controller = controller
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # 📌 Title and dimensions
        self.setWindowTitle("Work Order")
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
        work_order_logo = resource_path("views/assets/work_order_find.png")
        self.logo = QLabel(self)
        pixmap = QPixmap(str(work_order_logo)).scaled(self.width() - 20, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo)

        # 📌 Work order input field
        self.work_order_input: QLineEdit = QLineEdit()
        self.work_order_input.setPlaceholderText("Naskenujte pracovní příkaz")

        # 📌 Placeholder color
        self.palette = self.work_order_input.palette()
        self.placeholder_color = QColor("#757575")
        self.palette.setColor(QPalette.ColorRole.PlaceholderText, self.placeholder_color)
        self.work_order_input.setPalette(self.palette)

        # ⏭️ Continue button
        self.next_button: QPushButton = QPushButton("Pokračuj")

        # 📌 Back button
        self.back_button: QPushButton = QPushButton("Zpět")

        # 📌 Exit button
        self.exit_button: QPushButton = QPushButton("Ukončit")

        # 📌 Enter triggers continue
        self.work_order_input.returnPressed.connect(self.next_button.click)

        # 📦 Add widgets to layout
        layout.addWidget(self.work_order_input)
        layout.addWidget(self.next_button)

        # 📌 Bottom layout for navigation buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.back_button)
        bottom_layout.addWidget(self.exit_button)

        layout.addLayout(bottom_layout)

        # 📌 Setting the window layout
        self.setLayout(layout)

        # ⬆️ Window priority and visual effect
        self.activateWindow()
        self.raise_()
        self.work_order_input.setFocus()
        self.effects.fade_in(self, duration=500)
