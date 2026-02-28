"""Minimal VerificationService shim for tests.

Implements `run_module` returning a basic dict for known demo module ids.
"""

from __future__ import annotations

from typing import Any


class VerificationService:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - shim
        # capture workspace_root if provided so we can create db files
        self._workspace_root = kwargs.get("workspace_root")

    def run_module(self, module_id: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if module_id != "mvp_structural":
            return {"status": "NOT_READY", "message": f"Modulo '{module_id}' non pronto"}
        runtime = inputs or {}
        # simulate writing database file if workspace_root provided
        db_path = None
        db_name = runtime.get("db_name")
        if db_name and self._workspace_root:
            try:
                import os

                os.makedirs(self._workspace_root, exist_ok=True)
                db_path = os.path.join(self._workspace_root, db_name)
                # create empty file
                open(db_path, "a", encoding="utf-8").close()
            except Exception:
                db_path = None

        summary = {
            "module_id": module_id,
            "runtime": runtime,
            "check_code": runtime.get("check_code"),
            # naive status: FAIL for demo always
            "status": "FAIL",
        }
        result = {
            "status": "OK",
            "message": "Esecuzione demo completata",
            "summary": summary,
        }
        if db_path:
            result["db_path"] = db_path
        return result


__all__ = ["VerificationService"]
