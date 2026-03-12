"""Pressure coefficients – cp_e per edifici a pianta rettangolare.

Calcolo dei coefficienti di pressione esterna secondo EN 1991-1-4 §7.2.
Supporta pareti verticali e coperture (piane, monofalda, a due falde).
I coefficienti sono caricati da data/wind/coefficients/buildings.json
con possibilità di override utente via extra dict.
"""

from __future__ import annotations

import logging
from typing import Any

from src.wind.zone_loader import load_coefficient_file

logger = logging.getLogger(__name__)

# Dati in-memory (caricati al primo uso)
_BUILDINGS_DATA: dict[str, Any] | None = None


def _get_buildings_data() -> dict[str, Any]:
    """Carica e cache i dati edifici dal JSON."""
    global _BUILDINGS_DATA
    if _BUILDINGS_DATA is None:
        _BUILDINGS_DATA = load_coefficient_file("buildings.json")
    return _BUILDINGS_DATA


def _interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    """Interpolazione lineare con clamp agli estremi."""
    if not xs or not ys or len(xs) != len(ys):
        return 0.0
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


# ---------------------------------------------------------------------------
# Pareti verticali
# ---------------------------------------------------------------------------


def get_wall_cpe(
    h_m: float,
    d_m: float,
    zone: str,
    *,
    area_m2: float = 10.0,
    override: float | None = None,
) -> float:
    """Coefficiente di pressione esterna cp_e per pareti di edifici.

    Args:
        h_m: Altezza edificio [m].
        d_m: Profondità edificio nella direzione del vento [m].
        zone: Zona della parete ("D", "E", "A", "B", "C").
        area_m2: Area di riferimento [m²] (cp_e,10 per A≥10, cp_e,1 per A≤1).
        override: Valore di override utente (se specificato, ignora tabella).

    Returns:
        Coefficiente cp_e (positivo = pressione, negativo = depressione).
    """
    if override is not None:
        return override

    data = _get_buildings_data()
    walls = data.get("walls", {})
    h_d_ratios = walls.get("h_d_ratios", [0.25, 1.0, 5.0])
    zones_data = walls.get("zones", {})

    zone_upper = zone.upper()
    if zone_upper not in zones_data:
        logger.warning("Zona parete '%s' non riconosciuta; uso cp_e=0.", zone)
        return 0.0

    values = zones_data[zone_upper].get("values", [])
    h_d = h_m / d_m if d_m > 0 else 1.0

    cpe_10 = _interpolate(h_d, h_d_ratios, values)

    # Correzione per area < 10 m² (EC1 §7.2.1 Note 1)
    # cp_e = cp_e,1 - (cp_e,1 - cp_e,10) * log10(A) per 1 ≤ A ≤ 10
    if area_m2 < 10.0 and zone_upper in ("A",):
        # Solo per zone con differenza significativa cp_e,1 vs cp_e,10
        import math

        cpe_1 = cpe_10 * 1.17  # Approssimazione cp_e,1/cp_e,10 ≈ 1.17 per zona A
        if area_m2 <= 1.0:
            return cpe_1
        return cpe_1 - (cpe_1 - cpe_10) * math.log10(area_m2)

    return cpe_10


def get_all_wall_cpe(
    h_m: float,
    d_m: float,
    *,
    area_m2: float = 10.0,
    overrides: dict[str, float] | None = None,
) -> dict[str, float]:
    """Tutti i cp_e per le pareti di un edificio.

    Returns:
        Dict zona → cp_e per D, E, A, B, C.
    """
    overrides = overrides or {}
    result = {}
    for zone in ("D", "E", "A", "B", "C"):
        result[zone] = get_wall_cpe(
            h_m,
            d_m,
            zone,
            area_m2=area_m2,
            override=overrides.get(zone),
        )
    return result


# ---------------------------------------------------------------------------
# Coperture
# ---------------------------------------------------------------------------


def get_flat_roof_cpe(
    zone: str,
    *,
    area_m2: float = 10.0,
    override: float | None = None,
) -> float:
    """Coefficiente cp_e per copertura piana (EC1 Table 7.2, sharp eaves).

    Args:
        zone: Zona della copertura ("F", "G", "H", "I").
        area_m2: Area di riferimento [m²].
        override: Override utente.

    Returns:
        cp_e (tipicamente negativo = depressione).
    """
    if override is not None:
        return override

    data = _get_buildings_data()
    flat_roof = data.get("flat_roof", {})
    zones_data = flat_roof.get("zones", {})

    zone_upper = zone.upper()
    if zone_upper not in zones_data:
        logger.warning("Zona copertura piana '%s' non riconosciuta.", zone)
        return 0.0

    zd = zones_data[zone_upper]
    if area_m2 >= 10.0:
        return zd.get("cp_e_10", zd.get("cp_e_10_min", 0.0))
    elif area_m2 <= 1.0:
        return zd.get("cp_e_1", zd.get("cp_e_10", 0.0))
    else:
        import math

        cpe_10 = zd.get("cp_e_10", zd.get("cp_e_10_min", 0.0))
        cpe_1 = zd.get("cp_e_1", cpe_10)
        return cpe_1 - (cpe_1 - cpe_10) * math.log10(area_m2)


