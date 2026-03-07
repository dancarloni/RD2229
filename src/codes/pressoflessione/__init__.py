"""Package pressoflessione deviata multinorma (FASE J).

Re-export principali per uso esterno.
"""

from .base import (
    DominioNMy,
    PressoflessResult,
    PressoflessSpec,
    calcola_omogenizzata_biassiale,
    crea_armatura_rettangolare,
)
from .dispatcher import calcola_pressoflessione_deviata
from .dominio import (
    calcola_dominio_3d,
    disegna_dominio_2d_mxmy,
    disegna_dominio_2d_nm,
    disegna_dominio_3d,
)
from .instabilita_biassiale import amplifica_momenti_biassiale
from .ta_cls import (
    calcola_M_Rd_ta,
    verifica_bresler_ta,
    verifica_pressofless_ta_cls,
    verifica_sovrapposizione_elastica,
)

__all__ = [
    "PressoflessSpec",
    "PressoflessResult",
    "DominioNMy",
    "calcola_omogenizzata_biassiale",
    "crea_armatura_rettangolare",
    "calcola_pressoflessione_deviata",
    "calcola_dominio_3d",
    "disegna_dominio_3d",
    "disegna_dominio_2d_mxmy",
    "disegna_dominio_2d_nm",
    "amplifica_momenti_biassiale",
    "calcola_M_Rd_ta",
    "verifica_bresler_ta",
    "verifica_pressofless_ta_cls",
    "verifica_sovrapposizione_elastica",
]
