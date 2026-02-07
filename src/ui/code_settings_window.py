from __future__ import annotations

import json
import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from sections_app.services.notification import notify_error  # type: ignore[import]
from sections_app.services.notification import notify_info  # type: ignore[import]

logger = logging.getLogger(__name__)


class CodeSettingsWindow(tk.Toplevel):
    """Simple editor for .jsoncode settings."""

    def __init__(self, master: tk.Misc, code: str, settings_path: Path):
        super().__init__(master)
        self.code = code.upper()
        self.settings_path = settings_path
        self.title(f"Parametri {self.code}")
        self.geometry("800x600")

        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=6)

        tk.Label(toolbar, text=f"File: {self.settings_path}").pack(side="left")
        ttk.Button(toolbar, text="Ricarica", command=self._load).pack(side="right")
        ttk.Button(toolbar, text="Salva", command=self._save).pack(side="right", padx=(0, 6))

        self._text = tk.Text(self, wrap="none")
        self._text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self._text.yview)
        yscroll.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self._text.configure(yscrollcommand=yscroll.set)

    def _load(self) -> None:
        try:
            raw = self.settings_path.read_text(encoding="utf-8")
            self._text.delete("1.0", tk.END)
            self._text.insert(tk.END, raw)
        except Exception as exc:
            logger.exception("Errore caricamento %s", self.settings_path)
            notify_error(
                "Caricamento parametri",
                f"Errore nel caricamento: {exc}",
                source="code_settings_window",
            )

    def _save(self) -> None:
        try:
            data = json.loads(self._text.get("1.0", tk.END))
            self.settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            notify_info("Salvataggio parametri", "Salvataggio completato", source="code_settings_window")
        except json.JSONDecodeError as exc:
            notify_error("Salvataggio parametri", f"JSON non valido: {exc}", source="code_settings_window")
        except Exception as exc:
            logger.exception("Errore salvataggio %s", self.settings_path)
            notify_error(
                "Salvataggio parametri",
                f"Errore nel salvataggio: {exc}",
                source="code_settings_window",
            )
