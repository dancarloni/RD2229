"""Tipi e utilità comuni per le azioni sismiche multinorma.

Contratto di output comune (tutte le norme):
    esito:          "OK" | "NOT_APPLICABLE"
    norm_references: lista di riferimenti normativi
    decision_log:   lista di passaggi di calcolo
    trace:          {"run_id": uuid}
    F_base_kN:      taglio alla base [kN]
    C_effettivo:    V_b / W_tot (coefficiente sismico equivalente)
    metodo:         "STATICO_EQUIVALENTE" | "SPETTRALE"
    distribuzione:  [{piano, h_m, W_kN, F_kN}, ...]
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class PianoEdificio:
    """Dati di un piano dell'edificio per la distribuzione delle forze sismiche."""

    piano: int  # numero piano (1-based)
    h_m: float  # quota dal suolo [m]
    W_kN: float  # peso piano [kN]


def distribuzione_triangolare(
    F_base: float,
    piani: list[PianoEdificio],
) -> list[dict[str, Any]]:
    """Distribuisce F_base ai piani con legge triangolare.

    F_i = F_base * (W_i * h_i) / sum(W_j * h_j)

    Args:
        F_base: taglio alla base [kN]
        piani:  lista PianoEdificio ordinata dal basso verso l'alto

    Returns:
        Lista di dict {piano, h_m, W_kN, F_kN} con le forze distribuite.

    Raises:
        ValueError: se la lista è vuota o la somma W*h è zero.
    """
    if not piani:
        raise ValueError("Lista piani vuota")

    denominatore = sum(p.W_kN * p.h_m for p in piani)
    if denominatore <= 0:
        raise ValueError(f"Somma W*h deve essere > 0, ricevuto {denominatore}")

    return [
        {
            "piano": p.piano,
            "h_m": p.h_m,
            "W_kN": p.W_kN,
            "F_kN": round(F_base * (p.W_kN * p.h_m) / denominatore, 4),
        }
        for p in piani
    ]


def _base_contract(norm_ref: str) -> dict[str, Any]:
    """Restituisce il contratto base comune a tutte le norme."""
    return {
        "esito": "OK",
        "norm_references": [norm_ref],
        "decision_log": [],
        "trace": {"run_id": str(uuid.uuid4())},
    }
