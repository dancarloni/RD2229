from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .stress import StressResult

# Mapping: VB VerifResistCA_TA and LimitiArmaturaLong (partial)


@dataclass
class AllowableStresses:
    sigma_c_allow: float  # Sigca
    sigma_s_allow: float  # Sigfa
    sigma_c_med_allow: float  # Sigcar


@dataclass
class AllowableCheckResult:
    ok: bool
    check_concrete: bool
    check_steel: bool
    check_mean: bool
    messages: List[str]


def check_allowable_stresses_ta(stresses: StressResult, limits: AllowableStresses) -> AllowableCheckResult:
    messages = []
    check_concrete = abs(stresses.sigma_c_max) <= limits.sigma_c_allow
    if not check_concrete:
        messages.append(f"Concrete stress exceed limit: |{stresses.sigma_c_max:.2f}| > {limits.sigma_c_allow:.2f}")
    check_steel = abs(stresses.sigma_s_max) <= limits.sigma_s_allow
    if not check_steel:
        messages.append(f"Steel stress exceed limit: |{stresses.sigma_s_max:.2f}| > {limits.sigma_s_allow:.2f}")
    check_mean = abs(stresses.sigma_c_med) <= limits.sigma_c_med_allow
    if not check_mean:
        messages.append(
            f"Mean concrete stress exceed limit: |{stresses.sigma_c_med:.2f}| > {limits.sigma_c_med_allow:.2f}"
        )

    ok = check_concrete and check_steel and check_mean
    return AllowableCheckResult(
        ok=ok,
        check_concrete=check_concrete,
        check_steel=check_steel,
        check_mean=check_mean,
        messages=messages,
    )


# Simplified implementation of compute_long_rebar_limits_ta (translates LimitiArmaturaLong partially)
@dataclass
class LongitudinalRebarLimits:
    Afmin: float
    Afmax: float
    Afmin_tension_zone: float | None = None


def compute_long_rebar_limits_ta(
    section_area: float,
    Nx: float,
    fyd: float,
    fctm: float,
    geometry,
    is_column: bool,
    is_beam: bool,
    zona_sismica: bool,
) -> LongitudinalRebarLimits:
    # This implements a simplified version of LimitiArmaturaLong (VB):
    # - For columns (pilastri): Afmin = max(0.003 * Asez, ...), Afmax = 0.06 * Asez
    # - For beams: smaller minima (0.0015 * Asez or 0.0025 depending on TA vs others)

    if is_column:
        Afmin = max(0.003 * section_area, 0.0)
        Afmax = 0.06 * section_area
        Afmin_tension_zone = None
    else:
        # beam
        Afmin = 0.0015 * section_area
        Afmax = 0.06 * section_area
        Afmin_tension_zone = 0.0

    return LongitudinalRebarLimits(Afmin=Afmin, Afmax=Afmax, Afmin_tension_zone=Afmin_tension_zone)
