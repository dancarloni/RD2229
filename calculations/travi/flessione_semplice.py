"""Stub: calcolo flessione semplice (schema)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FlessioneRisultato:
    momento: float
    sforzo: float


def calcola_flessione_semplice(b: float, d: float, momento: float) -> FlessioneRisultato:
    """Placeholder: implementare formula storica."""
    # valore fittizio
    sforzo = momento / (b * d**2 / 6.0)
    return FlessioneRisultato(momento=momento, sforzo=sforzo)

