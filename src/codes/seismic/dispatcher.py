"""Dispatcher multinorma per le azioni sismiche.

Routing di calcola_azione_sismica() sulla norma_attiva specificata nello spec.

Norme supportate:
    RD2229   — coefficienti storici regionali
    DM92     — DM 3/6/1981 + agg. 1992 (statico equivalente)
    DM96     — DM 16/1/1996 (statico equivalente)
    OPCM3274 — OPCM 3274/2003, 4 zone, spettro elastico
    EC8      — EN 1998-1 (Tipo1/Tipo2)
    NTC2008  — NTC 2008 §3.2.3 (spettro elastico)
    NTC2018  — NTC 2018 §3.2.3 (spettro elastico)

Formato spec:
    norma_attiva: str              — chiave norma (case-insensitive)
    piani:        list[dict]       — [{piano, h_m, W_kN}, ...]
    + parametri specifici per norma (zona, ag_g, T_1, cat_suolo, ...)
"""

from __future__ import annotations

from typing import Any

from .base import PianoEdificio

NORME_SUPPORTATE = frozenset({
    "RD2229", "DM92", "DM96", "OPCM3274", "EC8", "NTC2008", "NTC2018",
})


def calcola_azione_sismica(norma_attiva: str, spec: dict[str, Any]) -> dict[str, Any]:
    """Dispatcher multinorma per le azioni sismiche.

    Args:
        norma_attiva: chiave norma (RD2229 | DM92 | DM96 | OPCM3274 | EC8 |
                      NTC2008 | NTC2018), case-insensitive.
        spec:         dizionario con i parametri richiesti dalla norma.
                      Deve contenere 'piani' come lista di dict con le chiavi
                      piano, h_m, W_kN.

    Returns:
        Dict con il contratto base comune + campi specifici della norma.

    Raises:
        ValueError: se norma_attiva non è supportata.
    """
    norma = norma_attiva.upper().strip()

    if norma not in NORME_SUPPORTATE:
        raise ValueError(
            f"Norma '{norma_attiva}' non supportata. "
            f"Valori ammessi: {sorted(NORME_SUPPORTATE)}"
        )

    piani = _parse_piani(spec.get("piani", []))

    if norma == "RD2229":
        from .rd2229 import calcola_azione_sismica_rd2229
        return calcola_azione_sismica_rd2229(
            piani,
            zona=spec["zona"],
            I=float(spec.get("I", 1.0)),
        )

    if norma == "DM92":
        from .dm92 import calcola_azione_sismica_dm92
        return calcola_azione_sismica_dm92(
            piani,
            zona_sismica=int(spec["zona_sismica"]),
            I=float(spec.get("I", 1.0)),
            epsilon=float(spec.get("epsilon", 1.0)),
        )

    if norma == "DM96":
        from .dm96 import calcola_azione_sismica_dm96
        return calcola_azione_sismica_dm96(
            piani,
            zona_sismica=int(spec["zona_sismica"]),
            I=float(spec.get("I", 1.0)),
            epsilon=float(spec.get("epsilon", 1.0)),
        )

    if norma == "OPCM3274":
        from .opcm3274 import calcola_azione_sismica_opcm3274
        return calcola_azione_sismica_opcm3274(
            piani,
            zona=int(spec["zona"]),
            T_1=float(spec["T_1"]),
            cat_suolo=spec.get("cat_suolo", "B"),
            cat_topografica=spec.get("cat_topografica", "T1"),
            q=float(spec.get("q", 1.5)),
        )

    if norma == "EC8":
        from .ec8 import calcola_azione_sismica_ec8
        return calcola_azione_sismica_ec8(
            piani,
            ag_g=float(spec["ag_g"]),
            cat_suolo=spec.get("cat_suolo", "B"),
            T_1=float(spec["T_1"]),
            tipo_spettro=spec.get("tipo_spettro", "TIPO1"),
            q=float(spec.get("q", 1.5)),
            xi=float(spec.get("xi", 5.0)),
        )

    if norma == "NTC2008":
        from .ntc2008 import calcola_azione_sismica_ntc2008
        return calcola_azione_sismica_ntc2008(
            piani,
            ag_g=float(spec["ag_g"]),
            F0=float(spec["F0"]),
            TC_star=float(spec["TC_star"]),
            cat_suolo=spec.get("cat_suolo", "B"),
            cat_topografica=spec.get("cat_topografica", "T1"),
            T_1=float(spec["T_1"]),
            q=float(spec.get("q", 1.5)),
            xi=float(spec.get("xi", 5.0)),
        )

    # NTC2018
    from ..ntc2018.spectrum import (
        CategoriaSuolo,
        CategoriaTopografica,
        calcola_CC,
        calcola_periodi,
        calcola_SS,
        calcola_ST,
        spettro_elastico,
    )
    from .base import _base_contract, distribuzione_triangolare

    _NORM_REF_NTC2018 = "NTC 2018 §3.2.3"
    result = _base_contract(_NORM_REF_NTC2018)
    log = result["decision_log"]

    ag_g = float(spec["ag_g"])
    F0 = float(spec["F0"])
    TC_star = float(spec["TC_star"])
    T_1 = float(spec["T_1"])
    q = float(spec.get("q", 1.5))
    xi = float(spec.get("xi", 5.0))
    cat_s = CategoriaSuolo(spec.get("cat_suolo", "B").upper())
    cat_t = CategoriaTopografica(spec.get("cat_topografica", "T1").upper())

    SS = calcola_SS(ag_g, F0, cat_s)
    ST = calcola_ST(cat_t)
    CC = calcola_CC(cat_s, TC_star)
    TB, TC, TD = calcola_periodi(TC_star, CC, ag_g)
    log.append(
        f"NTC2018: ag_g={ag_g}g, F0={F0}, TC*={TC_star}s, "
        f"SS={SS:.4f}, ST={ST:.2f}"
    )

    _G = 9.81
    Se_ms2 = spettro_elastico(ag_g, F0, SS, ST, TB, TC, TD, xi=xi, T=T_1)
    Sd_ms2 = Se_ms2 / q
    log.append(f"T_1={T_1}s, Se(T_1)={Se_ms2:.4f} m/s², Sd={Sd_ms2:.4f} m/s²")

    W_tot = sum(p.W_kN for p in piani)
    F_base = Sd_ms2 * W_tot / _G
    C_eff = F_base / W_tot if W_tot > 0 else 0.0
    distribuzione = distribuzione_triangolare(F_base, piani)

    result.update({
        "norm_references": [_NORM_REF_NTC2018],
        "F_base_kN": round(F_base, 3),
        "C_effettivo": round(C_eff, 6),
        "metodo": "SPETTRALE",
        "distribuzione": distribuzione,
        "ag_g": ag_g,
        "Se_T1_ms2": round(Se_ms2, 4),
        "T_1_s": T_1,
    })
    return result


def _parse_piani(piani_raw: list[dict[str, Any]]) -> list[PianoEdificio]:
    """Converte una lista di dict in lista di PianoEdificio."""
    return [
        PianoEdificio(
            piano=int(p["piano"]),
            h_m=float(p["h_m"]),
            W_kN=float(p["W_kN"]),
        )
        for p in piani_raw
    ]
