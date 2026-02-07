from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from sections_app.services.historical_calculations import (
    verify_flexure_allowable_stress,
)
from sections_app.services.repository import SectionRepository  # type: ignore[import]

logger = logging.getLogger(__name__)


class HistoricalModuleMainWindow(tk.Toplevel):
    """Finestra principale (stub) per i calcoli storici RD 2229 / Santarella / Giangreco.

    ✅ Estende tk.Toplevel per rimanere una finestra figlia della root principale.
    ✅ Può essere chiusa indipendentemente senza chiudere l'intera applicazione.
    """

    def __init__(self, master: tk.Tk, repository: SectionRepository):
        super().__init__(master)
        self.title("Historical Calculations - RD2229")
        self.geometry("720x420")
        self.repository = repository
        self.selected_section_id: Optional[str] = None
        self._build_ui()

        # ✅ Gestisci la chiusura della finestra in modo indipendente
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        """Handler per la chiusura della finestra - chiude solo questa Toplevel, non l'intera app."""
        self.destroy()

    def _build_ui(self) -> None:
        top = tk.Frame(self)
        top.pack(fill="x", padx=8, pady=8)

        tk.Label(top, text="Select section from archive:").grid(row=0, column=0, sticky="w")
        self.section_combo = ttk.Combobox(top, values=self._section_labels(), state="readonly", width=44)
        self.section_combo.grid(row=0, column=1, padx=8)
        self.section_combo.bind("<<ComboboxSelected>>", self._on_section_selected)

        tk.Label(top, text="Verification type:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.verify_var = tk.StringVar(value="Flexure (RD 2229 placeholder)")
        self.verify_combo = ttk.Combobox(
            top,
            textvariable=self.verify_var,
            values=["Flexure (RD 2229 placeholder)", "Axial + Flexure (TODO)", "Shear (TODO)"],
            state="readonly",
            width=44,
        )
        self.verify_combo.grid(row=1, column=1, padx=8, pady=(6, 0))

        tk.Label(top, text="Inputs (N, Mx, My) [TODO units]:").grid(row=2, column=0, sticky="w", pady=(6, 0))
        inputs_frame = tk.Frame(top)
        inputs_frame.grid(row=2, column=1, sticky="w")
        tk.Label(inputs_frame, text="N:").grid(row=0, column=0)
        self.n_entry = tk.Entry(inputs_frame, width=10)
        self.n_entry.grid(row=0, column=1, padx=(2, 8))
        tk.Label(inputs_frame, text="Mx:").grid(row=0, column=2)
        self.mx_entry = tk.Entry(inputs_frame, width=10)
        self.mx_entry.grid(row=0, column=3, padx=(2, 8))
        tk.Label(inputs_frame, text="My:").grid(row=0, column=4)
        self.my_entry = tk.Entry(inputs_frame, width=10)
        self.my_entry.grid(row=0, column=5, padx=(2, 8))

        tk.Button(top, text="Run verification", command=self._run_verification).grid(row=3, column=1, pady=(8, 0))

        self.output = tk.Text(self, height=14)
        self.output.pack(fill="both", expand=True, padx=8, pady=(8, 8))

    def _section_labels(self):
        return [f"{s.name} ({s.section_type})" for s in self.repository.get_all_sections()]

    def _on_section_selected(self, _event=None) -> None:
        sel = self.section_combo.get()
        # find by name - simple heuristic
        for s in self.repository.get_all_sections():
            if sel.startswith(s.name):
                self.selected_section_id = s.id
                break

    def _run_verification(self) -> None:
        section = None
        if self.selected_section_id:
            section = self.repository.find_by_id(self.selected_section_id)
        if not section:
            messagebox.showerror("Error", "Select a section from archive first")
            return
        try:
            N = float(self.n_entry.get() or 0.0)
            Mx = float(self.mx_entry.get() or 0.0)
            My = float(self.my_entry.get() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input")
            return

        result = verify_flexure_allowable_stress(section, N, Mx, My)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, result)
