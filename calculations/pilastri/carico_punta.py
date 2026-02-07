"""Modello per carico di punta su pilastri (concentrated load).

Questo modulo fornisce funzioni di base e strutture dati per
gestire e calcolare tensioni da carichi concentrati applicati
alla sommità di un pilastro.

Funzionalità principali (stub/minimale):
- `PointLoad` : dataclass per rappresentare un carico concentrato
- `compute_stress_concentrated(P, area)` : calcola la tensione media P/area

Il codice è volutamente semplice: serve come punto di partenza
per implementazioni storiche più dettagliate (es. distribuzione
del carico, eccentricità, verifica locali).

Esempio:
>>> from calculations.pilastri.carico_punta import compute_stress_concentrated
>>> compute_stress_concentrated(100e3, 0.02)
5000000.0
"""

from dataclasses import dataclass
from typing import Union


@dataclass
class PointLoad:
    """Rappresenta un carico concentrato.

    Attributes:
        P: forza in Newton
        e: eccentricità in metri (opzionale)
    """

    P: float
    e: float = 0.0


def compute_stress_concentrated(P: Union[int, float], area: Union[int, float]) -> float:
    """Calcola la tensione media dovuta a un carico concentrato.

    Parametri
    - P: carico concentrato (N)
    - area: area di applicazione (m^2)

    Ritorna la tensione media (Pa). Solleva ValueError se area <= 0.
    """
    if area <= 0:
        raise ValueError("L'area deve essere maggiore di zero.")
    return float(P) / float(area)


__all__ = ["PointLoad", "compute_stress_concentrated"]
