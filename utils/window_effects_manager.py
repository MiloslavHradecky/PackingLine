# utils/window_effects_manager.py

"""
Provides fade-in and fade-out animations for PyQt6 widgets using QPropertyAnimation.
Helps improve UI experience with smooth transitions.
"""

# 🧱 Standard library — none

# 🧠 Third-party
from PyQt6.QtCore import QPropertyAnimation


class WindowEffectsManager:
    """
    Manages window opacity animations for PyQt6 widgets.

    Attributes:
        _animations (dict): Stores active animations to prevent garbage collection.
    """
    def __init__(self):
        """
        Initializes the WindowEffectsManager with an empty animation registry.
        """
        self._animations = {}

    def fade_in(self, widget, duration=700):
        """
        Applies a fade-in effect to the given widget.

        Args:
            widget: The PyQt6 widget to animate.
            duration (int): Duration of the animation in milliseconds. Default is 700.
        """
        widget.setWindowOpacity(0.0)
        widget.show()
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.start()
        self._animations[widget] = animation  # ochrání před GC

    def fade_out(self, widget, duration=700):
        """
        Applies a fade-out effect to the given widget and closes it after completion.

        Args:
            widget: The PyQt6 widget to animate.
            duration (int): Duration of the animation in milliseconds. Default is 700.
        """
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.start()
        animation.finished.connect(widget.close)  # type: ignore
        self._animations[widget] = animation
