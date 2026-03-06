"""Azione sismica — DM 16/1/1996 (metodo statico equivalente).

Stessa formula del DM92; i coefficienti C sono identici.
La differenza rispetto al DM92 riguarda i confini di zona (aggiornati nel 1996)
e il riferimento normativo.

Formula: F_h = C * I * epsilon * W_tot
    C:       coefficiente sismico per zona (Tab. 1 DM 16/1/1996)
    I:       coefficiente di importanza
    epsilon: coefficiente di fondazione (default 1.0)
    W_tot:   peso totale dell'edificio [kN]

Zone sismiche DM96:
    1: C = 0.10  (alta sismicità)
    2: C = 0.07  (media sismicità)
    3: C = 0.04  (bassa sismicità)
"""

from __future__ import annotations

from typing import Any

from .base import PianoEdificio, _base_contract, distribuzione_triangolare

_NORM_REF = "DM 16/01/1996 §3.2"

COEFF_C: dict[int, float] = {
    1: 0.10,
    2: 0.07,
    3: 0.04,
}

_ZONE_VALIDE = set(COEFF_C)


def calcola_azione_sismica_dm96(
    piani: list[PianoEdificio],
    zona_sismica: int,
    I: float = 1.0,  # noqa: E741
    epsilon: float = 1.0,
) -> dict[str, Any]:
    """Calcola l'azione sismica secondo DM96 (statico equivalente).

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
            f"Zona sismica {zona_sismica} non valida per DM96. "
            f"Valori ammessi: {sorted(_ZONE_VALIDE)}"
        )

    C = COEFF_C[zona_sismica]
    W_tot = sum(p.W_kN for p in piani)

    log.append(f"DM96: zona={zona_sismica}, C={C}, I={I}, epsilon={epsilon}")
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
