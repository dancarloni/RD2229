from __future__ import annotations

from app.ui.verification_table_app import VerificationTableWindow


def run_demo() -> None:
    """Legacy demo entrypoint using Tkinter.

    Importing ``app.entrypoints.run_demo`` no longer pulls in ``tkinter`` at
    module level; the dependency is loaded lazily when the function is called.
    """
    try:
        import tkinter as tk
    except ImportError as exc:
        raise RuntimeError("Tkinter is not available in this environment") from exc

    root = tk.Tk()
    root.title("Verification Table - RD2229")
    root.geometry("1400x500")
    win = VerificationTableWindow(root)
    win.app.load_items_from_repository() if hasattr(win.app, "load_items_from_repository") else None
    root.mainloop()
