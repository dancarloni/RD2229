"""NTC2018 wind – calcolo azioni del vento secondo NTC 2018 §3.3.

Riferimento: NTC 2018 (D.M. 17/01/2018), Capitolo 3 – Azioni sulle costruzioni,
§3.3 Azione del vento.

NOTA: I valori dei parametri dipendenti dalla zona geografica (vb,0, a0, ka, ecc.)
sono definiti nelle tabelle normative NTC 2018 §3.3.2 e NON sono liberamente
riproducibili. Il professionista deve verificare e inserire i valori corretti
in data/wind/ntc2018_wind_zones.json.
"""

from __future__ import annotations

import logging
import math

from src.wind.models import BuildingGeom, WindSite
from src.wind.outputs import WindProfilePoint, WindResults

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parametri del terreno NTC2018 (Tabella 3.3.II)
# Fonte: NTC 2018 §3.3.4 – Azione statica del vento
# NOTA: Valori riportati in letteratura tecnica pubblica.
# Chiave: categoria terreno → (z0 [m], z_min [m], kr)
# ---------------------------------------------------------------------------
_TERRAIN_PARAMS_NTC2018: dict[str, tuple[float, float, float]] = {
    "I": (0.01, 2.0, 0.17),  # Mare aperto, laghi
    "II": (0.05, 4.0, 0.19),  # Campagna con bassa vegetazione
    "III": (0.10, 5.0, 0.20),  # Zone suburbane, foreste
    "IV": (0.30, 8.0, 0.22),  # Zone urbane dense
    "V": (0.70, 12.0, 0.23),  # Aree urbane ad alta densità
}

_DEFAULT_TERRAIN_CAT = "II"

# Parametri velocità di riferimento NTC2018 §3.3.2 (fallback defaults)
_VB0_DEFAULT_MS = 25.0  # [m/s] valore placeholder
_A0_DEFAULT_M = 500.0  # [m] altitudine di inizio riduzione
_KA_DEFAULT = 0.010  # [1/m] coefficiente riduzione altitudine


def _load_zone_params(zone_id: str) -> tuple[float, float, float, bool] | None:
    """Carica parametri zona dal JSON. Returns (vb0, a0, ka, is_placeholder) o None."""
    from src.wind.zone_loader import get_zone_params

    zp = get_zone_params(zone_id)
    if zp is None:
        return None
    return (zp.vb0_ms, zp.a0_m, zp.ka, zp.is_placeholder)


def compute_reference_wind_speed(site: WindSite) -> float:
    """Calcola la velocità di riferimento del vento vb [m/s] per NTC2018.

    Formula: vb = vb,0 * c_alt  (NTC2018 §3.3.2)
    dove c_alt = 1 se a ≤ a0, altrimenti riduzione lineare.

    Priorità valori:
    1. site.reference_wind_speed_ms (override utente diretto)
    2. site.extra["vb0_ms"] / site.extra["a0_m"] / site.extra["ka"] (espliciti)
    3. zone_id → lookup da JSON (data/wind/ntc2018_wind_zones.json)
    4. Valori default di fallback

    Args:
        site: Parametri del sito.

    Returns:
        Velocità di riferimento [m/s].
    """
    v, _ = _compute_reference_wind_speed_with_warnings(site)
    return v


def _compute_reference_wind_speed_with_warnings(
    site: WindSite,
) -> tuple[float, list[str]]:
    """Calcola vb con warnings (uso interno)."""
    warnings: list[str] = []

    if site.reference_wind_speed_ms is not None:
        return site.reference_wind_speed_ms, warnings

    # Priorità 2: valori espliciti in extra
    vb0 = site.extra.get("vb0_ms")
    a0 = site.extra.get("a0_m")
    ka = site.extra.get("ka")

    # Priorità 3: lookup da zone JSON
    zone_id = site.zone_id or site.extra.get("zone_id")
    if zone_id is not None and vb0 is None:
        zone_data = _load_zone_params(str(zone_id))
        if zone_data is not None:
            vb0, a0, ka, is_placeholder = zone_data
            if is_placeholder:
                warnings.append(
                    f"Zona {zone_id} usa valori PLACEHOLDER. "
                    "Verificare con NTC2018 Tabella 3.3.I."
                )
        else:
            warnings.append(
                f"Zona '{zone_id}' non trovata nel database; uso valori default."
            )

    # Priorità 4: fallback
    if vb0 is None:
        vb0 = _VB0_DEFAULT_MS
        warnings.append(
            f"Velocità base vb0 non specificata; usato valore placeholder "
            f"{_VB0_DEFAULT_MS} m/s. "
            "Impostare site.zone_id o site.extra['vb0_ms']."
        )
    a0 = a0 if a0 is not None else _A0_DEFAULT_M
    ka = ka if ka is not None else _KA_DEFAULT

    altitude = site.altitude_m
    if altitude <= a0:
        c_alt = 1.0
    else:
        c_alt = max(0.0, 1.0 - ka * (altitude - a0))

    return vb0 * c_alt, warnings


