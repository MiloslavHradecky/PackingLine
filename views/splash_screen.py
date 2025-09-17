"""
📦 Module: splash_screen.py

Defines the animated splash screen shown during application startup.

Responsibilities:
    - Display a logo and loading spinner (GIF)
    - Animate fade-in effect
    - Show loading message
    - Automatically close after a set duration and trigger callback

Used to enhance user experience during initialization.

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtWidgets import QSplashScreen, QLabel
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation

# 🧠 First-party (project-specific)
from utils.resources import resource_path


class SplashScreen(QSplashScreen):
    """
    ✨ Animated splash screen for application startup.

    Features:
        - Logo display with smooth scaling
        - Loading spinner (GIF animation)
        - Fade-in effect using QPropertyAnimation
        - Auto-close after specified duration
        - Callback execution after finish
    """
    def __init__(self, logo_path=None, spinner_path=None, duration_ms=2000):
        """
        Initializes the splash screen with logo, spinner, and fade-in animation.

        Args:
            logo_path (Path or str, optional): Path to splash logo image.
            spinner_path (Path or str, optional): Path to spinner GIF.
            duration_ms (int): Duration to display splash screen in milliseconds.
        """
        logo_path = resource_path("views/assets/splash_logo.png") if logo_path is None else logo_path
        spinner_path = resource_path("views/assets/spinner.gif") if spinner_path is None else spinner_path
        pixmap = QPixmap(str(logo_path)).scaled(1200, 800, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(0.0)
        self.duration = duration_ms

        # 📝 Text
        self.label = QLabel("Načítání aplikace…", self)
        self.label.setStyleSheet("color: white; font-size: 36px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._resize_label()

        # 🌀 Spinner (GIF animation)
        self.spinner = QLabel(self)
        movie = QMovie(str(spinner_path))
        self.spinner.setMovie(movie)
        movie.start()
        self.spinner.setFixedSize(128, 128)
        self.spinner.setScaledContents(True)
        self.spinner.setGeometry(self.width() // 2 - 64, self.height() - 200, 128, 128)  # pozice spinneru

    def _resize_label(self):
        """
        Positions the loading text label near the bottom of the splash screen.
        """
        width = self.pixmap().width() or 300
        height = self.pixmap().height() or 200
        self.label.setGeometry(0, height - 100, width, 50)

    def start(self, on_finish_callback):
        """
        Displays the splash screen with fade-in animation and closes after duration.

        Args:
            on_finish_callback (callable): Function to call after splash screen finishes.
        """
        self.show()
        self._animate_fade_in()
        QTimer.singleShot(self.duration, lambda: self._finish(on_finish_callback))

    def _animate_fade_in(self):
        """
        Applies a fade-in animation to the splash screen.
        """
        self.animation: QPropertyAnimation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1200)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.9)
        self.animation.start()

    def _finish(self, callback):
        """
        Closes the splash screen and triggers the provided callback.

        Args:
            callback (callable): Function to execute after splash screen closes.
        """
        self.close()
        callback()
