"""
📦 Module: order_data.py

Provides a simple data container for managing paths and parsed content
related to work order files (.lbl, .nor).

Author: Miloslav Hradecky
"""

from pathlib import Path


class OrderData:
    """
    Container for work order file paths and parsed content.

    Attributes:
        orders_dir (Path): Base directory for order files.
        lbl_file (Path | None): Path to .lbl file.
        nor_file (Path | None): Path to .nor file.
        lines (list[str] | None): Parsed lines from .lbl file.
    """
    def __init__(self):
        self.orders_dir = Path("T:/Prikazy")
        self.lbl_file = None
        self.nor_file = None
        self.lines = None

    def set_files(self, order_code: str):
        """
        Sets .lbl and .nor file paths based on the given order code.
        """
        self.lbl_file = self.orders_dir / f"{order_code}.lbl"
        self.nor_file = self.orders_dir / f"{order_code}.nor"
