"""Azione sismica — OPCM 3274/2003 (4 zone, spettro elastico semplificato).

Zone sismiche OPCM3274 con ag fisso (Tab. 1):
    1: ag = 0.35g
    2: ag = 0.25g
    3: ag = 0.15g
    4: ag = 0.05g

F0 = 2.5 (fisso per tutte le zone OPCM3274).
TC* per zona: Tab. 3 OPCM3274 (valori fissi per zona).

Metodo spettrale: V_b = Sd(T_1) * W_tot / g
    Sd(T_1) = Se(T_1) / q
    Se(T_1) calcolato dal modulo ntc2018.spectrum (stessa formula base).
"""

from __future__ import annotations

from typing import Any

from .base import PianoEdificio, _base_contract, distribuzione_triangolare

_NORM_REF = "OPCM 3274/2003 Allegato 2"

# ag [g] per zona OPCM3274 (Tab. 1)
ZONE_AG: dict[int, float] = {
    1: 0.35,
    2: 0.25,
    3: 0.15,
    4: 0.05,
}

# TC* [s] fisso per zona (Tab. 3 OPCM3274, valori rappresentativi)
TC_STAR_OPCM: dict[int, float] = {
    1: 0.42,
    2: 0.37,
    3: 0.30,
    4: 0.25,
}

_F0_OPCM = 2.5
_ZONE_VALIDE = set(ZONE_AG)

_G = 9.81  # m/s²


def calcola_azione_sismica_opcm3274(
    piani: list[PianoEdificio],
    zona: int,
    T_1: float,
    cat_suolo: str = "B",
    cat_topografica: str = "T1",
    q: float = 1.5,
) -> dict[str, Any]:
    """Calcola l'azione sismica secondo OPCM3274 (spettrale).

    Args:
        piani:          lista PianoEdificio.
        zona:           zona sismica OPCM3274 (1-4).
        T_1:            periodo fondamentale dell'edificio [s].
        cat_suolo:      categoria di sottosuolo A-E (default B).
        cat_topografica: categoria topografica T1-T4 (default T1).
        q:              fattore di comportamento (default 1.5).

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

    if zona not in _ZONE_VALIDE:
        raise ValueError(
            f"Zona OPCM3274 {zona} non valida. Valori ammessi: {sorted(_ZONE_VALIDE)}"
        )

    ag_g = ZONE_AG[zona]
    TC_star = TC_STAR_OPCM[zona]
    log.append(
        f"OPCM3274: zona={zona}, ag_g={ag_g}g, F0={_F0_OPCM}, TC*={TC_star}s"
    )

    # Parametri spettrali
    cat_s = CategoriaSuolo(cat_suolo.upper())
    cat_t = CategoriaTopografica(cat_topografica.upper())
    SS = calcola_SS(ag_g, _F0_OPCM, cat_s)
    ST = calcola_ST(cat_t)
    CC = calcola_CC(cat_s, TC_star)
    TB, TC, TD = calcola_periodi(TC_star, CC, ag_g)
    log.append(
        f"cat_suolo={cat_suolo}, SS={SS:.4f}, ST={ST:.2f}, "
        f"CC={CC:.4f}, TB={TB:.3f}, TC={TC:.3f}, TD={TD:.3f}"
    )

    # Se(T_1)
    Se_ms2 = spettro_elastico(ag_g, _F0_OPCM, SS, ST, TB, TC, TD, xi=5.0, T=T_1)
    Sd_ms2 = Se_ms2 / q
    log.append(
        f"T_1={T_1}s, Se(T_1)={Se_ms2:.4f} m/s², Sd(T_1)=Se/q={Sd_ms2:.4f} m/s²"
    )

    W_tot = sum(p.W_kN for p in piani)
    F_base = Sd_ms2 * W_tot / _G
    log.append(
        f"V_b = Sd({Sd_ms2:.4f}) * W_tot({W_tot:.3f}) / g = {F_base:.3f} kN"
    )

    C_eff = F_base / W_tot if W_tot > 0 else 0.0
    distribuzione = distribuzione_triangolare(F_base, piani)

    result.update({
        "F_base_kN": round(F_base, 3),
        "C_effettivo": round(C_eff, 6),
        "metodo": "SPETTRALE",
        "distribuzione": distribuzione,
        "ag_g": ag_g,
        "Se_T1_ms2": round(Se_ms2, 4),
        "T_1_s": T_1,
        "zona": zona,
    })
    return result
