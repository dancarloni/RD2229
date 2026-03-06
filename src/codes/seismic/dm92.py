"""Azione sismica — DM 3/6/1981 e aggiornamento 1992 (metodo statico equivalente).

Formula: F_h = C * I * epsilon * W_tot
    C:       coefficiente sismico per zona (Tab. 1 DM92)
    I:       coefficiente di importanza
    epsilon: coefficiente di fondazione (default 1.0)
    W_tot:   peso totale dell'edificio [kN]

Zone sismiche DM92:
    1: C = 0.10  (alta sismicità)
    2: C = 0.07  (media sismicità)
    3: C = 0.04  (bassa sismicità)
"""

from __future__ import annotations

from typing import Any

from .base import PianoEdificio, _base_contract, distribuzione_triangolare

_NORM_REF = "DM 3/6/1981 — agg. 1992 §7"

COEFF_C: dict[int, float] = {
    1: 0.10,
    2: 0.07,
    3: 0.04,
}

_ZONE_VALIDE = set(COEFF_C)


def calcola_azione_sismica_dm92(
    piani: list[PianoEdificio],
    zona_sismica: int,
    I: float = 1.0,  # noqa: E741
    epsilon: float = 1.0,
) -> dict[str, Any]:
    """Calcola l'azione sismica secondo DM92 (statico equivalente).

    Args:
        piani:        lista PianoEdificio.
        zona_sismica: zona sismica 1, 2 o 3.
        I:            coefficiente di importanza (default 1.0).
        epsilon:      coefficiente di fondazione (default 1.0).

    Returns:
        Dict con contratto base + F_base_kN, C_effettivo, metodo, distribuzione.
    """
    result = _base_contract(_NORM_REF)
    log = result["decision_log"]

    if zona_sismica not in _ZONE_VALIDE:
        raise ValueError(
            f"Zona sismica {zona_sismica} non valida per DM92. "
            f"Valori ammessi: {sorted(_ZONE_VALIDE)}"
        )

    C = COEFF_C[zona_sismica]
    W_tot = sum(p.W_kN for p in piani)

    log.append(f"DM92: zona={zona_sismica}, C={C}, I={I}, epsilon={epsilon}")
    F_base = C * I * epsilon * W_tot
    log.append(
        f"F_base = C({C}) * I({I}) * eps({epsilon}) * W_tot({W_tot:.3f}) "
        f"= {F_base:.3f} kN"
    )

    C_eff = F_base / W_tot if W_tot > 0 else 0.0
    distribuzione = distribuzione_triangolare(F_base, piani)

    result.update({
        "F_base_kN": round(F_base, 3),
        "C_effettivo": round(C_eff, 6),
        "metodo": "STATICO_EQUIVALENTE",
        "distribuzione": distribuzione,
        "zona_sismica": zona_sismica,
        "C": C,
    })
    return result
