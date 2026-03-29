
import tkinter as tk
from tkinter import ttk, messagebox

class SollecitazioniView(ttk.Frame):
    """
    Inserimento delle sollecitazioni di progetto:
    N, Tx, Ty, Mx, My, Mz (sistema locale).
    """

    def __init__(self, parent, project_model):
        super().__init__(parent)
        self.project_model = project_model
        self._vars = {}
        self._build_ui()

    def _build_ui(self):
        frame = ttk.LabelFrame(self, text="Sollecitazioni di progetto")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        fields = [
            ("N [kN]", "N"),
            ("Tx [kN]", "Tx"),
            ("Ty [kN]", "Ty"),
            ("Mx [kNm]", "Mx"),
            ("My [kNm]", "My"),
            ("Mz [kNm]", "Mz"),
        ]

        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            var = tk.DoubleVar(value=0.0)
            self._vars[key] = var
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="ew", padx=5)

        frame.columnconfigure(1, weight=1)

        btn = ttk.Button(frame, text="Salva sollecitazioni ▶", command=self._save)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def _save(self):
        self.project_model.sollecitazioni = {k: v.get() for k, v in self._vars.items()}
        messagebox.showinfo("OK", "Sollecitazioni salvate nel progetto.")
