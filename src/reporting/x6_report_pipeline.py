"""Pipeline X6 per payload report auditabile con mapping normativo."""

from __future__ import annotations

import json
from typing import Any

from src.core.results import ResultsModel
from src.project.schema import ProjectModel

from .x6_audit_trail import build_audit_trail
from .x6_multi_norm_comparator import build_formula_table, get_normative_extracts
from .x6_warning_codes import infer_contract_warnings, normalize_warnings

# Verifiche di default per auto-popolamento se X3-X5 non forniscono formula_table
_DEFAULT_CHECK_TYPES = [
    "flessione",
    "taglio",
    "deformazione",
    "vibrazioni",
    "punzonamento",
    "aperture",
    "lc_fc",
    "pressoflessione",
]


def build_report_payload(
    project: ProjectModel,
    results: ResultsModel,
    *,
    decision_trace: list[str] | None = None,
) -> dict[str, Any]:
    """Restituisce un payload flat X6 pronto per export JSON."""
    norm_code = project.code_settings.norm_code or "NTC2018"

    coded_warnings = normalize_warnings(list(results.warnings))
    coded_warnings.extend(
        infer_contract_warnings(
            element_count=len(results.elements),
            has_trace=bool(results.trace),
            existing_structure=project.code_settings.existing_structure,
            lc=project.code_settings.lc,
        )
    )

    # Auto-popola formula_table dal comparatore se X3-X5 non l'hanno fornita
    formula_table: list[dict[str, Any]] = results.extra.get("formula_table", [])
    if not formula_table:
        formula_table = build_formula_table(_DEFAULT_CHECK_TYPES, norm_code)

    # Auto-popola normative_extracts dal comparatore se assenti
    normative_extracts: list[str] = results.extra.get("normative_extracts", [])
    if not normative_extracts:
        check_types_used = [
            entry.get("sezione", "") for entry in formula_table if entry.get("sezione")
        ]
        normative_extracts = get_normative_extracts(check_types_used, norm_code)

    payload: dict[str, Any] = {
        "phase_id": "X6",
        "project_name": project.project_info.name,
        "norm_code": norm_code,
        "existing_structure": project.code_settings.existing_structure,
        "lc": project.code_settings.lc,
        "input_summary": {
            "geometry_count": len(project.geometry),
            "materials_count": len(project.materials),
            "loads_count": len(project.loads),
            "pipeline_steps": list(project.pipeline_steps),
        },
        "checks_summary": {
            "global_ok": results.ok,
            "element_count": len(results.elements),
            "elements": [
                {
                    "element_id": elem.element_id,
                    "ok": elem.ok,
                    "metrics": dict(elem.metrics),
                    "messages": list(elem.messages),
                }
                for elem in results.elements
            ],
        },
        "formula_table": formula_table,
        "normative_extracts": normative_extracts,
        "warnings": coded_warnings,
        "trace_summary": list(results.trace),
        "decision_trace": list(decision_trace or []),
    }
    payload["audit_trail"] = build_audit_trail(
        project,
        results,
        decision_trace=payload["decision_trace"],
    )
    return payload


def build_report_payload_json(
    project: ProjectModel,
    results: ResultsModel,
    *,
    decision_trace: list[str] | None = None,
    indent: int = 2,
) -> str:
    """Serializza il payload flat X6 in JSON UTF-8."""
    return json.dumps(
        build_report_payload(project, results, decision_trace=decision_trace),
        ensure_ascii=False,
        indent=indent,
    )
