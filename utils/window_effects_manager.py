"""
📦 Module: window_effects_manager.py

Provides fade-in and fade-out animations for PyQt6 widgets.

Responsibilities:
- Animate window opacity for smooth transitions
- Prevent garbage collection of active animations
- Support optional callbacks after fade-out

Used across controllers to enhance user experience.

Author: Miloslav Hradecky
"""

# 🧩 Third-party libraries
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve


class WindowEffectsManager:
    """
    Manages fade-in and fade-out effects for PyQt6 widgets.

    Uses QPropertyAnimation to animate window opacity with easing curves.
    Prevents premature garbage collection by storing active animations.
    """
    def __init__(self):
        """
        Initializes animation manager and prepares internal storage.
        """
        self._animations = {}

    def fade_in(self, widget, duration=700):
        """
        Applies fade-in animation to the given widget.
        Sets initial opacity, starts animation, and stores reference.
        """
        widget.setWindowOpacity(0.0)
        widget.show()
        animation: QPropertyAnimation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
        self._animations[widget] = animation

    def fade_out(self, widget, duration=700, callback=None):
        """
        Applies fade-out animation to the given widget.
        Deletes widget after fade-out and optionally calls a callback.
        """
        animation: QPropertyAnimation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        def on_finished():
            widget.deleteLater()
            if callback:
                callback()

        animation.finished.connect(on_finished)
        animation.start()
        self._animations[widget] = animation
