"""Contratto dati esteso per casi speciali X8."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SpecialCaseType(StrEnum):
    """Tipologie supportate dal perimetro X8."""

    PREDALLES = "predalles"
    COLLABORANTE = "collaborante_acciaio_calcestruzzo"
    CLT = "clt"


@dataclass(slots=True)
class SpecialCaseInput:
    """Input standardizzato per valutazioni preliminari X8."""

    case_type: SpecialCaseType
    norm_code: str = "NTC2018"
    span_m: float = 0.0
    gk_kg_m2: float = 0.0
    qk_kg_m2: float = 0.0
    width_m: float = 1.0
    height_cm: float = 0.0
    notes: str = ""
    material_profile: dict[str, Any] = field(default_factory=lambda: {})
    advanced_inputs: dict[str, Any] = field(default_factory=lambda: {})


@dataclass(slots=True)
class SpecialCaseResult:
    """Risultato X8 orientato a report e audit trail."""

    case_type: str
    in_scope_v1: bool
    blocked: bool
    warnings: list[str] = field(default_factory=lambda: [])
    assumptions: list[str] = field(default_factory=lambda: [])
    benchmark_values: dict[str, float] = field(default_factory=lambda: {})
    recommended_actions: list[str] = field(default_factory=lambda: [])
    normative_refs: list[str] = field(default_factory=lambda: [])

    def to_dict(self) -> dict[str, Any]:
        """Serializza in dict JSON-friendly."""
        return {
            "case_type": self.case_type,
            "in_scope_v1": self.in_scope_v1,
            "blocked": self.blocked,
            "warnings": list(self.warnings),
            "assumptions": list(self.assumptions),
            "benchmark_values": dict(self.benchmark_values),
            "recommended_actions": list(self.recommended_actions),
            "normative_refs": list(self.normative_refs),
        }
