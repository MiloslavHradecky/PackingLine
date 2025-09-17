"""
📦 Module: print_window.py

This module defines the PrintWindow class, which provides a graphical interface
for printing labels based on scanned serial numbers. It includes:
- Display of work order and product information
- Input field for serial number scanning
- Buttons for printing and exiting
- Visual enhancements via WindowEffectsManager

Used in conjunction with a controller to handle print logic.

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

# 🧠 First-party (project-specific)
from utils.window_effects_manager import WindowEffectsManager
from utils.resources import resource_path


class PrintWindow(QWidget):
    """
    GUI window for printing product labels based on serial number input.

    Responsibilities:
        - Display work order and product name
        - Provide input field for scanning serial numbers
        - Trigger print action via button or Enter key
        - Allow user to exit the window
        - Apply visual effects and styling

    Args:
        order_code (str): Code of the active work order.
        product_name (str): Human-readable name of the product.
        controller (object, optional): Controller instance for handling print logic.
    """

    def __init__(self, order_code: str, product_name: str, controller=None):
        """
        Initializes the PrintWindow and sets up its visual components.

        Steps:
            - Sets window title, size, and icon
            - Displays order and product info in styled label
            - Loads and shows logo
            - Creates input field for serial number
            - Adds print and exit buttons
            - Connects Enter key to print action
            - Applies layout and fade-in animation

        Args:
            order_code (str): Code of the active work order.
            product_name (str): Human-readable product name.
            controller (object, optional): Controller instance for handling print logic.
        """
        super().__init__()

        self.order_code = order_code
        self.product_name = product_name
        self.controller = controller

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # 🪟 Title and size
        self.setWindowTitle("Print Line B")
        self.setFixedSize(400, 500)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        self.effects = WindowEffectsManager()

        # 📌 Window icon settings
        icon_path = resource_path("views/assets/main.ico")
        self.setWindowIcon(QIcon(str(icon_path)))

        # 🔠 Font
        label_font = QFont('Arial', 11, QFont.Weight.Bold)

        # 📌 Setting the window background colour
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#D8E9F3'))
        self.setPalette(palette)

        # 🧱 Layout definition
        layout = QVBoxLayout()

        # 📌 Dynamic label with order and product
        self.print_label = QLabel(f'''
            <span style="color: black;">
                Příkaz:&nbsp;<b><span style="color:#C0392B">{self.order_code}</span></b>
                &nbsp;&nbsp;&nbsp;
                Produkt:&nbsp;<b><span style="color:#C0392B">{self.product_name}</span></b>
            </span>
        ''')
        self.print_label.setFont(label_font)
        self.print_label.setFixedHeight(32)
        self.print_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 📌 Logo
        print_logo = resource_path("views/assets/print.png")
        self.logo = QLabel(self)
        pixmap = QPixmap(str(print_logo)).scaled(self.width() - 20, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 📌 Serial number input
        self.serial_number_input: QLineEdit = QLineEdit()
        self.serial_number_input.setPlaceholderText('Naskenujte serial number')

        # 📌 Placeholder color
        self.palette = self.serial_number_input.palette()
        self.placeholder_color = QColor('#757575')
        self.palette.setColor(QPalette.ColorRole.PlaceholderText, self.placeholder_color)
        self.serial_number_input.setPalette(self.palette)

        # 🖨️ Print button
        self.print_button: QPushButton = QPushButton('Tisk')

        # 📌 Back button
        self.back_button: QPushButton = QPushButton('Zpět')

        # 📌 Exit button
        self.exit_button: QPushButton = QPushButton("Ukončit")

        # 📌 Enter triggers print
        self.serial_number_input.returnPressed.connect(self.print_button.click)

        # 📌 Add elements to the main layout
        layout.addWidget(self.print_label)
        layout.addWidget(self.logo)
        layout.addWidget(self.serial_number_input)
        layout.addWidget(self.print_button)

        # 📌 Bottom layout for navigation buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.back_button)
        bottom_layout.addWidget(self.exit_button)

        layout.addLayout(bottom_layout)

        # 📦 Finalize layout
        self.setLayout(layout)
        self.activateWindow()
        self.raise_()
        self.serial_number_input.setFocus()

        # ✨ Launch animation
        self.effects.fade_in(self, duration=500)

    def reset_input_focus(self):
        """
        Clears the serial number input field and sets focus back to it.

        Used after a successful print or to reset the input state.
        """
        self.serial_number_input.clear()
        self.serial_number_input.setFocus()
