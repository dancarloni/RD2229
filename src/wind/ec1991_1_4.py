"""EN 1991-1-4 wind – calcolo azioni del vento secondo Eurocodice EN 1991-1-4.

Riferimento: EN 1991-1-4:2005 – Eurocode 1: Actions on structures –
Part 1-4: General actions – Wind actions.

NOTA: I valori dei parametri nazionali (National Annex) variano per paese.
      Alcuni valori fondamentali (es. vb,0 della zona geografica) devono essere
      forniti dall'utente tramite i parametri del sito.

TODO: Parametri National Annex italiani da inserire in data/wind/en1991_na_it.json
"""

from __future__ import annotations

import logging
import math

from src.wind.models import BuildingGeom, WindSite
from src.wind.outputs import WindProfilePoint, WindResults

logger = logging.getLogger(__name__)

# Parametri terreno EN 1991-1-4 Table 4.1
# Chiave: categoria → (z0 [m], z_min [m])
_TERRAIN_PARAMS_EN: dict[str, tuple[float, float]] = {
    "0": (0.003, 1.0),  # Sea, coastal
    "I": (0.01, 1.0),  # Lake, flat plain
    "II": (0.05, 2.0),  # Low vegetation, rural
    "III": (0.30, 5.0),  # Regular cover of vegetation, suburban
    "IV": (1.00, 10.0),  # Urban, industrial areas
}

_DEFAULT_CAT = "II"
_VB0_DEFAULT_MS = 25.0  # placeholder


def _terrain_params(category: str) -> tuple[float, float]:
    """Restituisce (z0, z_min) per la categoria di terreno."""
    cat = category.upper()
    if cat not in _TERRAIN_PARAMS_EN:
        logger.warning("Categoria EN '%s' non riconosciuta; uso '%s'.", cat, _DEFAULT_CAT)
        return _TERRAIN_PARAMS_EN[_DEFAULT_CAT]
    return _TERRAIN_PARAMS_EN[cat]


def compute_mean_wind_velocity(
    z: float,
    v_b: float,
    category: str,
) -> float:
    """Velocità media del vento vm(z) secondo EN 1991-1-4 §4.3.

    vm(z) = cr(z) * c0(z) * vb

    dove cr(z) = kr * ln(max(z, z_min) / z0)
    e c0 = 1.0 (terreno piano).

    Args:
        z: Quota [m].
        v_b: Velocità di riferimento di base [m/s].
        category: Categoria di esposizione del terreno.

    Returns:
        Velocità media [m/s].
    """
    z0, z_min = _terrain_params(category)
    z_eff = max(z, z_min)
    # kr calcolato da z0 secondo EN 1991-1-4 eq. 4.5
    kr = 0.19 * (z0 / 0.05) ** 0.07
    cr = kr * math.log(z_eff / z0)
    return cr * v_b


def compute_kinetic_pressure_en(v_ms: float) -> float:
    """Pressione cinetica qb = 0.5 * ρ * vb² [kN/m²].

    ρ = 1.25 kg/m³ (EN 1991-1-4 §4.5 Note 2).
    """
    q_Pa = 0.5 * 1.25 * v_ms**2
    return q_Pa / 1000.0


def run_en1991_1_4_wind(
    site: WindSite,
    building: BuildingGeom,
) -> WindResults:
    """Calcolo azioni del vento secondo EN 1991-1-4.

    Args:
        site: Parametri del sito.
        building: Geometria edificio.

    Returns:
        :class:`WindResults`.
    """
    warnings: list[str] = []

    v_b = site.reference_wind_speed_ms
    if v_b is None:
        v_b = site.extra.get("vb_ms", _VB0_DEFAULT_MS)
        warnings.append(
            f"Velocità base vb non specificata; usato placeholder {v_b} m/s. "
            "Impostare site.reference_wind_speed_ms o site.extra['vb_ms']."
        )

    q_b = compute_kinetic_pressure_en(v_b)

    h = building.height_m
    if h <= 0:
        warnings.append("Altezza edificio non positiva; uso 10 m.")
        h = 10.0

    n_pts = max(5, min(20, int(h / 2)))
    z_values = [h * i / (n_pts - 1) for i in range(1, n_pts + 1)]

    profile: list[WindProfilePoint] = []
    for z in z_values:
        vm = compute_mean_wind_velocity(z, v_b, site.terrain_category)
        qm = compute_kinetic_pressure_en(vm)
        profile.append(WindProfilePoint(z_m=z, v_m_s=round(vm, 3), q_kN_m2=round(qm, 4)))

    # Pressioni sulle zone dell'edificio
    pressure_zones = []
    if building.width_m > 0 and building.depth_m > 0:
        from src.wind.pressure_coefficients import compute_building_pressure_zones
        from src.wind.outputs import PressureZoneResults

        q_at_h = profile[-1].q_kN_m2 if profile else q_b
        zones_data = compute_building_pressure_zones(
            h, building.width_m, building.depth_m, q_at_h,
        )
        for zd in zones_data:
            pressure_zones.append(PressureZoneResults(
                zone_id=zd["zone_id"],
                description=zd["description"],
                cpe=zd["cpe"],
                cpi=zd["cpi"],
                we_kN_m2=zd["we_kN_m2"],
                wi_kN_m2=zd["wi_kN_m2"],
                net_kN_m2=zd["net_kN_m2"],
            ))

    return WindResults(
        method="EN1991_1_4",
        v_b_ms=round(v_b, 3),
        v_ref_ms=round(v_b, 3),
        q_b_kN_m2=round(q_b, 4),
        velocity_profile=profile,
        pressure_zones=pressure_zones,
        warnings=warnings,
        extra={
            "terrain_category": site.terrain_category,
            "note": "EN 1991-1-4 – parametri National Annex da verificare",
        },
    )
