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
    """Window to manage HistoricalMaterialLibrary and import into MaterialRepository.

    Visualizza i materiali con doppia notazione:
    - Moderna (fck, fcd, fyk, fyd)
    - Storica RD 2229/39 (σ_c,28, σ_c, σ_sn, σ_s)
    """

    # Colonne con doppia notazione (moderna / storica RD 2229/39)
    COLUMNS = [
        ("name", "Nome"),
        ("code", "Codice"),
        ("type", "Tipo"),
        ("source", "Fonte"),
        # Calcestruzzo - doppia notazione
        ("fck", "fck / σ_c,28"),       # resistenza cubica 28 gg
        ("fcd", "fcd / σ_c"),          # tensione ammissibile
        ("tau_c0", "τ_c0"),            # taglio servizio
        ("tau_c1", "τ_c1"),            # taglio max
        ("n", "n"),                     # coeff. omogeneizzazione
        # Acciaio - doppia notazione
        ("fyk", "fyk / σ_sn"),         # snervamento
        ("fyd", "fyd / σ_s"),          # tensione ammissibile
        # Moduli elastici
        ("Ec", "E_c"),
        ("Es", "E_s"),
        # Coefficienti
        ("gamma_c", "γ_c"),
        ("gamma_s", "γ_s"),
        ("notes", "Note"),
    ]

    def __init__(self, master: tk.Misc, library: HistoricalMaterialLibrary, material_repository: Optional[MaterialRepository] = None) -> None:
        super().__init__(master)
        self.title("Archivio Materiali Storici - RD 2229/39")
        self.geometry("1200x520")
        self.library = library
        self.material_repository = material_repository

        self._build_ui()
        self._load_library()

    def _build_ui(self) -> None:
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Treeview con larghezze colonne ottimizzate
        cols = [c[0] for c in self.COLUMNS]
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)

        # Larghezze personalizzate per colonna
        col_widths = {
            "name": 160, "code": 130, "type": 70, "source": 120,
            "fck": 80, "fcd": 70, "tau_c0": 50, "tau_c1": 50, "n": 40,
            "fyk": 80, "fyd": 70, "Ec": 80, "Es": 80,
            "gamma_c": 40, "gamma_s": 40, "notes": 200
        }
        for key, label in self.COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=col_widths.get(key, 80), anchor="center")
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
                # Calcestruzzo
                str(hist.fck or ""),      # fck / σ_c,28
                str(hist.fcd or ""),      # fcd / σ_c
                str(hist.tau_c0 or ""),   # τ_c0 taglio servizio
                str(hist.tau_c1 or ""),   # τ_c1 taglio max
                str(hist.n or ""),        # n coeff. omogeneizzazione
                # Acciaio
                str(hist.fyk or ""),      # fyk / σ_sn
                str(hist.fyd or ""),      # fyd / σ_s
                # Moduli elastici
                str(hist.Ec or ""),
                str(hist.Es or ""),
                # Coefficienti
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
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="w")

        tk.Label(frm, text="Codice").grid(row=1, column=0, sticky="w")
        self.code_entry = tk.Entry(frm, width=40)
        self.code_entry.grid(row=1, column=1, columnspan=2, sticky="w")

        tk.Label(frm, text="Fonte").grid(row=2, column=0, sticky="w")
        self.source_entry = tk.Entry(frm, width=40)
        self.source_entry.grid(row=2, column=1, columnspan=2, sticky="w")

        tk.Label(frm, text="Tipo").grid(row=3, column=0, sticky="w")
        self.type_var = tk.StringVar(value=HistoricalMaterialType.CONCRETE.value)
        self.type_combo = ttk.Combobox(frm, textvariable=self.type_var, values=[t.value for t in HistoricalMaterialType], state="readonly")
        self.type_combo.grid(row=3, column=1, columnspan=2, sticky="w")

        # Separatore - Calcestruzzo
        row = 4
        tk.Label(frm, text="─── CALCESTRUZZO ───", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10, 2))
        row += 1

        # Campi calcestruzzo con doppia notazione
        # Formato: (label_moderna, label_storica, key, tooltip)
        concrete_fields = [
            ("fck", "σ_c,28", "fck", "Resistenza cubica 28 gg [kg/cm²]"),
            ("fcd", "σ_c", "fcd", "Tensione ammissibile [kg/cm²]"),
            ("τ_c0", "τ servizio", "tau_c0", "Taglio di servizio [kg/cm²]"),
            ("τ_c1", "τ max", "tau_c1", "Taglio massimo [kg/cm²]"),
            ("n", "Es/Ec", "n", "Coefficiente di omogeneizzazione"),
            ("E_c", "", "Ec", "Modulo elastico cls [kg/cm²]"),
        ]

        self.num_fields = {}
        for label_mod, label_hist, key, tooltip in concrete_fields:
            full_label = f"{label_mod}" if not label_hist else f"{label_mod} / {label_hist}"
            tk.Label(frm, text=full_label).grid(row=row, column=0, sticky="w")
            ent = tk.Entry(frm, width=15)
            ent.grid(row=row, column=1, sticky="w")
            tk.Label(frm, text=tooltip, fg="gray").grid(row=row, column=2, sticky="w", padx=(5, 0))
            self.num_fields[key] = ent
            row += 1

        # Separatore - Acciaio
        tk.Label(frm, text="─── ACCIAIO ───", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10, 2))
        row += 1

        # Campi acciaio con doppia notazione
        steel_fields = [
            ("fyk", "σ_sn", "fyk", "Tensione di snervamento [kg/cm²]"),
            ("fyd", "σ_s", "fyd", "Tensione ammissibile [kg/cm²]"),
            ("E_s", "", "Es", "Modulo elastico acciaio [kg/cm²]"),
        ]

        for label_mod, label_hist, key, tooltip in steel_fields:
            full_label = f"{label_mod}" if not label_hist else f"{label_mod} / {label_hist}"
            tk.Label(frm, text=full_label).grid(row=row, column=0, sticky="w")
            ent = tk.Entry(frm, width=15)
            ent.grid(row=row, column=1, sticky="w")
            tk.Label(frm, text=tooltip, fg="gray").grid(row=row, column=2, sticky="w", padx=(5, 0))
            self.num_fields[key] = ent
            row += 1

        # Separatore - Coefficienti
        tk.Label(frm, text="─── COEFFICIENTI ───", font=("TkDefaultFont", 9, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10, 2))
        row += 1

        # Coefficienti di sicurezza
        coeff_fields = [
            ("γ_c", "gamma_c", "Rapporto fck/fcd (≈3 per cls)"),
            ("γ_s", "gamma_s", "Rapporto fyk/fyd (=2 per acciaio)"),
        ]

        for label, key, tooltip in coeff_fields:
            tk.Label(frm, text=label).grid(row=row, column=0, sticky="w")
            ent = tk.Entry(frm, width=15)
            ent.grid(row=row, column=1, sticky="w")
            tk.Label(frm, text=tooltip, fg="gray").grid(row=row, column=2, sticky="w", padx=(5, 0))
            self.num_fields[key] = ent
            row += 1

        # Note
        tk.Label(frm, text="Note").grid(row=row, column=0, sticky="nw", pady=(10, 0))
        self.notes_text = tk.Text(frm, width=50, height=4)
        self.notes_text.grid(row=row, column=1, columnspan=2, sticky="w", pady=(10, 0))

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
        # Popola tutti i campi numerici (inclusi nuovi: tau_c0, tau_c1, n)
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
        # Build object - parse numeric fields
        numeric = {}
        for k, ent in self.num_fields.items():
            txt = ent.get().strip().replace(",", ".")  # supporta virgola decimale
            try:
                numeric[k] = float(txt) if txt else None
            except ValueError:
                messagebox.showerror("Errore", f"Valore non valido per {k}: {txt}")
                return

        notes = self.notes_text.get("1.0", "end").strip()
        hist = HistoricalMaterial(
            id=code,
            name=name,
            code=code,
            source=source,
            type=mtype,
            # Calcestruzzo
            fck=numeric.get("fck"),       # σ_c,28
            fcd=numeric.get("fcd"),       # σ_c
            tau_c0=numeric.get("tau_c0"), # τ servizio
            tau_c1=numeric.get("tau_c1"), # τ max
            n=numeric.get("n"),           # coeff. omogeneizzazione
            Ec=numeric.get("Ec"),
            # Acciaio
            fyk=numeric.get("fyk"),       # σ_sn
            fyd=numeric.get("fyd"),       # σ_s
            Es=numeric.get("Es"),
            # Coefficienti
            gamma_c=numeric.get("gamma_c"),
            gamma_s=numeric.get("gamma_s"),
            notes=notes,
        )
        self.result = hist
        self.destroy()
