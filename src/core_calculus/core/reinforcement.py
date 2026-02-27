from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RebarLayer:
    area: float  # mm^2 o cm^2 (definire unità nel progetto)
    cover: float
    bar_diameter: float
    bar_count: int | None = None


@dataclass(frozen=True)
class Stirrups:
    diameter: float
    spacing: float
    presence_of_bent_bars: bool = False


@dataclass(frozen=True)
class SectionReinforcement:
    upper_layers: list[RebarLayer]
    lower_layers: list[RebarLayer]
    stirrups: Stirrups | None = None
    additional_layers: list[RebarLayer] | None = None