def get_pitched_roof_cpe(
    roof_angle_deg: float,
    zone: str,
    *,
    windward: bool = True,
    override: float | None = None,
) -> tuple[float, float]:
    """Coefficiente cp_e per copertura inclinata a due falde (EC1 Table 7.4).

    Args:
        roof_angle_deg: Angolo di inclinazione [°].
        zone: Zona ("F", "G", "H" sopravento; "I", "J" sottovento).
        windward: True se falda sopravento.
        override: Override utente (restituito come (override, override)).

    Returns:
        Tupla (cp_e_min, cp_e_max) per la zona. Per coperture con angoli bassi,
        cp_e può essere sia positivo che negativo.
    """
    if override is not None:
        return (override, override)

    data = _get_buildings_data()
    pitched = data.get("pitched_roof", {})
    angles = pitched.get("angles_deg", [5, 15, 30, 45, 60, 75])

    zone_upper = zone.upper()

    if windward:
        ww = pitched.get("windward_zones", {})
        if zone_upper not in ww:
            logger.warning("Zona copertura '%s' non trovata (sopravento).", zone)
            return (0.0, 0.0)
        cp_min = _interpolate(roof_angle_deg, angles, ww[zone_upper].get("cp_e_10_min", []))
        cp_max = _interpolate(roof_angle_deg, angles, ww[zone_upper].get("cp_e_10_max", []))
    else:
        lw = pitched.get("leeward_zones", {})
        if zone_upper not in lw:
            logger.warning("Zona copertura '%s' non trovata (sottovento).", zone)
            return (0.0, 0.0)
        cp_val = _interpolate(roof_angle_deg, angles, lw[zone_upper].get("cp_e_10", []))
        cp_min = cp_val
        cp_max = cp_val

    return (cp_min, cp_max)


def compute_building_pressure_zones(
    h_m: float,
    b_m: float,
    d_m: float,
    q_p_kN_m2: float,
    *,
    roof_angle_deg: float = 0.0,
    cpi_values: tuple[float, float] = (0.2, -0.2),
    overrides: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Calcola le pressioni su tutte le zone di un edificio.

    Args:
        h_m: Altezza edificio [m].
        b_m: Larghezza (perpendicolare al vento) [m].
        d_m: Profondità (parallela al vento) [m].
        q_p_kN_m2: Pressione di picco [kN/m²].
        roof_angle_deg: Angolo copertura [°] (0 = piano).
        cpi_values: (cp_i_pos, cp_i_neg) per pressione interna.
        overrides: Override cp_e per zona {zona: valore}.

    Returns:
        Lista di dict con zone_id, cpe, cpi, we, wi, net per ogni zona.
    """
    overrides = overrides or {}
    results = []

    # Pareti
    wall_cpes = get_all_wall_cpe(h_m, d_m, overrides=overrides)
    for zone_id, cpe in wall_cpes.items():
        for cpi in cpi_values:
            we = cpe * q_p_kN_m2
            wi = cpi * q_p_kN_m2
            results.append(
                {
                    "zone_id": f"wall_{zone_id}_cpi{cpi:+.1f}",
                    "description": f"Parete {zone_id} (cp_i={cpi:+.1f})",
                    "cpe": cpe,
                    "cpi": cpi,
                    "we_kN_m2": round(we, 4),
                    "wi_kN_m2": round(wi, 4),
                    "net_kN_m2": round(we - wi, 4),
                }
            )

    # Copertura
    if abs(roof_angle_deg) < 5.0:
        # Copertura piana
        for zone in ("F", "G", "H", "I"):
            cpe = get_flat_roof_cpe(zone, override=overrides.get(f"roof_{zone}"))
            for cpi in cpi_values:
                we = cpe * q_p_kN_m2
                wi = cpi * q_p_kN_m2
                results.append(
                    {
                        "zone_id": f"roof_{zone}_cpi{cpi:+.1f}",
                        "description": f"Copertura piana {zone} (cp_i={cpi:+.1f})",
                        "cpe": cpe,
                        "cpi": cpi,
                        "we_kN_m2": round(we, 4),
                        "wi_kN_m2": round(wi, 4),
                        "net_kN_m2": round(we - wi, 4),
                    }
                )
    else:
        # Copertura inclinata
        for zone in ("F", "G", "H"):
            cp_min, cp_max = get_pitched_roof_cpe(
                roof_angle_deg,
                zone,
                windward=True,
                override=overrides.get(f"roof_{zone}"),
            )
            for cpi in cpi_values:
                for label, cpe in [("min", cp_min), ("max", cp_max)]:
                    we = cpe * q_p_kN_m2
                    wi = cpi * q_p_kN_m2
                    results.append(
                        {
                            "zone_id": f"roof_ww_{zone}_{label}_cpi{cpi:+.1f}",
                            "description": f"Copertura sopravento {zone} ({label}, cp_i={cpi:+.1f})",
                            "cpe": cpe,
                            "cpi": cpi,
                            "we_kN_m2": round(we, 4),
                            "wi_kN_m2": round(wi, 4),
                            "net_kN_m2": round(we - wi, 4),
                        }
                    )

        for zone in ("I", "J"):
            cp_min, cp_max = get_pitched_roof_cpe(
                roof_angle_deg,
                zone,
                windward=False,
                override=overrides.get(f"roof_{zone}"),
            )
            for cpi in cpi_values:
                we = cp_min * q_p_kN_m2
                wi = cpi * q_p_kN_m2
                results.append(
                    {
                        "zone_id": f"roof_lw_{zone}_cpi{cpi:+.1f}",
                        "description": f"Copertura sottovento {zone} (cp_i={cpi:+.1f})",
                        "cpe": cp_min,
                        "cpi": cpi,
                        "we_kN_m2": round(we, 4),
                        "wi_kN_m2": round(wi, 4),
                        "net_kN_m2": round(we - wi, 4),
                    }
                )

    return results
