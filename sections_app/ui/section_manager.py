from __future__ import annotations

import logging
from typing import Callable, Dict, Optional, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from sections_app.models.sections import CSV_HEADERS, Section
from sections_app.services.repository import CsvSectionSerializer, SectionRepository

logger = logging.getLogger(__name__)


class TreeviewTooltip:
    """Gestisce tooltip su celle del Treeview al passaggio del mouse."""

    def __init__(self, tree: ttk.Treeview):
        self.tree = tree
        self.tipwindow: Optional[tk.Toplevel] = None
        self.current_item: Optional[str] = None
        self.current_column: Optional[str] = None

        self.tree.bind("<Motion>", self.on_motion)
        self.tree.bind("<Leave>", self.on_leave)

    def on_motion(self, event: tk.Event) -> None:
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or not col_id:
            self.hide_tip()
            return

        if (row_id, col_id) == (self.current_item, self.current_column):
            return

        self.current_item, self.current_column = row_id, col_id
        
        # Converti col_id (es. "#1", "#2") in nome colonna
        columns = list(self.tree["columns"])
        try:
            col_index = int(col_id.replace("#", "")) - 1
            if 0 <= col_index < len(columns):
                col_name = columns[col_index]
                value = self.tree.set(row_id, col_name)
            else:
                value = ""
        except Exception:
            value = ""

        if not value:
            self.hide_tip()
            return

        self.show_tip(value, event.x_root + 10, event.y_root + 10)

    def show_tip(self, text: str, x: int, y: int) -> None:
        self.hide_tip()
        self.tipwindow = tw = tk.Toplevel(self.tree)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            justify="left",
        )
        label.pack(ipadx=2, ipady=1)

    def hide_tip(self) -> None:
        if self.tipwindow is not None:
            self.tipwindow.destroy()
            self.tipwindow = None
            self.current_item = None
            self.current_column = None

    def on_leave(self, event: tk.Event) -> None:
        self.hide_tip()


def sort_treeview(tree: ttk.Treeview, col: str, reverse: bool) -> None:
    """
    Ordina il Treeview per colonna. Supporta numeri e stringhe.
    
    Rileva automaticamente il tipo di dato (numerico o testuale) e ordina di conseguenza.
    Il click ripetuto alterna l'ordinamento crescente/decrescente.
    
    Args:
        tree: Il Treeview da ordinare
        col: Nome della colonna su cui ordinare
        reverse: True per ordinamento decrescente
    """
    data = [(tree.set(item, col), item) for item in tree.get_children("")]

    def try_num(value: str) -> float | str:
        """Tenta di convertire il valore a numero, altrimenti lo mantiene stringa."""
        if value == "":
            return ""
        try:
            return float(value.replace(",", "."))
        except (ValueError, AttributeError):
            return value

    # Ordina con key che gestisce sia numeri che stringhe
    data.sort(key=lambda t: (isinstance(try_num(t[0]), str), try_num(t[0])), reverse=reverse)

    # Ricrea l'ordine delle righe nel Treeview
    for index, (_, item) in enumerate(data):
        tree.move(item, "", index)

    # Aggiorna il heading con il nuovo ordinamento alternato
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


