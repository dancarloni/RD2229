"""
LC/FC adjustments for existing structures.

Implements material property adjustments based on:
- NTC 2018 Cap. 8 (Livelli di Conoscenza, Fattori di Confidenza)
- EC2 EN 1992-1-1:2023 Annex I (assessment of existing RC structures)
- prEN 1990-2 (basis of assessment of existing structures)

DOES NOT modify base Material objects; returns adjusted properties.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AdjustedMaterialProperties:
    """Adjusted material properties after LC/FC application.

    Contains both original and adjusted values for transparency.
    """

    # Original values
    f_ck_original: float  # MPa
    f_yk_original: float  # MPa

    # Adjusted values (after FC application)
    f_ck_adjusted: float  # MPa
    f_yk_adjusted: float  # MPa

    # Safety factors (may be adjusted for assessment)
    gamma_c: float = 1.5  # NTC 2018 default for new structures
    gamma_s: float = 1.15  # NTC 2018 default for new structures

    # Design strengths (computed from adjusted values)
    f_cd: float = 0.0  # MPa
    f_yd: float = 0.0  # MPa

    # Metadata
    lc: str | None = None  # LC1, LC2, LC3
    fc: float | None = None  # Confidence Factor

    def __post_init__(self) -> None:
        """Compute design strengths from adjusted values."""
        if self.f_cd == 0.0:
            self.f_cd = 0.85 * self.f_ck_adjusted / self.gamma_c
        if self.f_yd == 0.0:
            self.f_yd = self.f_yk_adjusted / self.gamma_s


def apply_lc_fc_adjustments(
    material: Any,
    lc: str,
    fc: float,
    use_ntc2018: bool = True,
) -> AdjustedMaterialProperties:
    """Apply LC/FC adjustments to material properties for existing structures.

    According to NTC 2018 § 8.5.4, the confidence factor FC is applied to
    material properties to account for uncertainty in knowledge level.

    f_ck,adjusted = f_ck / FC
    f_yk,adjusted = f_yk / FC

    Args:
        material: Material object with f_ck, f_yk properties
        lc: Livello di Conoscenza ("LC1", "LC2", "LC3")
        fc: Fattore di Confidenza (typically 1.0 - 1.35)
        use_ntc2018: If True, use NTC 2018 rules; else EC2/prEN 1990-2

    Returns:
        AdjustedMaterialProperties with original and adjusted values

    Raises:
        ValueError: If LC or FC invalid, or material properties missing
    """
    # Validate inputs
    valid_lc = ["LC1", "LC2", "LC3"]
    if lc not in valid_lc:
        raise ValueError(f"Invalid LC: '{lc}'. Valid values: {valid_lc}")

    if fc < 1.0 or fc > 1.5:
        raise ValueError(f"FC out of range [1.0, 1.5]: {fc}")

    # Get original material properties
    if not hasattr(material, "f_ck") or not hasattr(material, "f_yk"):
        raise ValueError("Material must have f_ck and f_yk properties")

    f_ck_orig = float(material.f_ck)  # MPa
    f_yk_orig = float(material.f_yk)  # MPa

    if f_ck_orig <= 0 or f_yk_orig <= 0:
        raise ValueError(f"Material properties must be positive: f_ck={f_ck_orig}, f_yk={f_yk_orig}")

    # Apply FC to reduce material strengths (more conservative for higher FC)
    # NTC 2018 § 8.5.4: f_m = f_m,mean / FC
    # For design: f_k,adjusted = f_k / FC (where f_k is characteristic value from tests)
    f_ck_adj = f_ck_orig / fc
    f_yk_adj = f_yk_orig / fc

    # Safety factors
    # For existing structures under assessment, NTC 2018 § 8.5.4 allows:
    # - Same gamma_c, gamma_s as new structures for SLU (conservative)
    # - Reduced gamma factors for SLE (not implemented here)
    # Future: Implement reduced gamma per § 8.5.4 Table 8.2
    gamma_c = 1.5
    gamma_s = 1.15

    return AdjustedMaterialProperties(
        f_ck_original=f_ck_orig,
        f_yk_original=f_yk_orig,
        f_ck_adjusted=f_ck_adj,
        f_yk_adjusted=f_yk_adj,
        gamma_c=gamma_c,
        gamma_s=gamma_s,
        lc=lc,
        fc=fc,
    )


def get_typical_fc_for_lc(lc: str) -> float:
    """Get typical FC value for given LC according to NTC 2018 Table 8.2.

    Args:
        lc: Livello di Conoscenza ("LC1", "LC2", "LC3")

    Returns:
        Typical FC value

    Raises:
        ValueError: If LC invalid
    """
    fc_map = {
        "LC1": 1.35,  # Conoscenza limitata
        "LC2": 1.20,  # Conoscenza adeguata
        "LC3": 1.00,  # Conoscenza accurata (piena)
    }

    if lc not in fc_map:
        raise ValueError(f"Invalid LC: '{lc}'. Valid values: {list(fc_map.keys())}")

    return fc_map[lc]


def get_lc_description_it(lc: str) -> str:
    """Get Italian description of Knowledge Level.

    Args:
        lc: Livello di Conoscenza ("LC1", "LC2", "LC3")

    Returns:
        Italian description

    Raises:
        ValueError: If LC invalid
    """
    descriptions = {
        "LC1": "Conoscenza limitata",
        "LC2": "Conoscenza adeguata",
        "LC3": "Conoscenza accurata (piena)",
    }

    if lc not in descriptions:
        raise ValueError(f"Invalid LC: '{lc}'. Valid values: {list(descriptions.keys())}")

    return descriptions[lc]
