# 🚀 SplashScreen – animated startup screen with logo, text and spinner

"""
This module defines the SplashScreen class, which displays an animated splash screen
during application startup. It includes:
- A logo image
- A loading text label
- A spinner animation (GIF)
- Fade-in effect and timed dismissal

Used to enhance user experience during initialization.
"""

# 🎨 Third-party (PyQt6)
from PyQt6.QtWidgets import QSplashScreen, QLabel
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation

# 🧠 First-party (project-specific)
from utils.resources import resource_path


class SplashScreen(QSplashScreen):
    """
    Animated splash screen shown during application startup.

    Responsibilities:
        - Display logo and loading text
        - Show spinner animation (GIF)
        - Apply fade-in effect
        - Automatically close after a set duration
        - Trigger callback when finished

    Args:
        logo_path (str, optional): Path to the logo image.
        spinner_path (str, optional): Path to the spinner GIF.
        duration_ms (int): Duration to show splash screen in milliseconds.
    """
    def __init__(self, logo_path=None, spinner_path=None, duration_ms=2000):
        """
        Initializes the splash screen with logo, spinner, and fade-in effect.

        Steps:
            - Loads logo and spinner resources
            - Sets window flags and opacity
            - Creates and positions loading text label
            - Starts spinner animation

        Args:
            logo_path (str, optional): Path to logo image. Defaults to predefined asset.
            spinner_path (str, optional): Path to spinner GIF. Defaults to predefined asset.
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

    def _animate_fade_in(self):  # pylint: disable=attribute-defined-outside-init
        """
        Applies a fade-in animation to the splash screen.
        """
        self.animation = QPropertyAnimation(self, b"windowOpacity")
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
