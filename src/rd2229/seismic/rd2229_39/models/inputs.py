"""DTO di input per azioni sismiche RD2229/39."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class FloorMassBreakdown:
    """Massa di piano (breakdown) per audit e tracciabilità."""

    level_id: str
    elevation_m: float

    m_floor: float = 0.0
    m_cols_above: float = 0.0
    m_cols_below: float = 0.0
    m_walls_above: float = 0.0
    m_walls_below: float = 0.0


@dataclass(frozen=True)
class MassAttributionPolicySpec:
    split_above: float = 0.5
    split_below: float = 0.5


@dataclass(frozen=True)
class EdgeFloorsPolicySpec:
    treat_missing_above_as_zero: bool = True
    treat_missing_below_as_zero: bool = True


@dataclass(frozen=True)
class FloorForcesRequest:
    floors: list[FloorMassBreakdown]
    p: float  # used only if p_mode == "MANUAL"
    g: float = 9.81
    mass_policy: MassAttributionPolicySpec = MassAttributionPolicySpec()
    edge_policy: EdgeFloorsPolicySpec = EdgeFloorsPolicySpec()
    # seismic coefficient mode: default manual for backward compatibility
    p_mode: Literal["MANUAL", "TABLE"] = "MANUAL"
    p_table_path: str | None = None
    p_table_key: str | None = None
    notes: str | None = None
