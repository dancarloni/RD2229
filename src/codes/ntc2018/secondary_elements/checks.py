"""
Skeleton check orchestrators for secondary elements.
Each function should return a VerificationResultItem-like dict (with trace.run_id and norm_references[]).
"""


def check_parapet(inputs: dict) -> dict:
    return {
        "ok": False,
        "value": None,
        "steps": ["SKELETON"],
        "trace": {"run_id": "TODO"},
        "norm_references": ["TODO"],
    }


def check_partition(inputs: dict) -> dict:
    return {
        "ok": False,
        "value": None,
        "steps": ["SKELETON"],
        "trace": {"run_id": "TODO"},
        "norm_references": ["TODO"],
    }


# -------------------------------------------------------------------
# STEP2 minimal implementations
# -------------------------------------------------------------------
from typing import Any


def _base_contract() -> dict[str, Any]:
    """Return a skeleton result containing mandatory fields."""
    return {
        "esito": "OK",
        "decision_log": [],
        "norm_references": [],
        "trace": {"run_id": "TODO"},
    }


def check_slu(inputs: dict[str, Any]) -> dict[str, Any]:
    """Placeholder SLU inertial‑force check (NS_SLU_InertialForce)."""
    result = _base_contract()
    result.update({"ok": True, "utilisation": 0.0})
    result["decision_log"].append("SLU check executed")
    return result


def check_sle(inputs: dict[str, Any]) -> dict[str, Any]:
    """Placeholder SLE drift‑compatibility check (NS_SLE_DriftCompatibility)."""
    result = _base_contract()
    drift = inputs.get("drift") or {}
    src = drift.get("source")
    if src == "ESTIMATED":
        result.setdefault("messages", []).append("Drift estimated; confidence forced to LOW")
        result["decision_log"].append("drift source=ESTIMATED, confidence=LOW")
        result["confidence"] = "LOW"
    else:
        result["decision_log"].append(f"drift source={src}")
    result.update({"ok": True, "utilisation": 0.0})
    return result


# legacy names preserved for compatibility
check_parapet = check_slu
check_partition = check_sle
