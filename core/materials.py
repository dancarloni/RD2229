from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    name: str
    unit_weight: float  # kN/m^3


@dataclass(frozen=True)
class Concrete(Material):
    fck: float  # MPa


@dataclass(frozen=True)
class Steel(Material):
    fyk: float  # MPa
