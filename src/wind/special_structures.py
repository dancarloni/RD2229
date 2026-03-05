"""Special structures – coefficienti di pressione per strutture speciali.

Supporta:
- Tettoie (canopies): monopitch, duopitch, trough, multibay — EC1 §7.3
- Pensiline (shelters): tettoia addossata a edificio
- Insegne (signs): lastra piena, traforata, reticolare — EC1 §7.4.3
- Pannelli fotovoltaici (solar): terra, tetto piano, tetto inclinato, tracker
- Muri isolati (free-standing walls) e recinzioni — EC1 §7.4.1

I coefficienti sono caricati da data/wind/coefficients/ con override utente.
"""

from __future__ import annotations

import logging
import math
from typing import Any

from src.wind.zone_loader import load_coefficient_file

logger = logging.getLogger(__name__)

# Cache dati
_CANOPIES_DATA: dict[str, Any] | None = None
_SIGNS_DATA: dict[str, Any] | None = None
_SOLAR_DATA: dict[str, Any] | None = None


def _get_canopies_data() -> dict[str, Any]:
    global _CANOPIES_DATA
    if _CANOPIES_DATA is None:
        _CANOPIES_DATA = load_coefficient_file("canopies.json")
    return _CANOPIES_DATA


def _get_signs_data() -> dict[str, Any]:
    global _SIGNS_DATA
    if _SIGNS_DATA is None:
        _SIGNS_DATA = load_coefficient_file("signs.json")
    return _SIGNS_DATA


def _get_solar_data() -> dict[str, Any]:
    global _SOLAR_DATA
    if _SOLAR_DATA is None:
        _SOLAR_DATA = load_coefficient_file("solar_panels.json")
    return _SOLAR_DATA


def _interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    """Interpolazione lineare con clamp."""
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


# ===========================================================================
# Tettoie (Canopies) — EC1 §7.3
# ===========================================================================

def get_canopy_cp(
    canopy_type: str,
    angle_deg: float,
    blockage_ratio: float,
    zone: str,
    *,
    override_max: float | None = None,
    override_min: float | None = None,
) -> tuple[float, float]:
    """Coefficienti di pressione netta per tettoie.

    Args:
        canopy_type: "CANOPY_MONO", "CANOPY_DUO", "CANOPY_TROUGH".
        angle_deg: Angolo di inclinazione [°].
        blockage_ratio: Rapporto di blocco φ (0=aperta, 1=completamente chiusa).
        zone: Zona della tettoia ("A", "B", "C").
        override_max: Override cp_net_max.
        override_min: Override cp_net_min.

    Returns:
        Tupla (cp_net_max, cp_net_min).
    """
    if override_max is not None and override_min is not None:
        return (override_max, override_min)

    data = _get_canopies_data()

    # Seleziona dataset per tipologia
    type_key = {
        "CANOPY_MONO": "monopitch",
        "CANOPY_DUO": "duopitch",
        "CANOPY_TROUGH": "trough",
    }.get(canopy_type.upper(), "monopitch")

    canopy_data = data.get(type_key, {})
    if not canopy_data:
        logger.warning("Dati tettoia '%s' non trovati; uso valori conservativi.", canopy_type)
        return (2.0, -2.0)

    angles = canopy_data.get("angles_deg", [])
    zone_upper = zone.upper()

    # Interpola tra blockage 0 e 1
    phi = max(0.0, min(1.0, blockage_ratio))

    b0 = canopy_data.get("blockage_0", {})
    b1 = canopy_data.get("blockage_1", {})

    if zone_upper not in b0 or zone_upper not in b1:
        logger.warning("Zona '%s' non trovata per tettoia '%s'.", zone, canopy_type)
        return (2.0, -2.0)

    cp_max_0 = _interpolate(angle_deg, angles, b0[zone_upper].get("cp_net_max", []))
    cp_min_0 = _interpolate(angle_deg, angles, b0[zone_upper].get("cp_net_min", []))
    cp_max_1 = _interpolate(angle_deg, angles, b1[zone_upper].get("cp_net_max", []))
    cp_min_1 = _interpolate(angle_deg, angles, b1[zone_upper].get("cp_net_min", []))

    cp_max = cp_max_0 + phi * (cp_max_1 - cp_max_0)
    cp_min = cp_min_0 + phi * (cp_min_1 - cp_min_0)

    return (
        override_max if override_max is not None else round(cp_max, 3),
        override_min if override_min is not None else round(cp_min, 3),
    )


