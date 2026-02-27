"""RC fire check – verifica semplificata resistenza al fuoco per sezioni RC.

Implementa il metodo tabellare semplificato per sezioni rettangolari RC
soggette a incendio standard (curva ISO 834).

Riferimenti (pubblici):
- NTC 2018, §3.6.1 – Azioni di incendio (requisiti prestazionali)
- EN 1992-1-2:2004, §5.6 – Simplified calculation method for beams and slabs
- EN 1992-1-2:2004, Table 5.4/5.5 – Axis distance requirements
  (NOTA: i valori delle tabelle EN 1992-1-2 non sono liberamente riproducibili;
   i valori qui usati sono parametri placeholder configurabili dall'utente
   tramite data/fire/axis_distance_table.json – vedi TODO)

TODO: Caricare i valori reali da data/fire/axis_distance_table.json
      (da compilare dal professionista in base alle norme applicabili).
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

# ---------------------------------------------------------------------------
# Tabella placeholder asse-distanza minima (axis distance) [mm]
# Chiave: (durata_min, lati_esposti) → {b_min_mm, a_min_mm}
# TODO: sostituire con valori da data/fire/axis_distance_table.json
# ---------------------------------------------------------------------------
_AXIS_DISTANCE_TABLE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "fire", "axis_distance_table.json")

_AXIS_DISTANCE_PLACEHOLDER: dict[str, dict[str, float]] = {
    # Formato chiave: "{durata}_{lati}" (es. "60_3")
    "30_3": {"b_min_mm": 80.0, "a_min_mm": 25.0},
    "60_3": {"b_min_mm": 120.0, "a_min_mm": 35.0},
    "90_3": {"b_min_mm": 150.0, "a_min_mm": 45.0},
    "120_3": {"b_min_mm": 200.0, "a_min_mm": 50.0},
    "30_4": {"b_min_mm": 80.0, "a_min_mm": 25.0},
    "60_4": {"b_min_mm": 120.0, "a_min_mm": 35.0},
    "90_4": {"b_min_mm": 150.0, "a_min_mm": 45.0},
    "120_4": {"b_min_mm": 200.0, "a_min_mm": 50.0},
}


def _load_axis_distance_table() -> dict[str, dict[str, float]]:
    """Carica la tabella axis distance da file JSON, o usa il placeholder."""
    try:
        with open(_AXIS_DISTANCE_TABLE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug("Tabella axis distance non trovata; uso valori placeholder.")
    except Exception as exc:
        logger.warning("Errore caricamento tabella axis distance: %s", exc)
    return _AXIS_DISTANCE_PLACEHOLDER


@dataclass
class ElementResultFire:
    """Risultato della verifica al fuoco per un singolo elemento."""

    element_id: str = ""
    # Status: "OK" | "KO" | "NOT_VERIFIED" | "SKIPPED"
    status: str = "NOT_VERIFIED"
    metrics: dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


def run_rc_fire_check(
    project: ProjectModel,
    element: GeometryEntry,
) -> ElementResultFire:
    """Esegue la verifica di resistenza al fuoco RC semplificata.

    Metodo: confronto dimensionale (larghezza minima, asse-distanza armatura).
    Se i dati sono insufficienti restituisce status=NOT_VERIFIED con motivazioni.

    Args:
        project: Modello del progetto.
        element: Elemento da verificare (deve essere già eleggibile).

    Returns:
        :class:`ElementResultFire` con status, metriche e messaggi.
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

    # Larghezza in mm (converti da cm se necessario)
    units_length = project.code_settings.units_length or "cm"
    b_mm = element.width * (10.0 if units_length == "cm" else 1.0)
    h_mm = element.height * (10.0 if units_length == "cm" else 1.0)

    metrics["b_mm"] = b_mm
    metrics["h_mm"] = h_mm
    metrics["cover_mm"] = cover_mm
    metrics["exposure_sides"] = exp_sides

    # Cerca valori nella tabella
    table = _load_axis_distance_table()
    key = f"{required_min}_{exp_sides}"
    row = table.get(key)

    if row is None:
        # Prova a trovare la durata più vicina disponibile
        available_keys = [k for k in table if k.endswith(f"_{exp_sides}")]
        if not available_keys:
            messages.append(
                f"Nessun dato tabellare per durata={required_min} min, lati={exp_sides}. "
                "Compilare data/fire/axis_distance_table.json con valori normativi appropriati."
            )
            return ElementResultFire(
                element_id=element.id,
                status="NOT_VERIFIED",
                metrics=metrics,
                messages=messages,
            )
        # Usa la durata più conservativa ≥ required_min
        usable = sorted([(int(k.split("_")[0]), k) for k in available_keys if int(k.split("_")[0]) >= required_min])
        if not usable:
            messages.append(f"Durata {required_min} min supera valori tabellari disponibili per {exp_sides} lati.")
            return ElementResultFire(
                element_id=element.id,
                status="NOT_VERIFIED",
                metrics=metrics,
                messages=messages,
            )
        row = table[usable[0][1]]
        messages.append(f"[INFO] Usata durata tabellare {usable[0][0]} min (richiesta: {required_min} min).")

    b_min_mm: float = row.get("b_min_mm", 0.0)
    a_min_mm: float = row.get("a_min_mm", 0.0)

    metrics["b_min_required_mm"] = b_min_mm
    metrics["a_min_required_mm"] = a_min_mm

    # Verifica larghezza
    ok_b = b_mm >= b_min_mm
    metrics["ok_larghezza"] = ok_b

    # Verifica asse-distanza armatura (copriferro)
    if cover_mm is None:
        ok_a = False
        messages.append("Copriferro non disponibile: verifica asse-distanza non eseguita.")
    else:
        ok_a = cover_mm >= a_min_mm
        metrics["ok_asse_distanza"] = ok_a
        if not ok_a:
            messages.append(f"KO – copriferro {cover_mm:.1f} mm < a_min richiesta {a_min_mm:.1f} mm " f"(R{required_min}).")
        else:
            messages.append(f"OK – copriferro {cover_mm:.1f} mm ≥ a_min {a_min_mm:.1f} mm (R{required_min}).")

    if not ok_b:
        messages.append(f"KO – larghezza {b_mm:.1f} mm < b_min richiesta {b_min_mm:.1f} mm (R{required_min}).")
    else:
        messages.append(f"OK – larghezza {b_mm:.1f} mm ≥ b_min {b_min_mm:.1f} mm (R{required_min}).")

    overall_ok = ok_b and (cover_mm is not None) and ok_a
    status = "OK" if overall_ok else "KO"

    return ElementResultFire(
        element_id=element.id,
        status=status,
        metrics=metrics,
        messages=messages,
    )
