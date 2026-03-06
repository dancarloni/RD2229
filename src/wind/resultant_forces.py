"""Resultant forces – forze risultanti dalle pressioni del vento.

Calcola le forze risultanti su zone/elementi strutturali a partire
dalle pressioni e dalle aree tributarie. Output mappabile a CalcInput
(N, Tx, Mx) per integrazione con verifiche strutturali.
"""

from __future__ import annotations

import logging
from typing import Any

from src.wind.outputs import PressureZoneResults, ZoneForce

logger = logging.getLogger(__name__)


def compute_zone_force(
    pressure: PressureZoneResults,
    *,
    tributary_area_m2: float | None = None,
    application_point_m: float = 0.0,
    eccentricity_m: float = 0.0,
) -> ZoneForce:
    """Calcola la forza risultante su una zona dalla pressione netta.

    F = p_net · A_tributaria

    Args:
        pressure: Pressioni sulla zona.
        tributary_area_m2: Area tributaria [m²]. Se None, usa pressure.area_m2.
        application_point_m: Quota di applicazione della forza [m].
        eccentricity_m: Eccentricità orizzontale [m] (±b/4 per insegne).

    Returns:
        ZoneForce con la forza risultante.
    """
    area = tributary_area_m2 if tributary_area_m2 is not None else pressure.area_m2
    if area <= 0:
        return ZoneForce(
            zone_id=pressure.zone_id,
            F_kN=0.0,
            direction="none",
            tributary_area_m2=area,
            application_point_m=application_point_m,
            eccentricity_m=eccentricity_m,
        )

    F = pressure.net_kN_m2 * area
    direction = "pressure" if F >= 0 else "suction"

    return ZoneForce(
        zone_id=pressure.zone_id,
        F_kN=round(F, 4),
        direction=direction,
        tributary_area_m2=area,
        application_point_m=application_point_m,
        eccentricity_m=eccentricity_m,
    )


def compute_resultant_forces(
    pressure_zones: list[PressureZoneResults],
    *,
    default_area_m2: float = 0.0,
    height_m: float = 0.0,
    eccentricity_m: float = 0.0,
    force_application_point_m: float | None = None,
) -> list[ZoneForce]:
    """Calcola le forze risultanti per tutte le zone di pressione.

    Args:
        pressure_zones: Pressioni su tutte le zone.
        default_area_m2: Area tributaria default se non specificata nella zona.
        height_m: Altezza struttura [m] per stimare punti di applicazione.
        eccentricity_m: Eccentricità orizzontale [m] (±b/4 per insegne, CNR-DT 207 G.7).
        force_application_point_m: Punto di applicazione forza [m] (override).

    Returns:
        Lista di ZoneForce.
    """
    forces = []
    for pz in pressure_zones:
        area = pz.area_m2 if pz.area_m2 > 0 else default_area_m2

        if force_application_point_m is not None:
            app_point = force_application_point_m
        elif "roof" in pz.zone_id.lower():
            app_point = height_m
        else:
            app_point = height_m * 0.5

        force = compute_zone_force(
            pz,
            tributary_area_m2=area,
            application_point_m=app_point,
            eccentricity_m=eccentricity_m,
        )
        if abs(force.F_kN) > 0:
            forces.append(force)

    return forces


def sum_horizontal_forces(forces: list[ZoneForce]) -> float:
    """Somma delle forze orizzontali (pressione/depressione su pareti).

    Args:
        forces: Lista di forze risultanti.

    Returns:
        Forza orizzontale totale [kN] (positiva = sopravento).
    """
    total = 0.0
    for f in forces:
        if f.direction in ("pressure", "suction", "drag"):
            total += f.F_kN
    return round(total, 4)


def sum_vertical_forces(forces: list[ZoneForce]) -> float:
    """Somma delle forze verticali (uplift su copertura).

    Args:
        forces: Lista di forze risultanti.

    Returns:
        Forza verticale totale [kN] (positiva = verso il basso).
    """
    total = 0.0
    for f in forces:
        if f.direction in ("uplift",):
            total += f.F_kN
    return round(total, 4)


def compute_base_moment(
    forces: list[ZoneForce],
) -> float:
    """Calcola il momento ribaltante alla base.

    M = Σ (F_i · z_i)

    Args:
        forces: Forze con punti di applicazione.

    Returns:
        Momento alla base [kNm].
    """
    M = 0.0
    for f in forces:
        M += f.F_kN * f.application_point_m
    return round(M, 4)


def forces_to_calc_input(
    forces: list[ZoneForce],
    *,
    include_friction: float = 0.0,
) -> dict[str, float]:
    """Converte le forze risultanti in formato CalcInput.

    Mappa le forze vento a:
    - N: forza assiale (uplift verticale)
    - Tx: taglio orizzontale (somma forze pareti)
    - Mx: momento ribaltante alla base

    Args:
        forces: Forze risultanti.
        include_friction: Forza di attrito aggiuntiva [kN].

    Returns:
        Dict con N, Tx, Mx per CalcInput.
    """
    Tx = sum_horizontal_forces(forces) + include_friction
    N = sum_vertical_forces(forces)
    Mx = compute_base_moment(forces)

    return {
        "N": round(N, 4),
        "Tx": round(Tx, 4),
        "Mx": round(Mx, 4),
    }
