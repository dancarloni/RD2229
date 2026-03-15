"""Utility per conversioni unità usate nel calcolo strutturale.

Questo modulo è progettato per essere riutilizzabile da più moduli (solai, scale, verifiche, ecc.).
"""

from __future__ import annotations

_KGF_TO_KN = 0.00980665
_KGCM2_TO_MPA = 0.0980665
_CM_TO_M = 0.01


def kgf_to_kn(value: float) -> float:
    """Convert kgf in kN."""
    return value * _KGF_TO_KN


def kgf_m2_to_kn_m2(value: float) -> float:
    """Convert kgf/m^2 in kN/m^2."""
    return value * _KGF_TO_KN


def kgcm2_to_mpa(value: float) -> float:
    """Convert kgf/cm² in MPa."""
    return value * _KGCM2_TO_MPA


def cm_to_m(value: float) -> float:
    """Convert cm in m."""
    return value * _CM_TO_M
