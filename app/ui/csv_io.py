from __future__ import annotations
from typing import List, Tuple
import csv
import logging
from app.domain.models import VerificationInput
from app.ui.verification_table_app import COLUMNS

logger = logging.getLogger(__name__)

NUMERIC_ATTRS = {
    "n_homog",
    "N",
    "Mx",
    "My",
    "Mz",
    "Tx",
    "Ty",
    "At",
    "As_sup",
    "As_inf",
    "d_sup",
    "d_inf",
    "stirrup_step",
    "stirrup_diameter",
}


def _format_value_for_csv(value: object) -> str:
    if isinstance(value, (int, float)):
        return str(value).replace(".", ",")
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return ""
        try:
            f = float(s.replace(",", "."))
            return str(f).replace(".", ",")
        except Exception:
            return s
    return str(value)


def export_csv(path: str, rows: List[VerificationInput], include_header: bool = True) -> None:
    keys = [c[0] for c in COLUMNS]
    header = [c[1] for c in COLUMNS]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter=";")
        if include_header:
            writer.writerow(header)
        for r in rows:
            row = []
            for k in keys:
                raw = getattr(r, _col_to_attr(k))
                row.append(_format_value_for_csv(raw))
            writer.writerow(row)


def _col_to_attr(col: str) -> str:
    mapping = {
        "element": "element_name",
        "section": "section_id",
        "verif_method": "verification_method",
        "mat_concrete": "material_concrete",
        "mat_steel": "material_steel",
        "n": "n_homog",
        "N": "N",
        "Mx": "Mx",
        "My": "My",
        "Mz": "Mz",
        "Tx": "Tx",
        "Ty": "Ty",
        "At": "At",
        "As_p": "As_inf",
        "As": "As_sup",
        "d_p": "d_inf",
        "d": "d_sup",
        "stirrups_step": "stirrup_step",
        "stirrups_diam": "stirrup_diameter",
        "stirrups_mat": "stirrup_material",
        "notes": "notes",
    }
    return mapping[col]


def import_csv(path: str) -> Tuple[List[VerificationInput], int, List[str]]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh, delimiter=";")
            rows = list(reader)
    except Exception as e:
        logger.exception("Import CSV: impossibile leggere/parsare il file '%s': %s", path, e)
        return [], 0, [str(e)]
    if not rows:
        return [], 0, []

    expected_header = [c[1] for c in COLUMNS]
    header = [h.strip() for h in rows[0]]

    # Simple mapping: assume header equals expected or same set
    if set(header) == set(expected_header):
        index_map = [header.index(h) for h in expected_header]
    else:
        # fallback: try to align by subset
        index_map = [header.index(h) if h in header else None for h in expected_header]

    models = []
    errors = []
    for i, row in enumerate(rows[1:], start=2):
        kwargs = {}
        row_bad = False
        for key, idx in zip([c[0] for c in COLUMNS], index_map):
            if idx is None:
                continue
            v = row[idx] if idx < len(row) else ""
            attr = _col_to_attr(key)
            if attr in NUMERIC_ATTRS:
                s = str(v).strip()
                if not s:
                    kwargs[attr] = 0.0
                    continue
                try:
                    kwargs[attr] = float(s.replace(",", "."))
                except Exception:
                    msg = f"Riga {i}: valore numerico non valido per '{key}': '{v}'"
                    errors.append(msg)
                    row_bad = True
                    break
            else:
                kwargs[attr] = v
        if row_bad:
            continue
        try:
            models.append(VerificationInput(**kwargs))
        except Exception as e:
            errors.append(f"Riga {i}: errore creazione modello: {e}")
    imported = len(models)
    skipped = max(0, (len(rows) - 1) - imported)
    return models, skipped, errors