def compute_kinetic_pressure(v_ms: float) -> float:
    """Pressione cinetica q = 0.5 * ρ * v² [kN/m²].

    Densità aria ρ = 1.25 kg/m³ (NTC2018 §3.3.3).

    Args:
        v_ms: Velocità [m/s].

    Returns:
        Pressione cinetica [kN/m²].
    """
    rho = 1.25  # kg/m³
    q_Pa = 0.5 * rho * v_ms**2
    return q_Pa / 1000.0  # kN/m²


def compute_velocity_profile_ntc2018(
    site: WindSite,
    v_ref_ms: float,
    z_values: list[float],
) -> list[WindProfilePoint]:
    """Calcola il profilo di velocità/pressione per le quote z_values.

    Usa la formula di profilo logaritmico NTC2018 §3.3.4.
    La velocità media è: vm(z) = cr(z) * vb  dove cr(z) = kr * ln(z/z0).

    Args:
        site: Parametri del sito.
        v_ref_ms: Velocità di riferimento [m/s].
        z_values: Quote [m] in cui calcolare il profilo.

    Returns:
        Lista di :class:`WindProfilePoint`.
    """
    cat = site.terrain_category.upper()
    params = _TERRAIN_PARAMS_NTC2018.get(cat)
    if params is None:
        logger.warning(
            "Categoria terreno '%s' non riconosciuta per NTC2018; uso '%s'.",
            cat,
            _DEFAULT_TERRAIN_CAT,
        )
        params = _TERRAIN_PARAMS_NTC2018[_DEFAULT_TERRAIN_CAT]

    z0, z_min, kr = params
    profile: list[WindProfilePoint] = []

    for z in z_values:
        z_eff = max(z, z_min)
        cr = kr * math.log(z_eff / z0)
        v_z = cr * v_ref_ms * getattr(site, "orography_factor", 1.0)
        q_z = compute_kinetic_pressure(v_z)
        profile.append(WindProfilePoint(z_m=z, v_m_s=round(v_z, 3), q_kN_m2=round(q_z, 4)))

    return profile


def run_ntc2018_wind(
    site: WindSite,
    building: BuildingGeom,
) -> WindResults:
    """Calcolo completo azioni del vento secondo NTC 2018 §3.3.

    Args:
        site: Parametri del sito.
        building: Geometria dell'edificio.

    Returns:
        :class:`WindResults` con profilo e pressioni calcolate.
    """
    warnings: list[str] = []

    # Velocità di riferimento (con lookup zona da JSON)
    v_ref, v_warnings = _compute_reference_wind_speed_with_warnings(site)
    warnings.extend(v_warnings)
    q_b = compute_kinetic_pressure(v_ref)

    # Quote per il profilo (da 0 a h_edificio, 10 punti)
    h = building.height_m
    if h <= 0:
        warnings.append("Altezza edificio non positiva; uso 10 m come default.")
        h = 10.0

    n_pts = max(5, min(20, int(h / 2)))
    z_values = [h * i / (n_pts - 1) for i in range(1, n_pts + 1)]

    profile = compute_velocity_profile_ntc2018(site, v_ref, z_values)

    # Verifica monotonia del profilo
    if len(profile) > 1:
        for i in range(1, len(profile)):
            if profile[i].v_m_s < profile[i - 1].v_m_s * 0.99:
                warnings.append(f"Profilo vento non monotono a z={profile[i].z_m} m.")
                break

    # Pressioni sulle zone dell'edificio (se dimensioni disponibili)
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
        method="NTC2018",
        v_b_ms=round(v_ref, 3),
        v_ref_ms=round(v_ref, 3),
        q_b_kN_m2=round(q_b, 4),
        velocity_profile=profile,
        pressure_zones=pressure_zones,
        warnings=warnings,
        extra={
            "terrain_category": site.terrain_category,
            "altitude_m": site.altitude_m,
        },
    )
