from __future__ import annotations

import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class ComparatorWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Comparator")
        self.geometry("400x200")
        tk.Label(self, text="Comparator placeholder").pack(padx=8, pady=8)
        logger.debug("ComparatorWindow placeholder created")
