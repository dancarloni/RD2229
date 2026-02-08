"""Bas adapter: lightweight translation of key routines from Visual Basic modules
(PrincipCA_TA.bas and CA_SLU.bas) for torsion and deviated bending.

This module exposes functions that compute torsion checks and deviated-bending
based results using formulas and structure inspired by the .bas code found in
visual_basic/PrincipCA_TA.bas and visual_basic/CA_SLU.bas.

Note: This is a pragmatic, readable translation focused on the formulas needed
for comparison with the existing Python implementations: it returns a
structured dict with numeric results and messages so it can be displayed in a
comparator GUI and compared with TA/SLU implementations.

The adapter contains some simplified argument lists that mirror the original
VB code and uses conservative error handling; suppress warnings about unused
arguments and broad exception captures.
"""

# pylint: disable=unused-argument, broad-exception-caught

from __future__ import annotations

import logging
import math
from typing import Any

from core.verification_core import (
    LoadCase,
    MaterialProperties,
    ReinforcementLayer,
    SectionGeometry,
)

logger = logging.getLogger(__name__)


def _rectangular_Psi(aa: float, bb: float) -> float:
    # Psi = 3 + 2.6 / (0.45 + aa/bb)  (from PrincipCA_TA.bas)
    if bb == 0:
        return 3.0
    return 3.0 + 2.6 / (0.45 + aa / bb)


def _area_and_perimeter(sec: SectionGeometry, delta: float) -> tuple[float, float, float, float]:
    b = sec.width
    h = sec.height
    b1 = b - 2 * delta
    h1 = h - 2 * delta
    A_loc = max(b1, 0.0) * max(h1, 0.0)
    p_loc = 2 * max(b1, 0.0) + 2 * max(h1, 0.0)
    return A_loc, p_loc, b, h


def _compute_ta_branch(
    results_loc: dict[str, Any],
    mat: MaterialProperties,
    Mx_loc: float,
    p_loc: float,
    A_loc: float,
    Ty_loc: float,
    Tz_loc: float,
) -> None:
    TauC1 = getattr(mat, "TauC1", 0.0)
    TauC1_t = TauC1 * 1.1 if (abs(Ty_loc) > 0 or abs(Tz_loc) > 0) else TauC1

    sigma_fa = getattr(mat, "fyk", 450.0)
    if sigma_fa < 2000:
        sigma_fa = sigma_fa * 10.197

    if TauC1_t == 0:
        results_loc.setdefault("messages", []).append(
            "TA torsion thresholds not provided; only outputs Taux_max"
        )
        return

    teta = math.radians(getattr(mat, "teta_to_deg", 30.0))
    if A_loc > 0 and math.tan(teta) != 0:
        Al_to = abs(Mx_loc) * p_loc / (2.0 * A_loc * sigma_fa * math.tan(teta))
    else:
        Al_to = 0.0

    Asw_to = getattr(mat, "Asw_to", 1.0)
    alfa_to = math.radians(getattr(mat, "alfa_to_deg", 30.0))
    if Asw_to * math.sin(math.pi - teta - alfa_to) != 0:
        Pst_to = 2.0 * A_loc * Asw_to * sigma_fa * math.sin(math.pi - teta - alfa_to) / abs(Mx_loc)
    else:
        Pst_to = 0.0

    results_loc.update({"Al_to": Al_to, "Pst_to": Pst_to})


