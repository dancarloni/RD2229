"""DM 30/05/1972 - Norme tecniche per costruzioni in cemento armato.

Modulo di verifica strutturale secondo il Decreto Ministeriale 30 maggio 1972,
metodo Tensioni Ammissibili (TA puro).

Il DM72 è una norma storica a cui ricadono molti edifici costruiti negli anni '70.
È l'evoluzione del RD2229/39 con aggiornamenti alle tensioni ammissibili e alle
prescrizioni tecnologiche.

Caratteristiche chiave:
- Tensioni ammissibili: σ_c,adm = Rck/4, n_omog = 10
- Metodo TA puro (γ = 1.0)
- Applicabile a: c.a. normale, precompresso, strutture metalliche

Exports:
- check_flessione_ta_dm72: Verifica flessione semplice
- check_pressoflessione_ta_dm72: Verifica pressoflessione
- check_taglio_ta_dm72: Verifica taglio
- check_minimi_ta_dm72: Armatura minima
- verifica_stabilita_ta: Instabilità aste compresse (condiviso con RD2229)
"""

from .checks import (
    AllowableStressesExtracted,
    check_flessione_ta_dm72,
    check_minimi_ta_dm72,
    check_pressoflessione_ta_dm72,
    check_punzonamento_ta_dm72,
    check_taglio_ta_dm72,
    check_torsione_ta_dm72,
    get_dm72_allowable_stresses,
)

__all__ = [
    "AllowableStressesExtracted",
    "get_dm72_allowable_stresses",
    "check_flessione_ta_dm72",
    "check_pressoflessione_ta_dm72",
    "check_taglio_ta_dm72",
    "check_minimi_ta_dm72",
    "check_torsione_ta_dm72",
    "check_punzonamento_ta_dm72",
]
