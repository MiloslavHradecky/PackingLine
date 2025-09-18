"""
📦 Module: window_stack_manager.py

Manages a stack of active windows in a PyQt6 application.

Responsibilities:
    - Push and pop windows with visibility control
    - Hide previous window when a new one is shown
    - Restore previous window when current is closed
    - Handle graceful exit transitions

Used by controllers to manage navigation between screens.

Author: Miloslav Hradecky
"""


class WindowStackManager:
    """
    Manages a stack of windows for navigation and visibility control.

    Ensures only one window is visible at a time, and restores previous
    windows when the current one is closed — unless the app is exiting.
    """

    def __init__(self):
        """
        Initializes the window stack and exit flag.
        """
        self._stack = []
        self._is_exiting = False

    def mark_exiting(self):
        """
        Marks the application as exiting to prevent window restoration.
        """
        self._is_exiting = True

    def push(self, window):
        """
        Adds a new window to the stack and hides the previous one.

        Args:
            window (QWidget): The window to show.
        """
        if self._stack:
            self._stack[-1].hide()
        self._stack.append(window)
        window.destroyed.connect(self._on_window_closed)
        window.show()

    def pop(self):
        """
        Removes the top window from the stack and restores the previous one if applicable.

        Returns:
            QWidget or None: The window that was removed.
        """
        if not self._stack:
            return None

        closing = self._stack.pop()

        if self._stack and not self._is_exiting:
            previous = self._stack[-1]
            if not previous.isVisible():
                previous.show()

        return closing

    def _on_window_closed(self):
        """
        Handles cleanup when a window is closed.

        Pops the window from the stack and restores the previous one unless exiting.
        """
        if self._is_exiting:
            return

        if self._stack:
            self._stack.pop()
            if self._stack:
                previous = self._stack[-1]
                if not previous.isVisible():
                    previous.show()