def get_canopy_multibay_factor(bay_index: int) -> float:
    """Fattore di riduzione per tettoie multi-campata (EC1 §7.3.4).

    Args:
        bay_index: Indice della campata (0=prima, 1=seconda, 2+=successive).

    Returns:
        Fattore moltiplicativo (1.0 per prima campata).
    """
    data = _get_canopies_data()
    mb = data.get("multibay", {}).get("bay_reduction_factors", {})

    if bay_index == 0:
        return mb.get("first_bay", 1.0)
    elif bay_index == 1:
        return mb.get("second_bay", 0.87)
    else:
        return mb.get("third_and_subsequent", 0.68)


def compute_canopy_pressures(
    canopy_type: str,
    angle_deg: float,
    blockage_ratio: float,
    q_p_kN_m2: float,
    *,
    num_bays: int = 1,
    overrides: dict[str, dict[str, float]] | None = None,
) -> list[dict[str, Any]]:
    """Calcola le pressioni su tutte le zone di una tettoia.

    Args:
        canopy_type: Tipo tettoia.
        angle_deg: Angolo [°].
        blockage_ratio: Blocco φ.
        q_p_kN_m2: Pressione di picco [kN/m²].
        num_bays: Numero di campate (1 per singola, >1 per multibay).
        overrides: Override per zona.

    Returns:
        Lista di dict con zone_id, cp_net_max, cp_net_min, w_max, w_min.
    """
    overrides = overrides or {}
    results = []

    for bay_idx in range(num_bays):
        bay_factor = get_canopy_multibay_factor(bay_idx) if num_bays > 1 else 1.0
        bay_label = f"_bay{bay_idx + 1}" if num_bays > 1 else ""

        for zone in ("A", "B", "C"):
            ov = overrides.get(zone, {})
            cp_max, cp_min = get_canopy_cp(
                canopy_type, angle_deg, blockage_ratio, zone,
                override_max=ov.get("cp_net_max"),
                override_min=ov.get("cp_net_min"),
            )
            cp_max *= bay_factor
            cp_min *= bay_factor

            results.append({
                "zone_id": f"canopy_{zone}{bay_label}",
                "description": f"Tettoia zona {zone}{bay_label}",
                "cp_net_max": round(cp_max, 3),
                "cp_net_min": round(cp_min, 3),
                "w_max_kN_m2": round(cp_max * q_p_kN_m2, 4),
                "w_min_kN_m2": round(cp_min * q_p_kN_m2, 4),
                "bay_factor": bay_factor,
            })

    return results


# ===========================================================================
# Pensiline (Shelters) — tettoia addossata a edificio
# ===========================================================================

_SHELTER_REDUCTION = 0.75  # Riduzione cp per effetto parete retrostante


def compute_shelter_pressures(
    angle_deg: float,
    blockage_ratio: float,
    q_p_kN_m2: float,
    *,
    reduction_factor: float = _SHELTER_REDUCTION,
    overrides: dict[str, dict[str, float]] | None = None,
) -> list[dict[str, Any]]:
    """Calcola le pressioni su una pensilina (tettoia addossata a edificio).

    Trattata come CANOPY_MONO con fattore di riduzione per parete retrostante.

    Args:
        angle_deg: Angolo di inclinazione [°].
        blockage_ratio: Blocco φ.
        q_p_kN_m2: Pressione di picco [kN/m²].
        reduction_factor: Fattore di riduzione per effetto parete (default 0.75).
        overrides: Override per zona.

    Returns:
        Lista pressioni per zona.
    """
    base_results = compute_canopy_pressures(
        "CANOPY_MONO", angle_deg, blockage_ratio, q_p_kN_m2,
        overrides=overrides,
    )

    for r in base_results:
        r["zone_id"] = r["zone_id"].replace("canopy_", "shelter_")
        r["description"] = r["description"].replace("Tettoia", "Pensilina")
        r["cp_net_max"] = round(r["cp_net_max"] * reduction_factor, 3)
        r["cp_net_min"] = round(r["cp_net_min"] * reduction_factor, 3)
        r["w_max_kN_m2"] = round(r["cp_net_max"] * q_p_kN_m2, 4)
        r["w_min_kN_m2"] = round(r["cp_net_min"] * q_p_kN_m2, 4)
        r["shelter_reduction"] = reduction_factor

    return base_results


# ===========================================================================
# Insegne (Signs) — EC1 §7.4.3
# ===========================================================================

