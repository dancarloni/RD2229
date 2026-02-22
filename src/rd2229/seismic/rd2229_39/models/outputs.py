"""DTO di output per azioni sismiche RD2229/39."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TraceRecord:
    norm_code: str
    method_id: str
    component: str
    norm_ref: List[str]
    assumptions: List[str]
    warnings: List[str]
    derived_from: Optional[str] = None
    factor: Optional[float] = None


@dataclass(frozen=True)
class FloorForceComponent:
    component: str
    forces_by_level: Dict[str, float]
    base_shear: float
    trace: TraceRecord


@dataclass(frozen=True)
class FloorForcesResult:
    components: Dict[str, FloorForceComponent]

    @staticmethod
    def combine(parts: List["FloorForceComponent"]) -> "FloorForcesResult":
        return FloorForcesResult(components={p.component: p for p in parts})
