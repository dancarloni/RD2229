from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

ResultStatus = Literal["OK", "WARN", "FAIL"]
ElementRole = Literal["PRIMARY", "SECONDARY"]


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class TraceRecord:
    run_id: str
    norm_code: str
    norm_references: list[str]
    method_id: str
    assumptions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    norma_attiva: str
    created_at: str = field(default_factory=utc_now_iso)
    schema_version: int = 1


@dataclass(frozen=True)
class Material:
    id: str
    project_id: str
    code: str
    kind: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Section:
    id: str
    project_id: str
    kind: str
    dimensions: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Element:
    id: str
    project_id: str
    section_id: str
    material_id: str
    role: ElementRole = "PRIMARY"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoadCase:
    id: str
    project_id: str
    name: str
    category: str
    actions: dict[str, float] = field(default_factory=dict)
    environmental: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Combination:
    id: str
    project_id: str
    name: str
    factors: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class CheckRequest:
    id: str
    project_id: str
    element_id: str
    combination_id: str
    check_code: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerificationResult:
    id: str
    request_id: str
    project_id: str
    status: ResultStatus
    value: float
    trace: TraceRecord
    created_at: str = field(default_factory=utc_now_iso)