def get_sign_cf(
    b_m: float,
    h_m: float,
    *,
    solidity_ratio: float = 1.0,
    ground_clearance_m: float = 0.0,
    is_lattice: bool = False,
    member_type: str = "flat",
    override: float | None = None,
) -> float:
    """Coefficiente di forza cf per insegne e pannelli pubblicitari.

    Args:
        b_m: Larghezza dell'insegna [m].
        h_m: Altezza dell'insegna [m].
        solidity_ratio: Rapporto pieni/vuoti φ (1.0 = piena).
        ground_clearance_m: Distanza dal suolo [m].
        is_lattice: True per struttura reticolare di supporto.
        member_type: "flat" o "circular" (per reticolari).
        override: Override utente.

    Returns:
        Coefficiente di forza cf.
    """
    if override is not None:
        return override

    data = _get_signs_data()

    if is_lattice:
        lattice = data.get("lattice_structure", {})
        if member_type.lower() == "circular":
            cf_0 = lattice.get("circular_members", {}).get("cf_0_subcritical", 1.2)
        else:
            cf_0 = lattice.get("flat_members", {}).get("cf_0", 2.0)

        # Riduzione per solidity
        sol = data.get("solidity_effect", {})
        phi_vals = sol.get("phi_values", [])
        eta_vals = sol.get("eta_values", [])
        eta = _interpolate(solidity_ratio, phi_vals, eta_vals) if phi_vals else solidity_ratio
        return round(cf_0 * eta, 3)

    # Insegna piena o traforata
    cf_solid = data.get("solid_plate", {}).get("cf_default", 1.8)

    if solidity_ratio < 1.0:
        sol = data.get("solidity_effect", {})
        phi_vals = sol.get("phi_values", [])
        eta_vals = sol.get("eta_values", [])
        eta = _interpolate(solidity_ratio, phi_vals, eta_vals) if phi_vals else solidity_ratio
        cf = cf_solid * eta
    else:
        cf = cf_solid

    # Fattore di vicinanza al suolo
    if ground_clearance_m > 0 and h_m > 0:
        gc_data = data.get("ground_clearance_factor", {})
        zg_h_vals = gc_data.get("z_g_over_h", [])
        factor_vals = gc_data.get("factor", [])
        zg_over_h = ground_clearance_m / h_m
        gc_factor = _interpolate(zg_over_h, zg_h_vals, factor_vals) if zg_h_vals else 1.0
        cf *= gc_factor

    return round(cf, 3)


def compute_sign_force(
    b_m: float,
    h_m: float,
    q_p_kN_m2: float,
    *,
    solidity_ratio: float = 1.0,
    ground_clearance_m: float = 0.0,
    is_lattice: bool = False,
    member_type: str = "flat",
    override_cf: float | None = None,
) -> dict[str, Any]:
    """Calcola la forza del vento su un'insegna.

    F_w = cf · q_p · A_ref

    Args:
        b_m: Larghezza [m].
        h_m: Altezza [m].
        q_p_kN_m2: Pressione di picco [kN/m²].
        Tutti gli altri parametri come get_sign_cf().

    Returns:
        Dict con cf, area, F_kN.
    """
    cf = get_sign_cf(
        b_m, h_m,
        solidity_ratio=solidity_ratio,
        ground_clearance_m=ground_clearance_m,
        is_lattice=is_lattice,
        member_type=member_type,
        override=override_cf,
    )
    area = b_m * h_m * solidity_ratio
    F_kN = cf * q_p_kN_m2 * area

    return {
        "zone_id": "sign",
        "description": f"Insegna {b_m:.1f}×{h_m:.1f} m",
        "cf": cf,
        "solidity_ratio": solidity_ratio,
        "area_ref_m2": round(area, 2),
        "q_p_kN_m2": q_p_kN_m2,
        "F_kN": round(F_kN, 3),
        "application_point_m": ground_clearance_m + h_m / 2.0,
    }


# ===========================================================================
# Pannelli fotovoltaici (Solar panels)
# ===========================================================================

