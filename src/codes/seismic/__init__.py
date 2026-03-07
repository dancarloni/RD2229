"""Azioni sismiche multinorma.

Moduli disponibili:
    base       — tipi comuni, distribuzione triangolare, contratto base
    rd2229     — coefficienti storici regionali (ante-L64/1974)
    dm92       — DM 3/6/1981 + agg. 1992 (statico equivalente)
    dm96       — DM 16/1/1996 (statico equivalente)
    opcm3274   — OPCM 3274/2003, 4 zone, spettro elastico
    ec8        — EN 1998-1 (Tipo1/Tipo2)
    ntc2008    — NTC 2008 §3.2.3 (spettro elastico, parametri utente)
    dispatcher — routing multinorma
"""

from .base import PianoEdificio, distribuzione_triangolare
from .dispatcher import calcola_azione_sismica

__all__ = [
    "PianoEdificio",
    "distribuzione_triangolare",
    "calcola_azione_sismica",
]
