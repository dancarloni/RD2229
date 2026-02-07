from __future__ import annotations

import json
import logging
from typing import List, Optional, Tuple

from app.domain.models import VerificationInput  # type: ignore[import]
from sections_app.services.notification import notify_error, notify_info

logger = logging.getLogger(__name__)


def _elem_dict_to_input(e: dict) -> VerificationInput:
    """Map a flexible element dict into VerificationInput."""
    try:
        return VerificationInput(
            element_name=e.get("name") or e.get("id") or "",
            section_id=e.get("section_id") or e.get("sec_id") or e.get("section") or "",
            verification_method=e.get("method") or e.get("verification_method") or "TA",
            material_concrete=e.get("cls_id") or e.get("material_concrete") or "",
            material_steel=e.get("steel_id") or e.get("material_steel") or "",
            n_homog=(float(e.get("coeff_n", e.get("n_homog", 15.0))) if e.get("coeff_n", None) is not None else 15.0),
            N=float(e.get("N", 0.0)) if e.get("N", None) is not None else 0.0,
            Mx=(
                float(e.get("Mx", e.get("M", 0.0))) if e.get("Mx", None) is not None or e.get("M", None) is not None else 0.0
            ),
            My=float(e.get("My", 0.0)) if e.get("My", None) is not None else 0.0,
            Mz=float(e.get("Mz", 0.0)) if e.get("Mz", None) is not None else 0.0,
            Tx=float(e.get("Tx", 0.0)) if e.get("Tx", None) is not None else 0.0,
            Ty=(
                float(e.get("Ty", e.get("T", 0.0))) if e.get("Ty", None) is not None or e.get("T", None) is not None else 0.0
            ),
            At=float(e.get("At", 0.0)) if e.get("At", None) is not None else 0.0,
            As_sup=(
                float(e.get("As", e.get("As_sup", 0.0)))
                if e.get("As", None) is not None or e.get("As_sup", None) is not None
                else 0.0
            ),
            As_inf=(
                float(e.get("As_p", e.get("As_inf", 0.0)))
                if e.get("As_p", None) is not None or e.get("As_inf", None) is not None
                else 0.0
            ),
            d_sup=(
                float(e.get("d", e.get("d_sup", 4.0)))
                if e.get("d", None) is not None or e.get("d_sup", None) is not None
                else 4.0
            ),
            d_inf=(
                float(e.get("d_p", e.get("d_inf", 4.0)))
                if e.get("d_p", None) is not None or e.get("d_inf", None) is not None
                else 4.0
            ),
            stirrup_step=(
                float(e.get("passo_staffe", e.get("stirrup_step", 0.0)))
                if e.get("passo_staffe", None) is not None or e.get("stirrup_step", None) is not None
                else 0.0
            ),
            stirrup_diameter=(
                float(e.get("stirrups_diam", e.get("stirrup_diameter", 0.0)))
                if e.get("stirrups_diam", None) is not None or e.get("stirrup_diameter", None) is not None
                else 0.0
            ),
            stirrup_material=e.get("stirrups_mat", e.get("stirrup_material", "")) or "",
            notes=e.get("notes", "") or "",
        )
    except Exception as ex:
        logger.exception("Error mapping element dict to VerificationInput: %s", ex)
        raise


def load_project(app_obj, path: Optional[str]) -> Tuple[int, List[str]]:
    """Load project file (jsonp) and add elements to the app's table.

    Returns (imported_count, errors)
    """
    if app_obj.project is None:
        notify_error("Carica progetto", "Modulo progetto non disponibile", source="verification_table")
        return 0, ["No project module"]
    try:
        if path is None:
            from tkinter import filedialog

            path = filedialog.askopenfilename(filetypes=[("JSONP", "*.jsonp")])
            if not path:
                return 0, []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        imported = 0
        errors = []
        for el in data.get("elements") or []:
            try:
                inp = _elem_dict_to_input(el)
                item = app_obj._add_row()
                app_obj.update_row_from_model(app_obj.tree.index(item), inp)
                imported += 1
            except Exception as e:
                logger.exception("Error importing element: %s", e)
                errors.append(str(e))
        if errors:
            notify_error(
                "Carica progetto",
                f"Errore caricamento progetto: {errors}",
                source="verification_table",
            )
        else:
            notify_info("Carica progetto", f"Progetto caricato: {path}", source="verification_table")
        return imported, errors
    except Exception as e:
        logger.exception("Errore load_project: %s", e)
        notify_error("Carica progetto", f"Errore caricamento progetto: {e}", source="verification_table")
        return 0, [str(e)]


def save_project(app_obj, path: Optional[str]) -> Tuple[bool, str]:
    """Save current app rows into project file. Returns (ok, path_or_error)."""
    if app_obj.project is None:
        notify_error("Salva progetto", "Modulo progetto non disponibile", source="verification_table")
        return False, "no_project"
    try:
        if path is None:
            from tkinter import filedialog

            path = filedialog.asksaveasfilename(defaultextension=".jsonp", filetypes=[("JSONP", "*.jsonp")])
            if not path:
                return False, "aborted"
        rows = app_obj.get_rows()
        elems = []
        for idx, r in enumerate(rows, start=1):
            el = {
                "id": f"E{idx:03d}",
                "name": r.element_name,
                "section_id": r.section_id,
                "cls_id": r.material_concrete,
                "steel_id": r.material_steel,
                "method": r.verification_method,
                "N": r.N,
                "Mx": r.Mx,
                "My": r.My,
                "Mz": r.Mz,
                "Tx": r.Tx,
                "Ty": r.Ty,
                "At": r.At,
                "coeff_n": r.n_homog,
                "As": r.As_sup,
                "As_p": r.As_inf,
                "d": r.d_sup,
                "d_p": r.d_inf,
                "passo_staffe": r.stirrup_step,
                "stirrups_diam": r.stirrup_diameter,
                "stirrups_mat": r.stirrup_material,
                "notes": r.notes,
            }
            elems.append(el)
        app_obj.project.elements = elems
        app_obj.project.save_to_file(path)
        notify_info("Salva progetto", f"Progetto salvato: {path}", source="verification_table")
        return True, path
    except Exception as e:
        logger.exception("Errore save_project: %s", e)
        notify_error("Salva progetto", f"Errore salvataggio progetto: {e}", source="verification_table")
        return False, str(e)


def add_list_elements(app_obj, path: Optional[str]) -> Tuple[int, List[str]]:
    """Add a list of elements to the current project/table from a .jsonp file."""
    if app_obj.project is None:
        notify_error(
            "Aggiungi lista di elementi",
            "Modulo progetto non disponibile",
            source="verification_table",
        )
        return 0, ["no_project"]
    try:
        if path is None:
            from tkinter import filedialog

            path = filedialog.askopenfilename(filetypes=[("JSONP", "*.jsonp")])
            if not path:
                return 0, []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        new_elems = 0
        errors = []
        for el in data.get("elements") or []:
            try:
                inp = _elem_dict_to_input(el)
                item = app_obj._add_row()
                app_obj.update_row_from_model(app_obj.tree.index(item), inp)
                new_elems += 1
            except Exception as e:
                logger.exception("Error adding element from list: %s", e)
                errors.append(str(e))
        notify_info(
            "Aggiungi lista di elementi",
            f"Aggiunti elementi: {new_elems}",
            source="verification_table",
        )
        return new_elems, errors
    except Exception as e:
        logger.exception("Errore add_list_elements: %s", e)
        notify_error("Aggiungi lista di elementi", f"Errore apertura file: {e}", source="verification_table")
        return 0, [str(e)]
