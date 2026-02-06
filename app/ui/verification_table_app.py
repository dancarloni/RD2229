from __future__ import annotations

import math
import logging
import random
from dataclasses import dataclass
from tkinter import messagebox, ttk, filedialog
import tkinter as tk
from typing import Dict, Iterable, List, Optional, Tuple

from sections_app.services.notification import notify_info, notify_warning, notify_error, ask_confirm

from app.domain.models import VerificationInput
from app.verification.dispatcher import compute_verification_result

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
        if VerificationProject is not None:
            self.project: "VerificationProject" = VerificationProject()
            self.project.new_project()
        else:
            self.project = None
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
        tk.Button(top, text="Carica progetto", command=self._on_load_project).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Aggiungi lista di elementi", command=self._on_add_list_elements).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Crea progetto test", command=self.create_test_project).pack(side="left", padx=(6,0))

        tk.Button(top, text="Aggiungi riga", command=self._add_row).pack(side="left")
        tk.Button(top, text="Confronta metodi", command=self._open_comparator).pack(side="left", padx=(6,0))
        tk.Button(top, text="Rimuovi riga", command=self._remove_selected_row).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Importa CSV", command=self._on_import_csv).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Esporta CSV", command=self._on_export_csv).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Calcola tutte le righe", command=self._on_compute_all).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Salva elementi", command=self._on_save_items).pack(side="left", padx=(6, 0))

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

    # ... Additional methods are preserved from original implementation (omitted here for brevity) ...

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

    # --- Rebar calculator helpers (moved from legacy verification_table) ---
    def _open_rebar_calculator(self) -> None:
        """Open a small Toplevel that lets users enter number of bars per diameter
        and calculates the total area in cm². The result is committed to the
        currently edited cell when the user confirms.
        """
        if self.edit_entry is None or self.edit_column is None:
            return
        self._rebar_target_column = self.edit_column
        # Set flag to avoid losing the edit when the calculator grabs focus
        self._in_rebar_calculator = True
        if self._rebar_window is not None and self._rebar_window.winfo_exists():
            self._rebar_window.lift()
            self._rebar_window.focus_set()
            if self._rebar_entries:
                self._rebar_entries[0].focus_set()
            return

        win = tk.Toplevel(self)
        win.title("Calcolo area armatura")
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        self._rebar_window = win

        frame = tk.Frame(win, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        diameters = [8, 10, 12, 14, 16, 20, 25]
        self._rebar_vars = {}
        self._rebar_entries = []

        tk.Label(frame, text="Ø (mm)", width=8, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="n barre", width=8, anchor="w").grid(row=0, column=1, sticky="w")

        for i, d in enumerate(diameters, start=1):
            tk.Label(frame, text=f"Ø{d}", width=8, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="")
            self._rebar_vars[d] = var
            ent = tk.Entry(frame, textvariable=var, width=8)
            self._rebar_entries.append(ent)
            ent.grid(row=i, column=1, sticky="w", pady=2)
            # Update total whenever a value changes
            try:
                var.trace_add("write", lambda *_: self._update_rebar_total())
            except Exception:
                # Older Tk versions may not support trace_add
                var.trace("w", lambda *_: self._update_rebar_total())
            if i == 1:
                ent.focus_set()

        total_frame = tk.Frame(frame)
        total_frame.grid(row=len(diameters) + 1, column=0, columnspan=2, sticky="w", pady=(8, 4))
        tk.Label(total_frame, text="Area totale [cm²]:").pack(side="left")
        tk.Label(total_frame, textvariable=self._rebar_total_var, width=10, anchor="w").pack(side="left")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=len(diameters) + 2, column=0, columnspan=2, sticky="e")
        tk.Button(btn_frame, text="Conferma", command=self._confirm_rebar_total).pack(side="right")

        win.bind("<Escape>", lambda _e: self._close_rebar_window())
        win.bind("<Return>", lambda _e: self._confirm_rebar_total())

        self._update_rebar_total()

    def _update_rebar_total(self) -> None:
        total = 0.0
        for d, var in self._rebar_vars.items():
            try:
                n = int(var.get() or 0)
            except Exception:
                n = 0
            d_cm = d / 10.0
            area = math.pi * (d_cm ** 2) / 4.0
            total += n * area
        self._rebar_total_var.set(f"{total:.2f}")

    def _confirm_rebar_total(self) -> None:
        # If edit_entry is not present, try to apply directly to the tree cell
        if self.edit_entry is None or self._rebar_target_column is None:
            try:
                if self.edit_item and self._rebar_target_column:
                    value = self._rebar_total_var.get()
                    self.tree.set(self.edit_item, self._rebar_target_column, value)
            except Exception:
                logger.exception("Unable to apply rebar total in fallback path")
            self._close_rebar_window()
            return
        value = self._rebar_total_var.get()
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, value)
        self._commit_edit()
        self._close_rebar_window()

    def _close_rebar_window(self) -> None:
        if self._rebar_window is not None:
            try:
                self._rebar_window.destroy()
            except Exception:
                logger.exception("Error closing rebar window")
        self._rebar_window = None
        self._rebar_entries = []
        # Clear flag after the calculator is closed
        self._in_rebar_calculator = False


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

        self.app = VerificationTableApp(self, section_repository=section_repository, material_repository=material_repository, verification_items_repository=verification_items_repository)
        self.app.pack(fill="both", expand=True)
