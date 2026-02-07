"""historical_material_window.py - Finestra per la gestione dei materiali storici.

Visualizza i materiali con doppia notazione (moderna e storica RD 2229/39)
e supporta il popolamento automatico dei valori in base alla fonte normativa.

AVVERTENZA: I valori calcolati automaticamente sono da considerarsi DI ESEMPIO.
Devono essere VERIFICATI da un ingegnere strutturista prima dell'uso in
calcoli reali di progettazione o verifica.
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from core_models.materials import MaterialRepository  # type: ignore[import]
from historical_materials import (
    HistoricalMaterial,
    HistoricalMaterialLibrary,
    HistoricalMaterialType,
)
from sections_app.services.notification import (
    ask_confirm,
    notify_error,
    notify_info,
    notify_warning,
)

# Import del modulo fonti normative
try:
    from material_sources import (
        MaterialSource,
        get_all_source_names,
        get_default_values_for_source,
        get_source_by_name,
        get_source_library,
    )

    SOURCES_AVAILABLE = True
except ImportError:
    SOURCES_AVAILABLE = False
    logging.warning("Modulo material_sources non disponibile. Funzionalità fonte limitata.")

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
        ("fck", "fck / σ_c,28"),  # resistenza cubica 28 gg
        ("fcd", "fcd / σ_c"),  # tensione ammissibile
        ("tau_c0", "τ_c0"),  # taglio servizio
        ("tau_c1", "τ_c1"),  # taglio max
        ("n", "n"),  # coeff. omogeneizzazione
        # Acciaio - doppia notazione
        ("fyk", "fyk / σ_sn"),  # snervamento
        ("fyd", "fyd / σ_s"),  # tensione ammissibile
        # Moduli elastici
        ("Ec", "E_c"),
        ("Es", "E_s"),
        # Coefficienti
        ("gamma_c", "γ_c"),
        ("gamma_s", "γ_s"),
        ("notes", "Note"),
    ]

    def __init__(
        self,
        master: tk.Misc,
        library: HistoricalMaterialLibrary,
        material_repository: Optional[MaterialRepository] = None,
    ) -> None:
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
            "name": 160,
            "code": 130,
            "type": 70,
            "source": 120,
            "fck": 80,
            "fcd": 70,
            "tau_c0": 50,
            "tau_c1": 50,
            "n": 40,
            "fyk": 80,
            "fyd": 70,
            "Ec": 80,
            "Es": 80,
            "gamma_c": 40,
            "gamma_s": 40,
            "notes": 200,
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

        # Pulsante gestione fonti (se disponibile il modulo)
        if SOURCES_AVAILABLE:
            tk.Button(btn_frame, text="Gestisci fonti...", command=self._on_manage_sources).pack(side="left", padx=4)

        tk.Button(btn_frame, text="Importa in archivio materiali", command=self._on_import_selected).pack(
            side="right", padx=4
        )

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
                (getattr(hist, "type", "").value if hasattr(hist, "type") else str(getattr(hist, "type", ""))),
                hist.source or "",
                # Calcestruzzo
                str(hist.fck or ""),  # fck / σ_c,28
                str(hist.fcd or ""),  # fcd / σ_c
                str(hist.tau_c0 or ""),  # τ_c0 taglio servizio
                str(hist.tau_c1 or ""),  # τ_c1 taglio max
                str(hist.n or ""),  # n coeff. omogeneizzazione
                # Acciaio
                str(hist.fyk or ""),  # fyk / σ_sn
                str(hist.fyd or ""),  # fyd / σ_s
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
            notify_warning("Modifica", "Seleziona una riga da modificare", source="historical_material_window")
            return
        code = sel[0]
        hist = self.library.find_by_code(code)
        if hist is None:
            notify_error("Errore", "Elemento non trovato", source="historical_material_window")
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
            notify_warning("Elimina", "Seleziona una riga da eliminare", source="historical_material_window")
            return

        def _on_confirm_delete(ans: bool):
            if not ans:
                return
            try:
                code = sel[0]
                mat = self.library.find_by_code(code)
                if mat:
                    # remove
                    self.library._materials = [m for m in self.library._materials if m.code != code]
                    self.library.save_to_file()
                    self._refresh_table()
            except Exception:
                logger.exception("Errore eliminazione materiale dopo conferma")

        try:
            ask_confirm(
                "Conferma",
                "Sei sicuro di voler eliminare la riga selezionata?",
                callback=_on_confirm_delete,
                source="historical_material_window",
            )
        except Exception:
            logger.exception("Errore mostrando conferma eliminazione")

    def _on_import_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            notify_warning(
                "Importa",
                "Seleziona uno o più materiali da importare",
                source="historical_material_window",
            )
            return
        if self.material_repository is None:
            notify_error("Importa", "Archivio materiali non disponibile", source="historical_material_window")
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
        notify_info("Importa", f"Importati {imported} materiali", source="historical_material_window")

    def _on_manage_sources(self) -> None:
        """Apre la finestra di gestione fonti normative."""
        if not SOURCES_AVAILABLE:
            messagebox.showerror("Errore", "Modulo material_sources non disponibile")
            return
        dlg = SourceManagerWindow(self)
        self.wait_window(dlg)


class _HistoricalEditDialog(tk.Toplevel):
    """Dialog per inserimento/modifica di un materiale storico.

    Supporta:
    - Selezione fonte normativa tramite ComboBox
    - Popolamento automatico dei valori in base alla fonte
    - Modifica manuale di tutti i parametri
    """

    def __init__(self, master: tk.Misc, title: str = "", material: Optional[HistoricalMaterial] = None) -> None:
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.grab_set()
        self.result: Optional[HistoricalMaterial] = None
        self._is_new = material is None
        self._original_material = material

        self._create_fields()
        if material:
            self._populate(material)
        self._build_buttons()

    def _create_fields(self) -> None:
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)
        self._main_frame = frm

        # Basic fields
        tk.Label(frm, text="Nome").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(frm, width=40)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="w")

        tk.Label(frm, text="Codice").grid(row=1, column=0, sticky="w")
        self.code_entry = tk.Entry(frm, width=40)
        self.code_entry.grid(row=1, column=1, columnspan=2, sticky="w")

        # =====================================================================
        # FONTE NORMATIVA - ComboBox invece di Entry
        # =====================================================================
        tk.Label(frm, text="Fonte").grid(row=2, column=0, sticky="w")

        source_frame = tk.Frame(frm)
        source_frame.grid(row=2, column=1, columnspan=2, sticky="w")

        self.source_var = tk.StringVar()
        if SOURCES_AVAILABLE:
            # ComboBox con fonti predefinite
            source_names = get_all_source_names()
            self.source_combo = ttk.Combobox(source_frame, textvariable=self.source_var, values=source_names, width=30)
            self.source_combo.pack(side="left")
            # Binding per popolamento automatico quando cambia la fonte
            self.source_combo.bind("<<ComboboxSelected>>", self._on_source_changed)

            # Pulsante per ricaricare valori dalla fonte
            self.reload_btn = tk.Button(source_frame, text="Ricarica valori", command=self._on_reload_from_source)
            self.reload_btn.pack(side="left", padx=(5, 0))
        else:
            # Fallback a Entry se il modulo fonti non è disponibile
            self.source_entry = tk.Entry(source_frame, textvariable=self.source_var, width=40)
            self.source_entry.pack(side="left")

        # Tipo materiale
        tk.Label(frm, text="Tipo").grid(row=3, column=0, sticky="w")
        self.type_var = tk.StringVar(value=HistoricalMaterialType.CONCRETE.value)
        self.type_combo = ttk.Combobox(
            frm,
            textvariable=self.type_var,
            values=[t.value for t in HistoricalMaterialType],
            state="readonly",
        )
        self.type_combo.grid(row=3, column=1, columnspan=2, sticky="w")
        # Binding per aggiornare i campi quando cambia il tipo
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_changed)

        # =====================================================================
        # CALCESTRUZZO
        # =====================================================================
        row = 4
        tk.Label(frm, text="─── CALCESTRUZZO ───", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(10, 2)
        )
        row += 1

        # Campi calcestruzzo con doppia notazione
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

        # =====================================================================
        # ACCIAIO
        # =====================================================================
        tk.Label(frm, text="─── ACCIAIO ───", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(10, 2)
        )
        row += 1

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

        # =====================================================================
        # COEFFICIENTI
        # =====================================================================
        tk.Label(frm, text="─── COEFFICIENTI ───", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(10, 2)
        )
        row += 1

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

        # =====================================================================
        # NOTE
        # =====================================================================
        tk.Label(frm, text="Note").grid(row=row, column=0, sticky="nw", pady=(10, 0))
        self.notes_text = tk.Text(frm, width=50, height=4)
        self.notes_text.grid(row=row, column=1, columnspan=2, sticky="w", pady=(10, 0))

    def _build_buttons(self) -> None:
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        tk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="right", padx=4)
        tk.Button(btn_frame, text="Salva", command=self._on_save).pack(side="right", padx=4)

    def _populate(self, material: HistoricalMaterial) -> None:
        """Popola i campi con i valori del materiale esistente."""
        self.name_entry.insert(0, material.name)
        self.code_entry.insert(0, material.code)
        self.source_var.set(material.source or "")
        self.type_var.set(material.type.value if hasattr(material, "type") else str(material.type))

        # Popola tutti i campi numerici
        for k, ent in self.num_fields.items():
            val = getattr(material, k, None)
            if val is not None:
                ent.insert(0, str(val))

        if material.notes:
            self.notes_text.insert("1.0", material.notes)

    def _on_source_changed(self, event=None) -> None:
        """Chiamato quando l'utente seleziona una fonte dalla ComboBox.

        Per materiali nuovi, popola automaticamente i valori.
        Per materiali esistenti, chiede conferma prima di sovrascrivere.
        """
        if not SOURCES_AVAILABLE:
            return

        source_name = self.source_var.get()
        if not source_name:
            return

        # Solo per materiali nuovi, popola automaticamente
        if self._is_new:
            self._apply_source_values(source_name, ask_confirm=False)
        # Per materiali esistenti, non sovrascrivere automaticamente
        # L'utente può usare il pulsante "Ricarica valori"

    def _on_type_changed(self, event=None) -> None:
        """Chiamato quando l'utente cambia il tipo di materiale."""
        # Potrebbe essere utile per futuri miglioramenti
        pass

    def _on_reload_from_source(self) -> None:
        """Ricarica i valori calcolati dalla fonte normativa selezionata.

        Chiede conferma prima di sovrascrivere i valori esistenti.
        """
        if not SOURCES_AVAILABLE:
            messagebox.showerror("Errore", "Modulo material_sources non disponibile")
            return

        source_name = self.source_var.get()
        if not source_name:
            messagebox.showwarning("Ricarica", "Seleziona prima una fonte normativa")
            return

        if not messagebox.askyesno(
            "Conferma ricarica",
            f"Vuoi sovrascrivere i valori calcolabili con quelli predefiniti "
            f"della fonte '{source_name}'?\n\n"
            "I campi di input (fck, fyk) NON verranno modificati.\n"
            "I campi calcolati (fcd, τ, n, E, γ) verranno aggiornati.",
        ):
            return

        self._apply_source_values(source_name, ask_confirm=False)

    def _apply_source_values(self, source_name: str, ask_confirm: bool = True) -> None:
        """Applica i valori predefiniti della fonte ai campi calcolabili.

        AVVERTENZA: I valori calcolati sono da considerarsi DI ESEMPIO.
        Devono essere verificati prima dell'uso in progettazione reale.

        Args:
            source_name: Nome della fonte normativa
            ask_confirm: Se True, chiede conferma prima di sovrascrivere

        """
        if not SOURCES_AVAILABLE:
            return

        source = get_source_by_name(source_name)
        if source is None:
            logger.warning("Fonte '%s' non trovata", source_name)
            return

        # Determina tipo materiale
        material_type = self.type_var.get()

        # Raccogli parametri di input
        base_params = {}

        # Per calcestruzzo: fck (o sigma_c28)
        fck_val = self.num_fields.get("fck")
        if fck_val:
            txt = fck_val.get().strip().replace(",", ".")
            if txt:
                try:
                    base_params["fck"] = float(txt)
                except ValueError:
                    pass

        # Per acciaio: fyk (o sigma_sn)
        fyk_val = self.num_fields.get("fyk")
        if fyk_val:
            txt = fyk_val.get().strip().replace(",", ".")
            if txt:
                try:
                    base_params["fyk"] = float(txt)
                except ValueError:
                    pass

        # Calcola valori predefiniti
        defaults = get_default_values_for_source(source.id, material_type, base_params)

        # Applica i valori calcolati ai campi (senza sovrascrivere gli input)
        fields_to_update = {
            "fcd": defaults.get("fcd"),
            "tau_c0": defaults.get("tau_c0"),
            "tau_c1": defaults.get("tau_c1"),
            "n": defaults.get("n"),
            "Ec": defaults.get("Ec"),
            "fyd": defaults.get("fyd"),
            "Es": defaults.get("Es"),
            "gamma_c": defaults.get("gamma_c"),
            "gamma_s": defaults.get("gamma_s"),
        }

        for key, value in fields_to_update.items():
            if value is not None and key in self.num_fields:
                ent = self.num_fields[key]
                ent.delete(0, tk.END)
                ent.insert(0, str(value))

        # Aggiungi note di calcolo
        calc_notes = defaults.get("calculation_notes", "")
        if calc_notes:
            current_notes = self.notes_text.get("1.0", tk.END).strip()
            if current_notes:
                # Aggiungi in coda se ci sono già note
                if "AVVERTENZA" not in current_notes:
                    self.notes_text.insert(tk.END, f"\n\n{calc_notes}")
            else:
                self.notes_text.insert("1.0", calc_notes)

        logger.info("Applicati valori da fonte '%s' per materiale tipo '%s'", source_name, material_type)

    def _on_save(self) -> None:
        """Salva il materiale."""
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        source = self.source_var.get().strip()

        try:
            mtype = HistoricalMaterialType(self.type_var.get())
        except Exception:
            mtype = HistoricalMaterialType.OTHER

        if not code:
            messagebox.showerror("Errore", "Codice obbligatorio")
            return

        # Parse numeric fields
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
            fck=numeric.get("fck"),
            fcd=numeric.get("fcd"),
            tau_c0=numeric.get("tau_c0"),
            tau_c1=numeric.get("tau_c1"),
            n=numeric.get("n"),
            Ec=numeric.get("Ec"),
            # Acciaio
            fyk=numeric.get("fyk"),
            fyd=numeric.get("fyd"),
            Es=numeric.get("Es"),
            # Coefficienti
            gamma_c=numeric.get("gamma_c"),
            gamma_s=numeric.get("gamma_s"),
            notes=notes,
        )
        self.result = hist
        self.destroy()


