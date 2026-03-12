"""Azione sismica — EN 1998-1 (Eurocodice 8, spettro elastico Tipo1/Tipo2).

Parametri spettrali (S, TB, TC, TD) fissi per categoria di sottosuolo
(Tab. 3.2 EN 1998-1:2004).

F0 = 2.5 (equivalente all'amplificazione di picco in EC8, con eta=1).

Metodo spettrale: V_b = Sd(T_1) * W_tot / g
    Sd(T_1) = Se(T_1) / q
    Se(T_1): formula a 4 rami con i parametri EC8.
"""

from __future__ import annotations

import math
from typing import Any

from .base import PianoEdificio, _base_contract, distribuzione_triangolare

_NORM_REF = "EN 1998-1:2004 §3.2.2"

# (S, TB [s], TC [s], TD [s]) per categoria di sottosuolo
EC8_TYPE1: dict[str, tuple[float, float, float, float]] = {
    "A": (1.00, 0.15, 0.40, 2.0),
    "B": (1.20, 0.15, 0.50, 2.0),
    "C": (1.15, 0.20, 0.60, 2.0),
    "D": (1.35, 0.20, 0.80, 2.0),
    "E": (1.40, 0.15, 0.50, 2.0),
}

EC8_TYPE2: dict[str, tuple[float, float, float, float]] = {
    "A": (1.00, 0.05, 0.25, 1.2),
    "B": (1.35, 0.05, 0.25, 1.2),
    "C": (1.50, 0.10, 0.25, 1.2),
    "D": (1.80, 0.10, 0.30, 1.2),
    "E": (1.60, 0.05, 0.25, 1.2),
}

_TIPI_VALIDI = {"TIPO1", "TIPO2"}
_G = 9.81  # m/s²


def _spettro_elastico_ec8(
    ag_g: float,
    S: float,
    TB: float,
    TC: float,
    TD: float,
    xi: float,
    T: float,
) -> float:
    """Spettro elastico EN 1998-1 eq. 3.2 a 4 rami.

    eta = max(sqrt(10 / (5 + xi)), 0.55)
    """
    ag = ag_g * _G
    eta = max(math.sqrt(10.0 / (5.0 + xi)), 0.55)
    F0 = 2.5  # amplificazione di picco EN 1998-1

    if T <= 0:
        return ag * S * (1.0 + T / TB * (eta * F0 - 1.0)) if TB > 0 else ag * S * eta * F0
    if T < TB:
        return ag * S * (1.0 + T / TB * (eta * F0 - 1.0))
    if T <= TC:
        return ag * S * eta * F0
    if T <= TD:
        return ag * S * eta * F0 * TC / T
    return ag * S * eta * F0 * TC * TD / T**2


def calcola_azione_sismica_ec8(
    piani: list[PianoEdificio],
    ag_g: float,
    cat_suolo: str,
    T_1: float,
    tipo_spettro: str = "TIPO1",
    q: float = 1.5,
    xi: float = 5.0,
) -> dict[str, Any]:
    """Calcola l'azione sismica secondo EC8 (spettrale).

    Args:
        piani:        lista PianoEdificio.
        ag_g:         accelerazione al suolo a_g/g [adimensionale].
        cat_suolo:    categoria di sottosuolo A-E (EN 1998-1 Tab. 3.1).
        T_1:          periodo fondamentale dell'edificio [s].
        tipo_spettro: "TIPO1" (default) o "TIPO2".
        q:            fattore di comportamento (default 1.5).
        xi:           smorzamento [%] (default 5.0).

    Returns:
        Dict con contratto base + F_base_kN, C_effettivo, metodo, distribuzione,
        ag_g, Se_T1_ms2, T_1_s.
    """
    result = _base_contract(_NORM_REF)
    log = result["decision_log"]

    tipo_upper = tipo_spettro.upper()
    if tipo_upper not in _TIPI_VALIDI:
        raise ValueError(
            f"tipo_spettro '{tipo_spettro}' non valido. Valori ammessi: {sorted(_TIPI_VALIDI)}"
        )

    cat_upper = cat_suolo.upper()
    tabella = EC8_TYPE1 if tipo_upper == "TIPO1" else EC8_TYPE2
    if cat_upper not in tabella:
        raise ValueError(
            f"Categoria suolo '{cat_suolo}' non valida per EC8. "
            f"Valori ammessi: {sorted(tabella)}"
        )

    S, TB, TC, TD = tabella[cat_upper]
    log.append(f"EC8 {tipo_upper}: cat_suolo={cat_upper}, " f"S={S}, TB={TB}, TC={TC}, TD={TD}")
    log.append(f"ag_g={ag_g}g, T_1={T_1}s, q={q}, xi={xi}%")

    Se_ms2 = _spettro_elastico_ec8(ag_g, S, TB, TC, TD, xi, T_1)
    Sd_ms2 = Se_ms2 / q
    log.append(f"Se(T_1)={Se_ms2:.4f} m/s², Sd(T_1)=Se/q={Sd_ms2:.4f} m/s²")

    W_tot = sum(p.W_kN for p in piani)
    F_base = Sd_ms2 * W_tot / _G
    log.append(f"V_b = Sd({Sd_ms2:.4f}) * W_tot({W_tot:.3f}) / g = {F_base:.3f} kN")

    C_eff = F_base / W_tot if W_tot > 0 else 0.0
    distribuzione = distribuzione_triangolare(F_base, piani)

    result.update(
        {
            "F_base_kN": round(F_base, 3),
            "C_effettivo": round(C_eff, 6),
            "metodo": "SPETTRALE",
            "distribuzione": distribuzione,
            "ag_g": ag_g,
            "Se_T1_ms2": round(Se_ms2, 4),
            "T_1_s": T_1,
            "tipo_spettro": tipo_upper,
            "cat_suolo": cat_upper,
            "S": S,
        }
    )
    return result