class SectionManager(tk.Toplevel):
    """
    Finestra di gestione dell'archivio sezioni con visualizzazione completa di tutti i dati.
    
    Caratteristiche:
    - Mostra tutte le proprietà geometriche e calcolate in colonne strette e ottimizzate
    - ID nascosta ma presente per tracciamento interno
    - Ordinamento cliccabile sulle intestazioni (crescente/decrescente)
    - Tooltip al passaggio del mouse per valori lunghi
    - Import/export CSV mantenendo la compatibilità
    """

    def __init__(
        self,
        master: tk.Tk,
        repository: SectionRepository,
        serializer: CsvSectionSerializer,
        on_edit: Callable[[Section], None],
    ) -> None:
        super().__init__(master)
        self.title("Archivio Sezioni - Visualizzazione Completa")
        
        self.repository = repository
        self.serializer = serializer
        self.on_edit = on_edit
        
        # Traccia se il sorting è stato mai toccato per la colonna corrente
        self._sort_state: Dict[str, bool] = {}

        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        """Costruisce l'interfaccia della finestra con Treeview e bottoni."""
        # Frame principale per il treeview con scrollbar
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Scrollbar orizzontale e verticale
        xscroll = tk.Scrollbar(tree_frame, orient="horizontal")
        xscroll.pack(side="bottom", fill="x")
        
        yscroll = tk.Scrollbar(tree_frame, orient="vertical")
        yscroll.pack(side="right", fill="y")

        # Determina le colonne dinamicamente da un esempio di sezione (to_dict)
        sections_list = self.repository.get_all_sections()
        if sections_list:
            sample = sections_list[0].to_dict()
            # Manteniamo ordine con 'id','name','section_type' iniziali quando presenti
            self.columns = list(sample.keys())
        else:
            # Fallback alle HEADERS predefinite se archivio vuoto
            self.columns = list(CSV_HEADERS)
        logger.debug("Colonne Treeview: %s", self.columns)

        # Creazione Treeview con tutte le colonne
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.columns,
            show="headings",
            height=14,
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
        )
        xscroll.config(command=self.tree.xview)
        yscroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # Mappa colonne a larghezze minime e anchor
        col_config: Dict[str, Tuple[int, str]] = {
            "id": (0, "w"),                          # invisibile
            "name": (100, "w"),                      # nome sezione (sinistra)
            "section_type": (90, "center"),          # tipo sezione
            "width": (65, "center"),                 # b (cm)
            "height": (65, "center"),                # h (cm)
            "diameter": (65, "center"),              # d (cm)
            "flange_width": (70, "center"),          # bf (cm)
            "flange_thickness": (70, "center"),      # hf (cm)
            "web_thickness": (70, "center"),         # bw (cm)
            "web_height": (70, "center"),            # hw (cm)
            "t_horizontal": (70, "center"),          # t horizontal (cm)
            "t_vertical": (70, "center"),            # t vertical (cm)
            "outer_diameter": (70, "center"),        # outer diameter (cm)
            "thickness": (70, "center"),             # thickness (cm)
            "rotation_angle_deg": (70, "center"),   # rotation angle (deg)
            "area": (75, "center"),                  # Area (cm²)
            "x_G": (65, "center"),                   # x_G (cm)
            "y_G": (65, "center"),                   # y_G (cm)
            "Ix": (80, "center"),                    # Ix (cm⁴)
            "Iy": (80, "center"),                    # Iy (cm⁴)
            "Ixy": (75, "center"),                   # Ixy (cm⁴)
            "Qx": (70, "center"),                    # Qx (cm³)
            "Qy": (70, "center"),                    # Qy (cm³)
            "rx": (65, "center"),                    # rx (cm)
            "ry": (65, "center"),                    # ry (cm)
            "core_x": (70, "center"),                # x nocciolo (cm)
            "core_y": (70, "center"),                # y nocciolo (cm)
            "ellipse_a": (75, "center"),             # a ellisse (cm)
            "ellipse_b": (75, "center"),             # b ellisse (cm)
            "note": (120, "w"),                      # note/commenti
        }

        # Mappa colonne a etichette di intestazione leggibili
        header_labels: Dict[str, str] = {
            "id": "",
            "name": "Nome Sezione",
            "section_type": "Tipo",
            "width": "b (cm)",
            "height": "h (cm)",
            "diameter": "d (cm)",
            "flange_width": "bf (cm)",
            "flange_thickness": "hf (cm)",
            "web_thickness": "bw (cm)",
            "web_height": "hw (cm)",
            "t_horizontal": "t horizontal (cm)",
            "t_vertical": "t vertical (cm)",
            "outer_diameter": "outer d (cm)",
            "thickness": "thickness (cm)",
            "rotation_angle_deg": "rot (deg)",
            "area": "Area (cm²)",
            "x_G": "x_G (cm)",
            "y_G": "y_G (cm)",
            "Ix": "Ix (cm⁴)",
            "Iy": "Iy (cm⁴)",
            "Ixy": "Ixy (cm⁴)",
            "Qx": "Qx (cm³)",
            "Qy": "Qy (cm³)",
            "rx": "rx (cm)",
            "ry": "ry (cm)",
            "core_x": "x nocciolo (cm)",
            "core_y": "y nocciolo (cm)",
            "ellipse_a": "a ellisse (cm)",
            "ellipse_b": "b ellisse (cm)",
            "note": "Note",
        }

        # Configura ogni colonna
        for col in self.columns:
            width, anchor = col_config.get(col, (70, "center"))
            label = header_labels.get(col, col)
            
            if col == "id":
                # Colonna ID: completamente invisibile
                self.tree.column(col, width=0, minwidth=0, stretch=False)
                self.tree.heading(col, text="")
            else:
                # Colonne visibili: larghezza stretta, anchor appropriato, no stretch
                self.tree.column(col, width=width, minwidth=width, anchor=anchor, stretch=False)
                # Heading cliccabile per sorting (inizia sempre con False=crescente)
                self.tree.heading(
                    col, 
                    text=label, 
                    command=lambda c=col: self._on_heading_click(c)
                )

        # Tooltip per le celle
        self.tooltip = TreeviewTooltip(self.tree)

        # OBIETTIVO 1: Calcola larghezza finestra sommando le colonne + margini
        try:
            total_col_width = sum(self.tree.column(col, option="width") for col in self.columns)
            margin = 40  # padx + scrollbar + buffer
            calculated_width = max(total_col_width + margin, 800)
            self.geometry(f"{calculated_width}x550")
            logger.debug(f"Finestra dimensionata: {calculated_width}x550")
        except Exception as e:
            logger.debug(f"Larghezza dinamica fallita: {e}")
            self.geometry("1600x550")

        # Frame per i pulsanti di azione
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(fill="x", padx=8, pady=(0, 8))

        tk.Button(buttons_frame, text="Nuova sezione", command=self._new_section).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Modifica", command=self._edit_section).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Elimina", command=self._delete_section).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Importa CSV", command=self._import_csv).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Esporta CSV", command=self._export_csv).pack(side="left", padx=4)

    def _on_heading_click(self, col: str) -> None:
        """
        Handler per il click su un intestazione: alterna ordinamento crescente/decrescente.
        
        Mantiene stato di toggle per ogni colonna per permettere ordinamenti alternati.
        
        Args:
            col: Nome della colonna cliccata
        """
        # Se è la prima volta che clicchiamo questa colonna, iniziamo con False (crescente)
        current_state = self._sort_state.get(col, False)
        self._sort_state[col] = not current_state
        sort_treeview(self.tree, col, not current_state)

    def _refresh_table(self) -> None:
        """
        Svuota il Treeview e lo ricarica con tutte le sezioni dall'archivio.
        
        Legge i dati da `section.to_dict()` per ottenere tutti i campi, inclusi
        i valori calcolati (area, baricentro, momenti di inerzia, ecc.).
        """
        # Rimuove tutti gli elementi esistenti
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Aggiunge tutte le sezioni come righe nel Treeview
        for section in self.repository.get_all_sections():
            data_dict = section.to_dict()
            # Estrae i valori nell'ordine delle colonne, lasciando vuoto se non presente
            values = [data_dict.get(col, "") for col in self.columns]
            # Usa l'ID della sezione come id della riga (per identificarla dopo)
            self.tree.insert("", "end", iid=section.id, values=values)
        
        logger.debug("Treeview ricaricato con %d sezioni", len(self.tree.get_children()))

    def reload_sections_in_treeview(self) -> None:
        """Public API: ricarica tutte le sezioni nel treeview (chiamabile dopo add/update/delete)."""
        logger.debug("Ricarico sezioni nel Treeview")
        self._refresh_table()

    def _get_selected_section(self) -> Optional[Section]:
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Info", "Seleziona una sezione")
            return None
        return self.repository.find_by_id(selected)

    def _new_section(self) -> None:
        messagebox.showinfo("Nuova", "Compila i campi nella finestra principale e salva.")

    def _edit_section(self) -> None:
        section = self._get_selected_section()
        if not section:
            return
        self.on_edit(section)
        self.destroy()

    def _delete_section(self) -> None:
        section = self._get_selected_section()
        if not section:
            return
        confirm_msg = (
            f"Sei sicuro di voler eliminare la sezione '{section.name}'?\n\n"
            f"Tipo: {section.section_type}\n"
            f"ID: {section.id}\n\n"
            f"Questa operazione non può essere annullata."
        )
        if messagebox.askyesno("Conferma eliminazione", confirm_msg):
            self.repository.delete_section(section.id)
            self.reload_sections_in_treeview()
            messagebox.showinfo("Eliminazione", f"Sezione '{section.name}' eliminata dall'archivio.")
            logger.debug("Sezione eliminata tramite UI: %s", section.id)

    def _import_csv(self) -> None:
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
        self.reload_sections_in_treeview()
        logger.debug("Import CSV completato: %s sezioni aggiunte", added)

    def _export_csv(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Esporta CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not file_path:
            return
        self.serializer.export_to_csv(file_path, self.repository.get_all_sections())
        messagebox.showinfo("Esporta CSV", "Esportazione completata")

