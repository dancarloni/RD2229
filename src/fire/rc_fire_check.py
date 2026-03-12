"""RC fire check – verifica semplificata resistenza al fuoco per sezioni RC.

Implementa il metodo tabellare semplificato per sezioni rettangolari RC
soggette a incendio standard (curva ISO 834).

Riferimenti (pubblici):
- NTC 2018, §3.6.1 – Azioni di incendio (requisiti prestazionali)
- EN 1992-1-2:2004, §5.6 – Simplified calculation method for beams and slabs
- EN 1992-1-2:2004, Table 5.4/5.5 – Axis distance requirements

La tabella dati è caricata da data/fire/axis_distance_table.json.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.fire.curves import iso834_temperature
from src.fire.eligibility import _get_cover_mm, _get_exposure_sides

if TYPE_CHECKING:
    from src.project.schema import GeometryEntry, ProjectModel

logger = logging.getLogger(__name__)

_AXIS_DISTANCE_TABLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "fire", "axis_distance_table.json"
)

_FALLBACK_TABLE: dict[str, dict[str, float]] = {
    "30_3": {"b_min_mm": 80.0, "a_min_mm": 25.0},
    "60_3": {"b_min_mm": 120.0, "a_min_mm": 35.0},
    "90_3": {"b_min_mm": 150.0, "a_min_mm": 45.0},
    "120_3": {"b_min_mm": 200.0, "a_min_mm": 50.0},
}

_cached_table: dict | None = None


def _load_axis_distance_table() -> dict:
    """Carica la tabella axis distance da file JSON, o usa il fallback."""
    global _cached_table
    if _cached_table is not None:
        return _cached_table

    try:
        with open(_AXIS_DISTANCE_TABLE_PATH, encoding="utf-8") as f:
            _cached_table = json.load(f)
            return _cached_table
    except FileNotFoundError:
        logger.debug("Tabella axis distance non trovata; uso valori fallback.")
    except Exception as exc:
        logger.warning("Errore caricamento tabella axis distance: %s", exc)
    _cached_table = _FALLBACK_TABLE
    return _cached_table


def reset_fire_table_cache() -> None:
    """Reset della cache della tabella (utile per i test)."""
    global _cached_table
    _cached_table = None


def _lookup_fire_requirements(
    table: dict,
    element_type: str,
    rating_minutes: int,
    exposure_sides: int,
) -> dict[str, float] | None:
    """Cerca i requisiti minimi dalla tabella, con fallback per tipo elemento.

    Strategia di ricerca:
    1. Tabella per tipo elemento (es. "travi_isostatiche" → "R60")
    2. Chiave legacy "{durata}_{lati}" (es. "60_3")
    3. Durata più conservativa disponibile ≥ richiesta
    """
    rating_key = f"R{rating_minutes}"
    legacy_key = f"{rating_minutes}_{exposure_sides}"

    # Mappa tipo elemento → categoria tabella
    type_map = {
        "beam": "travi_isostatiche",
        "trave": "travi_isostatiche",
        "trave_continua": "travi_continue",
        "continuous_beam": "travi_continue",
        "column": "pilastri",
        "pilastro": "pilastri",
        "slab": "solai",
        "solaio": "solai",
    }

    category = type_map.get(element_type.lower(), "")

    # 1. Cerca per tipo elemento
    if category and category in table:
        cat_table = table[category]
        if rating_key in cat_table:
            return cat_table[rating_key]
        # Cerca durata più vicina ≥ richiesta
        available = []
        for k in cat_table:
            if k.startswith("R") and k[1:].isdigit():
                mins = int(k[1:])
                if mins >= rating_minutes:
                    available.append((mins, k))
        if available:
            available.sort()
            return cat_table[available[0][1]]

    # 2. Chiave legacy
    if legacy_key in table:
        row = table[legacy_key]
        if isinstance(row, dict) and "b_min_mm" in row:
            return row

    # 3. Fallback con durata ≥ richiesta per i lati dati
    suffix = f"_{exposure_sides}"
    usable = []
    for k, v in table.items():
        if k.endswith(suffix) and isinstance(v, dict) and "b_min_mm" in v:
            try:
                mins = int(k.split("_")[0])
                if mins >= rating_minutes:
                    usable.append((mins, v))
            except ValueError:
                continue
    if usable:
        usable.sort()
        return usable[0][1]

    return None


@dataclass
class ElementResultFire:
    """Risultato della verifica al fuoco per un singolo elemento."""

    element_id: str = ""
    status: str = "NOT_VERIFIED"  # "OK" | "KO" | "NOT_VERIFIED" | "SKIPPED"
    metrics: dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


def run_rc_fire_check(
    project: ProjectModel,
    element: GeometryEntry,
) -> ElementResultFire:
    """Esegue la verifica di resistenza al fuoco RC semplificata.

    Metodo: confronto dimensionale (larghezza minima, asse-distanza armatura).
    Se i dati sono insufficienti restituisce status=NOT_VERIFIED con motivazioni.
    """
    messages: list[str] = []
    metrics: dict[str, Any] = {}

    fire_cfg = project.fire
    required_min = fire_cfg.required_rating_minutes
    cover_mm = _get_cover_mm(project, element)
    exp_sides = _get_exposure_sides(project, element)

    # Temperatura ISO 834 a fine durata richiesta
    temp_at_end = iso834_temperature(required_min)
    metrics["iso834_temp_end_celsius"] = round(temp_at_end, 1)
    metrics["required_rating_minutes"] = required_min

    # Larghezza in mm
    units_length = project.code_settings.units_length or "cm"
    b_mm = element.width * (10.0 if units_length == "cm" else 1.0)
    h_mm = element.height * (10.0 if units_length == "cm" else 1.0)

    metrics["b_mm"] = b_mm
    metrics["h_mm"] = h_mm
    metrics["cover_mm"] = cover_mm
    metrics["exposure_sides"] = exp_sides

    # Cerca valori nella tabella
    table = _load_axis_distance_table()
    element_type = getattr(element, "type", getattr(element, "tipo", "beam"))
    row = _lookup_fire_requirements(table, element_type, required_min, exp_sides)

    if row is None:
        messages.append(
            f"Nessun dato tabellare per durata={required_min} min, tipo={element_type}, "
            f"lati={exp_sides}. Compilare data/fire/axis_distance_table.json."
        )
        return ElementResultFire(
            element_id=element.id,
            status="NOT_VERIFIED",
            metrics=metrics,
            messages=messages,
        )

    b_min_mm: float = row.get("b_min_mm", 0.0)
    a_min_mm: float = row.get("a_min_mm", 0.0)
    h_min_mm: float = row.get("h_min_mm", 0.0)

    metrics["b_min_required_mm"] = b_min_mm
    metrics["a_min_required_mm"] = a_min_mm
    if h_min_mm > 0:
        metrics["h_min_required_mm"] = h_min_mm

    # Verifica larghezza (o altezza per solai)
    if h_min_mm > 0:
        ok_dim = h_mm >= h_min_mm
        metrics["ok_dimensione"] = ok_dim
        if ok_dim:
            messages.append(
                f"OK – altezza {h_mm:.1f} mm >= h_min {h_min_mm:.1f} mm (R{required_min})."
            )
        else:
            messages.append(
                f"KO – altezza {h_mm:.1f} mm < h_min {h_min_mm:.1f} mm (R{required_min})."
            )
    else:
        ok_dim = b_mm >= b_min_mm
        metrics["ok_larghezza"] = ok_dim
        if ok_dim:
            messages.append(
                f"OK – larghezza {b_mm:.1f} mm >= b_min {b_min_mm:.1f} mm (R{required_min})."
            )
        else:
            messages.append(
                f"KO – larghezza {b_mm:.1f} mm < b_min {b_min_mm:.1f} mm (R{required_min})."
            )

    # Verifica asse-distanza armatura (copriferro)
    if cover_mm is None:
        ok_a = False
        messages.append("Copriferro non disponibile: verifica asse-distanza non eseguita.")
    else:
        ok_a = cover_mm >= a_min_mm
        metrics["ok_asse_distanza"] = ok_a
        if ok_a:
            messages.append(
                f"OK – copriferro {cover_mm:.1f} mm >= a_min {a_min_mm:.1f} mm (R{required_min})."
            )
        else:
            messages.append(
                f"KO – copriferro {cover_mm:.1f} mm < a_min {a_min_mm:.1f} mm (R{required_min})."
            )

    overall_ok = ok_dim and (cover_mm is not None) and ok_a
    status = "OK" if overall_ok else "KO"

    return ElementResultFire(
        element_id=element.id,
        status=status,
        metrics=metrics,
        messages=messages,
    )


def run_fire_check_standalone(
    element_type: str,
    rating_minutes: int,
    b_mm: float,
    cover_mm: float,
    exposure_sides: int = 3,
) -> dict[str, Any]:
    """Verifica al fuoco standalone (senza ProjectModel).

    Per uso diretto da CLI o da action_repo.

    Returns:
        dict con ok, messages, metrics
    """
    table = _load_axis_distance_table()
    row = _lookup_fire_requirements(table, element_type, rating_minutes, exposure_sides)

    if row is None:
        return {
            "ok": False,
            "messages": [f"Nessun dato tabellare per R{rating_minutes}, tipo={element_type}."],
            "metrics": {},
        }

    b_min = row.get("b_min_mm", 0.0)
    a_min = row.get("a_min_mm", 0.0)
    h_min = row.get("h_min_mm", 0.0)

    ok_dim = (b_mm >= h_min) if h_min > 0 else (b_mm >= b_min)
    ok_a = cover_mm >= a_min

    messages = []
    if ok_dim:
        messages.append(f"OK – dimensione {b_mm:.1f} mm >= minimo {max(b_min, h_min):.1f} mm.")
    else:
        messages.append(f"KO – dimensione {b_mm:.1f} mm < minimo {max(b_min, h_min):.1f} mm.")
    if ok_a:
        messages.append(f"OK – copriferro {cover_mm:.1f} mm >= a_min {a_min:.1f} mm.")
    else:
        messages.append(f"KO – copriferro {cover_mm:.1f} mm < a_min {a_min:.1f} mm.")

    return {
        "ok": ok_dim and ok_a,
        "messages": messages,
        "metrics": {
            "b_min_mm": b_min,
            "a_min_mm": a_min,
            "b_mm": b_mm,
            "cover_mm": cover_mm,
            "rating_minutes": rating_minutes,
        },
    }
