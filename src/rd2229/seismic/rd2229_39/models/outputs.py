"""DTO di output per azioni sismiche RD2229/39."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TraceRecord:
    norm_code: str
    method_id: str
    component: str
    norm_ref: list[str]
    assumptions: list[str]
    warnings: list[str]
    derived_from: str | None = None
    factor: float | None = None


@dataclass(frozen=True)
class FloorForceComponent:
    component: str
    forces_by_level: dict[str, float]
    base_shear: float
    trace: TraceRecord


@dataclass(frozen=True)
class FloorForcesResult:
    components: dict[str, FloorForceComponent]

    @staticmethod
    def combine(parts: list[FloorForceComponent]) -> FloorForcesResult:
        return FloorForcesResult(components={p.component: p for p in parts})
