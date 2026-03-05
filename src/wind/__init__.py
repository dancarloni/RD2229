"""src.wind – Modulo calcolo azioni del vento (NTC2018, EN 1991-1-4, CNR-DT 207)."""

from src.wind.aeroelastic import (
    AeroelasticCheckResult,
    GallopingResult,
    VortexSheddingResult,
    check_aeroelastic_effects,
)
from src.wind.cnr_dt207 import CscdDetailedResult, compute_structural_factor_detailed
from src.wind.models import (
    BuildingGeom,
    InternalPressureConfig,
    StructureGeom,
    Terrain,
    TopographyParams,
    WindDirection,
    WindSite,
)
from src.wind.outputs import (
    FrictionForce,
    PressureZoneResults,
    WindCombination,
    WindProfilePoint,
    WindResults,
    ZoneForce,
)
from src.wind.report import (
    generate_force_summary_table,
    generate_summary_table,
    wind_results_to_dict,
    wind_results_to_json,
)
from src.wind.service import WindActionService, WindConfig

__all__ = [
    # Modelli
    "BuildingGeom",
    "InternalPressureConfig",
    "StructureGeom",
    "Terrain",
    "TopographyParams",
    "WindDirection",
    "WindSite",
    # Output
    "FrictionForce",
    "PressureZoneResults",
    "WindCombination",
    "WindProfilePoint",
    "WindResults",
    "ZoneForce",
    # Servizio
    "WindActionService",
    "WindConfig",
    # CNR-DT 207
    "CscdDetailedResult",
    "compute_structural_factor_detailed",
    # Aeroelastico
    "AeroelasticCheckResult",
    "GallopingResult",
    "VortexSheddingResult",
    "check_aeroelastic_effects",
    # Report
    "generate_force_summary_table",
    "generate_summary_table",
    "wind_results_to_dict",
    "wind_results_to_json",
]
