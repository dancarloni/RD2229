from __future__ import annotations

from dataclasses import dataclass

# Mapping to VB: f_Sigc (4.3.3) and f_Sigf (4.3.4)
# We implement parameterized constitutive laws capturing the same branches used in the VB code.


@dataclass
class ConcreteLawTA:
    """Concrete constitutive parameters for TA method.

    Units:
      - fcd: [kg/cm^2] (design compressive strength)
      - Ec: [kg/cm^2] (elastic modulus, consistent with stresses in kg/cm^2)
      - strains eps_* are dimensionless (unitless)
    """

    fcd: float  # design compressive strength (kg/cm^2)
    Ec: float  # elastic modulus (kg/cm^2)
    eps_c2: float
    eps_c3: float
    eps_c4: float
    eps_cu: float
    parab_rect: bool = True  # blnParabRettang
    allow_tension: bool = False  # if False, concrete in tension considered zero in TA (typical)


@dataclass
class SteelLawTA:
    """Steel constitutive parameters for TA method.

    Units:
      - Es: [kg/cm^2]
      - fyd: [kg/cm^2]
      - eps_yd, eps_su: dimensionless
    """

    Es: float
    fyd: float
    eps_yd: float
    eps_su: float
    elastoplastic: bool = True  # blnElastPerfettPlastico
    bilinear: bool = False
    Kincr: float = 0.0  # strain hardening coefficient if used


def sigma_c(eps: float, law: ConcreteLawTA) -> float:
    """Concrete stress-strain relation (approximation of VB f_Sigc).

    Inputs:
      - eps: strain (dimensionless)
      - law: ConcreteLawTA with Ec [kg/cm^2] and fcd [kg/cm^2]

    Returns:
      - stress in [kg/cm^2] (negative = compression, positive = tension)

    Note: The VB code used Excel scaling factors (fmL, fmFL) and mixed units. This
    implementation adopts a consistent unit system: lengths [cm], areas [cm^2],
    forces [kg], moments [kg·m], stresses [kg/cm^2].

    """
    # Tension (positive eps) or zero strain: linear elastic for positive strains, zero if tension not allowed
    if eps >= 0:
        if eps == 0:
            return 0.0
        if law.allow_tension:
            return law.Ec * eps
        # typically concrete cannot resist tension in TA method -> zero
        return 0.0

    # Compression branch (eps < 0)
    # We implement a smooth parabola that reaches -fcd at eps = -eps_cu
    eps_abs = abs(eps)
    if eps_abs >= law.eps_cu:
        return -law.fcd

    # Simple parabolic softening scaled such that at eps = eps_c2 stress is ~ -fcd
    # Use a normalized shape controlled by eps_c2 and eps_cu
    denom = (law.eps_cu - 0.0) if (law.eps_cu > 0) else 1.0
    x = min(eps_abs / denom, 1.0)
    # Parabolic: sigma = -fcd * (1 - (x)**2)
    return -law.fcd * (1.0 - x * x)


def sigma_s(eps: float, law: SteelLawTA) -> float:
    """Approximation of VB f_Sigf(Eps) (4.3.4).

    Elastic up to eps_yd (yield), then plastic plateau or bilinear hardening depending on flags.
    Positive eps: tension positive stress; negative eps: compression, symmetric behaviour.
    """
    sign = 1.0 if eps >= 0 else -1.0
    eps_abs = abs(eps)

    if eps_abs <= law.eps_yd:
        return sign * law.Es * eps_abs

    # beyond yield
    if law.elastoplastic and not law.bilinear:
        # perfectly plastic: stress = sign * fyd
        return sign * law.fyd
    if law.bilinear:
        # bilinear: linear hardening beyond yield with factor Kincr
        eps_pl = eps_abs - law.eps_yd
        return sign * (law.fyd + law.Kincr * law.Es * eps_pl)
    # default plastic plateau
    return sign * law.fyd
