from __future__ import annotations

import tkinter as tk

from app.ui.verification_table_app import VerificationTableWindow


def run_demo() -> None:
    root = tk.Tk()
    root.title("Verification Table - RD2229")
    root.geometry("1400x500")
    win = VerificationTableWindow(root)
    win.app.load_items_from_repository() if hasattr(win.app, "load_items_from_repository") else None
    root.mainloop()
