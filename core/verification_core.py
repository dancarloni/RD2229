"""
Core calculation module for structural verifications.

This module implements the calculation procedures from Visual Basic .bas files
for TA (Tensioni Ammissibili), SLU (Stato Limite Ultimo), and SLE (Stato Limite Esercizio).

The calculations are organized by verification type and follow the formulas from:
- PrincipCA_TA.bas for TA calculations
- CA_SLU.bas for SLU calculations
- CA_SLE.bas for SLE calculations
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
from core_models.materials import Material


class VerificationType(str, Enum):
    """Types of structural verification."""

    BENDING_SIMPLE = "bending_simple"  # Flessione retta (only Mx or My)
    BENDING_DEVIATED = "bending_deviated"  # Flessione deviata (Mx and My)
    AXIAL_SIMPLE = "axial_simple"  # Compressione/Trazione (N only)
    AXIAL_BENDING_SIMPLE = "axial_bending_simple"  # Presso/Tensioflessione semplice
    AXIAL_BENDING_DEVIATED = "axial_bending_deviated"  # Presso/Tensioflessione deviata
    TORSION = "torsion"  # Torsione (Mz)
    SHEAR = "shear"  # Taglio (Tx/Ty)
    SHEAR_TORSION = "shear_torsion"  # Taglio + Torsione


@dataclass
class SectionGeometry:
    """Cross-section geometry parameters."""

    width: float  # b [cm]
    height: float  # h [cm]

    def area(self) -> float:
        """Calculate cross-section area [cm²]."""
        return self.width * self.height

    def inertia_y(self) -> float:
        """Calculate moment of inertia about y-axis [cm⁴]."""
        return self.width * self.height**3 / 12

    def inertia_z(self) -> float:
        """Calculate moment of inertia about z-axis [cm⁴]."""
        return self.height * self.width**3 / 12


@dataclass
class ReinforcementLayer:
    """Reinforcement layer (superior or inferior)."""

    area: float  # As [cm²]
    distance: float  # d or d' from compressed edge [cm]

    def centroid_distance(self, section_height: float) -> float:
        """Distance from section centroid [cm]."""
        return self.distance - section_height / 2


@dataclass
class MaterialProperties:
    """Material properties for concrete and steel."""

    # Concrete
    fck: float  # Characteristic compressive strength [kg/cm² or MPa]
    fcd: Optional[float] = None  # Design compressive strength
    Ec: Optional[float] = None  # Elastic modulus

    # Steel
    fyk: float = 0.0  # Characteristic yield strength
    fyd: Optional[float] = None  # Design yield strength
    Es: float = 2100000.0  # Elastic modulus [kg/cm²] or 200000 [MPa]

    # Homogenization
    n: Optional[float] = None  # Es/Ec

    def __post_init__(self):
        """Calculate derived properties if not provided."""
        if self.fcd is None:
            self.fcd = self.fck  # Will be adjusted by safety factors

        if self.fyd is None and self.fyk > 0:
            self.fyd = self.fyk  # Will be adjusted by safety factors

        if self.Ec is None:
            # Default formula from RD2229: Ec = 550000 * fck / (fck + 200)
            self.Ec = 550000.0 * self.fck / (self.fck + 200.0)

        if self.n is None:
            self.n = self.Es / self.Ec if self.Ec > 0 else 15.0


@dataclass
class LoadCase:
    """Load case with all force and moment components."""

    N: float = 0.0  # Axial force [kg or kN]
    Mx: float = 0.0  # Bending moment about x-axis [kg·cm or kN·m]
    My: float = 0.0  # Bending moment about y-axis [kg·cm or kN·m]
    Mz: float = 0.0  # Torsional moment [kg·cm or kN·m]
    Tx: float = 0.0  # Shear force in x direction [kg or kN]
    Ty: float = 0.0  # Shear force in y direction [kg or kN]
    At: float = 0.0  # Torsion reinforcement area [cm²]

    def get_verification_type(self) -> VerificationType:
        """Determine the verification type based on load components."""
        has_N = abs(self.N) > 1e-6
        has_Mx = abs(self.Mx) > 1e-6
        has_My = abs(self.My) > 1e-6
        has_Mz = abs(self.Mz) > 1e-6
        has_Tx = abs(self.Tx) > 1e-6
        has_Ty = abs(self.Ty) > 1e-6

        # Shear + Torsion
        if has_Mz and (has_Tx or has_Ty):
            return VerificationType.SHEAR_TORSION

        # Pure torsion
        if has_Mz and not (has_N or has_Mx or has_My):
            return VerificationType.TORSION

        # Pure shear
        if (has_Tx or has_Ty) and not (has_N or has_Mx or has_My or has_Mz):
            return VerificationType.SHEAR

        # Deviated bending (with or without axial)
        if has_Mx and has_My:
            if has_N:
                return VerificationType.AXIAL_BENDING_DEVIATED
            else:
                return VerificationType.BENDING_DEVIATED

        # Simple bending (with or without axial)
        if has_Mx or has_My:
            if has_N:
                return VerificationType.AXIAL_BENDING_SIMPLE
            else:
                return VerificationType.BENDING_SIMPLE

        # Pure axial
        if has_N:
            return VerificationType.AXIAL_SIMPLE

        # Default to simple bending
        return VerificationType.BENDING_SIMPLE


@dataclass
class NeutralAxis:
    """Neutral axis position and orientation."""

    x: float = 0.0  # Distance from top edge [cm]
    y: float = 0.0  # Coordinate y (for deviated bending) [cm]
    inclination: float = 0.0  # Inclination angle [degrees]

    def depth_ratio(self, section_height: float) -> float:
        """Ratio of neutral axis depth to section height."""
        return self.x / section_height if section_height > 0 else 0.0


@dataclass
class StressState:
    """Stress state at various points."""

    sigma_c_max: float = 0.0  # Max concrete stress (compressed edge) [kg/cm² or MPa]
    sigma_c_min: float = 0.0  # Min concrete stress (tensile edge) [kg/cm² or MPa]
    sigma_s_tensile: float = 0.0  # Steel stress in tensile zone [kg/cm² or MPa]
    sigma_s_compressed: float = 0.0  # Steel stress in compressed zone [kg/cm² or MPa]
    # Equivalent FRC stress contribution referenced to tensile reinforcement
    # (kg/cm² or MPa)
    sigma_frc: float = 0.0

    def max_stress(self) -> float:
        """Maximum stress magnitude."""
        return max(
            abs(self.sigma_c_max),
            abs(self.sigma_c_min),
            abs(self.sigma_s_tensile),
            abs(self.sigma_s_compressed),
            abs(self.sigma_frc),
        )


@dataclass
class VerificationResult:
    """Complete verification result."""

    verification_type: VerificationType
    neutral_axis: NeutralAxis
    stress_state: StressState

    # Safety factors and utilization
    safety_factor_concrete: float = 1.0
    safety_factor_steel: float = 1.0
    utilization_concrete: float = 0.0  # σ_c / σ_c,adm
    utilization_steel: float = 0.0  # σ_s / σ_s,adm

    # Verification outcome
    is_verified: bool = False
    messages: "Optional[list[str]]" = None

    def __post_init__(self):
        """Initialize messages list."""
        if self.messages is None:
            self.messages = []


def calculate_neutral_axis_simple_bending(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    reinforcement_compressed: ReinforcementLayer,
    material: MaterialProperties,
    method: str = "TA",
) -> NeutralAxis:
    """
    Calculate neutral axis for simple bending.

    Based on equilibrium equations from PrincipCA_TA.bas.
    For rectangular section with double reinforcement.

    Args:
        section: Section geometry
        reinforcement_tensile: Tensile reinforcement (bottom)
        reinforcement_compressed: Compressed reinforcement (top)
        material: Material properties
        method: Calculation method ("TA", "SLU", "SLE")

    Returns:
        Neutral axis position
    """
    b = section.width
    h = section.height
    As = reinforcement_tensile.area
    As_prime = reinforcement_compressed.area
    d = reinforcement_tensile.distance
    d_prime = reinforcement_compressed.distance
    n = material.n or 15.0

    if method == "TA":
        # Allowable stress method - homogenized section
        # Equilibrium: n*As*(d-x) = b*x²/2 + (n-1)*As'*(x-d')
        # Quadratic equation: (b/2)*x² + [n*As + (n-1)*As']*x - [n*As*d + (n-1)*As'*d'] = 0

        a = b / 2.0
        b_coef = n * As + (n - 1) * As_prime
        c = -(n * As * d + (n - 1) * As_prime * d_prime)

        # Solve quadratic equation
        discriminant = b_coef**2 - 4 * a * c
        if discriminant < 0:
            # No real solution - use approximate
            x = d / 3.0
        else:
            x = (-b_coef + math.sqrt(discriminant)) / (2 * a)

            # Ensure x is within section
            if x < 0:
                x = d / 3.0
            elif x > h:
                x = 2 * h / 3.0

    elif method == "SLU":
        # Ultimate limit state - iterative solution
        # Simplified for now - will be enhanced
        x = d / 3.0

    else:  # SLE
        # Serviceability limit state - elastic analysis
        # Similar to TA but with cracked section analysis
        x = d / 3.0

    return NeutralAxis(x=x, y=0.0, inclination=0.0)


def calculate_neutral_axis_deviated_bending(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    reinforcement_compressed: ReinforcementLayer,
    material: MaterialProperties,
    Mx: float,
    My: float,
    N: float = 0.0,
    method: str = "SLU",
    *,
    eps_cu: float = 0.0035,
    max_iter: int = 60,
    tol: float = 1e-3,
) -> NeutralAxis:
    """
    Iterative neutral axis calculation for deviated bending (SLU-style).

    Approach:
    - Rotate axes so that the bending resultant is aligned with X (angle = atan2(My,Mx)).
    - Solve for neutral axis depth x (measured from compressed edge) by bisection
      on the equilibrium of axial force: C + Fs' + Fs - (-N) = 0, where N>0 is tension.
    - Concrete compression resultant uses a rectangular stress block with depth 'x'
      and design stress 'fcd' (MaterialProperties.fcd).
    - Steel stresses computed from linear strain distribution capped by fyd (material.fyd).

    Note: this is an SLU-oriented implementation (uses eps_cu and fcd/fyd). For TA/SLE
    it will behave similarly but may be conservative; method selection can adjust
    coefficients if needed.
    """
    b = section.width
    h = section.height

    # Angle of bending resultant (degrees)
    if abs(Mx) < 1e-12 and abs(My) < 1e-12:
        inclination = 0.0
    else:
        inclination = math.degrees(math.atan2(My, Mx))

    # Material properties
    fcd = material.fcd if material.fcd is not None else material.fck
    fyd = material.fyd if material.fyd is not None else material.fyk
    Es = material.Es if material.Es is not None else 2100000.0

    # Reinforcement positions (distance from top compressed edge)
    d_top = reinforcement_compressed.distance
    d_bot = reinforcement_tensile.distance

    # Limits for neutral axis search
    x_min = 1e-6
    x_max = h * 0.999

    def internal_axial_result(x_val: float) -> float:
        """Compute internal axial resultant (compression positive) for given x."""
        # Concrete compression resultant using simplified rectangular block (0.8*x)
        Ac = b * 0.8 * x_val
        Cc = Ac * fcd
        # centroid lever arm of stress block from top approximately 0.4*x
        # Steel strains (linear): epsilon = eps_cu * (x - y)/x
        # Positive epsilon => compression, negative => tension
        # Top reinforcement
        eps_top = eps_cu * (x_val - d_top) / x_val if x_val > 0 else 0.0
        sigma_s_top = max(min(Es * eps_top, fyd), -fyd)
        Fs_top = reinforcement_compressed.area * sigma_s_top
        # Bottom reinforcement
        eps_bot = eps_cu * (x_val - d_bot) / x_val if x_val > 0 else 0.0
        sigma_s_bot = max(min(Es * eps_bot, fyd), -fyd)
        Fs_bot = reinforcement_tensile.area * sigma_s_bot
        # Total internal axial (compression positive). External N: positive = tension
        # Equilibrium: Cc + Fs_top + Fs_bot + N = 0  => residual = Cc + Fs_top + Fs_bot + N
        return Cc + Fs_top + Fs_bot + N

    # Check sign at ends to ensure bisection applicability
    r1 = internal_axial_result(x_min)
    r2 = internal_axial_result(x_max)
    if abs(r1) < tol:
        x_sol = x_min
    elif abs(r2) < tol:
        x_sol = x_max
    elif r1 * r2 > 0:
        # No sign change: fallback to simple estimate (d/3)
        x_sol = d_bot / 3.0
    else:
        # Bisection
        a = x_min
        bnd = x_max
        fa = r1
        _ = r2
        x_sol = (a + bnd) / 2.0
        for _ in range(max_iter):
            fm = internal_axial_result(x_sol)
            if abs(fm) < tol:
                break
            if fa * fm <= 0:
                bnd = x_sol
                _ = fm
            else:
                a = x_sol
                fa = fm
            x_sol = 0.5 * (a + bnd)

    na = NeutralAxis(x=x_sol, y=0.0, inclination=inclination)
    return na


def calculate_stresses_simple_bending(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    reinforcement_compressed: ReinforcementLayer,
    material: MaterialProperties,
    moment: float,
    neutral_axis: NeutralAxis,
    method: str = "TA",
    frc_material: "Optional[Material]" = None,
    frc_area: float = 0.0,
) -> StressState:
    """
    Calculate stresses for simple bending.

    Based on formulas from PrincipCA_TA.bas.

    Args:
        section: Section geometry
        reinforcement_tensile: Tensile reinforcement
        reinforcement_compressed: Compressed reinforcement
        material: Material properties
        moment: Bending moment [kg·cm or kN·m]
        neutral_axis: Neutral axis position
        method: Calculation method

    Returns:
        Stress state
    """
    b = section.width
    d = reinforcement_tensile.distance
    d_prime = reinforcement_compressed.distance
    x = neutral_axis.x
    n = material.n or 15.0

    if method == "TA":
        # Calculate moment of inertia of homogenized section
        # I = b*x³/3 + n*As*(d-x)² + (n-1)*As'*(x-d')²
        I_homog = (
            b * x**3 / 3.0
            + n * reinforcement_tensile.area * (d - x) ** 2
            + (n - 1) * reinforcement_compressed.area * (x - d_prime) ** 2
        )

        # Concrete stress at compressed edge
        if I_homog > 0:
            sigma_c_max = moment * x / I_homog
        else:
            sigma_c_max = 0.0

        # Steel stress in tensile zone
        if I_homog > 0:
            sigma_s_tensile = n * moment * (d - x) / I_homog
        else:
            sigma_s_tensile = 0.0

        # Steel stress in compressed zone
        if I_homog > 0 and x > d_prime:
            sigma_s_compressed = n * moment * (x - d_prime) / I_homog
        else:
            sigma_s_compressed = 0.0

        # Concrete stress at tensile edge (usually small or zero in cracked section)
        sigma_c_min = 0.0

        # ---- FRC contribution (MVP) ----
        sigma_frc_equiv = 0.0
        try:
            if (
                frc_material
                and getattr(frc_material, "frc_enabled", False)
                and frc_area
                and I_homog > 0
            ):
                # Estimate curvature kappa = M / (Ec * I_homog)
                Ec = material.Ec if material.Ec and material.Ec > 0 else 1.0
                curvature = moment / (Ec * I_homog)
                # Strain at tensile reinforcement position (distance from neutral axis)
                strain_at_frc = curvature * (d - x)
                # Compute stress in FRC material using existing core.frc model
                from core.frc import frc_stress

                frc_sigma = frc_stress(frc_material, strain_at_frc)
                # Total axial force from FRC
                frc_force = frc_sigma * frc_area
                # Convert to an equivalent stress referenced to tensile reinforcement area
                if reinforcement_tensile.area > 0:
                    sigma_frc_equiv = frc_force / reinforcement_tensile.area
                # Add FRC equivalent stress to steel tensile stress
                sigma_s_tensile += sigma_frc_equiv
        except Exception:
            # Defensive: if anything fails, keep sigma_frc as zero and continue
            sigma_frc_equiv = 0.0

    elif method == "SLU":
        # Ultimate limit state - stress block
        # Simplified for now
        sigma_c_max = 0.0
        sigma_s_tensile = 0.0
        sigma_s_compressed = 0.0
        sigma_c_min = 0.0

    else:  # SLE
        # Serviceability - elastic
        sigma_c_max = 0.0
        sigma_s_tensile = 0.0
        sigma_s_compressed = 0.0
        sigma_c_min = 0.0

    return StressState(
        sigma_c_max=sigma_c_max,
        sigma_c_min=sigma_c_min,
        sigma_s_tensile=sigma_s_tensile,
        sigma_s_compressed=sigma_s_compressed,
    )


def calculate_stresses_deviated_bending(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    reinforcement_compressed: ReinforcementLayer,
    material: MaterialProperties,
    Mx: float,
    My: float,
    neutral_axis: NeutralAxis,
    N: float = 0.0,
    method: str = "SLU",
) -> StressState:
    """
    Stresses for deviated bending computed using the neutral axis found iteratively.

    Uses equivalent moment magnitude for stress intensity, but neutral axis depth
    results from axial equilibrium (so stresses reflect N–M interaction).
    """
    equiv_moment = math.hypot(Mx, My)
    # Reuse simple bending stress computation using the more accurate neutral axis
    return calculate_stresses_simple_bending(
        section=section,
        reinforcement_tensile=reinforcement_tensile,
        reinforcement_compressed=reinforcement_compressed,
        material=material,
        moment=equiv_moment,
        neutral_axis=neutral_axis,
        method=method,
    )


def _rectangular_torsion_constant(b: float, h: float) -> float:
    """Approximate torsional constant J for a solid rectangle (Saint‑Venant).

    Formula from engineering approximations (Roark / standard tables).
    """
    # Ensure b <= h for stability
    bb = min(b, h)
    hh = max(b, h)
    ratio = bb / hh
    # Empirical approximation
    J = bb * hh**3 * (1.0 / 3.0 - 0.21 * ratio * (1.0 - (bb**4) / (12.0 * hh**4)))
    return max(J, 1e-6)


def estimate_required_torsion_reinforcement(
    section: SectionGeometry,
    reinforcement_tensile: ReinforcementLayer,
    loads: LoadCase,
    material: Optional[MaterialProperties] = None,
) -> float:
    """Estimate required torsion reinforcement area At [cm²] (simplified NTC-like).

    Formula (approximate): At_req = T (kg·cm) / (2 * z (cm) * fyd (kg/cm²))

    Note: This is a simplified engineering estimate to give an order of magnitude.
    It assumes T input is in kg·m (converted to kg·cm) and material.fyd is in MPa
    (converted to kg/cm²). Use with caution and prefer exact code formulas if needed.
    """
    T = abs(loads.Mz)
    if T <= 0:
        return 0.0
    # Convert kg·m to kg·cm
    T_kgcm = T * 100.0
    # Lever arm z ~ 0.9 * d (d = distance from compressed edge to tensile reinforcement)
    d = reinforcement_tensile.distance
    z = 0.9 * d if d and d > 0 else 0.9 * (section.height / 2.0)
    # material.fyd may be in MPa; convert to kg/cm² if small magnitude suggests MPa
    fyd = (
        material.fyd
        if (material and material.fyd is not None)
        else (material.fyk if material else 380.0)
    )
    # If fyd seems like MPa (e.g. < 2000), convert
    if fyd and fyd < 2000:
        fyd = fyd * 10.197
    if fyd <= 0 or z <= 0:
        return 0.0
    At_req = T_kgcm / (2.0 * z * fyd)
    return max(At_req, 0.0)


def calculate_shear_torsion_stresses(
    section: SectionGeometry,
    loads: LoadCase,
    reinforcement_area: float,
    material: Optional[MaterialProperties] = None,
) -> StressState:
    """
    Shear + Torsion simplified assessment.

    - Shear stress: τ_shear = V / A
    - Torsion stress: τ_torsion ≈ Mz * r / J (r ~ half smallest dimension)
    - Equivalent demand combined with von Mises-like sqrt(sum squares) and
      converted to an equivalent steel stress using reinforcement area.

    Returns StressState with sigma_c_max carrying the shear/torsion scalar and
    sigma_s_tensile approximating the required steel stress for the given At.
    """
    b = section.width
    h = section.height
    area = b * h
    v = math.hypot(abs(loads.Tx), abs(loads.Ty))
    torsion = abs(loads.Mz)

    tau_shear = v / area if area > 0 else 0.0

    J = _rectangular_torsion_constant(b, h)
    r = min(b, h) / 2.0
    tau_torsion = torsion * r / J if J > 0 else 0.0

    tau_eq = math.hypot(tau_shear, tau_torsion)

    # Convert to an equivalent steel stress assuming reinforcement_area resists shear/torsion
    if reinforcement_area and reinforcement_area > 0:
        sigma_s_tensile = tau_eq * area / reinforcement_area
    else:
        sigma_s_tensile = tau_eq

    return StressState(
        sigma_c_max=tau_eq,
        sigma_c_min=0.0,
        sigma_s_tensile=sigma_s_tensile,
        sigma_s_compressed=0.0,
    )


def verify_allowable_stresses(
    stress_state: StressState, material: MaterialProperties, sigma_c_adm: float, sigma_s_adm: float
) -> Tuple[bool, float, float, list[str]]:
    """
    Verify allowable stresses (TA method).

    Based on VerifResistCA_TA from PrincipCA_TA.bas.

    Args:
        stress_state: Calculated stresses
        material: Material properties
        sigma_c_adm: Allowable concrete stress
        sigma_s_adm: Allowable steel stress

    Returns:
        Tuple of (is_verified, utilization_concrete, utilization_steel, messages)
    """
    messages = []

    # Check concrete
    util_concrete = abs(stress_state.sigma_c_max) / sigma_c_adm if sigma_c_adm > 0 else 0.0

    # Check steel
    util_steel = max(
        abs(stress_state.sigma_s_tensile) / sigma_s_adm if sigma_s_adm > 0 else 0.0,
        abs(stress_state.sigma_s_compressed) / sigma_s_adm if sigma_s_adm > 0 else 0.0,
    )

    is_verified = util_concrete <= 1.0 and util_steel <= 1.0

    if util_concrete > 1.0:
        messages.append(f"Concrete stress exceeds allowable: {util_concrete:.2%}")

    if util_steel > 1.0:
        messages.append(f"Steel stress exceeds allowable: {util_steel:.2%}")

    if is_verified:
        messages.append("Verification PASSED - all stresses within limits")
    else:
        messages.append("Verification FAILED - stresses exceed allowable values")

    return is_verified, util_concrete, util_steel, messages