def get_solar_panel_cp(
    layout: str,
    tilt_deg: float,
    position: str = "interior",
    *,
    roof_angle_deg: float = 0.0,
    row_index: int = 0,
    tracking_angle_deg: float = 0.0,
    override_max: float | None = None,
    override_min: float | None = None,
) -> tuple[float, float]:
    """Coefficienti di pressione netta per pannelli fotovoltaici.

    Args:
        layout: "SOLAR_GROUND", "SOLAR_FLAT_ROOF", "SOLAR_PITCHED_ROOF", "SOLAR_TRACKER".
        tilt_deg: Inclinazione pannello [°].
        position: "edge", "interior", "corner" (per tetto piano).
        roof_angle_deg: Angolo tetto [°] (per SOLAR_PITCHED_ROOF).
        row_index: Indice fila (0=prima, per schermatura).
        tracking_angle_deg: Angolo tracking istantaneo [°] (per tracker).
        override_max: Override cp_net_max.
        override_min: Override cp_net_min.

    Returns:
        Tupla (cp_net_max, cp_net_min).
    """
    if override_max is not None and override_min is not None:
        return (override_max, override_min)

    data = _get_solar_data()
    layout_upper = layout.upper()

    if layout_upper == "SOLAR_GROUND":
        return _solar_ground_cp(data, tilt_deg, position, row_index)

    if layout_upper == "SOLAR_FLAT_ROOF":
        return _solar_flat_roof_cp(data, tilt_deg, position)

    if layout_upper == "SOLAR_PITCHED_ROOF":
        return _solar_pitched_roof_cp(data, tilt_deg, roof_angle_deg)

    if layout_upper == "SOLAR_TRACKER":
        return _solar_tracker_cp(data, tracking_angle_deg, position)

    logger.warning("Layout PV '%s' non riconosciuto.", layout)
    return (1.5, -2.0)


def _solar_ground_cp(
    data: dict, tilt_deg: float, position: str, row_index: int,
) -> tuple[float, float]:
    """CP per pannelli a terra."""
    gm = data.get("ground_mounted", {})
    angles = gm.get("tilt_angles_deg", [])

    if position.lower() == "edge":
        cp_max = _interpolate(tilt_deg, angles, gm.get("edge_panel", {}).get("cp_net_max", []))
        cp_min = _interpolate(tilt_deg, angles, gm.get("edge_panel", {}).get("cp_net_min", []))
    else:
        cp_max = _interpolate(tilt_deg, angles, gm.get("interior_panel", {}).get("cp_net_max", []))
        cp_min = _interpolate(tilt_deg, angles, gm.get("interior_panel", {}).get("cp_net_min", []))

    # Schermatura per file successive
    shielding = gm.get("shielding_factors", {})
    if row_index == 0:
        factor = shielding.get("row_1", 1.0)
    elif row_index == 1:
        factor = shielding.get("row_2", 0.85)
    else:
        factor = shielding.get("row_3_plus", 0.70)

    return (round(cp_max * factor, 3), round(cp_min * factor, 3))


def _solar_flat_roof_cp(
    data: dict, tilt_deg: float, position: str,
) -> tuple[float, float]:
    """CP per pannelli su tetto piano."""
    fr = data.get("flat_roof", {})
    angles = fr.get("tilt_angles_deg", [])

    pos_key = {
        "corner": "corner_zone",
        "edge": "edge_zone",
        "interior": "interior_zone",
    }.get(position.lower(), "interior_zone")

    zone_data = fr.get(pos_key, {})
    cp_max = _interpolate(tilt_deg, angles, zone_data.get("cp_net_max", []))
    cp_min = _interpolate(tilt_deg, angles, zone_data.get("cp_net_min", []))

    return (round(cp_max, 3), round(cp_min, 3))


def _solar_pitched_roof_cp(
    data: dict, tilt_deg: float, roof_angle_deg: float,
) -> tuple[float, float]:
    """CP per pannelli su tetto inclinato (parametrico)."""
    pr = data.get("pitched_roof", {})
    angles = pr.get("roof_angles_deg", [])

    # Se pannello flush al tetto
    if abs(tilt_deg - roof_angle_deg) < 2.0:
        flush = pr.get("flush_mounted", {})
        cp_max = _interpolate(roof_angle_deg, angles, flush.get("cp_net_max", []))
        cp_min = _interpolate(roof_angle_deg, angles, flush.get("cp_net_min", []))
    else:
        # Pannello inclinato rispetto al tetto
        flush = pr.get("flush_mounted", {})
        cp_max_base = _interpolate(roof_angle_deg, angles, flush.get("cp_net_max", []))
        cp_min_base = _interpolate(roof_angle_deg, angles, flush.get("cp_net_min", []))

        tilted = pr.get("tilted_above_roof", {})
        f_max = tilted.get("extra_tilt_factor_max", 1.3)
        f_min = tilted.get("extra_tilt_factor_min", 1.4)

        cp_max = cp_max_base * f_max
        cp_min = cp_min_base * f_min

    return (round(cp_max, 3), round(cp_min, 3))


