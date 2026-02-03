from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from rd2229.sections_app.models.sections import (
    CircularSection,
    RectangularSection,
    Section,
    TSection,
)
from rd2229.sections_app.services.calculations import compute_transform
from rd2229.sections_app.services.repository import CsvSectionSerializer, SectionRepository
from rd2229.sections_app.ui.section_manager import SectionManager

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
}


class MainWindow(tk.Tk):
    """Finestra principale dell'applicazione."""

    def __init__(self, repository: SectionRepository, serializer: CsvSectionSerializer):
        super().__init__()
        self.title("Gestione Proprietà Sezioni")
        self.geometry("980x620")
        self.repository = repository
        self.serializer = serializer
        self.current_section: Optional[Section] = None
        # Quando si modifica una sezione dal Section Manager, qui viene salvato l'id
        self.editing_section_id: Optional[str] = None
        # Riferimento opzionale al manager per aggiornamenti UI
        self.section_manager: Optional[SectionManager] = None

        self._build_layout()
        # Memorizza l'ultima tipologia selezionata per evitare rielaborazioni ridondanti
        self._last_selected_type: Optional[str] = self.section_var.get()
        # Avvia un polling leggero per intercettare cambi di selezione che a volte
        # vengono mostrati nella combo senza emettere l'evento (fallback UX)
        self._polling_id = self.after(300, self._poll_section_selection)
        # Assicura di fermare il polling quando la finestra viene distrutta
        self.bind("<Destroy>", lambda e: self._cancel_polling())

    def _build_layout(self) -> None:
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(main_frame)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._build_left_panel()
        self._build_right_panel()

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
            self.section_var.trace_add('write', lambda *a: self._on_section_change())
        except Exception:
            # Fallback per versioni più vecchie di tkinter che usano trace_var
            self.section_var.trace('w', lambda *a: self._on_section_change())
        
        # Pulsante per applicare esplicitamente la tipologia (fallback UX)
        self.apply_type_btn = tk.Button(self.left_frame, text="Applica tipo", command=self._on_section_change, width=12)
        self.apply_type_btn.pack(anchor="w", pady=(0, 4))
        
        # Tooltip sulla combobox
        self._create_tooltip(self.section_combo, "Seleziona il tipo di sezione da analizzare")

        # Label indicatore stato editing
        self.editing_mode_label = tk.Label(
            self.left_frame, 
            text="Modalità: Nuova sezione",
            font=("Arial", 9, "italic"),
            fg="#0066cc"
        )
        self.editing_mode_label.pack(anchor="w", pady=(0, 8))

        tk.Label(self.left_frame, text="Nome sezione").pack(anchor="w")
        self.name_entry = tk.Entry(self.left_frame, width=30)
        self.name_entry.pack(anchor="w", pady=(0, 8))

        self.inputs_frame = tk.LabelFrame(self.left_frame, text="Dati geometrici")
        self.inputs_frame.pack(fill="x", pady=(0, 8))
        self.inputs: Dict[str, tk.Entry] = {}
        self._create_inputs()

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

    def _create_inputs(self) -> None:
        """
        Ricostruisce dinamicamente i campi di input in base alla tipologia di sezione selezionata.
        
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
            vcmd = (self.register(self._validate_float_input), '%P')
            entry = tk.Entry(
                self.inputs_frame,
                width=18,
                validate="key",
                validatecommand=vcmd
            )
            entry.grid(row=row, column=1, padx=4, pady=4, sticky="ew")
            
            # Memorizza l'entry per accesso successivo
            self.inputs[field] = entry
            
            # Aggiunge tooltip se disponibile
            if field in field_tooltips:
                self._create_tooltip(entry, field_tooltips[field])
            
        # Configura il peso della colonna per espansione
        self.inputs_frame.columnconfigure(1, weight=1)
        
        logger.debug(f"Creati {len(self.inputs)} campi input")

    def _build_section_from_inputs(self) -> Optional[Section]:
        definition = SECTION_DEFINITIONS[self.section_var.get()]
        section_class = definition["class"]
        values: Dict[str, float] = {}

        for field, _label in definition["fields"]:
            raw = self.inputs[field].get().strip()
            if not raw:
                messagebox.showerror("Errore", f"{field} è richiesto")
                return None
            try:
                value = float(raw)
                if value <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Errore", f"{field} deve essere un numero positivo")
                return None
            values[field] = value

        name = self.name_entry.get().strip() or self.section_var.get()
        section = section_class(name=name, **values)
        return section

    def calculate_properties(self) -> None:
        section = self._build_section_from_inputs()
        if not section:
            return
        self.current_section = section
        props = section.compute_properties()
        self._show_properties(props, section)

    def show_graphic(self) -> None:
        if not self.current_section or not self.current_section.properties:
            messagebox.showinfo("Info", "Calcola prima le proprietà")
            return
        self._draw_section(self.current_section)

    def _show_properties(self, props, section: Section) -> None:
        output = (
            f"Sezione: {section.name}\n"
            f"Tipo: {section.section_type}\n\n"
            f"Area: {props.area:.3f} cm²\n"
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
        self.canvas.delete("all")
        width, height = self._section_dimensions(section)
        transform = compute_transform(width, height, int(self.canvas["width"]), int(self.canvas["height"]))

        if isinstance(section, RectangularSection):
            self._draw_rectangle(section, transform)
        elif isinstance(section, CircularSection):
            self._draw_circle(section, transform)
        elif isinstance(section, TSection):
            self._draw_t_section(section, transform)

        if section.properties:
            self._draw_centroid(section, transform)
            self._draw_ellipse(section, transform)
            self._draw_core(section, transform)

    def _section_dimensions(self, section: Section) -> Tuple[float, float]:
        if isinstance(section, RectangularSection):
            return section.width, section.height
        if isinstance(section, CircularSection):
            return section.diameter, section.diameter
        if isinstance(section, TSection):
            return section.flange_width, section.total_height
        return 1.0, 1.0

    def _draw_rectangle(self, section: RectangularSection, transform) -> None:
        x0, y0 = transform.to_canvas(0, 0, section.height)
        x1, y1 = transform.to_canvas(section.width, section.height, section.height)
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="#1f77b4", width=2)

    def _draw_circle(self, section: CircularSection, transform) -> None:
        diameter = section.diameter
        x0, y0 = transform.to_canvas(0, 0, diameter)
        x1, y1 = transform.to_canvas(diameter, diameter, diameter)
        self.canvas.create_oval(x0, y0, x1, y1, outline="#1f77b4", width=2)

    def _draw_t_section(self, section: TSection, transform) -> None:
        height = section.total_height
        web_x0 = (section.flange_width - section.web_thickness) / 2
        web_x1 = web_x0 + section.web_thickness

        flange_x0, flange_y0 = transform.to_canvas(0, height - section.flange_thickness, height)
        flange_x1, flange_y1 = transform.to_canvas(section.flange_width, height, height)
        self.canvas.create_rectangle(flange_x0, flange_y0, flange_x1, flange_y1, outline="#1f77b4", width=2)

        web_x0_c, web_y0 = transform.to_canvas(web_x0, 0, height)
        web_x1_c, web_y1 = transform.to_canvas(web_x1, section.web_height, height)
        self.canvas.create_rectangle(web_x0_c, web_y0, web_x1_c, web_y1, outline="#1f77b4", width=2)

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
        x0 = props.centroid_x - props.ellipse_b
        x1 = props.centroid_x + props.ellipse_b
        y0 = props.centroid_y - props.ellipse_a
        y1 = props.centroid_y + props.ellipse_a
        cx0, cy0 = transform.to_canvas(x0, y0, height)
        cx1, cy1 = transform.to_canvas(x1, y1, height)
        self.canvas.create_oval(cx0, cy0, cx1, cy1, outline="#ff7f0e", dash=(4, 2))

    def _draw_core(self, section: Section, transform) -> None:
        props = section.properties
        if not props:
            return
        height = self._section_dimensions(section)[1]
        x0 = props.centroid_x - props.core_x
        x1 = props.centroid_x + props.core_x
        y0 = props.centroid_y - props.core_y
        y1 = props.centroid_y + props.core_y
        cx0, cy0 = transform.to_canvas(x0, y0, height)
        cx1, cy1 = transform.to_canvas(x1, y1, height)
        self.canvas.create_rectangle(cx0, cy0, cx1, cy1, outline="#2ca02c", dash=(2, 2))

    def save_section(self) -> None:
        # Costruisce la sezione dai campi (o usa current_section se presente)
        section = self._build_section_from_inputs()
        if not section:
            return

        # Calcola proprietà sempre prima di salvare
        try:
            section.compute_properties()
        except Exception as e:
            logger.exception("Errore nel calcolo proprietà prima del salvataggio: %s", e)
            messagebox.showerror("Errore", f"Errore nel calcolo proprietà: {e}")
            return

        # Salvataggio: nuova sezione o update
        if self.editing_section_id is None:
            added = self.repository.add_section(section)
            if added:
                messagebox.showinfo(
                    "Salvataggio", 
                    f"Sezione '{section.name}' salvata correttamente nell'archivio.\nID: {section.id}"
                )
                logger.debug("Sezione creata: %s", section.id)
            else:
                messagebox.showinfo("Salvataggio", "Sezione duplicata: non salvata")
        else:
            try:
                self.repository.update_section(self.editing_section_id, section)
                messagebox.showinfo(
                    "Aggiornamento", 
                    f"Sezione '{section.name}' aggiornata correttamente nell'archivio.\nID: {self.editing_section_id}"
                )
                logger.debug("Sezione aggiornata: %s", self.editing_section_id)
                # reset dello stato di edit
                self.editing_section_id = None
                self._update_editing_mode_label()
            except Exception as e:
                logger.exception("Errore aggiornamento sezione %s: %s", self.editing_section_id, e)
                messagebox.showerror("Errore", f"Impossibile aggiornare la sezione: {e}")
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
        if hasattr(self, 'section_manager') and self.section_manager is not None:
            if self.section_manager.winfo_exists():
                # Porta in primo piano la finestra esistente
                self.section_manager.lift()
                self.section_manager.focus_force()
                logger.debug("Section Manager già aperto, portato in primo piano")
                return
        
        # Crea nuova istanza del manager
        manager = SectionManager(self, self.repository, self.serializer, self.load_section_into_form)
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

    def reset_form(self) -> None:
        """Reset completo della form alla modalità nuova sezione."""
        self.editing_section_id = None
        self.current_section = None
        self.name_entry.delete(0, tk.END)
        for entry in self.inputs.values():
            entry.delete(0, tk.END)
        self.output_text.delete("1.0", tk.END)
        self.canvas.delete("all")
        self._update_editing_mode_label()
        logger.debug("Form resettata")

    def _update_editing_mode_label(self) -> None:
        """Aggiorna la label che mostra lo stato editing corrente."""
        if self.editing_section_id is None:
            self.editing_mode_label.config(
                text="Modalità: Nuova sezione",
                fg="#0066cc"
            )
        else:
            section_name = self.current_section.name if self.current_section else "(sconosciuto)"
            self.editing_mode_label.config(
                text=f"Modalità: Modifica sezione '{section_name}'\nID: {self.editing_section_id[:8]}...",
                fg="#cc6600"
            )
    
    def _validate_float_input(self, value: str) -> bool:
        """
        Valida input numerico: accetta solo float con massimo 1 cifra decimale.
        
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
            if '.' in value:
                parts = value.split('.')
                # Massimo 1 cifra decimale
                if len(parts) == 2 and len(parts[1]) <= 1:
                    return True
                else:
                    return False
            else:
                # Numero intero OK
                return True
        except ValueError:
            return False
    
    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """
        Crea un tooltip che appare al passaggio del mouse su un widget.
        
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
                pady=2
            )
            label.pack()
            
            # Memorizza riferimento al tooltip
            widget._tooltip = tooltip
        
        def on_leave(event):
            # Distrugge tooltip
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
