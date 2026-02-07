from __future__ import annotations

import logging
import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Dict, Optional, Tuple

from sections_app.ui.historical_material_window import HistoricalMaterialWindow
from sections_app.ui.section_manager import SectionManager

from core_models.materials import MaterialRepository
from sections_app.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    Section,
    TSection,
    VSection,
)
from sections_app.services.calculations import compute_transform
from sections_app.services.notification import (
    notify_error,
    notify_info,
)
from sections_app.services.repository import CsvSectionSerializer, SectionRepository

logger = logging.getLogger(__name__)

# ========================================================================
# CONFIGURAZIONE TIPOLOGIE DI SEZIONE
# ========================================================================
# Per aggiungere una nuova tipologia di sezione:
# 1. Creare la classe corrispondente in sections.py (es. ISectionm LSection)
# 2. Aggiungere una voce in questo dizionario con:
#    - chiave: nome visualizzato nella combobox
#    - "class": la classe del modello
#    - "fields": lista di tuple (nome_campo, label_con_unità)
#    - "tooltip": descrizione opzionale per l'utente
#    - "field_tooltips": dizionario opzionale con tooltip per ogni campo
# 3. Implementare il disegno grafico in _draw_section se necessario
# 4. Tutte le unità sono in cm, valori con 1 cifra decimale
# ========================================================================

SECTION_DEFINITIONS = {
    "Rettangolare": {
        "class": RectangularSection,
        "fields": [
            ("width", "Larghezza b (cm)"),
            ("height", "Altezza h (cm)"),
        ],
        "tooltip": "Sezione rettangolare piena con base b e altezza h",
        "field_tooltips": {
            "width": "Larghezza della base della sezione (cm, 1 decimale)",
            "height": "Altezza totale della sezione (cm, 1 decimale)",
        },
    },
    "Circolare": {
        "class": CircularSection,
        "fields": [("diameter", "Diametro D (cm)")],
        "tooltip": "Sezione circolare piena con diametro D",
        "field_tooltips": {
            "diameter": "Diametro del cerchio (cm, 1 decimale)",
        },
    },
    "A T": {
        "class": TSection,
        "fields": [
            ("flange_width", "Larghezza ala bf (cm)"),
            ("flange_thickness", "Spessore ala hf (cm)"),
            ("web_thickness", "Spessore anima bw (cm)"),
            ("web_height", "Altezza anima hw (cm)"),
        ],
        "tooltip": "Sezione a T con ala superiore e anima verticale",
        "field_tooltips": {
            "flange_width": "Larghezza dell'ala superiore (cm, 1 decimale)",
            "flange_thickness": "Spessore dell'ala superiore (cm, 1 decimale)",
            "web_thickness": "Spessore dell'anima verticale (cm, 1 decimale)",
            "web_height": "Altezza dell'anima verticale (cm, 1 decimale)",
        },
    },
    "Ad L": {
        "class": LSection,
        "fields": [
            ("width", "Larghezza ala orizzontale (cm)"),
            ("height", "Altezza ala verticale (cm)"),
            ("t_horizontal", "Spessore ala orizzontale (cm)"),
            ("t_vertical", "Spessore ala verticale (cm)"),
        ],
        "tooltip": "Sezione ad L (angolare) con due ali perpendicolari",
        "field_tooltips": {
            "width": "Larghezza dell'ala orizzontale (cm, 1 decimale)",
            "height": "Altezza dell'ala verticale (cm, 1 decimale)",
            "t_horizontal": "Spessore dell'ala orizzontale (cm, 1 decimale)",
            "t_vertical": "Spessore dell'ala verticale (cm, 1 decimale)",
        },
    },
    "Ad I (doppio T)": {
        "class": ISection,
        "fields": [
            ("flange_width", "Larghezza ali bf (cm)"),
            ("flange_thickness", "Spessore ali hf (cm)"),
            ("web_height", "Altezza anima hw (cm)"),
            ("web_thickness", "Spessore anima bw (cm)"),
        ],
        "tooltip": "Sezione ad I (doppio T simmetrico)",
        "field_tooltips": {
            "flange_width": "Larghezza delle ali superiore e inferiore (cm, 1 decimale)",
            "flange_thickness": "Spessore delle ali (cm, 1 decimale)",
            "web_height": "Altezza dell'anima verticale (cm, 1 decimale)",
            "web_thickness": "Spessore dell'anima verticale (cm, 1 decimale)",
        },
    },
    "A Π (pi greco)": {
        "class": PiSection,
        "fields": [
            ("flange_width", "Larghezza ala superiore (cm)"),
            ("flange_thickness", "Spessore ala superiore (cm)"),
            ("web_height", "Altezza anime (cm)"),
            ("web_thickness", "Spessore anime laterali (cm)"),
        ],
        "tooltip": "Sezione a Π con ala superiore e due anime laterali",
        "field_tooltips": {
            "flange_width": "Larghezza dell'ala superiore orizzontale (cm, 1 decimale)",
            "flange_thickness": "Spessore dell'ala superiore (cm, 1 decimale)",
            "web_height": "Altezza delle anime laterali verticali (cm, 1 decimale)",
            "web_thickness": "Spessore delle anime laterali (cm, 1 decimale)",
        },
    },
    "A T rovescia": {
        "class": InvertedTSection,
        "fields": [
            ("flange_width", "Larghezza ala inferiore (cm)"),
            ("flange_thickness", "Spessore ala inferiore (cm)"),
            ("web_thickness", "Spessore anima (cm)"),
            ("web_height", "Altezza anima (cm)"),
        ],
        "tooltip": "Sezione a T rovescia con ala inferiore",
        "field_tooltips": {
            "flange_width": "Larghezza dell'ala inferiore (cm, 1 decimale)",
            "flange_thickness": "Spessore dell'ala inferiore (cm, 1 decimale)",
            "web_thickness": "Spessore dell'anima verticale (cm, 1 decimale)",
            "web_height": "Altezza dell'anima verticale (cm, 1 decimale)",
        },
    },
    "A C (canale)": {
        "class": CSection,
        "fields": [
            ("width", "Larghezza totale (cm)"),
            ("height", "Altezza totale (cm)"),
            ("flange_thickness", "Spessore ali orizzontali (cm)"),
            ("web_thickness", "Spessore anima verticale (cm)"),
        ],
        "tooltip": "Sezione a C (canale) con ali orizzontali e anima verticale",
        "field_tooltips": {
            "width": "Larghezza totale della sezione (cm, 1 decimale)",
            "height": "Altezza totale della sezione (cm, 1 decimale)",
            "flange_thickness": "Spessore delle ali orizzontali (cm, 1 decimale)",
            "web_thickness": "Spessore dell'anima verticale (cm, 1 decimale)",
        },
    },
    "Circolare cava": {
        "class": CircularHollowSection,
        "fields": [
            ("outer_diameter", "Diametro esterno De (cm)"),
            ("thickness", "Spessore parete s (cm)"),
        ],
        "tooltip": "Sezione circolare cava (tubo)",
        "field_tooltips": {
            "outer_diameter": "Diametro esterno del tubo (cm, 1 decimale)",
            "thickness": "Spessore della parete (cm, 1 decimale)",
        },
    },
    "Rettangolare cava": {
        "class": RectangularHollowSection,
        "fields": [
            ("width", "Larghezza esterna (cm)"),
            ("height", "Altezza esterna (cm)"),
            ("thickness", "Spessore parete (cm)"),
        ],
        "tooltip": "Sezione rettangolare cava (tubo rettangolare)",
        "field_tooltips": {
            "width": "Larghezza esterna della sezione (cm, 1 decimale)",
            "height": "Altezza esterna della sezione (cm, 1 decimale)",
            "thickness": "Spessore delle pareti (cm, 1 decimale)",
        },
    },
    "A V": {
        "class": VSection,
        "fields": [
            ("width", "Larghezza alla base (cm)"),
            ("height", "Altezza (cm)"),
            ("thickness", "Spessore pareti (cm)"),
        ],
        "tooltip": "Sezione a V con apertura verso l'alto",
        "field_tooltips": {
            "width": "Larghezza alla base della V (cm, 1 decimale)",
            "height": "Altezza della sezione (cm, 1 decimale)",
            "thickness": "Spessore delle pareti inclinate (cm, 1 decimale)",
        },
    },
    "A V rovescia": {
        "class": InvertedVSection,
        "fields": [
            ("width", "Larghezza alla base superiore (cm)"),
            ("height", "Altezza (cm)"),
            ("thickness", "Spessore pareti (cm)"),
        ],
        "tooltip": "Sezione a V rovescia con apertura verso il basso",
        "field_tooltips": {
            "width": "Larghezza alla base superiore (cm, 1 decimale)",
            "height": "Altezza della sezione (cm, 1 decimale)",
            "thickness": "Spessore delle pareti inclinate (cm, 1 decimale)",
        },
    },
}


