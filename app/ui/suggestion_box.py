from __future__ import annotations
import tkinter as tk
from typing import Callable, List, Optional


class SuggestionBox:
    def __init__(self, parent: tk.Misc, on_select: Optional[Callable[[str], None]] = None):
        self.parent = parent
        self.on_select = on_select
        self._box: Optional[tk.Toplevel] = None
        self._list: Optional[tk.Listbox] = None

    def ensure(self) -> None:
        if self._box is not None and self._box.winfo_exists():
            return
        self._box = tk.Toplevel(self.parent)
        self._box.wm_overrideredirect(True)
        self._box.attributes("-topmost", True)
        self._list = tk.Listbox(self._box, height=6)
        self._list.pack(fill="both", expand=True)
        self._list.bind("<ButtonRelease-1>", self._on_click)
        self._list.bind("<Return>", self._on_enter)
        self._list.bind("<Escape>", lambda _e: self.hide())

    def show(self, items: List[str], x: int, y: int, width: int, height: int) -> None:
        self.ensure()
        if not self._box or not self._list:
            return
        self._list.delete(0, "end")
        for it in items:
            self._list.insert("end", it)
        self._box.geometry(f"{width}x{height}+{x}+{y}")
        self._box.deiconify()
        self._box.lift()

    def hide(self) -> None:
        if self._box is not None:
            try:
                self._box.withdraw()
            except Exception:
                pass

    def _on_click(self, _ev) -> None:
        if not self._list:
            return
        sel = self._list.curselection()
        if not sel:
            return
        value = self._list.get(sel[0])
        if self.on_select:
            self.on_select(value)
        self.hide()

    def _on_enter(self, _ev) -> None:
        if not self._list:
            return
        sel = self._list.curselection()
        if not sel:
            return
        value = self._list.get(sel[0])
        if self.on_select:
            self.on_select(value)
        self.hide()
