"""Package section_params — parametri statici sezione c.a. (FASE I).

Re-esporta le interfacce principali.
"""

from .composita import (
    DatiIPE,
    IPE_TABLE,
    calcola_sezione_composta,
    calcola_tensioni_sle_composita,
)
from .norme_n import (
    NORME_SUPPORTATE,
    NormaHnParams,
    RD2229_N_OPTIONS,
    get_n_for_norm,
)
from .omogenizzata import (
    BarraArmatura,
    calcola_asse_neutro_fessurato,
    calcola_parametri_sezione_completi,
    calcola_sezione_omogenizzata,
    calcola_tensioni_sle,
)

__all__ = [
    # norme_n
    "NORME_SUPPORTATE",
    "NormaHnParams",
    "RD2229_N_OPTIONS",
    "get_n_for_norm",
    # omogenizzata
    "BarraArmatura",
    "calcola_asse_neutro_fessurato",
    "calcola_parametri_sezione_completi",
    "calcola_sezione_omogenizzata",
    "calcola_tensioni_sle",
    # composita
    "DatiIPE",
    "IPE_TABLE",
    "calcola_sezione_composta",
    "calcola_tensioni_sle_composita",
]