def _solar_tracker_cp(
    data: dict, tracking_angle_deg: float, position: str,
) -> tuple[float, float]:
    """CP per inseguitori solari monoassiali."""
    tr = data.get("tracker", {})
    angles = tr.get("tracking_angles_deg", [])

    if position.lower() == "edge":
        zone_data = tr.get("edge_tracker", {})
    else:
        zone_data = tr.get("interior_tracker", {})

    cp_max = _interpolate(abs(tracking_angle_deg), angles, zone_data.get("cp_net_max", []))
    cp_min = _interpolate(abs(tracking_angle_deg), angles, zone_data.get("cp_net_min", []))

    return (round(cp_max, 3), round(cp_min, 3))


def compute_solar_pressures(
    layout: str,
    tilt_deg: float,
    q_p_kN_m2: float,
    *,
    roof_angle_deg: float = 0.0,
    num_rows: int = 1,
    positions: list[str] | None = None,
    tracking_angle_deg: float = 0.0,
    overrides: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Calcola le pressioni su pannelli fotovoltaici.

    Args:
        layout: Tipo layout PV.
        tilt_deg: Inclinazione pannello [°].
        q_p_kN_m2: Pressione di picco [kN/m²].
        roof_angle_deg: Angolo tetto [°].
        num_rows: Numero di file.
        positions: Posizioni per ciascuna riga (se None, "edge" per prima, "interior" per altre).
        tracking_angle_deg: Angolo tracking [°].
        overrides: Override coefficienti.

    Returns:
        Lista di dict con zona, cp, pressioni.
    """
    results = []
    overrides = overrides or {}

    for row_idx in range(num_rows):
        if positions and row_idx < len(positions):
            pos = positions[row_idx]
        else:
            pos = "edge" if row_idx == 0 else "interior"

        cp_max, cp_min = get_solar_panel_cp(
            layout, tilt_deg, pos,
            roof_angle_deg=roof_angle_deg,
            row_index=row_idx,
            tracking_angle_deg=tracking_angle_deg,
            override_max=overrides.get(f"row{row_idx}_max"),
            override_min=overrides.get(f"row{row_idx}_min"),
        )

        results.append({
            "zone_id": f"pv_row{row_idx + 1}_{pos}",
            "description": f"PV fila {row_idx + 1} ({pos})",
            "cp_net_max": cp_max,
            "cp_net_min": cp_min,
            "w_max_kN_m2": round(cp_max * q_p_kN_m2, 4),
            "w_min_kN_m2": round(cp_min * q_p_kN_m2, 4),
            "row_index": row_idx,
            "position": pos,
        })

    return results


# ===========================================================================
# Muri isolati / parapetti / recinzioni — EC1 §7.4.1
# ===========================================================================

def get_freestanding_wall_cp(
    length_m: float,
    height_m: float,
    *,
    solidity_ratio: float = 1.0,
    return_corner: bool = False,
    override: float | None = None,
) -> float:
    """Coefficiente cp_net per muri isolati e recinzioni (EC1 §7.4.1).

    Args:
        length_m: Lunghezza muro [m].
        height_m: Altezza muro [m].
        solidity_ratio: Rapporto pieni/vuoti per recinzioni.
        return_corner: True per zona d'angolo (cp più alto).
        override: Override utente.

    Returns:
        cp_net.
    """
    if override is not None:
        return override

    l_h = length_m / height_m if height_m > 0 else 5.0

    # EC1 Table 7.9 (valori semplificati)
    if return_corner:
        # Zona A (bordo): cp più alto
        if l_h >= 5:
            cp = 2.1
        elif l_h >= 3:
            cp = 2.3
        else:
            cp = 2.5
    else:
        # Zona B (centrale)
        if l_h >= 5:
            cp = 1.2
        elif l_h >= 3:
            cp = 1.4
        else:
            cp = 1.6

    # Riduzione per solidity (recinzioni)
    if solidity_ratio < 1.0:
        sol_data = _get_signs_data().get("solidity_effect", {})
        phi_vals = sol_data.get("phi_values", [])
        eta_vals = sol_data.get("eta_values", [])
        if phi_vals:
            eta = _interpolate(solidity_ratio, phi_vals, eta_vals)
            cp *= eta

    return round(cp, 3)
