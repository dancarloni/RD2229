"""Zone loader – caricamento zone geografiche NTC2018 per il vento.

Carica i parametri delle zone (vb0, a0, ka) dal file JSON e fornisce
funzioni di lookup per zona geografica.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Percorso default del file zone
_DEFAULT_ZONES_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "wind" / "ntc2018_wind_zones.json"
)


@dataclass
class ZoneParams:
    """Parametri di una zona geografica NTC2018."""

    zone_id: str
    vb0_ms: float  # Velocità base di riferimento [m/s]
    a0_m: float  # Altitudine di inizio riduzione [m]
    ka: float  # Coefficiente riduzione altitudine [1/m]
    description: str = ""
    is_placeholder: bool = True


def load_wind_zones(path: str | Path | None = None) -> dict[str, ZoneParams]:
    """Carica le zone geografiche dal file JSON.

    Args:
        path: Percorso al file JSON. Se None, usa il default.

    Returns:
        Dizionario zone_id → ZoneParams.
    """
    file_path = Path(path) if path is not None else _DEFAULT_ZONES_PATH

    if not file_path.exists():
        logger.warning("File zone vento non trovato: %s", file_path)
        return {}

    with open(file_path, encoding="utf-8") as f:
        raw: dict[str, Any] = json.load(f)

    zones: dict[str, ZoneParams] = {}
    for key, value in raw.items():
        if key.startswith("_"):
            continue
        if not isinstance(value, dict):
            continue

        zones[key] = ZoneParams(
            zone_id=key,
            vb0_ms=float(value.get("vb0_ms", 25.0)),
            a0_m=float(value.get("a0_m", 500.0)),
            ka=float(value.get("ka", 0.010)),
            description=value.get("description", ""),
            is_placeholder=bool(value.get("_placeholder", True)),
        )

    return zones


def get_zone_params(
    zone_id: str,
    zones: dict[str, ZoneParams] | None = None,
    *,
    zones_path: str | Path | None = None,
) -> ZoneParams | None:
    """Restituisce i parametri per una zona geografica.

    Args:
        zone_id: Identificativo zona (es. "1", "3", "6").
        zones: Dizionario zone pre-caricato. Se None, carica dal file.
        zones_path: Percorso al file JSON (usato solo se zones è None).

    Returns:
        ZoneParams o None se zona non trovata.
    """
    if zones is None:
        zones = load_wind_zones(zones_path)

    zp = zones.get(str(zone_id))
    if zp is None:
        logger.warning("Zona vento '%s' non trovata nel database.", zone_id)
        return None

    if zp.is_placeholder:
        logger.warning(
            "Zona '%s' usa valori PLACEHOLDER. Verificare con NTC2018 Tab. 3.3.I.",
            zone_id,
        )

    return zp


def load_coefficients_index(
    coefficients_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Carica l'indice dei file di coefficienti.

    Args:
        coefficients_dir: Directory dei coefficienti. Se None, usa default.

    Returns:
        Contenuto del file index.json.
    """
    if coefficients_dir is None:
        coefficients_dir = (
            Path(__file__).resolve().parent.parent.parent / "data" / "wind" / "coefficients"
        )
    else:
        coefficients_dir = Path(coefficients_dir)

    index_path = coefficients_dir / "index.json"
    if not index_path.exists():
        logger.warning("Indice coefficienti non trovato: %s", index_path)
        return {}

    with open(index_path, encoding="utf-8") as f:
        return json.load(f)


def load_coefficient_file(
    filename: str,
    coefficients_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Carica un file di coefficienti dalla directory.

    Args:
        filename: Nome del file (es. "buildings.json").
        coefficients_dir: Directory dei coefficienti. Se None, usa default.

    Returns:
        Contenuto del file JSON.
    """
    if coefficients_dir is None:
        coefficients_dir = (
            Path(__file__).resolve().parent.parent.parent / "data" / "wind" / "coefficients"
        )
    else:
        coefficients_dir = Path(coefficients_dir)

    file_path = coefficients_dir / filename
    if not file_path.exists():
        logger.warning("File coefficienti non trovato: %s", file_path)
        return {}

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)
