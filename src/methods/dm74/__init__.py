"""DM 30/05/1974 - Norme tecniche per cemento armato, precompresso e strutture metalliche.

Modulo di verifica strutturale secondo il Decreto Ministeriale 30 maggio 1974,
metodo Tensioni Ammissibili (TA puro).

Il DM74 è una norma storica che copre edifici costruiti fra 1974 e 1992.
Evoluzione del DM72 con l'importante cambiamento del coefficiente di omogenizzazione
da n=10 a n=15.

Caratteristiche chiave:
- Tensioni ammissibili: σ_c,adm = Rck/4, n_omog = 15 (differenza chiave da DM72)
- Metodo TA puro (γ = 1.0)
- Classi Rck: 150-400 kg/cm²
- Acciai: Fe32, Aq42, FeB32k, FeB38k, FeB44k
- Applicabile a: c.a. normale, precompresso, strutture metalliche

Exports:
- check_flessione_ta_dm74: Verifica flessione semplice
- check_pressoflessione_ta_dm74: Verifica pressoflessione
- check_taglio_ta_dm74: Verifica taglio
- check_minimi_ta_dm74: Armatura minima
"""

from .checks import (
    AllowableStressesExtracted,
    check_flessione_ta_dm74,
    check_minimi_ta_dm74,
    check_pressoflessione_ta_dm74,
    check_punzonamento_ta_dm74,
    check_taglio_ta_dm74,
    check_torsione_ta_dm74,
    get_dm74_allowable_stresses,
)

__all__ = [
    "AllowableStressesExtracted",
    "get_dm74_allowable_stresses",
    "check_flessione_ta_dm74",
    "check_pressoflessione_ta_dm74",
    "check_taglio_ta_dm74",
    "check_minimi_ta_dm74",
    "check_torsione_ta_dm74",
    "check_punzonamento_ta_dm74",
]
