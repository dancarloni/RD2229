"""
DM 14/02/1992 — Normativa italiana per il calcolo strutturale.

Estende il metodo delle tensioni ammissibili (TA) e stati limite (SL).
Valido per strutture in cemento armato, acciaio e muratura.

Copre:
  - Flessione semplice (TA + SL)
  - Pressoflessione (N-M)
  - Taglio
  - Torsione

Coefficienti parziali: γ_c = 1.6, γ_s = 1.15 (allineati ai cataloghi DM92)
Conversione: R_ck (cubica) = f_ck (cilindrica) / 0.83
Unità: tensioni in kg/cm², geometria in cm
"""

from .checks import (
    VerificaDM92Flessione,
    VerificaDM92Pressoflessione,
    VerificaDM92Taglio,
    VerificaDM92Torsione,
    kgcm2_to_mpa,
    mpa_to_kgcm2,
    rck_to_fck,
    verifica_flessione_sl,
    verifica_flessione_ta,
    verifica_pressoflessione,
    verifica_taglio,
    verifica_torsione,
)

__all__ = [
    "VerificaDM92Flessione",
    "VerificaDM92Pressoflessione",
    "VerificaDM92Taglio",
    "VerificaDM92Torsione",
    "verifica_flessione_ta",
    "verifica_flessione_sl",
    "verifica_pressoflessione",
    "verifica_taglio",
    "verifica_torsione",
    "mpa_to_kgcm2",
    "kgcm2_to_mpa",
    "rck_to_fck",
]