class MainWindow(tk.Toplevel):
    """Finestra del modulo Geometry - aperta come Toplevel dalla finestra principale ModuleSelector.

    ✅ Estende tk.Toplevel (non tk.Tk) - rimane una finestra figlia della root principale.
    ✅ Accetta la finestra parent nel costruttore.
    ✅ Un solo mainloop() nell'applicazione (nel ModuleSelector).
    """

    def __init__(
        self,
        master: tk.Tk,  # ✅ NUOVO: richiede il parent (ModuleSelector)
        repository: SectionRepository,
        serializer: CsvSectionSerializer,
        material_repository: Optional[MaterialRepository] = None,
    ):
        super().__init__(master=master)  # ✅ Passa master a Toplevel
        self.title("Gestione Proprietà Sezioni")
        self.geometry("980x620")
        self.repository = repository
        self.section_repository: SectionRepository = repository
        self.serializer = serializer
        self.material_repository: Optional[MaterialRepository] = material_repository
        self.current_section: Optional[Section] = None
        # Quando si modifica una sezione dal Section Manager, qui viene salvato l'id
        self.editing_section_id: Optional[str] = None
        # Riferimento opzionale al manager per aggiornamenti UI
        self.section_manager: Optional[SectionManager] = None
        # Riferimento opzionale alla finestra di gestione materiali storici
        self._material_manager_window: Optional[HistoricalMaterialWindow] = None

        self._create_menu()
        self._build_layout()
        # Memorizza l'ultima tipologia selezionata per evitare rielaborazioni ridondanti
        self._last_selected_type: Optional[str] = self.section_var.get()
        # Avvia un polling leggero per intercettare cambi di selezione che a volte
        # vengono mostrati nella combo senza emettere l'evento (fallback UX)
        self._polling_id = self.after(300, self._poll_section_selection)
        # Assicura di fermare il polling quando la finestra viene distrutta
        self.bind("<Destroy>", lambda e: self._cancel_polling())

        # ✅ Gestisci la chiusura della finestra in modo indipendente
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(main_frame)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._build_left_panel()
        self._build_right_panel()

    def _create_menu(self) -> None:
        """Crea il menu della finestra principale."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Importa CSV...", command=self.import_csv)
        file_menu.add_command(label="Esporta CSV...", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Esporta backup completo...", command=self.export_full_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)

        # Menu Gestione: strumenti aggiuntivi (es. gestione materiali)
        gestione_menu = tk.Menu(menubar, tearoff=0)
        gestione_menu.add_command(label="Materiali…", command=self.open_material_manager)
        menubar.add_cascade(label="Gestione", menu=gestione_menu)

    def open_material_manager(self) -> None:
        """Apre (o porta in primo piano) la finestra di gestione materiali storici.

        La finestra riceve l'istanza di `HistoricalMaterialLibrary` e il
        `MaterialRepository` attualmente in uso dall'applicazione.
        """
        # Se la finestra è già aperta, portala in primo piano
        if hasattr(self, "_material_manager_window") and self._material_manager_window is not None:
            try:
                if self._material_manager_window.winfo_exists():
                    self._material_manager_window.lift()
                    self._material_manager_window.focus_force()
                    logger.debug("Material Manager già aperto, portato in primo piano")
                    return
            except Exception:
                pass

        # Crea libreria storica e apri finestra
        try:
            from historical_materials import HistoricalMaterialLibrary

            library = HistoricalMaterialLibrary()
        except Exception:
            logger.exception("Impossibile inizializzare HistoricalMaterialLibrary")
            library = None

        self._material_manager_window = HistoricalMaterialWindow(
            master=self, library=library, material_repository=self.material_repository
        )
        # Pulizia del riferimento quando la finestra viene chiusa
        try:
            self._material_manager_window.protocol(
                "WM_DELETE_WINDOW",
                lambda w=self._material_manager_window: (
                    setattr(self, "_material_manager_window", None),
                    w.destroy(),
                ),
            )
            self._material_manager_window.bind(
                "<Destroy>",
                lambda e, w=self._material_manager_window: setattr(
                    self, "_material_manager_window", None
                ),
            )
        except Exception:
            pass
        logger.debug("Material Manager aperto")

    def _build_left_panel(self) -> None:
        # Tipologia sezione con tooltip
        tipo_label = tk.Label(self.left_frame, text="Tipologia sezione")
        tipo_label.pack(anchor="w")

        self.section_var = tk.StringVar(value=list(SECTION_DEFINITIONS.keys())[0])
        self.section_combo = ttk.Combobox(
            self.left_frame,
            textvariable=self.section_var,
            values=list(SECTION_DEFINITIONS.keys()),
            state="readonly",
            width=28,
        )
        self.section_combo.pack(anchor="w", pady=(0, 8))

        # Evento per cambio tipologia - aggiorna campi dinamicamente
        self.section_combo.bind("<<ComboboxSelected>>", self._on_section_change)
        # Binding addizionali per coprire casi in cui l'evento non venga emesso
        self.section_combo.bind("<FocusOut>", self._on_section_change)
        self.section_combo.bind("<KeyRelease-Return>", self._on_section_change)
        self.section_combo.bind("<KeyRelease-Up>", self._on_section_change)
        self.section_combo.bind("<KeyRelease-Down>", self._on_section_change)
        # Inoltre, tracciamo ogni cambiamento della variabile per essere sicuri di intercettare
        # tutte le modalità di modifica (mouse, tastiera, programmatico)
        try:
            self.section_var.trace_add("write", lambda *a: self._on_section_change())
        except Exception:
            # Fallback per versioni più vecchie di tkinter che usano trace_var
            self.section_var.trace("w", lambda *a: self._on_section_change())

        # Pulsante per applicare esplicitamente la tipologia (fallback UX)
        self.apply_type_btn = tk.Button(
            self.left_frame, text="Applica tipo", command=self._on_section_change, width=12
        )
        self.apply_type_btn.pack(anchor="w", pady=(0, 4))

        # Tooltip sulla combobox
        self._create_tooltip(self.section_combo, "Seleziona il tipo di sezione da analizzare")

        # Label indicatore stato editing
        self.editing_mode_label = tk.Label(
            self.left_frame,
            text="Modalità: Nuova sezione",
            font=("Arial", 9, "italic"),
            fg="#0066cc",
        )
        self.editing_mode_label.pack(anchor="w", pady=(0, 8))

        tk.Label(self.left_frame, text="Nome sezione").pack(anchor="w")
        self.name_entry = tk.Entry(self.left_frame, width=30)
        self.name_entry.pack(anchor="w", pady=(0, 8))

        self.inputs_frame = tk.LabelFrame(self.left_frame, text="Dati geometrici")
        self.inputs_frame.pack(fill="x", pady=(0, 8))
        self.inputs: Dict[str, tk.Entry] = {}
        self._create_inputs()

        # Campo per angolo di rotazione (comune a tutte le sezioni)
        rotation_frame = tk.Frame(self.left_frame)
        rotation_frame.pack(fill="x", pady=(0, 8))
        tk.Label(rotation_frame, text="Angolo di rotazione θ (gradi):").pack(
            side="left", padx=(0, 4)
        )
        self.rotation_entry = tk.Entry(rotation_frame, width=10)
        self.rotation_entry.pack(side="left")
        self.rotation_entry.insert(0, "0.0")
        self._create_tooltip(
            self.rotation_entry,
            "Angolo di rotazione della sezione nel suo piano (gradi). "
            "Influenza i momenti d'inerzia globali e la grafica.",
        )

        # Campi per i fattori di forma a taglio (kappa_y, kappa_z)
        shear_frame = tk.Frame(self.left_frame)
        shear_frame.pack(fill="x", pady=(0, 8))
        tk.Label(shear_frame, text="Fattore di forma a taglio κ_y:").pack(side="left", padx=(0, 4))
        self.kappa_y_entry = tk.Entry(shear_frame, width=8)
        self.kappa_y_entry.pack(side="left")
        tk.Label(shear_frame, text="κ_z:").pack(side="left", padx=(8, 4))
        self.kappa_z_entry = tk.Entry(shear_frame, width=8)
        self.kappa_z_entry.pack(side="left")
        # Help button with detailed explanation (opens dialog)
        help_btn = tk.Button(shear_frame, text="?", width=2, command=self._show_shear_help)
        help_btn.pack(side="left", padx=(8, 0))
        self._create_tooltip(
            self.kappa_y_entry,
            "Fattore di forma a taglio κ_y (Timoshenko). Valore predefinito in base al tipo di sezione.",
        )
        self._create_tooltip(
            self.kappa_z_entry,
            "Fattore di forma a taglio κ_z (Timoshenko). Valore predefinito in base al tipo di sezione.",
        )
        self._create_tooltip(
            help_btn,
            "Informazioni dettagliate sui valori predefiniti di κ e sulle assunzioni (clicca per aprire)",
        )
        # Inizializza le entry con i valori di default per la tipologia corrente
        try:
            self._set_default_kappa_entries()
        except Exception:
            pass

        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.pack(fill="x", pady=(0, 8))

        tk.Button(
            self.buttons_frame,
            text="Calcola proprietà",
            command=self.calculate_properties,
            width=20,
        ).grid(row=0, column=0, padx=4, pady=2)
        tk.Button(
            self.buttons_frame,
            text="Mostra grafica",
            command=self.show_graphic,
            width=20,
        ).grid(row=0, column=1, padx=4, pady=2)
        tk.Button(
            self.buttons_frame,
            text="Salva nell'archivio",
            command=self.save_section,
            width=20,
        ).grid(row=1, column=0, padx=4, pady=2)
        tk.Button(
            self.buttons_frame,
            text="Gestisci archivio",
            command=self.open_manager,
            width=20,
        ).grid(row=1, column=1, padx=4, pady=2)

        tk.Button(
            self.buttons_frame,
            text="Importa CSV",
            command=self.import_csv,
            width=20,
        ).grid(row=2, column=0, padx=4, pady=2)
        tk.Button(
            self.buttons_frame,
            text="Esporta CSV",
            command=self.export_csv,
            width=20,
        ).grid(row=2, column=1, padx=4, pady=2)
        tk.Button(
            self.buttons_frame,
            text="Reset form",
            command=self.reset_form,
            width=20,
        ).grid(row=3, column=0, columnspan=2, padx=4, pady=2)

        self.display_frame = tk.Frame(self.left_frame)
        self.display_frame.pack(fill="x", pady=(0, 8))
        self.show_ellipse_var = tk.BooleanVar(value=True)
        self.show_core_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.display_frame,
            text="Mostra ellisse inerzia",
            variable=self.show_ellipse_var,
        ).pack(anchor="w")
        tk.Checkbutton(
            self.display_frame,
            text="Mostra nocciolo",
            variable=self.show_core_var,
        ).pack(anchor="w")

        # Pulsante per aprire l'Editor Materiali (coerente con il resto dei bottoni)
        # Posizionato sotto gli altri bottoni e collegato a `open_material_manager`.
        tk.Button(
            self.buttons_frame,
            text="Editor materiali",
            command=self.open_material_manager,
            width=42,
        ).grid(row=4, column=0, columnspan=2, padx=4, pady=4)

        self.output_frame = tk.LabelFrame(self.left_frame, text="Proprietà calcolate")
        self.output_frame.pack(fill="both", expand=True)
        self.output_text = tk.Text(self.output_frame, width=36, height=16)
        self.output_text.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_right_panel(self) -> None:
        tk.Label(self.right_frame, text="Grafica sezione").pack(anchor="w")
        self.canvas = tk.Canvas(self.right_frame, width=480, height=480, bg="white")
        self.canvas.pack(fill="both", expand=True)

    def _on_section_change(self, _event=None) -> None:
        """Handler per cambio tipologia sezione - ricostruisce campi input dinamicamente.

        Legge sia la StringVar sia il testo della ComboBox per essere robusto rispetto
        ai diversi modi in cui la selezione può essere cambiata dall'utente (mouse,
        tastiera, focus out, o modifica programmatica). Se la selezione è identica
        alla precedente viene ignorata (evita flicker e rielaborazioni inutili).
        """
        selected_from_var = self.section_var.get()
        selected_from_combo = self.section_combo.get()
        # Preferiamo il valore visibile nella combo, se presente
        tipo_selezionato = selected_from_combo or selected_from_var
        logger.debug(
            "Cambio tipologia sezione: var='%s' combo='%s' -> using '%s'",
            selected_from_var,
            selected_from_combo,
            tipo_selezionato,
        )

        # Ignora chiamate ripetute per la stessa selezione
        if getattr(self, "_last_selected_type", None) == tipo_selezionato:
            logger.debug("Selezione identica alla precedente (%s), skip", tipo_selezionato)
            return
        self._last_selected_type = tipo_selezionato

        # Assicura consistenza tra StringVar e combobox
        try:
            self.section_var.set(tipo_selezionato)
        except Exception:
            pass

        # Ricostruisce i campi di input per la nuova tipologia
        self._create_inputs()

        # Se era in modalità editing, resetta (la tipologia è cambiata)
        if self.editing_section_id is not None:
            logger.debug("Tipologia cambiata durante editing - reset modalità")
            self.editing_section_id = None
            self._update_editing_mode_label()

        # Pulisce eventuali calcoli precedenti
        self.current_section = None
        self.output_text.delete("1.0", tk.END)
        self.canvas.delete("all")

    def _poll_section_selection(self) -> None:
        """Polling leggero per rilevare il valore visualizzato nella ComboBox.

        Alcuni eventi di selezione non vengono emessi in tutte le situazioni; il
        polling è un fallback non invasivo che assicura che la GUI risponda
        coerentemente quando l'utente vede un valore diverso nella ComboBox.
        """
        try:
            visible = self.section_combo.get()
        except Exception:
            visible = None

        if visible and visible != getattr(self, "_last_selected_type", None):
            logger.debug("Polling: rilevata selezione visibile diversa: %s", visible)
            # Forza l'aggiornamento
            self._on_section_change()

        # Riesegui il polling periodicamente
        self._polling_id = self.after(300, self._poll_section_selection)

    def _cancel_polling(self) -> None:
        """Cancella il polling quando la finestra viene distrutta."""
        try:
            if getattr(self, "_polling_id", None):
                self.after_cancel(self._polling_id)
                self._polling_id = None
                logger.debug("Polling selezione ComboBox annullato")
        except Exception:
            pass

    def _on_close(self) -> None:
        """Handler per la chiusura della finestra - chiude solo questa Toplevel, non l'intera app.

        ✅ Assicura che il polling sia cancellato e la finestra sia distrutta correttamente.
        """
        self._cancel_polling()
        self.destroy()

    def _create_inputs(self) -> None:
        """Ricostruisce dinamicamente i campi di input in base alla tipologia di sezione selezionata.

        Logica:
        - Distrugge tutti i widget esistenti nel frame "Dati geometrici"
        - Legge la definizione della tipologia corrente da SECTION_DEFINITIONS
        - Crea Label + Entry per ogni campo richiesto dalla tipologia
        - Aggiunge tooltip esplicativi per ogni campo
        - Configura validazione per float a 1 cifra decimale
        """
        # Pulisce il frame dai widget precedenti
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.inputs.clear()

        # Recupera la definizione della tipologia selezionata
        tipo_sezione = self.section_var.get()
        definition = SECTION_DEFINITIONS[tipo_sezione]
        field_tooltips = definition.get("field_tooltips", {})

        logger.debug(f"Creazione campi input per tipologia: {tipo_sezione}")

        # Crea i campi di input dinamicamente
        for row, (field, label_text) in enumerate(definition["fields"]):
            # Label del parametro
            lbl = tk.Label(self.inputs_frame, text=label_text, anchor="w")
            lbl.grid(row=row, column=0, sticky="w", padx=4, pady=4)

            # Entry per l'input del valore
            # Usa validazione per accettare solo numeri con 1 decimale
            vcmd = (self.register(self._validate_float_input), "%P")
            entry = tk.Entry(self.inputs_frame, width=18, validate="key", validatecommand=vcmd)
            entry.grid(row=row, column=1, padx=4, pady=4, sticky="ew")

            # Memorizza l'entry per accesso successivo
            self.inputs[field] = entry

            # Aggiunge tooltip se disponibile
            if field in field_tooltips:
                self._create_tooltip(entry, field_tooltips[field])

        # Configura il peso della colonna per espansione
        self.inputs_frame.columnconfigure(1, weight=1)

        # Inizializza le entry dei fattori kappa con i valori di default per la tipologia
        try:
            self._set_default_kappa_entries()
        except Exception:
            pass

        logger.debug(f"Creati {len(self.inputs)} campi input")

    def _set_default_kappa_entries(self) -> None:
        """Imposta i valori di default per κ_y e κ_z basati sulla tipologia selezionata.

        I valori sono mantenuti in sincronia con le impostazioni centrali usate per il calcolo
        (vedi DEFAULT_SHEAR_KAPPAS in models.sections).
        """
        tipo = self.section_var.get()
        # Mappa dei default (tenere sincronizzati con DEFAULT_SHEAR_KAPPAS)
        defaults = {
            "Rettangolare": (5.0 / 6.0, 5.0 / 6.0),
            "Circolare": (10.0 / 9.0, 10.0 / 9.0),
            "Circolare cava": (1.0, 1.0),
            "Rettangolare cava": (5.0 / 6.0, 5.0 / 6.0),
            "A T": (1.0, 0.9),
            "Ad I (doppio T)": (1.0, 0.9),
            "A T rovescia": (1.0, 0.9),
            "A C (canale)": (1.0, 0.9),
        }
        ky, kz = defaults.get(tipo, (5.0 / 6.0, 5.0 / 6.0))
        try:
            self.kappa_y_entry.delete(0, tk.END)
            self.kappa_y_entry.insert(0, f"{ky:.6g}")
            self.kappa_z_entry.delete(0, tk.END)
            self.kappa_z_entry.insert(0, f"{kz:.6g}")
        except Exception:
            pass

    def _show_shear_help(self) -> None:
        """Mostra un dialog con spiegazione dei fattori di forma a taglio e i valori predefiniti.

        I valori e le assunzioni sono documentate anche in docs/SHEAR_FORM_FACTORS.md.
        """
        text = (
            "Fattori di forma a taglio (κ) - note rapide:\n\n"
            "- Rettangolare (b×h): κ ≈ 5/6 (~0.8333)\n"
            "- Circolare piena: κ ≈ 10/9 (~1.1111)\n"
            "- Sezioni T/I (anima prevalente): κ_y ≈ 1.0 (direzione anima), κ_z ≈ 0.9 (direzione trasversale)\n\n"
            "Definizione: A_y = κ_y * A_ref_y, A_z = κ_z * A_ref_z.\n"
            "Per sezioni con anima (T/I/C), A_ref_y è tipicamente l'area dell'anima (web_area = bw * hw),\n"
            "mentre per sezioni compatte si usa l'area totale.\n\n"
            "Questi sono valori di pratica ingegneristica tratti da testi classici (p.es. Roark, Timoshenko)\n"
            "e da tabelle usate comunemente in progettazione. Modifica i valori se desideri usare dati più precisi.\n\n"
            "Vedi file docs/SHEAR_FORM_FACTORS.md per dettagli e riferimenti."
        )
        notify_info("Fattori di forma a taglio (κ)", text, source="main_window")

    def _build_section_from_inputs(self) -> Optional[Section]:
        definition = SECTION_DEFINITIONS[self.section_var.get()]
        section_class = definition["class"]
        values: Dict[str, float] = {}

        for field, _label in definition["fields"]:
            raw = self.inputs[field].get().strip()
            if not raw:
                notify_error("Errore", f"{field} è richiesto", source="main_window")
                return None
            try:
                value = float(raw)
                if value <= 0:
                    raise ValueError
            except ValueError:
                notify_error(
                    "Errore", f"{field} deve essere un numero positivo", source="main_window"
                )
                return None
            values[field] = value

        # Leggi l'angolo di rotazione
        rotation_raw = self.rotation_entry.get().strip()
        try:
            rotation_angle_deg = float(rotation_raw) if rotation_raw else 0.0
        except ValueError:
            notify_error(
                "Errore", "Angolo di rotazione deve essere un numero", source="main_window"
            )
            return None

        name = self.name_entry.get().strip() or self.section_var.get()
        section = section_class(name=name, rotation_angle_deg=rotation_angle_deg, **values)

        # Leggi i fattori di forma a taglio (kappa) se forniti dall'utente
        try:
            k_y_raw = (
                self.kappa_y_entry.get().strip() if getattr(self, "kappa_y_entry", None) else ""
            )
            k_z_raw = (
                self.kappa_z_entry.get().strip() if getattr(self, "kappa_z_entry", None) else ""
            )
            k_y = float(k_y_raw) if k_y_raw else None
            k_z = float(k_z_raw) if k_z_raw else None
            if k_y is not None and k_y <= 0:
                raise ValueError("kappa_y must be positive")
            if k_z is not None and k_z <= 0:
                raise ValueError("kappa_z must be positive")
            if k_y is not None:
                section.shear_factor_y = k_y
            if k_z is not None:
                section.shear_factor_z = k_z
        except ValueError:
            notify_error(
                "Errore", "I fattori κ devono essere numeri positivi", source="main_window"
            )
            return None

        return section

    def calculate_properties(self) -> None:
        section = self._build_section_from_inputs()
        if not section:
            return
        self.current_section = section
        props = section.compute_properties()
        self._show_properties(props, section)

    def show_graphic(self) -> None:
        section = self._build_section_from_inputs()
        if not section:
            return
        try:
            section.compute_properties()
        except Exception as e:
            logger.exception("Errore nel calcolo proprietà: %s", e)
            messagebox.showerror("Errore", f"Errore nel calcolo proprietà: {e}")
            return
        self.current_section = section
        self._draw_section(section)

    def _show_properties(self, props, section: Section) -> None:
        output = (
            f"Sezione: {section.name}\n"
            f"Tipo: {section.section_type}\n\n"
            f"Area: {props.area:.3f} cm²\n"
            f"Area a taglio A_y: {(props.shear_area_y or 0.0):.3f} cm²\n"
            f"Area a taglio A_z: {(props.shear_area_z or 0.0):.3f} cm²\n"
            f"Baricentro: ({props.centroid_x:.3f}, {props.centroid_y:.3f}) cm\n"
            f"Ix: {props.ix:.3f} cm⁴\n"
            f"Iy: {props.iy:.3f} cm⁴\n"
            f"Ixy: {props.ixy:.3f} cm⁴\n"
            f"Qx: {props.qx:.3f} cm³\n"
            f"Qy: {props.qy:.3f} cm³\n"
            f"rx: {props.rx:.3f} cm\n"
            f"ry: {props.ry:.3f} cm\n"
            f"Nocciolo (x,y): ({props.core_x:.3f}, {props.core_y:.3f}) cm\n"
            f"Ellisse (a,b): ({props.ellipse_a:.3f}, {props.ellipse_b:.3f}) cm\n"
        )
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)

    def _draw_section(self, section: Section) -> None:
        """Disegna la sezione sul canvas applicando la rotazione se presente."""
        self.canvas.delete("all")
        width, height = self._section_dimensions(section)
        transform = compute_transform(
            width, height, int(self.canvas["width"]), int(self.canvas["height"])
        )

        # Disegna la sezione specifica con rotazione
        if isinstance(section, RectangularSection):
            self._draw_rectangle(section, transform)
        elif isinstance(section, CircularSection):
            self._draw_circle(section, transform)
        elif isinstance(section, TSection):
            self._draw_t_section(section, transform)
        elif isinstance(section, LSection):
            self._draw_l_section(section, transform)
        elif isinstance(section, ISection):
            self._draw_i_section(section, transform)
        elif isinstance(section, PiSection):
            self._draw_pi_section(section, transform)
        elif isinstance(section, InvertedTSection):
            self._draw_inverted_t_section(section, transform)
        elif isinstance(section, CSection):
            self._draw_c_section(section, transform)
        elif isinstance(section, CircularHollowSection):
            self._draw_circular_hollow(section, transform)
        elif isinstance(section, RectangularHollowSection):
            self._draw_rectangular_hollow(section, transform)
        elif isinstance(section, (VSection, InvertedVSection)):
            self._draw_v_section(section, transform)

        if section.properties:
            self._draw_centroid(section, transform)
            if getattr(self, "show_ellipse_var", None) is None or self.show_ellipse_var.get():
                self._draw_ellipse(section, transform)
            if getattr(self, "show_core_var", None) is None or self.show_core_var.get():
                self._draw_core(section, transform)

    def _rotate_point(
        self, x: float, y: float, cx: float, cy: float, angle_deg: float
    ) -> Tuple[float, float]:
        """Ruota un punto (x,y) attorno a (cx,cy) di angle_deg gradi."""
        from math import cos, radians, sin

        if angle_deg == 0:
            return x, y
        theta = radians(angle_deg)
        c = cos(theta)
        s = sin(theta)
        dx = x - cx
        dy = y - cy
        x_rot = cx + dx * c - dy * s
        y_rot = cy + dx * s + dy * c
        return x_rot, y_rot

    def _draw_rotated_polygon(self, points: list, section: Section, transform, **kwargs) -> None:
        """Disegna un poligono applicando la rotazione della sezione."""
        _, height = self._section_dimensions(section)
        props = section.properties
        if props:
            cx = props.centroid_x
            cy = props.centroid_y
        else:
            # Usa il centro geometrico della sezione
            cx = sum(p[0] for p in points) / len(points)
            cy = sum(p[1] for p in points) / len(points)

        # Ruota i punti attorno al baricentro
        rotated = [self._rotate_point(x, y, cx, cy, section.rotation_angle_deg) for x, y in points]

        # Trasforma in coordinate canvas
        canvas_points = []
        for x, y in rotated:
            cx_canvas, cy_canvas = transform.to_canvas(x, y, height)
            canvas_points.extend([cx_canvas, cy_canvas])

        self.canvas.create_polygon(canvas_points, **kwargs)

    def _section_dimensions(self, section: Section) -> Tuple[float, float]:
        """Calcola le dimensioni bounding box della sezione."""
        if isinstance(section, RectangularSection):
            return section.width, section.height
        if isinstance(section, CircularSection):
            return section.diameter, section.diameter
        if isinstance(section, TSection):
            return section.flange_width, section.total_height
        if isinstance(section, LSection):
            return section.width, section.height
        if isinstance(section, ISection):
            return section.flange_width, section.total_height
        if isinstance(section, PiSection):
            return section.flange_width, section.total_height
        if isinstance(section, InvertedTSection):
            return section.flange_width, section.total_height
        if isinstance(section, CSection):
            return section.width, section.height
        if isinstance(section, CircularHollowSection):
            return section.outer_diameter, section.outer_diameter
        if isinstance(section, RectangularHollowSection):
            return section.width, section.height
        if isinstance(section, (VSection, InvertedVSection)):
            return section.width, section.height
        return 1.0, 1.0

    def _draw_rectangle(self, section: RectangularSection, transform) -> None:
        """Disegna rettangolo con rotazione."""
        points = [
            (0, 0),
            (section.width, 0),
            (section.width, section.height),
            (0, section.height),
        ]
        self._draw_rotated_polygon(points, section, transform, outline="#1f77b4", width=2, fill="")

    def _draw_circle(self, section: CircularSection, transform) -> None:
        """Disegna cerchio (la rotazione non ha effetto visivo per circolare piena)."""
        diameter = section.diameter
        radius = diameter / 2
        _, height = self._section_dimensions(section)

        # Centro del cerchio
        cx_sec = radius
        cy_sec = radius

        # Trasforma in canvas
        cx, cy = transform.to_canvas(cx_sec, cy_sec, height)
        r_canvas = radius * transform.scale

        self.canvas.create_oval(
            cx - r_canvas, cy - r_canvas, cx + r_canvas, cy + r_canvas, outline="#1f77b4", width=2
        )

    def _draw_t_section(self, section: TSection, transform) -> None:
        """Disegna sezione a T con rotazione."""
        height = section.total_height
        web_x0 = (section.flange_width - section.web_thickness) / 2
        web_x1 = web_x0 + section.web_thickness

        # Ala (rettangolo superiore)
        flange_points = [
            (0, height - section.flange_thickness),
            (section.flange_width, height - section.flange_thickness),
            (section.flange_width, height),
            (0, height),
        ]

        # Anima (rettangolo inferiore centrale)
        web_points = [
            (web_x0, 0),
            (web_x1, 0),
            (web_x1, section.web_height),
            (web_x0, section.web_height),
        ]

        # Disegna come poligono unico per rotazione corretta
        all_points = [
            (0, height - section.flange_thickness),
            (0, height),
            (section.flange_width, height),
            (section.flange_width, height - section.flange_thickness),
            (web_x1, height - section.flange_thickness),
            (web_x1, 0),
            (web_x0, 0),
            (web_x0, height - section.flange_thickness),
        ]
        self._draw_rotated_polygon(
            all_points, section, transform, outline="#1f77b4", width=2, fill=""
        )

    def _draw_l_section(self, section: LSection, transform) -> None:
        """Disegna sezione ad L con rotazione."""
        h_vert = section.height - section.t_horizontal
        points = [
            (0, 0),
            (section.t_vertical, 0),
            (section.t_vertical, h_vert),
            (section.width, h_vert),
            (section.width, section.height),
            (0, section.height),
        ]
        self._draw_rotated_polygon(points, section, transform, outline="#1f77b4", width=2, fill="")

    def _draw_i_section(self, section: ISection, transform) -> None:
        """Disegna sezione ad I con rotazione."""
        height = section.total_height
        web_x0 = (section.flange_width - section.web_thickness) / 2
        web_x1 = web_x0 + section.web_thickness

        points = [
            # Ala inferiore
            (0, 0),
            (section.flange_width, 0),
            (section.flange_width, section.flange_thickness),
            (web_x1, section.flange_thickness),
            # Anima
            (web_x1, section.flange_thickness + section.web_height),
            # Ala superiore
            (section.flange_width, section.flange_thickness + section.web_height),
            (section.flange_width, height),
            (0, height),
            (0, section.flange_thickness + section.web_height),
            (web_x0, section.flange_thickness + section.web_height),
            # Anima sinistra
            (web_x0, section.flange_thickness),
            (0, section.flange_thickness),
        ]
        self._draw_rotated_polygon(points, section, transform, outline="#1f77b4", width=2, fill="")

    def _draw_pi_section(self, section: PiSection, transform) -> None:
        """Disegna sezione a Pi greco con rotazione."""
        height = section.total_height
        points = [
            (0, 0),
            (section.web_thickness, 0),
            (section.web_thickness, section.web_height),
            (section.flange_width - section.web_thickness, section.web_height),
            (section.flange_width - section.web_thickness, 0),
            (section.flange_width, 0),
            (section.flange_width, height),
            (0, height),
        ]
        self._draw_rotated_polygon(points, section, transform, outline="#1f77b4", width=2, fill="")

    def _draw_inverted_t_section(self, section: InvertedTSection, transform) -> None:
        """Disegna sezione a T rovescia con rotazione."""
        height = section.total_height
        web_x0 = (section.flange_width - section.web_thickness) / 2
        web_x1 = web_x0 + section.web_thickness

        points = [
            (0, 0),
            (section.flange_width, 0),
            (section.flange_width, section.flange_thickness),
            (web_x1, section.flange_thickness),
            (web_x1, height),
            (web_x0, height),
            (web_x0, section.flange_thickness),
            (0, section.flange_thickness),
        ]
        self._draw_rotated_polygon(points, section, transform, outline="#1f77b4", width=2, fill="")

    def _draw_c_section(self, section: CSection, transform) -> None:
        """Disegna sezione a C con rotazione."""
        h_web = section.height - 2 * section.flange_thickness
        points = [
            (0, 0),
            (section.width, 0),
            (section.width, section.flange_thickness),
            (section.web_thickness, section.flange_thickness),
            (section.web_thickness, section.flange_thickness + h_web),
            (section.width, section.flange_thickness + h_web),
            (section.width, section.height),
            (0, section.height),
        ]
        self._draw_rotated_polygon(points, section, transform, outline="#1f77b4", width=2, fill="")

    def _draw_circular_hollow(self, section: CircularHollowSection, transform) -> None:
        """Disegna cerchio cavo."""
        _, height = self._section_dimensions(section)
        r_out = section.outer_diameter / 2
        r_in = (section.outer_diameter - 2 * section.thickness) / 2

        cx_sec = r_out
        cy_sec = r_out

        cx, cy = transform.to_canvas(cx_sec, cy_sec, height)
        r_out_canvas = r_out * transform.scale
        r_in_canvas = r_in * transform.scale

        # Cerchio esterno
        self.canvas.create_oval(
            cx - r_out_canvas,
            cy - r_out_canvas,
            cx + r_out_canvas,
            cy + r_out_canvas,
            outline="#1f77b4",
            width=2,
        )
        # Cerchio interno
        self.canvas.create_oval(
            cx - r_in_canvas,
            cy - r_in_canvas,
            cx + r_in_canvas,
            cy + r_in_canvas,
            outline="#1f77b4",
            width=1,
        )

    def _draw_rectangular_hollow(self, section: RectangularHollowSection, transform) -> None:
        """Disegna rettangolo cavo con rotazione."""
        t = section.thickness
        w_in = section.width - 2 * t
        h_in = section.height - 2 * t

        # Poligono esterno
        outer = [
            (0, 0),
            (section.width, 0),
            (section.width, section.height),
            (0, section.height),
        ]
        self._draw_rotated_polygon(outer, section, transform, outline="#1f77b4", width=2, fill="")

        # Poligono interno
        inner = [
            (t, t),
            (t + w_in, t),
            (t + w_in, t + h_in),
            (t, t + h_in),
        ]
        self._draw_rotated_polygon(inner, section, transform, outline="#1f77b4", width=1, fill="")

    def _draw_v_section(self, section, transform) -> None:
        """Disegna sezione a V (approssimazione)."""
        # Approssimazione semplice della V
        half_w = section.width / 2
        t = section.thickness

        # Triangolo esterno
        outer = [
            (0, 0),
            (section.width, 0),
            (half_w, section.height),
        ]
        # Triangolo interno (approssimato)
        inner = [
            (t, 0),
            (section.width - t, 0),
            (half_w, section.height - t),
        ]

        self._draw_rotated_polygon(outer, section, transform, outline="#1f77b4", width=2, fill="")
        self._draw_rotated_polygon(inner, section, transform, outline="#1f77b4", width=1, fill="")

    def _draw_centroid(self, section: Section, transform) -> None:
        props = section.properties
        if not props:
            return
        height = self._section_dimensions(section)[1]
        cx, cy = transform.to_canvas(props.centroid_x, props.centroid_y, height)
        self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="red")
        self.canvas.create_text(cx + 6, cy - 6, text="G", fill="red")

    def _draw_ellipse(self, section: Section, transform) -> None:
        props = section.properties
        if not props:
            return
        height = self._section_dimensions(section)[1]
        if props.ellipse_a is None or props.ellipse_b is None:
            return
        angle_deg = props.principal_angle_deg or 0.0
        points = []
        steps = 60
        for i in range(steps + 1):
            t = (2 * math.pi * i) / steps
            x = props.centroid_x + props.ellipse_b * math.cos(t)
            y = props.centroid_y + props.ellipse_a * math.sin(t)
            x_rot, y_rot = self._rotate_point(x, y, props.centroid_x, props.centroid_y, angle_deg)
            cx, cy = transform.to_canvas(x_rot, y_rot, height)
            points.extend([cx, cy])
        self.canvas.create_line(points, fill="#ff7f0e", dash=(4, 2), smooth=True)

    def _draw_core(self, section: Section, transform) -> None:
        props = section.properties
        if not props:
            return
        height = self._section_dimensions(section)[1]
        if props.core_x is None or props.core_y is None:
            return
        angle_deg = props.principal_angle_deg or 0.0
        corners = [
            (props.centroid_x - props.core_x, props.centroid_y - props.core_y),
            (props.centroid_x + props.core_x, props.centroid_y - props.core_y),
            (props.centroid_x + props.core_x, props.centroid_y + props.core_y),
            (props.centroid_x - props.core_x, props.centroid_y + props.core_y),
        ]
        points = []
        for x, y in corners:
            x_rot, y_rot = self._rotate_point(x, y, props.centroid_x, props.centroid_y, angle_deg)
            cx, cy = transform.to_canvas(x_rot, y_rot, height)
            points.extend([cx, cy])
        self.canvas.create_polygon(points, outline="#2ca02c", dash=(2, 2), fill="")

    def save_section(self) -> None:
        # OBIETTIVO 3+4: Costruisce sezione e gestisce correttamente nuova vs modifica
        section = self._build_section_from_inputs()
        if not section:
            return

        # OBIETTIVO 4: Calcola proprietà automaticamente se assenti o se parametri sono cambiati
        try:
            # Calcola sempre le proprietà per assicurare valori aggiornati (sempre chiamare compute_properties)
            section.compute_properties()
            logger.debug("Proprietà calcolate per sezione: %s", section.name)
        except Exception as e:
            logger.exception("Errore nel calcolo proprietà: %s", e)
            messagebox.showerror("Errore", f"Errore nel calcolo proprietà: {e}")
            return

        # OBIETTIVO 3: Modifica non crea nuova sezione, fa update della sezione esistente
        if self.editing_section_id is None:
            # Nuova sezione
            added = self.repository.add_section(section)
            if added:
                messagebox.showinfo(
                    "Salvataggio",
                    f"Sezione '{section.name}' salvata correttamente nell'archivio.\nID: {section.id}",
                )
                logger.debug("Sezione creata: %s", section.id)
            else:
                messagebox.showinfo("Salvataggio", "Sezione duplicata: non salvata")
        else:
            # Modifica sezione esistente: aggiorna mantenendo lo stesso ID
            try:
                section.id = self.editing_section_id  # Preserva ID originale
                self.repository.update_section(self.editing_section_id, section)
                messagebox.showinfo(
                    "Aggiornamento",
                    f"Sezione '{section.name}' aggiornata correttamente nell'archivio.\nID: {self.editing_section_id}",
                )
                logger.debug("Sezione aggiornata: %s", self.editing_section_id)
                self.editing_section_id = None
                self._update_editing_mode_label()
            except Exception as e:
                logger.exception("Errore aggiornamento sezione %s: %s", self.editing_section_id, e)
                notify_error(
                    "Errore", f"Impossibile aggiornare la sezione: {e}", source="main_window"
                )
                return

        # Se il manager è aperto, ricarica la tabella
        mgr = getattr(self, "section_manager", None)
        if mgr and getattr(mgr, "winfo_exists", None) and mgr.winfo_exists():
            try:
                mgr.reload_sections_in_treeview()
            except Exception:
                logger.exception("Errore nel ricaricare il Section Manager dopo salvataggio")
        else:
            # Se la finestra manager non esiste più, puliamo il riferimento
            if mgr is not None:
                self.section_manager = None

    def open_manager(self) -> None:
        # Verifica se il manager è già aperto
        if hasattr(self, "section_manager") and self.section_manager is not None:
            if self.section_manager.winfo_exists():
                # Porta in primo piano la finestra esistente
                self.section_manager.lift()
                self.section_manager.focus_force()
                logger.debug("Section Manager già aperto, portato in primo piano")
                return

        # Crea nuova istanza del manager
        manager = SectionManager(
            self, self.repository, self.serializer, self.load_section_into_form
        )
        self.section_manager = manager
        # Assicura che quando il manager viene chiuso si rimuova il riferimento
        manager.protocol("WM_DELETE_WINDOW", lambda m=manager: self._on_manager_close(m))
        # Se il manager viene distrutto in altro modo (es. edit -> destroy), aggiorna il riferimento
        manager.bind("<Destroy>", lambda e, m=manager: self._on_manager_destroyed(m))
        logger.debug("Section Manager aperto")

    def _on_manager_destroyed(self, manager: SectionManager) -> None:
        # Se il manager è stato distrutto, rimuovi il riferimento
        if getattr(self, "section_manager", None) is manager:
            self.section_manager = None

    def _on_manager_close(self, manager: SectionManager) -> None:
        try:
            manager.destroy()
        finally:
            if getattr(self, "section_manager", None) is manager:
                self.section_manager = None

    def load_section_into_form(self, section: Section) -> None:
        """Carica i dati di una sezione nella form in modalità modifica."""
        label = self._label_from_section(section)
        if label:
            self.section_var.set(label)
            self._create_inputs()
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, section.name)

        for field, entry in self.inputs.items():
            value = getattr(section, field, "")
            entry.delete(0, tk.END)
            entry.insert(0, value)

        # Carica l'angolo di rotazione
        self.rotation_entry.delete(0, tk.END)
        self.rotation_entry.insert(0, str(section.rotation_angle_deg))

        # Carica i fattori kappa se presenti, altrimenti mostra i default
        try:
            if getattr(section, "shear_factor_y", None) is not None:
                self.kappa_y_entry.delete(0, tk.END)
                self.kappa_y_entry.insert(0, str(section.shear_factor_y))
            else:
                self._set_default_kappa_entries()
            if getattr(section, "shear_factor_z", None) is not None:
                self.kappa_z_entry.delete(0, tk.END)
                self.kappa_z_entry.insert(0, str(section.shear_factor_z))
            else:
                self._set_default_kappa_entries()
        except Exception:
            # Non blocchiamo il caricamento se il campo non esiste
            pass

        self.current_section = section
        # Imposta l'id di modifica in modo che il salvataggio faccia update
        self.editing_section_id = section.id
        self._update_editing_mode_label()
        if section.properties:
            self._show_properties(section.properties, section)

    def _label_from_section(self, section: Section) -> Optional[str]:
        for label, definition in SECTION_DEFINITIONS.items():
            if isinstance(section, definition["class"]):
                return label
        return None

    def import_csv(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Importa CSV",
            filetypes=[("CSV", "*.csv"), ("Tutti i file", "*.*")],
        )
        if not file_path:
            return
        sections = self.serializer.import_from_csv(file_path)
        added = 0
        for section in sections:
            if self.repository.add_section(section):
                added += 1
        messagebox.showinfo("Importa CSV", f"Importate {added} sezioni")

    def export_csv(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Esporta CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not file_path:
            return
        self.serializer.export_to_csv(file_path, self.repository.get_all_sections())
        messagebox.showinfo("Esporta CSV", "Esportazione completata")

    def export_full_backup(self) -> None:
        """Esporta backup completo di sezioni e materiali in una cartella scelta dall'utente."""
        if self.material_repository is None:
            notify_error(
                "Errore backup",
                "Archivio materiali non disponibile.",
            )
            return

        folder = filedialog.askdirectory(title="Seleziona cartella per backup")
        if not folder:
            return

        try:
            base = Path(folder)
            sections_path = base / "sections_backup.json"
            materials_path = base / "materials_backup.json"

            self.section_repository.export_backup(sections_path)
            self.material_repository.export_backup(materials_path)

            messagebox.showinfo(
                "Backup completato",
                f"Backup sezioni: {sections_path}\nBackup materiali: {materials_path}",
            )
        except Exception as exc:
            logger.exception("Errore esportazione backup completo")
            notify_error("Errore backup", f"Errore durante il backup: {exc}", source="main_window")

    def reset_form(self) -> None:
        """Reset completo della form alla modalità nuova sezione."""
        self.editing_section_id = None
        self.current_section = None
        self.name_entry.delete(0, tk.END)
        for entry in self.inputs.values():
            entry.delete(0, tk.END)
        self.rotation_entry.delete(0, tk.END)
        self.rotation_entry.insert(0, "0.0")
        self.output_text.delete("1.0", tk.END)
        self.canvas.delete("all")
        self._update_editing_mode_label()
        logger.debug("Form resettata")

    def _update_editing_mode_label(self) -> None:
        """Aggiorna la label che mostra lo stato editing corrente."""
        if self.editing_section_id is None:
            self.editing_mode_label.config(text="Modalità: Nuova sezione", fg="#0066cc")
        else:
            section_name = self.current_section.name if self.current_section else "(sconosciuto)"
            self.editing_mode_label.config(
                text=f"Modalità: Modifica sezione '{section_name}'\nID: {self.editing_section_id[:8]}...",
                fg="#cc6600",
            )

    def _validate_float_input(self, value: str) -> bool:
        """Valida input numerico: accetta solo float con massimo 1 cifra decimale.

        Args:
            value: Stringa da validare

        Returns:
            True se il valore è valido (vuoto, numero intero, o numero con max 1 decimale)

        """
        if value == "":
            return True

        # Accetta segno negativo all'inizio (anche se poi il valore deve essere positivo)
        if value == "-":
            return True

        try:
            # Verifica che sia un numero valido
            float(value)

            # Controlla il numero di cifre decimali
            if "." in value:
                parts = value.split(".")
                # Massimo 1 cifra decimale
                if len(parts) == 2 and len(parts[1]) <= 1:
                    return True
                return False
            # Numero intero OK
            return True
        except ValueError:
            return False

    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Crea un tooltip che appare al passaggio del mouse su un widget.

        Args:
            widget: Widget Tkinter su cui mostrare il tooltip
            text: Testo del tooltip

        """

        def on_enter(event):
            # Crea finestra tooltip
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                font=("Arial", 9),
                justify="left",
                padx=4,
                pady=2,
            )
            label.pack()

            # Memorizza riferimento al tooltip
            widget._tooltip = tooltip

        def on_leave(event):
            # Distrugge tooltip
            if hasattr(widget, "_tooltip"):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
