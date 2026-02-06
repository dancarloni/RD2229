"""
Bas adapter: lightweight translation of key routines from Visual Basic modules
(PrincipCA_TA.bas and CA_SLU.bas) for torsion and deviated bending.

This module exposes functions that compute torsion checks and deviated-bending
based results using formulas and structure inspired by the .bas code found in
visual_basic/PrincipCA_TA.bas and visual_basic/CA_SLU.bas.

Note: This is a pragmatic, readable translation focused on the formulas needed
for comparison with the existing Python implementations: it returns a
structured dict with numeric results and messages so it can be displayed in a
comparator GUI and compared with TA/SLU implementations.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, Optional

from core.verification_core import LoadCase, MaterialProperties, ReinforcementLayer, SectionGeometry

logger = logging.getLogger(__name__)


def _rectangular_Psi(aa: float, bb: float) -> float:
    # Psi = 3 + 2.6 / (0.45 + aa/bb)  (from PrincipCA_TA.bas)
    if bb == 0:
        return 3.0
    return 3.0 + 2.6 / (0.45 + aa / bb)


def bas_torsion_verification(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    reinforcement_compressed: ReinforcementLayer,
    material: MaterialProperties,
    loads: LoadCase,
    method: str = "TA",
) -> Dict[str, Any]:
    """
    Compute torsion verification values emulating PrincipCA_TA.bas routines.

    Returns a dict with keys: 'Taux_max', 'A', 'p', 'Al_to', 'Pst_to', 'Mtu1', 'Mtu2', 'Mtu3', 'Mtu', 'messages', 'ok'
    """
    B = section.width
    H = section.height
    Delta = 0.0  # copriferro + half bar diam, in .bas it's Cf + Df/2; we don't have Cf here
    # Use conservative default Delta 4 mm = 0.4 cm if not available
    Delta = 0.4

    results: Dict[str, Any] = {}
    messages = []

    Mx = loads.Mx
    Ty = loads.Tx  # note: mapping differences between variable names
    Tz = loads.Ty

    # determine A and p (area of resistive tube and perimeter) following .bas
    if abs(Mx) < 1e-12:
        messages.append("Mx = 0 -> torsion not active")
        results.update({"messages": messages, "ok": True})
        return results

    # Rectangular case
    b1 = B - 2 * Delta
    H1 = H - 2 * Delta
    A = max(b1, 0.0) * max(H1, 0.0)
    p = 2 * max(b1, 0.0) + 2 * max(H1, 0.0)

    # 1. Taux_max (TA formula) - use the rectangular branch
    # If B <= H then aa=H bb=B else swapped
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

    # default torsion armature parameters (crafted from .bas formulas)
    # Al_to: longitudinal torsion armature area required (cm^2)
    # Pst_to: spacing of transverse torsion armature
    # We translate both TA and SLU branches
    if method.upper() == "TA":
        # tau limits (TauC0/TauC1) derive from material variables; approximate
        TauC0 = getattr(material, "TauC0", 0.0)
        TauC1 = getattr(material, "TauC1", 0.0)
        TauC1_t = TauC1 * 1.1 if (abs(Ty) > 0 or abs(Tz) > 0) else TauC1

        # compute Sigf_l and Sigf_st for verification when CalcVerif True
        # We approximate Sigfa as allowable steel stress from material (sigma_fa)
        sigma_fa = getattr(
            material, "fyk", 450.0
        )  # MPa like, but consistent with code expectations
        # Convert to kg/cm2 if small
        if sigma_fa < 2000:
            sigma_fa = sigma_fa * 10.197

        if TauC1_t == 0:
            messages.append("TA torsion thresholds not provided; only outputs Taux_max")
        else:
            # compute armature needed (approx)
            # Al_to (cm2) = Abs(Mx) * p / (2 * A * Sigfa * tan(teta)) ; teta default assume 30deg
            teta = math.radians(getattr(material, "teta_to_deg", 30.0))
            if A > 0 and math.tan(teta) != 0:
                Al_to = abs(Mx) * p / (2.0 * A * sigma_fa * math.tan(teta))
            else:
                Al_to = 0.0
            # Pst_to compute similarly (approx)
            Asw_to = getattr(material, "Asw_to", 1.0)
            alfa_to = math.radians(getattr(material, "alfa_to_deg", 30.0))
            if Asw_to * math.sin(math.pi - teta - alfa_to) != 0:
                Pst_to = 2.0 * A * Asw_to * sigma_fa * math.sin(math.pi - teta - alfa_to) / abs(Mx)
            else:
                Pst_to = 0.0

            results.update({"Al_to": Al_to, "Pst_to": Pst_to})

    elif method.upper() in ("SLU", "SL08", "SL18"):
        # compute Mtu1, Mtu2, Mtu3 as in PrincipCA_TA.bas
        # Mtu3 = 2*A*t*(0.5*fcd)*sin(teta)*cos(teta)  where t ~ Asez/Psez (we don't have Asez/Psez; approximate)
        # Use t ~ H/4 as approximation
        t = max(section.height / 4.0, 2 * Delta)
        fcd = getattr(material, "fcd", getattr(material, "fck", 25.0))
        teta = math.radians(getattr(material, "teta_to_deg", 30.0))
        Mtu3 = 2.0 * A * t * (0.5 * fcd) * math.sin(teta) * math.cos(teta)

        # Mtu1 = 2 * Al_to * fyd * A / p * tan(teta)
        # Mtu2 = 2 * Asw_to * fyd * A * sin(pi - teta - alfa_to) / (Pst_to * sin(teta))
        fyd = getattr(material, "fyd", getattr(material, "fyk", 450.0))
        if fyd < 2000:
            fyd = fyd * 10.197
        Al_to = results.get(
            "Al_to", max(0.001, abs(Mx) * p / (2.0 * fyd * A * max(math.tan(teta), 1e-6)))
        )
        Asw_to = getattr(material, "Asw_to", 1.0)
        alfa_to = math.radians(getattr(material, "alfa_to_deg", 30.0))
        Pst_to = results.get(
            "Pst_to",
            max(
                1.0,
                2
                * Asw_to
                * fyd
                * A
                * math.sin(math.pi - teta - alfa_to)
                / (abs(Mx) * max(math.sin(teta), 1e-6)),
            ),
        )

        Mtu1 = 2.0 * Al_to * fyd * A / p * math.tan(teta)
        # protect division
        if Pst_to * math.sin(teta) != 0.0:
            Mtu2 = (
                2.0
                * Asw_to
                * fyd
                * A
                * math.sin(math.pi - teta - alfa_to)
                / (Pst_to * math.sin(teta))
            )
        else:
            Mtu2 = 0.0

        # Mtu is min of three
        Mtu = min(Mtu1, Mtu2, Mtu3)
        results.update(
            {"Mtu1": Mtu1, "Mtu2": Mtu2, "Mtu3": Mtu3, "Mtu": Mtu, "Al_to": Al_to, "Pst_to": Pst_to}
        )

    # final messages and pass/fail
    ok = True
    if method.upper() == "TA":
        # simple criteria: if TauC1t available and Taux_max > TauC1t -> fail
        TauC1 = getattr(material, "TauC1", 0.0)
        TauC1_t = TauC1 * 1.1
        if TauC1_t > 0 and Taux_max > TauC1_t:
            ok = False
            messages.append("Torsione: Taux_max exceeds TA threshold")
    else:
        Mx_abs = abs(Mx)
        if "Mtu" in results and results["Mtu"] > 0 and Mx_abs > results["Mtu"]:
            ok = False
            messages.append(f'Torsione SLU: Mx={Mx_abs:.3f} > Mtu={results["Mtu"]:.3f}')

    results["messages"] = messages
    results["ok"] = ok
    return results
