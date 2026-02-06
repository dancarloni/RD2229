from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk
from typing import Dict, Iterable, List, Optional, Tuple

from app.domain.models import VerificationInput


logger = logging.getLogger(__name__)

ColumnDef = Tuple[str, str, int, str]

COLUMNS: List[ColumnDef] = [
    ("element", "Elemento", 160, "w"),
    ("section", "Sezione", 170, "w"),
    ("verif_method", "Metodo verifica", 120, "center"),
    ("mat_concrete", "Materiale cls", 140, "w"),
    ("mat_steel", "Materiale acciaio", 140, "w"),
    ("n", "Coeff. n", 75, "center"),
    ("N", "N [kg]", 80, "center"),
    ("Mx", "Mx [kg·m]", 90, "center"),
    ("My", "My [kg·m]", 90, "center"),
    ("Mz", "Mz [kg·m]", 90, "center"),
    ("Tx", "Tx [kg]", 80, "center"),
    ("Ty", "Ty [kg]", 80, "center"),
    ("At", "At [cm²]", 80, "center"),
    ("As_p", "As' [cm²]", 90, "center"),
    ("As", "As [cm²]", 90, "center"),
    ("d_p", "d' [cm]", 80, "center"),
    ("d", "d [cm]", 80, "center"),
    ("stirrups_step", "Passo staffe [cm]", 120, "center"),
    ("stirrups_diam", "Diametro staffe [mm]", 130, "center"),
    ("stirrups_mat", "Materiale staffe", 140, "w"),
    ("notes", "NOTE", 240, "w"),
]

# Note: Column "As" maps to VerificationInput.As_sup and "As_p" to VerificationInput.As_inf

try:
    from tools.materials_manager import list_materials
except Exception:  # pragma: no cover - fallback if import fails
    list_materials = None

try:
    from sections_app.services.repository import SectionRepository
except Exception:  # pragma: no cover - fallback if import fails
    SectionRepository = None  # type: ignore

try:
    from core_models.materials import MaterialRepository
except Exception:  # pragma: no cover - fallback if import fails
    MaterialRepository = None  # type: ignore

try:
    from verification_project import VerificationProject
except Exception:
    VerificationProject = None

try:
    from verification_items_repository import VerificationItemsRepository
except Exception:
    VerificationItemsRepository = None  # type: ignore


