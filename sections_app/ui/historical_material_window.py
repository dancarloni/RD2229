from __future__ import annotations

import logging
from typing import List, Optional
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from historical_materials import HistoricalMaterial, HistoricalMaterialLibrary, HistoricalMaterialType
from core_models.materials import MaterialRepository

logger = logging.getLogger(__name__)


class HistoricalMaterialWindow(tk.Toplevel):
    """Window to manage HistoricalMaterialLibrary and import into MaterialRepository."""

    COLUMNS = [
        ("name", "Nome"),
        ("code", "Codice"),
        ("type", "Tipo"),
        ("source", "Fonte"),
        ("fck", "fck [kg/cm²]"),
        ("fcd", "fcd [kg/cm²]"),
        ("fyk", "fyk [kg/cm²]"),
        ("fyd", "fyd [kg/cm²]"),
        ("Ec", "Ec [kg/cm²]"),
        ("Es", "Es [kg/cm²]"),
        ("gamma_c", "γ_c"),
        ("gamma_s", "γ_s"),
        ("notes", "Note"),
    ]

    def __init__(self, master: tk.Misc, library: HistoricalMaterialLibrary, material_repository: Optional[MaterialRepository] = None) -> None:
        super().__init__(master)
        self.title("Archivio Materiali Storici")
        self.geometry("1000x480")
        self.library = library
        self.material_repository = material_repository

        self._build_ui()
        self._load_library()

    def _build_ui(self) -> None:
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Treeview
        cols = [c[0] for c in self.COLUMNS]
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for key, label in self.COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=100)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=(6, 12))

        tk.Button(btn_frame, text="Aggiungi", command=self._on_add).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Modifica", command=self._on_edit).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Elimina", command=self._on_delete).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Importa in archivio materiali", command=self._on_import_selected).pack(side="right", padx=4)

        # Bind double click to edit
        self.tree.bind("<Double-1>", lambda e: self._on_edit())

    def _load_library(self) -> None:
        # Load from file and refresh view
        try:
            self.library.load_from_file()
        except Exception:
            logger.exception("Errore caricamento historical library")
        self._refresh_table()

    def _refresh_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for hist in self.library.get_all():
            values = [
                hist.name,
                hist.code,
                getattr(hist, "type", "").value if hasattr(hist, "type") else str(getattr(hist, "type", "")),
                hist.source or "",
                str(hist.fck or ""),
                str(hist.fcd or ""),
                str(hist.fyk or ""),
                str(hist.fyd or ""),
                str(hist.Ec or ""),
                str(hist.Es or ""),
                str(hist.gamma_c or ""),
                str(hist.gamma_s or ""),
                hist.notes or "",
            ]
            self.tree.insert("", "end", iid=hist.code, values=values)

    def _on_add(self) -> None:
        dlg = _HistoricalEditDialog(self, title="Aggiungi materiale storico")
        self.wait_window(dlg)
        if dlg.result:
            self.library.add(dlg.result)
            self._refresh_table()

    def _on_edit(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Modifica", "Seleziona una riga da modificare")
            return
        code = sel[0]
        hist = self.library.find_by_code(code)
        if hist is None:
            messagebox.showerror("Errore", "Elemento non trovato")
            return
        dlg = _HistoricalEditDialog(self, title="Modifica materiale storico", material=hist)
        self.wait_window(dlg)
        if dlg.result:
            # replace by code
            self.library.add(dlg.result)
            self._refresh_table()

    def _on_delete(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Elimina", "Seleziona una riga da eliminare")
            return
        if not messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare la riga selezionata?"):
            return
        code = sel[0]
        mat = self.library.find_by_code(code)
        if mat:
            # remove
            self.library._materials = [m for m in self.library._materials if m.code != code]
            self.library.save_to_file()
            self._refresh_table()

    def _on_import_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Importa", "Seleziona uno o più materiali da importare")
            return
        if self.material_repository is None:
            messagebox.showerror("Importa", "Archivio materiali non disponibile")
            return
        imported = 0
        for code in sel:
            hist = self.library.find_by_code(code)
            if hist is None:
                continue
            try:
                mat = self.material_repository.import_historical_material(hist)
                self.material_repository.add(mat)
                imported += 1
            except Exception:
                logger.exception("Errore import materiale storico %s", code)
        messagebox.showinfo("Importa", f"Importati {imported} materiali")
        

class _HistoricalEditDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, title: str = "", material: Optional[HistoricalMaterial] = None) -> None:
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.grab_set()
        self.result: Optional[HistoricalMaterial] = None

        self._create_fields()
        if material:
            self._populate(material)
        self._build_buttons()

    def _create_fields(self) -> None:
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)

        # Basic fields
        tk.Label(frm, text="Nome").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(frm, width=40)
        self.name_entry.grid(row=0, column=1, sticky="w")

        tk.Label(frm, text="Codice").grid(row=1, column=0, sticky="w")
        self.code_entry = tk.Entry(frm, width=40)
        self.code_entry.grid(row=1, column=1, sticky="w")

        tk.Label(frm, text="Fonte").grid(row=2, column=0, sticky="w")
        self.source_entry = tk.Entry(frm, width=40)
        self.source_entry.grid(row=2, column=1, sticky="w")

        tk.Label(frm, text="Tipo").grid(row=3, column=0, sticky="w")
        self.type_var = tk.StringVar(value=HistoricalMaterialType.CONCRETE.value)
        self.type_combo = ttk.Combobox(frm, textvariable=self.type_var, values=[t.value for t in HistoricalMaterialType], state="readonly")
        self.type_combo.grid(row=3, column=1, sticky="w")

        # Numeric fields
        row = 4
        self.num_fields = {}
        for label, key in [("fck", "fck"), ("fcd", "fcd"), ("fyk", "fyk"), ("fyd", "fyd"), ("Ec", "Ec"), ("Es", "Es"), ("γ_c", "gamma_c"), ("γ_s", "gamma_s")]:
            tk.Label(frm, text=label).grid(row=row, column=0, sticky="w")
            ent = tk.Entry(frm, width=20)
            ent.grid(row=row, column=1, sticky="w")
            self.num_fields[key] = ent
            row += 1

        tk.Label(frm, text="Note").grid(row=row, column=0, sticky="nw")
        self.notes_text = tk.Text(frm, width=40, height=4)
        self.notes_text.grid(row=row, column=1, sticky="w")

    def _build_buttons(self) -> None:
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        tk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="right", padx=4)
        tk.Button(btn_frame, text="Salva", command=self._on_save).pack(side="right", padx=4)

    def _populate(self, material: HistoricalMaterial) -> None:
        self.name_entry.insert(0, material.name)
        self.code_entry.insert(0, material.code)
        self.source_entry.insert(0, material.source or "")
        self.type_var.set(material.type.value if hasattr(material, "type") else str(material.type))
        for k, ent in self.num_fields.items():
            val = getattr(material, k, None)
            if val is not None:
                ent.insert(0, str(val))
        if material.notes:
            self.notes_text.insert("1.0", material.notes)

    def _on_save(self) -> None:
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        source = self.source_entry.get().strip()
        try:
            mtype = HistoricalMaterialType(self.type_var.get())
        except Exception:
            mtype = HistoricalMaterialType.OTHER

        if not code:
            messagebox.showerror("Errore", "Codice obbligatorio")
            return
        # Build object
        numeric = {}
        for k, ent in self.num_fields.items():
            txt = ent.get().strip()
            numeric[k] = float(txt) if txt else None

        notes = self.notes_text.get("1.0", "end").strip()
        hist = HistoricalMaterial(
            id=code,
            name=name,
            code=code,
            source=source,
            type=mtype,
            fck=numeric.get("fck"),
            fcd=numeric.get("fcd"),
            fyk=numeric.get("fyk"),
            fyd=numeric.get("fyd"),
            Ec=numeric.get("Ec"),
            Es=numeric.get("Es"),
            gamma_c=numeric.get("gamma_c"),
            gamma_s=numeric.get("gamma_s"),
            notes=notes,
        )
        self.result = hist
        self.destroy()
