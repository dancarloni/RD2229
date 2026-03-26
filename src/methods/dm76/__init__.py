"""DM 31/12/1976 - Norme tecniche per cemento armato, precompresso e strutture metalliche.

Modulo di verifica strutturale secondo il Decreto Ministeriale 31 dicembre 1976,
metodo Tensioni Ammissibili (TA puro).

Il DM76 è l'aggiornamento consolidato del DM74, con valori tabulari identici.
È una norma storica che copre edifici costruiti fra 1976 e 1992.

Caratteristiche chiave:
- Tensioni ammissibili: σ_c,adm = Rck/4, n_omog = 15
- Metodo TA puro (γ = 1.0)
- Classi Rck: 150-400 kg/cm²
- Acciai: Fe32, Aq42, FeB32k, FeB38k, FeB44k
- Applicabile a: c.a. normale, precompresso, strutture metalliche

Exports:
- check_flessione_ta_dm76: Verifica flessione semplice
- check_pressoflessione_ta_dm76: Verifica pressoflessione
- check_taglio_ta_dm76: Verifica taglio
- check_minimi_ta_dm76: Armatura minima
"""

from .checks import (
    AllowableStressesExtracted,
    check_flessione_ta_dm76,
    check_minimi_ta_dm76,
    check_pressoflessione_ta_dm76,
    check_punzonamento_ta_dm76,
    check_taglio_ta_dm76,
    check_torsione_ta_dm76,
    get_dm76_allowable_stresses,
)

__all__ = [
    "AllowableStressesExtracted",
    "get_dm76_allowable_stresses",
    "check_flessione_ta_dm76",
    "check_pressoflessione_ta_dm76",
    "check_taglio_ta_dm76",
    "check_minimi_ta_dm76",
    "check_torsione_ta_dm76",
    "check_punzonamento_ta_dm76",
]
