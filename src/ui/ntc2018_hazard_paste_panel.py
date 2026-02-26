"""Thin UI panel for pasting NTC2018 hazard parameters from EdiLus-MS."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from verification_project import VerificationProject
from src.codes.ntc2018 import spectrum_paste_service as svc


class HazardPasteWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, project: Optional[VerificationProject] = None):
        super().__init__(master=master)
        self.title("Parametri sismici NTC2018 (Paste)")
        self.geometry("600x600")
        self.project = project or VerificationProject()
        if hasattr(self.project, "new_project"):
            self.project.new_project()

        # variables
        self.class_var = tk.StringVar(value="")
        self.vn_var = tk.StringVar(value="")
        self.vr_var = tk.StringVar(value="")
        self.site_var = tk.StringVar(value="")
        self.quality_var = tk.StringVar(value="")
        self.messages_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self) -> None:
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # input fields
        row = 0
        ttk.Label(frm, text="Classe uso (I-IV):").grid(column=0, row=row, sticky="w")
        ttk.Entry(frm, textvariable=self.class_var).grid(column=1, row=row, sticky="ew")
        row += 1
        ttk.Label(frm, text="Vita nominale anni:").grid(column=0, row=row, sticky="w")
        ttk.Entry(frm, textvariable=self.vn_var).grid(column=1, row=row, sticky="ew")
        row += 1
        ttk.Label(frm, text="Periodo riferimento anni:").grid(column=0, row=row, sticky="w")
        ttk.Entry(frm, textvariable=self.vr_var).grid(column=1, row=row, sticky="ew")
        row += 1
        ttk.Label(frm, text="Etichetta sito (facolt.):").grid(column=0, row=row, sticky="w")
        ttk.Entry(frm, textvariable=self.site_var).grid(column=1, row=row, sticky="ew")
        row += 1

        # raw paste
        ttk.Label(frm, text="Incolla tabella EdiLus-MS:").grid(column=0, row=row, sticky="nw")
        self.raw_text = tk.Text(frm, height=8, width=60)
        self.raw_text.grid(column=1, row=row, sticky="ew")
        row += 1
        analyze_btn = ttk.Button(frm, text="Analizza", command=self.analyze)
        analyze_btn.grid(column=1, row=row, sticky="e")
        row += 1

        # preview
        ttk.Label(frm, text="Preview righe parsate:").grid(column=0, row=row, sticky="nw")
        self.preview = tk.Text(frm, height=6, width=60, state="disabled")
        self.preview.grid(column=1, row=row, sticky="ew")
        row += 1

        ttk.Label(frm, text="Qualità:").grid(column=0, row=row, sticky="w")
        ttk.Label(frm, textvariable=self.quality_var).grid(column=1, row=row, sticky="w")
        row += 1
        ttk.Label(frm, text="Messaggi:").grid(column=0, row=row, sticky="nw")
        self.messages_label = ttk.Label(frm, textvariable=self.messages_var, wraplength=400)
        self.messages_label.grid(column=1, row=row, sticky="w")
        row += 1

        save_btn = ttk.Button(frm, text="Salva nel progetto", command=self.save)
        save_btn.grid(column=1, row=row, sticky="e")

        for i in range(2):
            frm.columnconfigure(i, weight=1)

    def analyze(self) -> None:
        raw = self.raw_text.get("1.0", "end").strip()
        rows, msgs, quality = svc.parse_edilus_ms_table(raw)
        self.quality_var.set(quality)
        self.messages_var.set("; ".join(msgs))
        # populate preview
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        for r in rows:
            self.preview.insert("end",
                f"{r.limit_state_label}: Tr={r.tr_years}, ag/g={r.ag_g}, F0={r.f0}, Tc*={r.tc_star_s}\n"
            )
        self.preview.config(state="disabled")

    def save(self) -> None:
        raw = self.raw_text.get("1.0", "end").strip()
        try:
            profile = svc.build_profile(
                class_of_use=self.class_var.get(),
                vita_nominale_years=int(self.vn_var.get() or 0),
                vr_years=int(self.vr_var.get() or 0),
                site_label=self.site_var.get() or None,
                raw_paste=raw,
            )
        except Exception as e:  # just in case
            messagebox.showerror("Errore", f"Impossibile costruire profilo: {e}")
            return
        self.project.seismic_inputs.ntc2018_hazard_profile = profile
        # mark dirty flag if available
        if hasattr(self.project, "dirty"):
            self.project.dirty = True
        messagebox.showinfo("Salva", "Profilo salvato nel progetto")
