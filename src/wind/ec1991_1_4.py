"""EN 1991-1-4 wind – calcolo azioni del vento secondo Eurocodice EN 1991-1-4.

Riferimento: EN 1991-1-4:2005 – Eurocode 1: Actions on structures –
Part 1-4: General actions – Wind actions.

Supporta caricamento parametri National Annex italiano da
data/wind/en1991_na_it.json (categorie terreno, zone, ecc.).
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

from src.wind.models import BuildingGeom, WindSite
from src.wind.outputs import PressureZoneResults, WindProfilePoint, WindResults

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
_VB0_DEFAULT_MS = 25.0
_RHO_AIR = 1.25  # kg/m³

# National Annex cache
_na_data: dict[str, Any] | None = None
_NA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "wind" / "en1991_na_it.json"


def _load_national_annex(path: Path | None = None) -> dict[str, Any]:
    """Carica il National Annex italiano.

    Args:
        path: Percorso del file JSON. Default: data/wind/en1991_na_it.json.

    Returns:
        Dizionario con i parametri NA.
    """
    global _na_data
    if _na_data is not None:
        return _na_data

    na_path = path or _NA_PATH
    if na_path.exists():
        with open(na_path, encoding="utf-8") as f:
            _na_data = json.load(f)
        logger.info("Caricato NA italiano da %s", na_path)
    else:
        logger.warning("NA italiano non trovato: %s. Uso parametri default.", na_path)
        _na_data = {}
    return _na_data


def reset_na_cache() -> None:
    """Resetta la cache del National Annex (utile per test)."""
    global _na_data
    _na_data = None


def get_na_exposure_category(category: str) -> dict[str, Any] | None:
    """Restituisce i parametri NA per una categoria di esposizione.

    Args:
        category: Categoria di esposizione (es. "I", "II", "III", "IV", "V").

    Returns:
        Dizionario con kr, z0_m, z_min_m, description, oppure None.
    """
    na = _load_national_annex()
    cats = na.get("exposure_categories", {})
    return cats.get(category)


def get_na_zone(zone_id: str) -> dict[str, Any] | None:
    """Restituisce i parametri NA per una zona geografica.

    Args:
        zone_id: Identificatore zona (es. "1", "2", ..., "9").

    Returns:
        Dizionario con vb0_ms, a0_m, ka, description, oppure None.
    """
    na = _load_national_annex()
    zones = na.get("zones", {})
    return zones.get(zone_id)


def _terrain_params(category: str) -> tuple[float, float]:
    """Restituisce (z0, z_min) per la categoria di terreno.

    Cerca prima nel National Annex (exposure_categories), poi
    nei parametri EN standard.
    """
    cat = category.upper()

    # Prova NA italiano (categorie esposizione I-V)
    na_cat = get_na_exposure_category(cat)
    if na_cat:
        return na_cat["z0_m"], na_cat["z_min_m"]

    # Fallback EN standard
    if cat not in _TERRAIN_PARAMS_EN:
        logger.warning("Categoria EN '%s' non riconosciuta; uso '%s'.", cat, _DEFAULT_CAT)
        return _TERRAIN_PARAMS_EN[_DEFAULT_CAT]
    return _TERRAIN_PARAMS_EN[cat]


def _get_kr(z0: float, category: str) -> float:
    """Restituisce il fattore kr.

    Cerca nel NA italiano; se non trovato, calcola da EN 1991-1-4 eq. 4.5.
    """
    na_cat = get_na_exposure_category(category.upper())
    if na_cat and "kr" in na_cat:
        return na_cat["kr"]
    return 0.19 * (z0 / 0.05) ** 0.07


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
    kr = _get_kr(z0, category)
    cr = kr * math.log(z_eff / z0)
    return cr * v_b


def compute_peak_velocity_pressure(
    z: float,
    v_b: float,
    category: str,
) -> float:
    """Pressione di picco della velocità qp(z) secondo EN 1991-1-4 §4.5.

    qp(z) = [1 + 7·Iv(z)] × 0.5 × ρ × vm²(z)

    Args:
        z: Quota [m].
        v_b: Velocità di base [m/s].
        category: Categoria di esposizione.

    Returns:
        Pressione di picco qp(z) [kN/m²].
    """
    z0, z_min = _terrain_params(category)
    z_eff = max(z, z_min)
    kr = _get_kr(z0, category)
    cr = kr * math.log(z_eff / z0)
    vm = cr * v_b

    # Iv(z) = kI / ln(z_eff / z0), kI = 1.0
    iv = 1.0 / math.log(z_eff / z0)

    qp_Pa = (1.0 + 7.0 * iv) * 0.5 * _RHO_AIR * vm**2
    return qp_Pa / 1000.0


def compute_kinetic_pressure_en(v_ms: float) -> float:
    """Pressione cinetica qb = 0.5 * ρ * vb² [kN/m²].

    ρ = 1.25 kg/m³ (EN 1991-1-4 §4.5 Note 2).
    """
    q_Pa = 0.5 * _RHO_AIR * v_ms**2
    return q_Pa / 1000.0


def compute_base_velocity(
    zone_id: str | None = None,
    altitude_m: float = 0.0,
    v_b0_override: float | None = None,
) -> float:
    """Calcola la velocità di base vb dal NA italiano.

    vb = vb,0                              per a_s ≤ a0
    vb = vb,0 + ka × (a_s - a0)           per a_s > a0

    Args:
        zone_id: ID zona geografica (es. "1"..."9").
        altitude_m: Altitudine del sito [m s.l.m.].
        v_b0_override: Override esplicito della velocità base [m/s].

    Returns:
        Velocità di base vb [m/s].
    """
    if v_b0_override is not None:
        return v_b0_override

    if zone_id is None:
        return _VB0_DEFAULT_MS

    zone = get_na_zone(zone_id)
    if zone is None:
        logger.warning(
            "Zona NA '%s' non trovata; uso vb,0 default = %.1f m/s", zone_id, _VB0_DEFAULT_MS
        )
        return _VB0_DEFAULT_MS

    vb0 = zone["vb0_ms"]
    a0 = zone["a0_m"]
    ka = zone["ka"]

    if altitude_m <= a0:
        return vb0
    return vb0 + ka * (altitude_m - a0)


def run_en1991_1_4_wind(
    site: WindSite,
    building: BuildingGeom,
) -> WindResults:
    """Calcolo azioni del vento secondo EN 1991-1-4 con NA italiano.

    Args:
        site: Parametri del sito.
        building: Geometria edificio.

    Returns:
        :class:`WindResults`.
    """
    warnings: list[str] = []

    # Velocità di base
    zone_id = site.extra.get("zone_id") if site.extra else None
    altitude = site.extra.get("altitude_m", 0.0) if site.extra else 0.0

    v_b = site.reference_wind_speed_ms
    if v_b is None:
        v_b = site.extra.get("vb_ms") if site.extra else None
    if v_b is None:
        v_b = compute_base_velocity(zone_id, altitude)
        if zone_id:
            zone_info = get_na_zone(zone_id)
            desc = zone_info["description"] if zone_info else f"zona {zone_id}"
            warnings.append(f"Velocità base calcolata da NA italiano: vb = {v_b:.1f} m/s ({desc}).")
        else:
            warnings.append(
                f"Velocità base vb non specificata; usato default {v_b} m/s. "
                "Impostare site.reference_wind_speed_ms o site.extra['zone_id']."
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
        qp = compute_peak_velocity_pressure(z, v_b, site.terrain_category)
        profile.append(WindProfilePoint(z_m=z, v_m_s=round(vm, 3), q_kN_m2=round(qp, 4)))

    # Pressioni sulle zone dell'edificio
    pressure_zones: list[PressureZoneResults] = []
    if building.width_m > 0 and building.depth_m > 0:
        from src.wind.pressure_coefficients import compute_building_pressure_zones

        q_at_h = profile[-1].q_kN_m2 if profile else q_b
        zones_data = compute_building_pressure_zones(
            h,
            building.width_m,
            building.depth_m,
            q_at_h,
        )
        for zd in zones_data:
            pressure_zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"],
                    description=zd["description"],
                    cpe=zd["cpe"],
                    cpi=zd["cpi"],
                    we_kN_m2=zd["we_kN_m2"],
                    wi_kN_m2=zd["wi_kN_m2"],
                    net_kN_m2=zd["net_kN_m2"],
                )
            )

    # Metadati NA
    na = _load_national_annex()
    extra: dict[str, Any] = {
        "terrain_category": site.terrain_category,
        "standard": "EN 1991-1-4:2005",
    }
    if zone_id and get_na_zone(zone_id):
        extra["na_zone"] = zone_id
        extra["na_zone_desc"] = get_na_zone(zone_id).get("description", "")  # type: ignore[union-attr]
    if na.get("rho_kg_m3"):
        extra["rho_kg_m3"] = na["rho_kg_m3"]

    return WindResults(
        method="EN1991_1_4",
        v_b_ms=round(v_b, 3),
        v_ref_ms=round(v_b, 3),
        q_b_kN_m2=round(q_b, 4),
        velocity_profile=profile,
        pressure_zones=pressure_zones,
        warnings=warnings,
        extra=extra,
    )
