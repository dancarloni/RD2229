"""
NTC 2008 — Norme tecniche per le costruzioni.

Wrapper su EN 1992-1-1 (Eurocode 2) con applicazione del Decreto.

NTC2008 applica EC2 con coefficienti parziali identici a DM92:
  - γ_c = 1.5 (calcestruzzo)
  - γ_s = 1.15 (acciaio)

Differenze dalla NTC2018:
  - Spettri di risposta differenti (§3.2)
  - Fattori di confidenza e meccanismi di collasso specifici

NTC2008 è implementata come wrapper operativo su EC2 per le verifiche di base.
"""

from .checks import VerificaNTC2008Flessione, verifica_flessione, verifica_taglio
from .combinazioni import (
    coefficiente_spettro_elastico_ntc2008,
    fattore_amplificazione_dinamica_ntc2008,
    genera_combinazioni_ntc2008,
)

__all__ = [
    "VerificaNTC2008Flessione",
    "verifica_flessione",
    "verifica_taglio",
    "coefficiente_spettro_elastico_ntc2008",
    "fattore_amplificazione_dinamica_ntc2008",
    "genera_combinazioni_ntc2008",
]
