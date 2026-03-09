"""Wind report – export strutturato dei risultati del calcolo del vento.

Genera report in formato dizionario/JSON dai WindResults, con sezioni:
- Parametri di input (sito, geometria, metodo)
- Profilo di velocità/pressione
- Pressioni per zone
- Forze risultanti
- Attrito
- Combinazioni di carico
- Verifiche aeroelastiche (se disponibili)
- Riepilogo e avvisi
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

from src.wind.outputs import (
    FrictionForce,
    PressureZoneResults,
    WindCombination,
    WindProfilePoint,
    WindResults,
    ZoneForce,
)

logger = logging.getLogger(__name__)


# ===========================================================================
# Serializzazione dataclass → dict
# ===========================================================================

def _profile_point_to_dict(p: WindProfilePoint) -> dict[str, Any]:
    return {
        "z_m": p.z_m,
        "v_m_s": p.v_m_s,
        "q_kN_m2": p.q_kN_m2,
    }


def _pressure_zone_to_dict(pz: PressureZoneResults) -> dict[str, Any]:
    d: dict[str, Any] = {
        "zone_id": pz.zone_id,
        "description": pz.description,
        "cpe": pz.cpe,
        "net_kN_m2": pz.net_kN_m2,
    }
    if pz.cpi != 0.0:
        d["cpi"] = pz.cpi
        d["we_kN_m2"] = pz.we_kN_m2
        d["wi_kN_m2"] = pz.wi_kN_m2
    if pz.area_m2 > 0:
        d["area_m2"] = pz.area_m2
    return d


def _zone_force_to_dict(f: ZoneForce) -> dict[str, Any]:
    d: dict[str, Any] = {
        "zone_id": f.zone_id,
        "F_kN": f.F_kN,
        "direction": f.direction,
    }
    if f.tributary_area_m2 > 0:
        d["tributary_area_m2"] = f.tributary_area_m2
    if f.application_point_m > 0:
        d["application_point_m"] = f.application_point_m
    if f.eccentricity_m != 0.0:
        d["eccentricity_m"] = f.eccentricity_m
    return d


def _friction_to_dict(fr: FrictionForce) -> dict[str, Any]:
    return {
        "surface_id": fr.surface_id,
        "c_fr": fr.c_fr,
        "area_m2": fr.area_m2,
        "F_fr_kN": fr.F_fr_kN,
    }


def _combination_to_dict(c: WindCombination) -> dict[str, Any]:
    d: dict[str, Any] = {
        "combo_id": c.combo_id,
        "description": c.description,
        "gamma_w": c.gamma_w,
        "psi": c.psi,
    }
    if c.pressures:
        d["pressures"] = [_pressure_zone_to_dict(p) for p in c.pressures]
    if c.resultant_forces:
        d["resultant_forces"] = [_zone_force_to_dict(f) for f in c.resultant_forces]
    return d


# ===========================================================================
# Generazione report
# ===========================================================================

def wind_results_to_dict(
    results: WindResults,
    *,
    include_profile: bool = True,
    include_combinations: bool = True,
    include_extra: bool = False,
    project_name: str = "",
    structure_description: str = "",
) -> dict[str, Any]:
    """Converte WindResults in un dizionario strutturato per report/export.

    Args:
        results: Risultati del calcolo vento.
        include_profile: Se True, include il profilo velocità/pressione.
        include_combinations: Se True, include le combinazioni di carico.
        include_extra: Se True, include i parametri intermedi (extra).
        project_name: Nome del progetto (opzionale).
        structure_description: Descrizione della struttura (opzionale).

    Returns:
        Dizionario strutturato con tutte le sezioni del report.
    """
    report: dict[str, Any] = {
        "meta": {
            "report_type": "wind_action",
            "date": date.today().isoformat(),
            "method": results.method,
        },
    }

    if project_name:
        report["meta"]["project"] = project_name
    if structure_description:
        report["meta"]["structure"] = structure_description

    # Sezione 1: Parametri base
    report["base_parameters"] = {
        "v_b_ms": results.v_b_ms,
        "v_ref_ms": results.v_ref_ms,
        "q_b_kN_m2": results.q_b_kN_m2,
        "topography_factor": results.topography_factor,
        "structural_factor": results.structural_factor,
    }
    if results.wind_direction_deg is not None:
        report["base_parameters"]["wind_direction_deg"] = results.wind_direction_deg

    # Sezione 2: Profilo velocità/pressione
    if include_profile and results.velocity_profile:
        report["velocity_profile"] = [
            _profile_point_to_dict(p) for p in results.velocity_profile
        ]
        # Pressione di picco alla sommità
        top = results.velocity_profile[-1]
        report["peak_pressure"] = {
            "z_ref_m": top.z_m,
            "v_m_s": top.v_m_s,
            "q_p_kN_m2": top.q_kN_m2,
        }

    # Sezione 3: Pressioni per zone
    if results.pressure_zones:
        report["pressure_zones"] = [
            _pressure_zone_to_dict(pz) for pz in results.pressure_zones
        ]

    # Sezione 4: Forze risultanti
    if results.resultant_forces:
        report["resultant_forces"] = [
            _zone_force_to_dict(f) for f in results.resultant_forces
        ]
        # Riepilogo forze
        from src.wind.resultant_forces import (
            forces_to_calc_input,
        )
        friction_total = sum(fr.F_fr_kN for fr in results.friction_forces)
        report["force_summary"] = forces_to_calc_input(
            results.resultant_forces, include_friction=friction_total,
        )

    # Sezione 5: Attrito
    if results.friction_forces:
        report["friction_forces"] = [
            _friction_to_dict(fr) for fr in results.friction_forces
        ]
        report["friction_total_kN"] = round(
            sum(fr.F_fr_kN for fr in results.friction_forces), 4
        )

    # Sezione 6: Combinazioni
    if include_combinations and results.combinations:
        report["combinations"] = [
            _combination_to_dict(c) for c in results.combinations
        ]

    # Sezione 7: Avvisi
    if results.warnings:
        report["warnings"] = results.warnings

    # Sezione 8: Extra (parametri intermedi)
    if include_extra and results.extra:
        report["extra"] = results.extra

    return report


def wind_results_to_json(
    results: WindResults,
    *,
    indent: int = 2,
    **kwargs: Any,
) -> str:
    """Converte WindResults in stringa JSON formattata.

    Args:
        results: Risultati del calcolo vento.
        indent: Indentazione JSON (default 2).
        **kwargs: Argomenti passati a wind_results_to_dict().

    Returns:
        Stringa JSON formattata.
    """
    report = wind_results_to_dict(results, **kwargs)
    return json.dumps(report, indent=indent, ensure_ascii=False)


def generate_summary_table(results: WindResults) -> list[dict[str, Any]]:
    """Genera una tabella riepilogativa delle pressioni per zone.

    Utile per output tabellare (CSV, Excel, DataFrame).

    Args:
        results: Risultati del calcolo vento.

    Returns:
        Lista di dict con colonne: zone_id, description, cpe, cpi,
        we, wi, net, area, F.
    """
    rows = []
    for pz in results.pressure_zones:
        area = pz.area_m2 if pz.area_m2 > 0 else 0.0
        F = round(pz.net_kN_m2 * area, 3) if area > 0 else 0.0
        rows.append({
            "zone_id": pz.zone_id,
            "description": pz.description,
            "cpe": pz.cpe,
            "cpi": pz.cpi,
            "we_kN_m2": pz.we_kN_m2,
            "wi_kN_m2": pz.wi_kN_m2,
            "net_kN_m2": pz.net_kN_m2,
            "area_m2": area,
            "F_kN": F,
        })
    return rows


def generate_force_summary_table(results: WindResults) -> list[dict[str, Any]]:
    """Genera una tabella riepilogativa delle forze risultanti.

    Args:
        results: Risultati del calcolo vento.

    Returns:
        Lista di dict con colonne: zone_id, F_kN, direction,
        application_point_m, eccentricity_m, M_kNm.
    """
    rows = []
    for f in results.resultant_forces:
        M = round(f.F_kN * f.application_point_m, 3)
        row: dict[str, Any] = {
            "zone_id": f.zone_id,
            "F_kN": f.F_kN,
            "direction": f.direction,
            "application_point_m": f.application_point_m,
            "M_kNm": M,
        }
        if f.eccentricity_m != 0.0:
            row["eccentricity_m"] = f.eccentricity_m
        rows.append(row)
    return rows
