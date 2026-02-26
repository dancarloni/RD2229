from __future__ import annotations

import csv
import logging

from app.domain.models import VerificationInput  # type: ignore[import]
from app.ui.verification_table_app import COLUMNS  # type: ignore[import]

logger: logging.Logger = logging.getLogger(__name__)

NUMERIC_ATTRS: set[str] = {
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
        s: str = value.strip()
        if not s:
            return ""
        try:
            f = float(s.replace(",", "."))
            return str(f).replace(".", ",")
        except Exception:
            return s
    return str(value)


def export_csv(path: str, rows: list[VerificationInput], include_header: bool = True) -> None:
    keys: list[str] = [c[0] for c in COLUMNS]
    header: list[str] = [c[1] for c in COLUMNS]
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
    mapping: dict[str, str] = {
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


def _row_to_kwargs(
    row: list[str], index_map: list[int | None], i: int
) -> tuple[dict[str, object], str | None]:
    kwargs: dict[str, object] = {}
    for key, idx in zip([c[0] for c in COLUMNS], index_map):
        if idx is None:
            continue
        v: str = row[idx] if idx < len(row) else ""
        attr: str = _col_to_attr(key)
        if attr in NUMERIC_ATTRS:
            s: str = str(v).strip()
            if not s:
                kwargs[attr] = 0.0
                continue
            try:
                kwargs[attr] = float(s.replace(",", "."))
            except Exception:
                return {}, f"Riga {i}: valore numerico non valido per '{key}': '{v}'"
        else:
            kwargs[attr] = v.strip() if isinstance(v, str) else v
    return kwargs, None


def import_csv(path: str) -> tuple[list[VerificationInput], int, list[str]]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh, delimiter=";")
            rows: list[list[str]] = list(reader)
    except Exception as exc:
        logger.exception("Import CSV: impossibile leggere/parsare il file '%s': %s", path, exc)
        return [], 0, [str(exc)]
    if not rows:
        return [], 0, []

    expected_header: list[str] = [c[1] for c in COLUMNS]
    header: list[str] = [h.strip() for h in rows[0]]

    # Simple mapping: assume header equals expected or same set
    index_map: list[int | None]
    if set(header) == set(expected_header):
        index_map = [header.index(h) for h in expected_header]
    else:
        # fallback: try to align by subset
        index_map = [header.index(h) if h in header else None for h in expected_header]

    models = []
    errors = []
    for i, row in enumerate(rows[1:], start=2):
        kwargs, err = _row_to_kwargs(row, index_map, i)
        if err:
            errors.append(err)
            continue
        try:
            models.append(VerificationInput(**kwargs))  # type: ignore[arg-type]
        except Exception as exc:
            errors.append(f"Riga {i}: errore creazione modello: {exc}")
            # pragma: no cover - defensive branch for malformed csv rows (tests cover normal paths)
    imported: int = len(models)
    skipped: int = max(0, (len(rows) - 1) - imported)
    return models, skipped, errors