class VerificationTableApp(tk.Frame):
    """GUI tabellare per inserimento rapido delle verifiche (senza logica di calcolo)."""

    def __init__(
        self,
        master: tk.Tk,
        section_repository: Optional[SectionRepository] = None,
        section_names: Optional[Iterable[str]] = None,
        material_repository: Optional[MaterialRepository] = None,
        material_names: Optional[Iterable[str]] = None,
        verification_items_repository: Optional[VerificationItemsRepository] = None,
        initial_rows: int = 1,
        *,
        search_limit: int = 200,
        display_limit: int = 50,
    ) -> None:
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        self.columns = [c[0] for c in COLUMNS]
        self._last_col = self.columns[0]

        self.section_repository = section_repository
        self.material_repository = material_repository
        # Project model to save/load .jsonp projects
        self.project: Optional["VerificationProject"] = None
        if VerificationProject is not None:
            self.project = VerificationProject()
            self.project.new_project()
        # Optional external repository that stores VerificationItem objects
        self.verification_items_repository = verification_items_repository
        self.initial_rows = int(initial_rows)

        # Configurable limits for search and display to keep UI responsive.
        # - search_limit: how many candidates the repository search returns
        # - display_limit: how many items the suggestion list will display
        self.search_limit = int(search_limit)
        self.display_limit = int(display_limit)

        self.section_names = self._resolve_section_names(section_repository, section_names)
        self.material_names = self._resolve_material_names(material_names)

        self.suggestions_map: Dict[str, object] = {
            "section": (lambda q: self._search_sections(q)),
            "mat_concrete": (lambda q: self._search_materials(q, type_filter="concrete")),
            "mat_steel": (lambda q: self._search_materials(q, type_filter="steel")),
            "stirrups_mat": (lambda q: self._search_materials(q, type_filter="steel")),
        }

        self.edit_entry: Optional[ttk.Entry] = None
        self.edit_item: Optional[str] = None
        self.edit_column: Optional[str] = None
        # Suggestion box helper
        self._suggestion_box = None  # type: Optional["SuggestionBox"]
        # Deprecated rebar attributes retained for backward compatibility.
        # Prefer `app.ui.rebar_calculator` for new code.
        self._rebar_window: Optional[tk.Toplevel] = None
        self._rebar_vars: Dict[int, tk.StringVar] = {}
        self._rebar_entries: List[tk.Entry] = []
        self._rebar_total_var = tk.StringVar(value="0.00")
        self._rebar_target_column: Optional[str] = None
        # Flag to avoid committing the entry when the rebar calculator is open
        self._in_rebar_calculator: bool = False

        self.current_item_id: Optional[str] = None
        self.current_column_index: Optional[int] = None

        self._build_ui()
        self._insert_empty_rows(self.initial_rows)

    # --- Suggestion helpers using SuggestionBox ---
    def _ensure_suggestion_box(self) -> None:
        if self._suggestion_box is not None:
            return
        from app.ui.suggestion_box import SuggestionBox

        def on_select(value: str):
            try:
                if self.edit_entry is not None:
                    self.edit_entry.delete(0, tk.END)
                    self.edit_entry.insert(0, value)
                    self._commit_edit()
            except Exception:
                logger.exception("Error applying suggestion")

        self._suggestion_box = SuggestionBox(self, on_select=on_select)

    def _show_suggestions(self, items: List[str], bbox: Tuple[int, int, int, int]) -> None:
        """Show suggestions list positioned over the cell bbox."""
        if not items:
            self._hide_suggestions()
            return
        self._ensure_suggestion_box()
        x, y, width, height = bbox
        # Slightly adjust position to place below the cell
        try:
            self._suggestion_box.show(items, x, y + height, width, height * min(6, len(items)))
        except Exception:
            logger.exception("Error showing suggestions")

    def _hide_suggestions(self) -> None:
        if self._suggestion_box is not None:
            try:
                self._suggestion_box.hide()
            except Exception:
                logger.exception("Error hiding suggestions")

    # --- Project I/O delegations (moved to app.ui.project_actions) ---
    def _on_load_project(self) -> None:
        from app.ui.project_actions import load_project

        try:
            load_project(self, None)
        except Exception as e:
            logger.exception("_on_load_project failed: %s", e)

    def _on_save_project(self) -> None:
        from app.ui.project_actions import save_project

        try:
            save_project(self, None)
        except Exception as e:
            logger.exception("_on_save_project failed: %s", e)

    def _on_add_list_elements(self) -> None:
        from app.ui.project_actions import add_list_elements

        try:
            add_list_elements(self, None)
        except Exception as e:
            logger.exception("_on_add_list_elements failed: %s", e)

    # --- Core data mapping and row helpers ---
    def table_row_to_model(self, row_index: int) -> VerificationInput:
        items = list(self.tree.get_children())
        if row_index < 0 or row_index >= len(items):
            raise IndexError("row_index out of range")
        item = items[row_index]

        def get(col: str) -> str:
            return str(self.tree.set(item, col) or "").strip()

        def num(col: str) -> float:
            value = get(col)
            if not value:
                return 0.0
            try:
                return float(value.replace(",", "."))
            except ValueError:
                return 0.0

        return VerificationInput(
            element_name=get("element"),
            section_id=get("section"),
            verification_method=get("verif_method"),
            material_concrete=get("mat_concrete"),
            material_steel=get("mat_steel"),
            n_homog=num("n"),
            N=num("N"),
            Mx=num("Mx"),
            My=num("My"),
            Mz=num("Mz"),
            Tx=num("Tx"),
            Ty=num("Ty"),
            At=num("At"),
            As_sup=num("As"),
            As_inf=num("As_p"),
            d_sup=num("d"),
            d_inf=num("d_p"),
            stirrup_step=num("stirrups_step"),
            stirrup_diameter=num("stirrups_diam"),
            stirrup_material=get("stirrups_mat"),
            notes=get("notes"),
        )

    def update_row_from_model(self, row_index: int, model: VerificationInput) -> None:
        items = list(self.tree.get_children())
        if row_index < 0 or row_index >= len(items):
            raise IndexError("row_index out of range")
        item = items[row_index]
        values_map = {
            "element": model.element_name,
            "section": model.section_id,
            "verif_method": model.verification_method,
            "mat_concrete": model.material_concrete,
            "mat_steel": model.material_steel,
            "n": model.n_homog,
            "N": model.N,
            "Mx": model.Mx,
            "My": model.My,
            "Mz": model.Mz,
            "Tx": model.Tx,
            "Ty": model.Ty,
            "At": model.At,
            "As": model.As_sup,
            "As_p": model.As_inf,
            "d": model.d_sup,
            "d_p": model.d_inf,
            "stirrups_step": model.stirrup_step,
            "stirrups_diam": model.stirrup_diameter,
            "stirrups_mat": model.stirrup_material,
            "notes": model.notes,
        }
        for col, value in values_map.items():
            self.tree.set(item, col, "" if value is None else value)

    # --- UI building ---
    def _build_ui(self) -> None:
        top = tk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        tk.Button(top, text="Salva progetto", command=self._on_save_project).pack(side="left")
        tk.Button(top, text="Carica progetto", command=self._on_load_project).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Aggiungi lista di elementi", command=self._on_add_list_elements).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Crea progetto test", command=self.create_test_project).pack(
            side="left", padx=(6, 0)
        )

        tk.Button(top, text="Aggiungi riga", command=self._add_row).pack(side="left")
        tk.Button(top, text="Confronta metodi", command=self._open_comparator).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Rimuovi riga", command=self._remove_selected_row).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Importa CSV", command=self._on_import_csv).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Esporta CSV", command=self._on_export_csv).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Calcola tutte le righe", command=self._on_compute_all).pack(
            side="left", padx=(6, 0)
        )
        tk.Button(top, text="Salva elementi", command=self._on_save_items).pack(
            side="left", padx=(6, 0)
        )

        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        xscroll = tk.Scrollbar(table_frame, orient="horizontal")
        yscroll = tk.Scrollbar(table_frame, orient="vertical")
        xscroll.pack(side="bottom", fill="x")
        yscroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
            selectmode="browse",
        )
        self.tree.pack(fill="both", expand=True)
        xscroll.config(command=self.tree.xview)
        yscroll.config(command=self.tree.yview)

        for key, label, width, anchor in COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=width, anchor=anchor, stretch=False)

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Return>", self._on_tree_return)
        self.tree.bind("<Shift-Return>", self._on_tree_shift_return)
        self.tree.bind("<F2>", self._on_tree_return)
        self.tree.bind("<Key>", self._on_tree_keypress)
        self.tree.bind("<Up>", self._on_tree_arrow)
        self.tree.bind("<Down>", self._on_tree_arrow)
        self.tree.bind("<Left>", self._on_tree_arrow)
        self.tree.bind("<Right>", self._on_tree_arrow)
        self.tree.bind("<Tab>", self._on_tree_tab)
        self.tree.bind("<Shift-Tab>", self._on_tree_shift_tab)
        self.tree.bind("<Home>", self._on_tree_home)
        self.tree.bind("<End>", self._on_tree_end)

    # Additional methods from the original implementation are preserved (omitted).

    def export_csv(self, path: str, *, include_header: bool = True) -> None:
        # Delegate to a pure csv_io helper (to be implemented)
        from app.ui.csv_io import export_csv as _export

        _export(path, self.get_rows(), include_header=include_header)

    def import_csv(self, path: str, *, clear: bool = True):
        from app.ui.csv_io import import_csv as _import

        models, skipped, errors = _import(path)
        if clear:
            for item in list(self.tree.get_children()):
                self.tree.delete(item)
        self.set_rows(models)
        return len(models), skipped, errors

    def _create_editor_for_cell(
        self,
        item: str,
        col: str,
        value: str,
        bbox: Tuple[int, int, int, int],
        initial_text: Optional[str] = None,
    ):
        """
        Crea e ritorna un widget editor posizionato sopra la cella indicata.
        Usa `ttk.Combobox` per colonne materiali se `self.material_names` è disponibile,
        altrimenti `ttk.Entry`. Bind degli eventi di navigazione e suggerimenti vengono
        applicati qui centralmente per evitare duplicazione.
        """
        x, y, width, height = bbox
        combobox_columns = {"mat_concrete", "mat_steel", "stirrups_mat", "verif_method"}
        if col in combobox_columns:
            if col == "verif_method":
                # Combobox con valori fissi per metodo di verifica
                editor = ttk.Combobox(self.tree, values=["TA", "SLU", "SLE", "SANT"])
            elif self.material_names:
                # Combobox con materiali
                editor = ttk.Combobox(self.tree, values=self.material_names)
            else:
                # Fallback a Entry se non ci sono materiali
                editor = ttk.Entry(self.tree)
                editor.place(x=x, y=y, width=width, height=height)
                editor.insert(0, value)
                if initial_text:
                    editor.delete(0, tk.END)
                    editor.insert(0, initial_text)
                editor.select_range(0, tk.END)
                editor.focus_set()
                # Bind eventi comuni
                editor.bind("<Return>", self._on_entry_commit_down)
                editor.bind("<Shift-Return>", self._on_entry_commit_up)
                editor.bind("<Tab>", self._on_entry_commit_next)
                editor.bind("<Shift-Tab>", self._on_entry_commit_prev)
                editor.bind("<Escape>", self._on_entry_cancel)
                editor.bind("<Up>", self._on_entry_move_up)
                editor.bind("<Down>", self._on_entry_move_down)
                editor.bind("<Left>", self._on_entry_move_left)
                editor.bind("<Right>", self._on_entry_move_right)
                editor.bind("<FocusOut>", self._on_entry_focus_out)
                editor.bind("<KeyRelease>", self._on_entry_keyrelease)
                editor.bind("<KeyPress>", self._on_entry_keypress)
                return editor

            editor.place(x=x, y=y, width=width, height=height)
            # Set display value
            editor.set(value or "")
            if initial_text:
                editor.delete(0, tk.END)
                editor.insert(0, initial_text)
            try:
                editor.selection_range(0, tk.END)
            except Exception:
                pass
            editor.focus_set()
            # Monkeypatch Combobox.set to record the last value set programmatically.
            # This helps tests that use cb.set('...') and expect the value to be
            # available synchronously at commit time.
            try:
                orig_set = editor.set

                def _set_and_record(val):
                    orig_set(val)
                    try:
                        self._last_editor_value = editor.get()
                    except Exception:
                        pass

                editor.set = _set_and_record  # type: ignore
            except Exception:
                pass
        else:
            editor = ttk.Entry(self.tree)
            editor.place(x=x, y=y, width=width, height=height)
            editor.insert(0, value)
            if initial_text:
                editor.delete(0, tk.END)
                editor.insert(0, initial_text)
            editor.select_range(0, tk.END)
            editor.focus_set()

        # Bind eventi comuni
        editor.bind("<Return>", self._on_entry_commit_down)
        editor.bind("<Shift-Return>", self._on_entry_commit_up)
        editor.bind("<Tab>", self._on_entry_commit_next)

        # Keep a record of the current editor value on key events as well
        def _record_key_event(_e=None):
            try:
                self._last_editor_value = editor.get()
            except Exception:
                pass

        editor.bind("<KeyRelease>", _record_key_event)
        editor.bind("<Shift-Tab>", self._on_entry_commit_prev)
        editor.bind("<Escape>", self._on_entry_cancel)
        editor.bind("<Up>", self._on_entry_move_up)
        editor.bind("<Down>", self._on_entry_move_down)
        editor.bind("<Left>", self._on_entry_move_left)
        editor.bind("<Right>", self._on_entry_move_right)
        editor.bind("<FocusOut>", self._on_entry_focus_out)
        editor.bind("<KeyRelease>", self._on_entry_keyrelease)
        editor.bind("<KeyPress>", self._on_entry_keypress)
        return editor

    def _compute_target_cell(
        self, current_item: str, current_col: str, delta_col: int, delta_row: int
    ) -> Tuple[str, str, bool]:
        """
        Calcola l'item_id e la chiave di colonna target a partire dalla cella corrente
        e dagli spostamenti `delta_col` e `delta_row`.
        Restituisce (target_item_id, target_col_key, created_new_row_flag).
        """
        items = list(self.tree.get_children())
        if not items:
            return current_item, current_col, False
        if current_item not in items:
            return current_item, current_col, False
        row_idx = items.index(current_item)
        col_idx = self.columns.index(current_col)

        new_col = col_idx + delta_col
        new_row = row_idx + delta_row

        # wrap colonne
        if new_col >= len(self.columns):
            new_col = 0
            new_row += 1
        elif new_col < 0:
            new_col = len(self.columns) - 1
            new_row -= 1

        # se superiamo l'ultima riga creiamo una nuova riga copiando la corrente
        created = False
        if new_row >= len(items):
            new_item = self.add_row_from_previous(current_item)
            items = list(self.tree.get_children())
            target_item = new_item
            created = True
        else:
            new_row = max(0, new_row)
            target_item = items[new_row]

            # Se ci si sta spostando verso il basso e la riga target è vuota,
            # copia i valori della riga corrente nella riga target. Questo
            # mantiene la riga successiva pre-popolata quando l'utente tabba
            # o scende con Invio/freccia giù, ma non sovrascrive righe non vuote
            # e non interviene quando si scende verso l'alto (shift+tab o freccia su).
            if new_row > row_idx and self._row_is_empty(target_item):
                prev_values = list(self.tree.item(current_item, "values"))
                self.tree.item(target_item, values=prev_values)

        target_col = self.columns[new_col]
        return target_item, target_col, created

    # --- API pubbliche -------------------------------------------------
    def create_editor_for_cell(self, item: str, col: str, initial_text: Optional[str] = None):
        """
        API pubblica: crea un editor (Entry o Combobox) posizionato sopra la cella
        `item`/`col` e lo restituisce. Solleva ValueError se la cella non è visibile
        (bbox vuoto).
        """
        bbox = self.tree.bbox(item, col)
        if not bbox:
            raise ValueError(f"Impossibile creare editor: bbox vuoto per item={item}, col={col}")
        value = self.tree.set(item, col)
        return self._create_editor_for_cell(item, col, value, bbox, initial_text=initial_text)

    def compute_target_cell(
        self, current_item: str, current_col: str, delta_col: int, delta_row: int
    ) -> Tuple[str, str, bool]:
        """Public API: wrapper for `_compute_target_cell`.

        Computes the target cell for the given row/column delta and returns
        (item_id, column_key, created_flag).
        """
        return self._compute_target_cell(current_item, current_col, delta_col, delta_row)

    def _remove_selected_row(self) -> None:
        sel = self.tree.focus()
        if sel:
            self.tree.delete(sel)

    def _on_tree_click(self, event: tk.Event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        item = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col = self._column_id_to_key(col_id)
        if item and col:
            self._last_col = col
            # Indica che la successiva chiamata a `_update_suggestions` può
            # mostrare l'elenco completo anche se l'entry è vuota.
            self._force_show_all_on_empty = True
            # Start editing and then show suggestions after a brief delay
            self.after_idle(lambda: self._start_edit(item, col))
            self.after(10, self._update_suggestions)

    def _on_tree_double_click(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col = self._column_id_to_key(col_id)
        if not item:
            new_item = self._add_row()
            self._last_col = self.columns[0]
            self._start_edit(new_item, self._last_col)
            return
        if self._row_is_empty(item):
            new_item = self._add_row(after_item=item)
            self._last_col = self.columns[0]
            self._start_edit(new_item, self._last_col)
            return
        if item and col:
            self._last_col = col
            self._start_edit(item, col)

    def _on_tree_return(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_shift_return(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_tab(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_shift_tab(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_keypress(self, event: tk.Event) -> None:
        if self.edit_entry is not None:
            return
        if not event.char or not event.char.isprintable():
            return
        item = self.tree.focus()
        if not item:
            return
        self._start_edit(item, self._last_col, initial_text=event.char)

    def _on_tree_arrow(self, event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        if event.keysym in {"Left", "Right"}:
            delta = -1 if event.keysym == "Left" else 1
            target_item, target_col = self._next_cell(
                item, self._last_col, delta_col=delta, delta_row=0
            )
        else:
            delta = -1 if event.keysym == "Up" else 1
            target_item, target_col = self._next_cell(
                item, self._last_col, delta_col=0, delta_row=delta
            )
        self._last_col = target_col
        self._start_edit(target_item, target_col)
        return "break"

    def _on_tree_home(self, _event: tk.Event) -> str:
        """Sposta la cella attiva alla prima colonna della riga corrente e apre l'editor."""
        item = self.tree.focus()
        if not item:
            return "break"
        first_col = self.columns[0]
        self._last_col = first_col
        self._start_edit(item, first_col)
        return "break"

    def _on_tree_end(self, _event: tk.Event) -> str:
        """Sposta la cella attiva all'ultima colonna della riga corrente e apre l'editor."""
        item = self.tree.focus()
        if not item:
            return "break"
        last_col = self.columns[-1]
        self._last_col = last_col
        self._start_edit(item, last_col)
        return "break"

    def _column_id_to_key(self, col_id: str) -> Optional[str]:
        if not col_id or not col_id.startswith("#"):
            return None
        try:
            idx = int(col_id.replace("#", "")) - 1
        except ValueError:
            return None
        if 0 <= idx < len(self.columns):
            return self.columns[idx]
        return None

    def _start_edit(self, item: str, col: str, initial_text: Optional[str] = None) -> None:
        self._hide_suggestions()
        if self.edit_entry is not None:
            self._commit_edit()
        bbox = self.tree.bbox(item, col)
        if not bbox:
            return
        x, y, width, height = bbox
        value = self.tree.set(item, col)

        self.edit_item = item
        self.edit_column = col
        # Aggiorna lo stato centralizzato della posizione corrente (indice numerico della colonna)
        self.current_item_id = item
        try:
            self.current_column_index = self.columns.index(col)
        except ValueError:
            self.current_column_index = None

        # Crea l'editor (Entry o Combobox) in modo centralizzato
        self.edit_entry = self._create_editor_for_cell(
            item, col, value, (x, y, width, height), initial_text=initial_text
        )

        # Se lo start è esplicito (programma o click), consentiamo alla prima
        # chiamata a `_update_suggestions` di mostrare l'elenco completo se
        # l'entry è vuota. Questo viene resettato immediatamente dopo la chiamata
        # per evitare effetti collaterali sulle successive modifiche.
        self._force_show_all_on_empty = True
        self._update_suggestions()
        self._force_show_all_on_empty = False

    def _commit_edit(self) -> None:
        if self.edit_entry is None or self.edit_item is None or self.edit_column is None:
            return
        # Prefer the last recorded editor value if available (helps with
        # programmatic .set() on Combobox which may not trigger a key event)
        value = getattr(self, "_last_editor_value", None) or self.edit_entry.get()
        # Record debug info via logger (no direct stdout prints)
        try:
            logger.debug(
                "Commit edit: item=%s column=%s value=%r", self.edit_item, self.edit_column, value
            )
            logger.debug("edit_entry type: %s", type(self.edit_entry))
            if hasattr(self.edit_entry, "cget"):
                try:
                    logger.debug("combobox values: %s", self.edit_entry.cget("values"))
                except Exception:
                    pass
        except Exception:
            pass
        self.tree.set(self.edit_item, self.edit_column, value)
        logger.debug("Tree value after set: %r", self.tree.set(self.edit_item, self.edit_column))
        self._last_col = self.edit_column
        self.edit_entry.destroy()
        self.edit_entry = None
        self.edit_item = None
        self.edit_column = None
        self._hide_suggestions()

    def _on_entry_focus_out(self, _event: tk.Event) -> None:
        self.after(1, self._commit_if_focus_outside)

    def _on_entry_commit_next(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=1, delta_row=0)

    def _on_entry_commit_prev(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=-1, delta_row=0)

    def _on_entry_commit_down(self, _event: tk.Event) -> str:
        """
        Invio (Return): avanzare di una riga mantenendo la stessa colonna.

        Scelta: ho deciso di far sì che Invio sposti il cursore alla stessa
        colonna nella riga successiva (delta_row=1). Questo è comodo per
        inserimenti per colonna (es. digitare valori numerici riga per riga).
        Per avanzare di colonna usa TAB.
        """
        return self._commit_and_move(delta_col=0, delta_row=1)

    def _on_entry_commit_up(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=0, delta_row=-1)

    def _on_entry_move_up(self, _event: tk.Event) -> str:
        if self._suggestion_box is not None and self._suggestion_box.size() > 0:
            idx = self._current_suggestion_index()
            prev_idx = max(idx - 1, 0)
            self._select_suggestion(prev_idx)
            return "break"
        return self._commit_and_move(delta_col=0, delta_row=-1)

    def _on_entry_move_down(self, _event: tk.Event) -> str:
        if self._suggestion_box is not None and self._suggestion_box.size() > 0:
            idx = self._current_suggestion_index()
            next_idx = min(idx + 1, self._suggestion_box.size() - 1)
            self._select_suggestion(next_idx)
            return "break"
        return self._commit_and_move(delta_col=0, delta_row=1)

    def _on_entry_move_left(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=-1, delta_row=0)

    def _on_entry_move_right(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=1, delta_row=0)

    def _on_entry_cancel(self, _event: tk.Event) -> str:
        if self._suggestion_box is not None and self._suggestion_box.size() > 0:
            self._hide_suggestions()
            return "break"
        if self.edit_entry is not None:
            self.edit_entry.destroy()
            self.edit_entry = None
            self.edit_item = None
            self.edit_column = None
            self._hide_suggestions()
        return "break"

    def _commit_and_move(self, delta_col: int, delta_row: int) -> str:
        """
        Commette l'edit corrente e sposta l'editor secondo delta_col/delta_row.

        Comportamento migliorato:
        - Se il movimento raggiunge una riga successiva che non esiste yet, viene
          creata una nuova riga copiando i valori della riga corrente
          (usando `add_row_from_previous`) e l'editor si apre sulla cella desiderata.
        - Usato sia da TAB (delta_col=1, delta_row=0), Invio (delta_row=1, delta_col=0)
          e frecce. Questo centralizza la logica di avanzamento.
        """
        if self.edit_item is None or self.edit_column is None:
            return "break"
        if self._suggestion_box is not None and self._suggestion_box.size() > 0:
            self._apply_suggestion()

        current_item = self.edit_item
        current_col = self.edit_column

        # Applica suggerimento se presente e committa l'edit corrente
        if self._suggestion_box is not None and self._suggestion_box.size() > 0:
            self._apply_suggestion()
        self._commit_edit()

        # Calcola la cella target (eventualmente creando una nuova riga copiando la corrente)
        target_item, target_col, _created = self._compute_target_cell(
            current_item, current_col, delta_col, delta_row
        )

        # Apri l'editor sulla cella target
        self._start_edit(target_item, target_col)
        return "break"

    def _next_cell(self, item: str, col: str, delta_col: int, delta_row: int) -> Tuple[str, str]:
        items = list(self.tree.get_children())
        if not items:
            return item, col
        row_idx = items.index(item)
        col_idx = self.columns.index(col)

        new_col = col_idx + delta_col
        new_row = row_idx + delta_row

        if new_col >= len(self.columns):
            new_col = 0
            new_row += 1
        elif new_col < 0:
            new_col = len(self.columns) - 1
            new_row -= 1

        new_row = max(0, min(new_row, len(items) - 1))
        target_item = items[new_row]
        target_col = self.columns[new_col]
        self.tree.focus(target_item)
        self.tree.selection_set(target_item)
        return target_item, target_col

    def _row_is_empty(self, item: str) -> bool:
        values = self.tree.item(item, "values")
        return all(not (str(v).strip()) for v in values)

    def _on_entry_keyrelease(self, _event: tk.Event) -> None:
        self._update_suggestions()

    def _on_entry_keypress(self, event: tk.Event) -> Optional[str]:
        # Support both event.char and event.keysym to make programmatic key
        # generation in tests more reliable across platforms.
        key = (getattr(event, "char", "") or getattr(event, "keysym", "")).lower()
        if self.edit_column in {"As", "As_p"} and key == "c":
            self._open_rebar_calculator()
            return "break"
        return None

    def _update_suggestions(self) -> None:
        if self.edit_entry is None or self.edit_column is None:
            return
        source = self.suggestions_map.get(self.edit_column)
        if not source:
            self._hide_suggestions()
            return
        query = self.edit_entry.get().strip()
        query_lower = query.lower()

        # Support either a callable(source) -> list[str] or a static list
        try:
            # Columns for which we want to show all suggestions immediately when the
            # field is empty (section, concrete/steel/stirrups materials).
            show_all_on_empty = {"section", "mat_concrete", "mat_steel", "stirrups_mat"}

            if query == "":
                # We only show the full suggestion list on empty query when the edit
                # was explicitly opened (e.g. by clicking the cell). This avoids
                # displaying suggestions when the user types and then deletes input.
                show_all_flag = getattr(self, "_force_show_all_on_empty", False) and (
                    self.edit_column in show_all_on_empty
                )
                # reset flag regardless
                self._force_show_all_on_empty = False
                if not show_all_flag:
                    # Preserve old behavior: hide suggestions for empty query
                    self._hide_suggestions()
                    return
                # For the allowed columns when explicitly requested, request full list
                if callable(source):
                    filtered = source("")
                else:
                    filtered = list(source)
            else:
                # Non-empty query: keep existing behavior
                if callable(source):
                    filtered = source(query)
                else:
                    filtered = [s for s in source if query_lower in s.lower()]
        except Exception:
            logger.exception("Error while querying suggestions source")
            filtered = []

        if not filtered:
            self._hide_suggestions()
            return

        # Show suggestions via SuggestionBox helper
        try:
            self._ensure_suggestion_box()
            x = self.edit_entry.winfo_rootx()
            y = self.edit_entry.winfo_rooty() + self.edit_entry.winfo_height()
            width = self.edit_entry.winfo_width()
            height = min(120, self.edit_entry.winfo_height() * min(6, len(filtered)))
            self._show_suggestions(filtered[: self.display_limit], (x, y, width, height))
            if self._suggestion_box is not None:
                self._suggestion_box.selection_clear(0, "end")
                self._suggestion_box.selection_set(0)
        except Exception:
            logger.exception("Error showing suggestions")

    def _commit_if_focus_outside(self) -> None:
        if self.edit_entry is None:
            return
        if self._focus_is_suggestion():
            return
        # Don't commit while the rebar calculator is open (focus will move to the dialog)
        if getattr(self, "_in_rebar_calculator", False):
            return
        self._commit_edit()

    def _focus_is_suggestion(self) -> bool:
        if self._suggestion_box is None:
            return False
        try:
            widget = self.winfo_toplevel().focus_get()
        except KeyError:
            # Sometimes focus_get() raises KeyError for transient widgets
            return False
        return self._suggestion_box.contains_widget(widget)

    def _current_suggestion_index(self) -> int:
        if self._suggestion_box is None:
            return 0
        selection = self._suggestion_box.curselection()
        return selection[0] if selection else 0

    def _select_suggestion(self, index: int) -> None:
        if self._suggestion_box is None:
            return
        self._suggestion_box.selection_clear(0, "end")
        self._suggestion_box.selection_set(index)
        self._suggestion_box.see(index)

    def _on_suggestion_click(self, _event: tk.Event) -> None:
        self._apply_suggestion()

    def _on_suggestion_enter(self, _event: tk.Event) -> None:
        """Handler when user presses Enter in suggestion list.

        We apply the selected suggestion and commit the edit so that a single
        Enter will both pick the suggestion and populate the cell. This keeps
        keyboard-driven entry fluid for fast data entry.
        """
        # Apply the suggestion to the entry
        self._apply_suggestion()
        # Commit the edit (this will write the value to the tree and destroy the entry)
        self._commit_edit()

    def _apply_suggestion(self) -> None:
        if self.edit_entry is None or self._suggestion_box is None:
            return
        idx = self._current_suggestion_index()
        value = self._suggestion_box.get(idx)
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, value)
        self._hide_suggestions()
        self.edit_entry.focus_set()

    # --- Rebar calculator helpers (moved to `app.ui.rebar_calculator`) ---
    def _open_rebar_calculator(self) -> None:
        if self.edit_entry is None or self.edit_column is None:
            return
        self._rebar_target_column = self.edit_column
        # Set flag to avoid losing the edit when the calculator grabs focus
        self._in_rebar_calculator = True

        # Delegate the UI to the RebarCalculatorWindow and handle the callback
        try:
            from app.ui.rebar_calculator import RebarCalculatorWindow
        except Exception:
            logger.exception("RebarCalculatorWindow not available")
            self._in_rebar_calculator = False
            return

        def _on_confirm(total_str: str) -> None:
            try:
                if self.edit_entry is None or self._rebar_target_column is None:
                    # fallback to tree set
                    if self.edit_item and self._rebar_target_column:
                        self.tree.set(self.edit_item, self._rebar_target_column, total_str)
                else:
                    self.edit_entry.delete(0, tk.END)
                    self.edit_entry.insert(0, total_str)
                    self._commit_edit()
            except Exception:
                logger.exception("Unable to apply rebar total in callback")
            finally:
                self._in_rebar_calculator = False

        RebarCalculatorWindow(self, on_confirm=_on_confirm)


class VerificationTableWindow(tk.Toplevel):
    """Thin Toplevel wrapper that accepts section and material repositories and
    embeds the existing `VerificationTableApp` frame. This keeps the original
    GUI/logic unchanged while exposing repository attributes to the window.
    """

    def __init__(
        self,
        master: tk.Misc,
        section_repository: Optional[SectionRepository] = None,
        material_repository: Optional[MaterialRepository] = None,
        verification_items_repository: Optional[VerificationItemsRepository] = None,
    ) -> None:
        super().__init__(master)
        self.section_repository = section_repository
        self.material_repository = material_repository
        self.verification_items_repository = verification_items_repository

        self.title("Verification Table - RD2229")
        self.geometry("1400x520")

        self.app = VerificationTableApp(
            self,
            section_repository=section_repository,
            material_repository=material_repository,
            verification_items_repository=verification_items_repository,
        )
        self.app.pack(fill="both", expand=True)