def _compute_slu_branch(
    results_loc: dict[str, Any],
    mat: MaterialProperties,
    Mx_loc: float,
    A_loc: float,
    p_loc: float,
    sec: SectionGeometry,
) -> None:
    delta_loc = 0.4
    t_loc = max(sec.height / 4.0, 2 * delta_loc)
    fcd = getattr(mat, "fcd", getattr(mat, "fck", 25.0))
    teta = math.radians(getattr(mat, "teta_to_deg", 30.0))
    Mtu3 = 2.0 * A_loc * t_loc * (0.5 * fcd) * math.sin(teta) * math.cos(teta)

    fyd = getattr(mat, "fyd", getattr(mat, "fyk", 450.0))
    if fyd < 2000:
        fyd = fyd * 10.197

    Al_to = results_loc.get(
        "Al_to", max(0.001, abs(Mx_loc) * p_loc / (2.0 * fyd * A_loc * max(math.tan(teta), 1e-6)))
    )
    Asw_to = getattr(mat, "Asw_to", 1.0)
    alfa_to = math.radians(getattr(mat, "alfa_to_deg", 30.0))
    Pst_to = results_loc.get(
        "Pst_to",
        max(
            1.0,
            2
            * Asw_to
            * fyd
            * A_loc
            * math.sin(math.pi - teta - alfa_to)
            / (abs(Mx_loc) * max(math.sin(teta), 1e-6)),
        ),
    )

    Mtu1 = 2.0 * Al_to * fyd * A_loc / p_loc * math.tan(teta)
    if Pst_to * math.sin(teta) != 0.0:
        Mtu2 = (
            2.0
            * Asw_to
            * fyd
            * A_loc
            * math.sin(math.pi - teta - alfa_to)
            / (Pst_to * math.sin(teta))
        )
    else:
        Mtu2 = 0.0

    Mtu = min(Mtu1, Mtu2, Mtu3)
    results_loc.update(
        {"Mtu1": Mtu1, "Mtu2": Mtu2, "Mtu3": Mtu3, "Mtu": Mtu, "Al_to": Al_to, "Pst_to": Pst_to}
    )


def _finalize_torsion(
    results_loc: dict[str, Any],
    mat: MaterialProperties,
    Mx_loc: float,
    Taux_max_loc: float,
    method_loc: str,
) -> None:
    ok_loc = True
    messages_loc = results_loc.get("messages", [])
    if method_loc.upper() == "TA":
        TauC1 = getattr(mat, "TauC1", 0.0)
        TauC1_t = TauC1 * 1.1
        if TauC1_t > 0 and Taux_max_loc > TauC1_t:
            ok_loc = False
            messages_loc.append("Torsione: Taux_max exceeds TA threshold")
    else:
        Mx_abs = abs(Mx_loc)
        if "Mtu" in results_loc and results_loc["Mtu"] > 0 and Mx_abs > results_loc["Mtu"]:
            ok_loc = False
            messages_loc.append(f'Torsione SLU: Mx={Mx_abs:.3f} > Mtu={results_loc["Mtu"]:.3f}')
    results_loc["messages"] = messages_loc
    results_loc["ok"] = ok_loc


def bas_torsion_verification(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    reinforcement_compressed: ReinforcementLayer,
    material: MaterialProperties,
    loads: LoadCase,
    method: str = "TA",
) -> dict[str, Any]:
    """Compute torsion verification values emulating PrincipCA_TA.bas routines.

    Returns a dict with keys describing the numeric outputs and messages. Typical
    keys include: 'Taux_max', 'A', 'p', 'Al_to', 'Pst_to', 'Mtu1', 'Mtu2',
    'Mtu3', 'Mtu', 'messages', 'ok'.
    """
    # nested helpers removed (moved to module-level counterparts)

    # main
    Delta = 0.4

    results: dict[str, Any] = {}

    Mx = loads.Mx
    Ty = loads.Tx  # note: mapping differences between variable names
    Tz = loads.Ty

    if abs(Mx) < 1e-12:
        results.update({"messages": ["Mx = 0 -> torsion not active"], "ok": True})
        return results

    A, p, B, H = _area_and_perimeter(section, Delta)

    if B <= H:
        aa = H
        bb = B
    else:
        aa = B
        bb = H
    Psi = _rectangular_Psi(aa, bb)
    Taux_max = Psi * abs(Mx) / (aa * bb**2) if aa * bb**2 != 0 else 0.0

    results["Taux_max"] = Taux_max
    results["A"] = A
    results["p"] = p

    if method.upper() == "TA":
        _compute_ta_branch(results, material, Mx, p, A, Ty, Tz)
    elif method.upper() in ("SLU", "SL08", "SL18"):
        _compute_slu_branch(results, material, Mx, A, p, section)

    _finalize_torsion(results, material, Mx, Taux_max, method)
    return results
