"""Combinations – combinazioni di carico del vento SLU/SLE.

Genera combinazioni secondo NTC2018 Tab. 2.5.I:
- SLU: γ_w = 1.5 (sfavorevole), γ_w = 0.0 (favorevole)
- SLE caratteristica: ψ0 = 0.6
- SLE frequente: ψ1 = 0.2
- SLE quasi-permanente: ψ2 = 0.0

Le combinazioni sono opzionali e attivate solo se richiesto.
"""

from __future__ import annotations

import logging

from src.wind.outputs import PressureZoneResults, WindCombination, ZoneForce

logger = logging.getLogger(__name__)

# Coefficienti ψ per vento — NTC2018 Tab. 2.5.I
_PSI_WIND_NTC2018 = {
    "psi_0": 0.6,
    "psi_1": 0.2,
    "psi_2": 0.0,
}

_PSI_WIND_EN1991 = {
    "psi_0": 0.6,
    "psi_1": 0.2,
    "psi_2": 0.0,
}


def _get_psi(norm_code: str) -> dict[str, float]:
    """Restituisce i coefficienti ψ per la norma specificata."""
    norm = norm_code.upper()
    if norm in ("NTC2018",):
        return _PSI_WIND_NTC2018
    if norm in ("EN1991", "EN1991_1_4", "EC"):
        return _PSI_WIND_EN1991
    logger.warning("Norma '%s' non riconosciuta per ψ; uso NTC2018.", norm_code)
    return _PSI_WIND_NTC2018


def _scale_pressures(
    pressures: list[PressureZoneResults],
    factor: float,
) -> list[PressureZoneResults]:
    """Scala le pressioni per un fattore (γ o ψ)."""
    scaled = []
    for p in pressures:
        scaled.append(PressureZoneResults(
            zone_id=p.zone_id,
            description=p.description,
            cpe=p.cpe,
            cpi=p.cpi,
            we_kN_m2=round(p.we_kN_m2 * factor, 4),
            wi_kN_m2=round(p.wi_kN_m2 * factor, 4),
            net_kN_m2=round(p.net_kN_m2 * factor, 4),
            area_m2=p.area_m2,
        ))
    return scaled


def _scale_forces(
    forces: list[ZoneForce],
    factor: float,
) -> list[ZoneForce]:
    """Scala le forze per un fattore."""
    scaled = []
    for f in forces:
        scaled.append(ZoneForce(
            zone_id=f.zone_id,
            F_kN=round(f.F_kN * factor, 4),
            direction=f.direction,
            tributary_area_m2=f.tributary_area_m2,
            application_point_m=f.application_point_m,
        ))
    return scaled


def generate_wind_combinations(
    pressures: list[PressureZoneResults],
    norm_code: str = "NTC2018",
    *,
    resultant_forces: list[ZoneForce] | None = None,
) -> list[WindCombination]:
    """Genera le combinazioni di carico del vento.

    Args:
        pressures: Pressioni base sulle zone.
        norm_code: Codice normativo ("NTC2018", "EN1991").
        resultant_forces: Forze risultanti base (opzionale).

    Returns:
        Lista di WindCombination per SLU e SLE.
    """
    psi = _get_psi(norm_code)
    forces = resultant_forces or []
    combos = []

    # SLU — vento sfavorevole (γ_w = 1.5)
    combos.append(WindCombination(
        combo_id="SLU_1.5",
        description="SLU — vento sfavorevole (γ_w=1.5)",
        gamma_w=1.5,
        psi=1.0,
        pressures=_scale_pressures(pressures, 1.5),
        resultant_forces=_scale_forces(forces, 1.5),
    ))

    # SLU — vento favorevole (γ_w = 0.0)
    combos.append(WindCombination(
        combo_id="SLU_0.0",
        description="SLU — vento favorevole (γ_w=0.0)",
        gamma_w=0.0,
        psi=1.0,
        pressures=_scale_pressures(pressures, 0.0),
        resultant_forces=_scale_forces(forces, 0.0),
    ))

    # SLE caratteristica (ψ0)
    combos.append(WindCombination(
        combo_id="SLE_car",
        description=f"SLE caratteristica (ψ0={psi['psi_0']})",
        gamma_w=1.0,
        psi=psi["psi_0"],
        pressures=_scale_pressures(pressures, psi["psi_0"]),
        resultant_forces=_scale_forces(forces, psi["psi_0"]),
    ))

    # SLE frequente (ψ1)
    combos.append(WindCombination(
        combo_id="SLE_freq",
        description=f"SLE frequente (ψ1={psi['psi_1']})",
        gamma_w=1.0,
        psi=psi["psi_1"],
        pressures=_scale_pressures(pressures, psi["psi_1"]),
        resultant_forces=_scale_forces(forces, psi["psi_1"]),
    ))

    # SLE quasi-permanente (ψ2)
    combos.append(WindCombination(
        combo_id="SLE_qp",
        description=f"SLE quasi-permanente (ψ2={psi['psi_2']})",
        gamma_w=1.0,
        psi=psi["psi_2"],
        pressures=_scale_pressures(pressures, psi["psi_2"]),
        resultant_forces=_scale_forces(forces, psi["psi_2"]),
    ))

    return combos
