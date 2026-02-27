from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from rd2229.mvp.pipeline import run_mvp_demo

from .settings_service import SettingsService


class VerificationService:
    def __init__(
        self,
        workspace_root: Path | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        self.workspace_root = workspace_root or Path.cwd()
        self.settings_service = settings_service or SettingsService(self.workspace_root)

    def run_module(self, module_id: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if module_id != "mvp_structural":
            return {
                "status": "NOT_READY",
                "message": f"Modulo '{module_id}' non ancora eseguibile in Alpha.",
            }

        runtime = self._resolve_runtime_inputs(inputs)

        db_dir = self.workspace_root / "logs" / "mvp"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / runtime["db_name"]

        config_path = self.workspace_root / "config" / "calculation_codes" / "MVP_PLACEHOLDER.jsoncode"
        if not config_path.exists():
            return {
                "status": "ERROR",
                "message": f"Config mancante: {config_path}",
            }

        summary = run_mvp_demo(
            str(db_path),
            str(config_path),
            axial_n=runtime["axial_n"],
            combination_factor=runtime["factor"],
            check_code=runtime["check_code"],
            threshold_override=runtime["threshold"],
        )
        return {
            "status": "OK",
            "message": "Esecuzione completata.",
            "summary": summary,
            "run_timestamp": datetime.now().isoformat(),
            "db_path": str(db_path),
            "config_path": str(config_path),
            "runtime_inputs": runtime,
        }

    def _resolve_runtime_inputs(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        model = self.settings_service.get_model()
        raw = inputs or {}

        axial_n = float(raw.get("axial_n", model.default_axial_n))
        factor = float(raw.get("factor", model.default_factor))
        threshold = float(raw.get("threshold", model.default_threshold))
        check_code = str(raw.get("check_code", model.default_check_code)).strip() or "MVP_REAL_MIN"
        db_name = str(raw.get("db_name", model.default_db_name)).strip() or "mvp_alpha.db"

        return {
            "axial_n": axial_n,
            "factor": factor,
            "threshold": threshold,
            "check_code": check_code,
            "db_name": db_name,
        }
