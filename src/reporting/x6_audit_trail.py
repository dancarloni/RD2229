"""Helper per audit trail della Fase X6."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from src.core.results import ResultsModel
from src.project.schema import ProjectModel


def _sha256_hex(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_audit_trail(
    project: ProjectModel,
    results: ResultsModel,
    *,
    decision_trace: list[str] | None = None,
) -> dict[str, Any]:
    """Costruisce un audit trail serializzabile per il report X6."""
    project_data = project.to_dict()
    results_data = dataclasses.asdict(results)
    timestamp = results.timestamp or datetime.now(UTC).isoformat()
    return {
        "phase_id": "X6",
        "generated_at": timestamp,
        "norm_code": project.code_settings.norm_code,
        "project_name": project.project_info.name,
        "schema_version": project.schema_version,
        "input_hash": _sha256_hex(project_data),
        "output_hash": _sha256_hex(results_data),
        "warnings_count": len(results.warnings),
        "element_count": len(results.elements),
        "decision_trace": list(decision_trace or []),
    }
