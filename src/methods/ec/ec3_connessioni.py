"""Verifiche connessioni EC3-1-8 (bulloni e saldature) in forma compatta."""

from __future__ import annotations

from math import sqrt
from typing import Any


def verifica_bullone_taglio_ec3(
    A_b: float,
    f_ub: float,
    V_ed: float,
    gamma_m2: float = 1.25,
    alpha_v: float = 0.6,
) -> dict[str, Any]:
    """Resistenza a taglio bullone categoria A (EC3-1-8 §3.6.1)."""
    if min(A_b, f_ub, gamma_m2, alpha_v) <= 0:
        raise ValueError("Parametri bullone devono essere > 0")

    V_Rd = alpha_v * f_ub * A_b / gamma_m2
    return {
        "esito": V_ed <= V_Rd * 1.001,
        "rateo": V_ed / V_Rd if V_Rd > 0 else 0.0,
        "V_ed": V_ed,
        "V_Rd": V_Rd,
        "riferimento_normativo": "EC3-1-8 §3.6.1",
    }


def verifica_saldatura_cordone_ec3(
    a_mm: float,
    l_mm: float,
    f_u: float,
    F_ed: float,
    beta_w: float = 0.8,
    gamma_m2: float = 1.25,
) -> dict[str, Any]:
    """Resistenza saldatura a cordone d'angolo (EC3-1-8 §4.5.3)."""
    if min(a_mm, l_mm, f_u, beta_w, gamma_m2) <= 0:
        raise ValueError("Parametri saldatura devono essere > 0")

    area_gola = a_mm * l_mm
    f_vwd = beta_w * f_u / (sqrt(3.0) * gamma_m2)
    F_Rd = area_gola * f_vwd
    return {
        "esito": F_ed <= F_Rd * 1.001,
        "rateo": F_ed / F_Rd if F_Rd > 0 else 0.0,
        "F_ed": F_ed,
        "F_Rd": F_Rd,
        "riferimento_normativo": "EC3-1-8 §4.5.3",
    }
