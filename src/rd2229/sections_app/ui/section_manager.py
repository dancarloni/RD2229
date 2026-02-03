from __future__ import annotations

import logging
from typing import Callable, Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from rd2229.sections_app.models.sections import CSV_HEADERS, Section
from rd2229.sections_app.services.repository import CsvSectionSerializer, SectionRepository

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
    """Ordina il Treeview per colonna. Supporta numeri e stringhe."""
    data = [(tree.set(item, col), item) for item in tree.get_children("")]

    def try_num(value: str):
        try:
            return float(value.replace(",", "."))
        except Exception:
            return value

    data.sort(key=lambda t: try_num(t[0]), reverse=reverse)

    for index, (_, item) in enumerate(data):
        tree.move(item, "", index)

    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


class SectionManager(tk.Toplevel):
    """Finestra di gestione dell'archivio sezioni con colonne complete, sorting e tooltip."""

    def __init__(
        self,
        master: tk.Tk,
        repository: SectionRepository,
        serializer: CsvSectionSerializer,
        on_edit: Callable[[Section], None],
    ) -> None:
        super().__init__(master)
        self.title("Archivio Sezioni - Dettaglio Completo")
        
        # Finestra larga per contenere tutte le colonne strette
        self.geometry("1400x520")
        self.repository = repository
        self.serializer = serializer
        self.on_edit = on_edit

        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        # Frame per il treeview (con scrollbar orizzontale)
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Scrollbar orizzontale
        xscroll = tk.Scrollbar(tree_frame, orient="horizontal")
        xscroll.pack(side="bottom", fill="x")

        # Usa CSV_HEADERS per generare tutte le colonne
        # La colonna "id" la mettiamo per prima ma invisibile
        all_columns = list(CSV_HEADERS)
        self.columns = all_columns

        self.tree = ttk.Treeview(
            tree_frame,
            columns=all_columns,
            show="headings",
            height=14,
            xscrollcommand=xscroll.set,
        )
        xscroll.config(command=self.tree.xview)
        self.tree.pack(fill="both", expand=True)

        # Configurazione colonne: ID invisibile, altre strette
        # Mappa nomi colonne a larghezze suggerite
        col_widths = {
            "id": 0,  # invisibile
            "name": 110,
            "section_type": 100,
            "width": 70,
            "height": 70,
            "outer_width": 80,
            "outer_height": 80,
            "inner_width": 80,
            "inner_height": 80,
            "diameter": 70,
            "flange_width": 80,
            "flange_thickness": 80,
            "web_thickness": 80,
            "web_height": 80,
            "area": 90,
            "x_G": 70,
            "y_G": 70,
            "Ix": 100,
            "Iy": 100,
            "Ixy": 90,
            "Qx": 80,
            "Qy": 80,
            "rx": 70,
            "ry": 70,
            "core_x": 70,
            "core_y": 70,
            "ellipse_a": 70,
            "ellipse_b": 70,
            "note": 140,
        }

        # Header labels con unità di misura
        HEADER_LABELS = {
            "width": "b (cm)",
            "height": "h (cm)",
            "outer_width": "b esterna (cm)",
            "outer_height": "h esterna (cm)",
            "inner_width": "b interna (cm)",
            "inner_height": "h interna (cm)",
            "diameter": "d (cm)",
            "area": "Area (cm²)",
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
            "x_G": "x_G (cm)",
            "y_G": "y_G (cm)",
            "name": "Nome",
            "section_type": "Tipo",
            "note": "Note",
        }

        for col in all_columns:
            w = col_widths.get(col, 70)
            label = HEADER_LABELS.get(col, col)
            if col == "id":
                # Colonna ID: esiste ma invisibile
                self.tree.column(col, width=0, minwidth=0, stretch=False)
                self.tree.heading(col, text="")
            else:
                self.tree.column(col, width=w, minwidth=w, anchor="center", stretch=False)
                # Heading con sorting
                self.tree.heading(col, text=label, command=lambda c=col: sort_treeview(self.tree, c, False))

        # Prova a impostare una larghezza finestra che eviti lo scroll ove possibile
        try:
            margin = 60
            total_width = sum(self.tree.column(col, option="width") for col in all_columns) + margin
            desired_height = 520
            self.geometry(f"{total_width}x{desired_height}")
        except Exception:
            logger.debug("Impossibile calcolare larghezza dinamica; si mantiene larghezza di default")

        # Tooltip
        self.tooltip = TreeviewTooltip(self.tree)

        # Pulsanti
        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=8, pady=(0, 8))

        tk.Button(buttons, text="Nuova sezione", command=self._new_section).pack(side="left", padx=4)
        tk.Button(buttons, text="Modifica sezione", command=self._edit_section).pack(side="left", padx=4)
        tk.Button(buttons, text="Elimina sezione", command=self._delete_section).pack(side="left", padx=4)
        tk.Button(buttons, text="Importa CSV", command=self._import_csv).pack(side="left", padx=4)
        tk.Button(buttons, text="Esporta CSV", command=self._export_csv).pack(side="left", padx=4)

    def _refresh_table(self) -> None:
        # Internal: svuota e ricarica il treeview usando l'ordine delle colonne self.columns
        for item in self.tree.get_children():
            self.tree.delete(item)

        for section in self.repository.get_all_sections():
            data_dict = section.to_dict()
            values = [data_dict.get(h, "") for h in self.columns]
            self.tree.insert("", "end", iid=section.id, values=values)

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
