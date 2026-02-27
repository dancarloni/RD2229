"""Minimal VerificationService shim for tests.

Implements `run_module` returning a basic dict for known demo module ids.
"""

from __future__ import annotations

from typing import Any


class VerificationService:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - shim
        pass

    def run_module(self, module_id: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if module_id != "mvp_structural":
            return {"status": "NOT_READY", "message": f"Modulo '{module_id}' non pronto"}
        runtime = inputs or {}
        return {
            "status": "OK",
            "message": "Esecuzione demo completata",
            "summary": {"module_id": module_id, "runtime": runtime},
        }


__all__ = ["VerificationService"]
