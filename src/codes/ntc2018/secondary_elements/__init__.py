"""Package NTC2018 per elementi secondari.

Contiene il nucleo generico legacy e i package tipizzati delle fasi S1-S9.
"""

from . import (
    camini,
    checks,
    common,
    controsoffitti,
    facciate,
    impianti,
    models,
    parapetti,
    scaffalature,
    speciali,
    storage_adapter,
    tramezzi,
)

__all__ = [
    "models",
    "checks",
    "storage_adapter",
    "common",
    "tramezzi",
    "parapetti",
    "controsoffitti",
    "impianti",
    "facciate",
    "camini",
    "scaffalature",
    "speciali",
]
