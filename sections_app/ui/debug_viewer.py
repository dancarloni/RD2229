from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from sections_app.services.debug_log_stream import get_log_buffer

logger = logging.getLogger(__name__)


class DebugViewerWindow(tk.Toplevel):
    """Real-time debug log viewer."""

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Debug Viewer")
        self.geometry("900x600")
        self._last_index = 0
        self._auto_scroll = tk.BooleanVar(value=True)
        self._filter_var = tk.StringVar(value="")

        self._build_ui()
        self._poll_logs()

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=6)

        tk.Label(toolbar, text="Filtro:").pack(side="left")
        filter_entry = ttk.Entry(toolbar, textvariable=self._filter_var, width=40)
        filter_entry.pack(side="left", padx=(6, 12))
        ttk.Checkbutton(toolbar, text="Auto-scroll", variable=self._auto_scroll).pack(side="left")
        ttk.Button(toolbar, text="Pulisci", command=self._clear).pack(side="right")

        body = tk.Frame(self)
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._text = tk.Text(body, wrap="none")
        self._text.pack(side="left", fill="both", expand=True)

        yscroll = ttk.Scrollbar(body, orient="vertical", command=self._text.yview)
        yscroll.pack(side="right", fill="y")
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self._text.xview)
        xscroll.pack(fill="x")

        self._text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self._text.configure(state="disabled")

    def _clear(self) -> None:
        self._last_index = 0
        self._text.configure(state="normal")
        self._text.delete("1.0", tk.END)
        self._text.configure(state="disabled")

    def _append_lines(self, lines: list[str]) -> None:
        if not lines:
            return
        self._text.configure(state="normal")
        for line in lines:
            self._text.insert(tk.END, line + "\n")
        self._text.configure(state="disabled")
        if self._auto_scroll.get():
            self._text.see(tk.END)

    def _poll_logs(self) -> None:
        try:
            buffer = get_log_buffer()
            if self._last_index > len(buffer):
                self._last_index = 0
            new_lines = buffer[self._last_index :]
            self._last_index = len(buffer)

            filter_text = self._filter_var.get().strip().lower()
            if filter_text:
                new_lines = [line for line in new_lines if filter_text in line.lower()]

            self._append_lines(new_lines)
        except Exception:
            logger.exception("Errore durante il polling dei log")
        finally:
            self.after(500, self._poll_logs)
