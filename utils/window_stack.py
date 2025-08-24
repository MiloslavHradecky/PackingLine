# utils/window_stack.py

"""
Provides a stack-based mechanism for managing visibility and lifecycle of PyQt6 windows.
Ensures only one window is visible at a time and restores previous windows when one is closed.
"""

# 🧱 Standard library — none

# 🧠 Third-party — assumed PyQt6 (not directly imported here)

class WindowStackManager:
    """
    Manages a stack of windows, ensuring only the topmost window is visible.

    Attributes:
        _stack (list): Internal list representing the window stack.
    """
    def __init__(self):
        """
        Initializes an empty window stack.
        """
        self._stack = []

    def push(self, window):
        """
        Pushes a new window onto the stack and displays it.

        Hides the current top window (if any), connects the window's destroyed signal,
        and shows the new window.

        Args:
            window: The PyQt6 window to push onto the stack.
        """
        if self._stack:
            self._stack[-1].hide()
        self._stack.append(window)
        window.destroyed.connect(self._on_window_closed)
        window.show()

    def pop(self):
        """
        Pops the top window from the stack and restores the previous one (if any).

        Returns:
            The window that was removed from the stack, or None if the stack was empty.
        """
        if not self._stack:
            return None

        closing = self._stack.pop()

        if self._stack:
            previous = self._stack[-1]
            if not previous.isVisible():
                previous.show()

        return closing

    def _on_window_closed(self):
        """
        Internal slot called when a window is destroyed.

        Automatically pops the window from the stack.
        """
        self.pop()
