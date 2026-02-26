"""Verification dispatcher for secondary elements.

This module implements the minimal STEP2 behaviour: read the active norm
from ``project_model.norma_attiva`` and route SLU/SLE requests to the
appropriate check functions provided by the ``src.codes.ntc2018
secondary_elements`` package.  All results are guaranteed to include
``trace.run_id`` and a non-empty ``norm_references`` list even when the
underlying check is a skeleton or not yet implemented.

Gating rules enforced here:
  * ``influence_on_global_model == True`` → immediately return
    NOT_APPLICABLE (no calculation performed).

The dispatcher is intentionally lightweight so that it can be called from
higher‑level verification services without introducing normative logic.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict


def _make_trace() -> Dict[str, str]:
    return {"run_id": str(uuid.uuid4())}


def _normalize_result(result: Dict[str, Any], base: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure that required contract fields exist on the result."""
    if "trace" not in result:
        result["trace"] = base["trace"]
    if not result.get("norm_references"):
        # copy to avoid mutating base
        result["norm_references"] = list(base["norm_references"])
    if "decision_log" not in result:
        result["decision_log"] = list(base.get("decision_log", []))
    return result


def run(
    inputs: Dict[str, Any], project_model: Any, limit_state: str
) -> Dict[str, Any]:
    """Dispatch a verification request for a secondary element.

    Args:
        inputs: dictionary representing the element spec (see models).
        project_model: object with attribute ``norma_attiva``.
        limit_state: string such as "SLU" or "SLE".

    Returns:
        A result dictionary fulfilling the STEP2 output contract.
    """
    norm = getattr(project_model, "norma_attiva", None)
    if norm is None:
        raise ValueError("project_model.norma_attiva must be set before running verifications")

    base = {"trace": _make_trace(), "norm_references": [norm], "decision_log": []}

    # gating: global model influence
    if inputs.get("influence_on_global_model"):
        return _normalize_result({
            "esito": "NOT_APPLICABLE",
            "messages": ["Requires global analysis: influence_on_global_model=True"],
        }, base)

    # route to the appropriate check module
    if limit_state == "SLU":
        from src.codes.ntc2018.secondary_elements import checks as _checks

        res = _checks.check_slu(inputs)
        return _normalize_result(res, base)
    elif limit_state == "SLE":
        from src.codes.ntc2018.secondary_elements import checks as _checks

        res = _checks.check_sle(inputs)
        return _normalize_result(res, base)
    else:
        return _normalize_result(
            {"esito": "ERROR", "messages": [f"Unsupported limit state '{limit_state}'"]},
            base,
        )
