"""Historical TA (Tensioni Ammissibili) extraction from legacy VBA.
This package provides modular Python implementations of core routines
for section homogenization and TA verifications translated from
PrincipCA_TA.bas (see comments in modules for mappings).
"""

from .checks import AllowableCheckResult, AllowableStresses, check_allowable_stresses_ta
from .geometry import SectionGeometry, SectionProperties, compute_section_properties
from .materials import ConcreteLawTA, SteelLawTA
from .stress import LoadState, StressResult, compute_normal_stresses_ta

__all__ = [
    "SectionGeometry",
    "SectionProperties",
    "compute_section_properties",
    "ConcreteLawTA",
    "SteelLawTA",
    "LoadState",
    "StressResult",
    "compute_normal_stresses_ta",
    "AllowableStresses",
    "AllowableCheckResult",
    "check_allowable_stresses_ta",
]
