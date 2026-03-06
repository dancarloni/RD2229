"""Verification dispatcher for secondary elements.

This module routes SLU/SLE verification requests for secondary elements
to the appropriate norm-specific check module based on
``project_model.norma_attiva``.

Norme supportate:
  * NTC2018 (default) — ``src.codes.ntc2018.secondary_elements``
  * DM96 / DM92 — ``src.codes.dm96.secondary_elements``
  * RD2229 — ``src.codes.rd2229.secondary_elements``

All results are guaranteed to include ``trace.run_id`` and a non-empty
``norm_references`` list.

Gating rules enforced here:
  * ``influence_on_global_model == True`` → immediately return
    NOT_APPLICABLE (no calculation performed).

The dispatcher is intentionally lightweight so that it can be called from
higher-level verification services without introducing normative logic.
"""

from __future__ import annotations

import uuid
from typing import Any


def _make_trace() -> dict[str, str]:
    return {"run_id": str(uuid.uuid4())}


def _normalize_result(result: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    """Ensure that required contract fields exist on the result."""
    if "trace" not in result:
        result["trace"] = base["trace"]
    if not result.get("norm_references"):
        # copy to avoid mutating base
        result["norm_references"] = list(base["norm_references"])
    if "decision_log" not in result:
        result["decision_log"] = list(base.get("decision_log", []))
    return result


def run(inputs: dict[str, Any], project_model: Any, limit_state: str) -> dict[str, Any]:
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
        return _normalize_result(
            {
                "esito": "NOT_APPLICABLE",
                "messages": ["Requires global analysis: influence_on_global_model=True"],
            },
            base,
        )

    # route to the appropriate check module based on norm
    norm_key = norm.upper().replace(" ", "").replace("/", "").replace(".", "")

    if norm_key in ("DM96", "DM0901996", "DM92", "DM14021992"):
        return _dispatch_dm96(inputs, limit_state, base)
    elif norm_key in ("RD2229", "RD222939", "RD2229_1939"):
        return _dispatch_rd2229(inputs, limit_state, base)
    else:
        # Default: NTC2018 (e norme successive)
        return _dispatch_ntc2018(inputs, limit_state, base)


def _dispatch_ntc2018(
    inputs: dict[str, Any], limit_state: str, base: dict[str, Any]
) -> dict[str, Any]:
    """Instrada a verifiche NTC2018 per elementi secondari."""
    if limit_state == "SLU":
        from src.codes.ntc2018.secondary_elements import checks as _checks

        return _normalize_result(_checks.check_slu(inputs), base)
    elif limit_state == "SLE":
        from src.codes.ntc2018.secondary_elements import checks as _checks

        return _normalize_result(_checks.check_sle(inputs), base)
    else:
        return _normalize_result(
            {"esito": "ERROR", "messages": [f"Unsupported limit state '{limit_state}'"]},
            base,
        )


def _dispatch_dm96(
    inputs: dict[str, Any], limit_state: str, base: dict[str, Any]
) -> dict[str, Any]:
    """Instrada a verifiche DM96 per elementi secondari."""
    if limit_state == "SLU":
        from src.codes.dm96.secondary_elements import checks as _checks

        return _normalize_result(_checks.check_slu_dm96(inputs), base)
    elif limit_state == "SLE":
        from src.codes.dm96.secondary_elements import checks as _checks

        return _normalize_result(_checks.check_sle_dm96(inputs), base)
    else:
        return _normalize_result(
            {"esito": "ERROR", "messages": [f"Unsupported limit state '{limit_state}'"]},
            base,
        )


def _dispatch_rd2229(
    inputs: dict[str, Any], limit_state: str, base: dict[str, Any]
) -> dict[str, Any]:
    """Instrada a verifiche RD2229 per elementi secondari."""
    if limit_state == "SLU":
        from src.codes.rd2229.secondary_elements import checks as _checks

        return _normalize_result(_checks.check_slu_rd2229(inputs), base)
    elif limit_state == "SLE":
        from src.codes.rd2229.secondary_elements import checks as _checks

        return _normalize_result(_checks.check_sle_rd2229(inputs), base)
    else:
        return _normalize_result(
            {"esito": "ERROR", "messages": [f"Unsupported limit state '{limit_state}'"]},
            base,
        )