# =============================================================================
# FINESTRA GESTIONE FONTI NORMATIVE
# =============================================================================


class SourceManagerWindow(tk.Toplevel):
    """Finestra per gestire l'elenco delle fonti normative.

    Permette di:
    - Visualizzare le fonti esistenti
    - Aggiungere nuove fonti personalizzate
    - Modificare fonti esistenti (nome, descrizione)
    - Eliminare fonti non predefinite
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Gestione Fonti Normative")
        self.geometry("700x450")
        self.transient(master)

        if not SOURCES_AVAILABLE:
            tk.Label(self, text="Modulo material_sources non disponibile").pack(pady=20)
            return

        self.source_lib = get_source_library()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        # Lista fonti
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        columns = ("id", "name", "year", "method", "historical", "user_defined")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nome")
        self.tree.heading("year", text="Anno")
        self.tree.heading("method", text="Metodo")
        self.tree.heading("historical", text="Storica")
        self.tree.heading("user_defined", text="Utente")

        self.tree.column("id", width=80)
        self.tree.column("name", width=200)
        self.tree.column("year", width=60)
        self.tree.column("method", width=80)
        self.tree.column("historical", width=60)
        self.tree.column("user_defined", width=60)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Descrizione fonte selezionata
        desc_frame = tk.LabelFrame(self, text="Descrizione")
        desc_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.desc_label = tk.Label(desc_frame, text="", wraplength=650, justify="left", anchor="w")
        self.desc_label.pack(fill="x", padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Pulsanti
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))

        tk.Button(btn_frame, text="Aggiungi fonte", command=self._on_add).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Modifica", command=self._on_edit).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Elimina", command=self._on_delete).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Chiudi", command=self.destroy).pack(side="right", padx=4)

        # Avviso
        warning_label = tk.Label(
            self,
            text="NOTA: Le fonti predefinite non possono essere eliminate. "
            "È possibile aggiungere fonti personalizzate.",
            fg="gray",
            font=("TkDefaultFont", 8),
        )
        warning_label.pack(pady=(0, 5))

    def _refresh_list(self) -> None:
        """Aggiorna la lista delle fonti."""
        self.tree.delete(*self.tree.get_children())
        for src in self.source_lib.get_all():
            values = (
                src.id,
                src.name,
                src.year or "",
                src.calculation_method.value,
                "Sì" if src.is_historical else "No",
                "Sì" if src.is_user_defined else "No",
            )
            self.tree.insert("", "end", iid=src.id, values=values)

    def _on_select(self, event=None) -> None:
        """Mostra la descrizione della fonte selezionata."""
        sel = self.tree.selection()
        if not sel:
            self.desc_label.config(text="")
            return
        src = self.source_lib.get_by_id(sel[0])
        if src:
            desc = f"{src.description}\n\nRiferimento: {src.reference}"
            if src.notes:
                desc += f"\n\nNote: {src.notes}"
            self.desc_label.config(text=desc)

    def _on_add(self) -> None:
        """Aggiunge una nuova fonte personalizzata."""
        dlg = _SourceEditDialog(self, title="Aggiungi fonte normativa")
        self.wait_window(dlg)
        if dlg.result:
            dlg.result.is_user_defined = True
            self.source_lib.add(dlg.result)
            self._refresh_list()

    def _on_edit(self) -> None:
        """Modifica la fonte selezionata."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Modifica", "Seleziona una fonte da modificare")
            return
        src = self.source_lib.get_by_id(sel[0])
        if src is None:
            return
        dlg = _SourceEditDialog(self, title="Modifica fonte normativa", source=src)
        self.wait_window(dlg)
        if dlg.result:
            self.source_lib.add(dlg.result)
            self._refresh_list()

    def _on_delete(self) -> None:
        """Elimina la fonte selezionata (solo se definita dall'utente)."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Elimina", "Seleziona una fonte da eliminare")
            return
        src = self.source_lib.get_by_id(sel[0])
        if src is None:
            return
        if not src.is_user_defined:
            messagebox.showwarning("Elimina", f"La fonte '{src.name}' è predefinita e non può essere eliminata.")
            return
        if not messagebox.askyesno("Conferma", f"Eliminare la fonte '{src.name}'?"):
            return
        self.source_lib.delete(src.id)
        self._refresh_list()


class _SourceEditDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare una fonte normativa."""

    def __init__(self, master: tk.Misc, title: str = "", source: Optional[MaterialSource] = None) -> None:
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.grab_set()
        self.result: Optional[MaterialSource] = None
        self._original = source

        self._create_fields()
        if source:
            self._populate(source)
        self._build_buttons()

    def _create_fields(self) -> None:
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        row = 0

        tk.Label(frm, text="ID (codice univoco)").grid(row=row, column=0, sticky="w")
        self.id_entry = tk.Entry(frm, width=30)
        self.id_entry.grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(frm, text="Nome").grid(row=row, column=0, sticky="w")
        self.name_entry = tk.Entry(frm, width=40)
        self.name_entry.grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(frm, text="Anno").grid(row=row, column=0, sticky="w")
        self.year_entry = tk.Entry(frm, width=10)
        self.year_entry.grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(frm, text="Metodo di calcolo").grid(row=row, column=0, sticky="w")
        from material_sources import CalculationMethod

        self.method_var = tk.StringVar(value=CalculationMethod.TENSIONI_AMMISSIBILI.value)
        self.method_combo = ttk.Combobox(
            frm,
            textvariable=self.method_var,
            values=[m.value for m in CalculationMethod],
            state="readonly",
            width=20,
        )
        self.method_combo.grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(frm, text="Riferimento normativo").grid(row=row, column=0, sticky="w")
        self.reference_entry = tk.Entry(frm, width=50)
        self.reference_entry.grid(row=row, column=1, sticky="w")
        row += 1

        self.historical_var = tk.BooleanVar()
        tk.Checkbutton(frm, text="Norma storica (non più in vigore)", variable=self.historical_var).grid(
            row=row, column=1, sticky="w"
        )
        row += 1

        tk.Label(frm, text="Descrizione").grid(row=row, column=0, sticky="nw")
        self.desc_text = tk.Text(frm, width=50, height=3)
        self.desc_text.grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(frm, text="Note").grid(row=row, column=0, sticky="nw")
        self.notes_text = tk.Text(frm, width=50, height=2)
        self.notes_text.grid(row=row, column=1, sticky="w")

    def _build_buttons(self) -> None:
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="right", padx=4)
        tk.Button(btn_frame, text="Salva", command=self._on_save).pack(side="right", padx=4)

    def _populate(self, source: MaterialSource) -> None:
        self.id_entry.insert(0, source.id)
        self.name_entry.insert(0, source.name)
        if source.year:
            self.year_entry.insert(0, str(source.year))
        self.method_var.set(source.calculation_method.value)
        self.reference_entry.insert(0, source.reference or "")
        self.historical_var.set(source.is_historical)
        if source.description:
            self.desc_text.insert("1.0", source.description)
        if source.notes:
            self.notes_text.insert("1.0", source.notes)

        # Disabilita ID se in modifica
        if self._original:
            self.id_entry.config(state="disabled")

    def _on_save(self) -> None:
        from material_sources import CalculationMethod, MaterialSource

        source_id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()

        if not source_id or not name:
            messagebox.showerror("Errore", "ID e Nome sono obbligatori")
            return

        year_txt = self.year_entry.get().strip()
        year = int(year_txt) if year_txt.isdigit() else None

        try:
            method = CalculationMethod(self.method_var.get())
        except ValueError:
            method = CalculationMethod.TENSIONI_AMMISSIBILI

        self.result = MaterialSource(
            id=source_id,
            name=name,
            description=self.desc_text.get("1.0", "end").strip(),
            year=year,
            calculation_method=method,
            is_historical=self.historical_var.get(),
            is_user_defined=True if self._original is None else self._original.is_user_defined,
            reference=self.reference_entry.get().strip(),
            notes=self.notes_text.get("1.0", "end").strip(),
        )
        self.destroy()
