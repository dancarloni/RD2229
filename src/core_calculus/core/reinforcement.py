from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class RebarLayer:
    area: float  # mm^2 o cm^2 (definire unità nel progetto)
    cover: float
    bar_diameter: float
    bar_count: Optional[int] = None


@dataclass(frozen=True)
class Stirrups:
    diameter: float
    spacing: float
    presence_of_bent_bars: bool = False


@dataclass(frozen=True)
class SectionReinforcement:
    upper_layers: List[RebarLayer]
    lower_layers: List[RebarLayer]
    stirrups: Optional[Stirrups] = None
    additional_layers: Optional[List[RebarLayer]] = None
