"""Azione sismica — NTC 2008 §3.2.3 (spettro elastico, parametri utente).

Stessa formula spettrale di NTC2018 (spectrum.py); la differenza rispetto a NTC2018
è solo nel riferimento normativo e nei parametri ag/F0/TC* della griglia NTC2008
(forniti dall'utente o da un'altra sorgente).

Il modulo riusa integralmente le funzioni di src.codes.ntc2018.spectrum.

Metodo spettrale: V_b = Sd(T_1) * W_tot / g
    Sd(T_1) = Se(T_1) / q
"""

from __future__ import annotations

from typing import Any

from .base import PianoEdificio, _base_contract, distribuzione_triangolare

_NORM_REF = "NTC 2008 §3.2.3"

_G = 9.81  # m/s²


def calcola_azione_sismica_ntc2008(
    piani: list[PianoEdificio],
    ag_g: float,
    F0: float,
    TC_star: float,
    cat_suolo: str,
    cat_topografica: str,
    T_1: float,
    q: float = 1.5,
    xi: float = 5.0,
) -> dict[str, Any]:
    """Calcola l'azione sismica secondo NTC2008 (spettrale).

    Args:
        piani:          lista PianoEdificio.
        ag_g:           accelerazione al suolo a_g/g [adimensionale].
        F0:             fattore di amplificazione spettrale.
        TC_star:        periodo caratteristico TC* [s].
        cat_suolo:      categoria di sottosuolo A-E.
        cat_topografica: categoria topografica T1-T4.
        T_1:            periodo fondamentale dell'edificio [s].
        q:              fattore di comportamento (default 1.5).
        xi:             smorzamento [%] (default 5.0).

    Returns:
        Dict con contratto base + F_base_kN, C_effettivo, metodo, distribuzione,
        ag_g, Se_T1_ms2, T_1_s.
    """
    from ..ntc2018.spectrum import (
        CategoriaSuolo,
        CategoriaTopografica,
        calcola_CC,
        calcola_periodi,
        calcola_SS,
        calcola_ST,
        spettro_elastico,
    )

    result = _base_contract(_NORM_REF)
    log = result["decision_log"]

    cat_s = CategoriaSuolo(cat_suolo.upper())
    cat_t = CategoriaTopografica(cat_topografica.upper())

    SS = calcola_SS(ag_g, F0, cat_s)
    ST = calcola_ST(cat_t)
    CC = calcola_CC(cat_s, TC_star)
    TB, TC, TD = calcola_periodi(TC_star, CC, ag_g)
    log.append(
        f"NTC2008: ag_g={ag_g}g, F0={F0}, TC*={TC_star}s, "
        f"cat_suolo={cat_suolo}, SS={SS:.4f}, ST={ST:.2f}"
    )
    log.append(f"CC={CC:.4f}, TB={TB:.3f}s, TC={TC:.3f}s, TD={TD:.3f}s")

    Se_ms2 = spettro_elastico(ag_g, F0, SS, ST, TB, TC, TD, xi=xi, T=T_1)
    Sd_ms2 = Se_ms2 / q
    log.append(f"T_1={T_1}s, Se(T_1)={Se_ms2:.4f} m/s², Sd(T_1)={Sd_ms2:.4f} m/s²")

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
            "SS": round(SS, 4),
            "ST": round(ST, 4),
            "TB_s": round(TB, 4),
            "TC_s": round(TC, 4),
            "TD_s": round(TD, 4),
        }
    )
    return result
