from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from rd2229.ui_qt.settings import SettingsModel, SettingsViewModel


class SettingsService:
    def __init__(self, workspace_root: Path | None = None) -> None:
        self.workspace_root = workspace_root or Path.cwd()
        self.settings_path = self.workspace_root / "logs" / "ui" / "launcher_settings.json"
        self.vm = SettingsViewModel()
        self.load()

    def load(self) -> SettingsModel:
        if not self.settings_path.exists():
            return self.vm.model

        raw = json.loads(self.settings_path.read_text(encoding="utf-8"))
        self.vm = SettingsViewModel(
            SettingsModel(
                recent_projects=list(raw.get("recent_projects") or []),
                default_axial_n=float(raw.get("default_axial_n", 120.0)),
                default_factor=float(raw.get("default_factor", 1.0)),
                default_threshold=float(raw.get("default_threshold", 1000.0)),
                default_check_code=str(raw.get("default_check_code", "MVP_REAL_MIN")),
                default_db_name=str(raw.get("default_db_name", "mvp_alpha.db")),
            )
        )
        return self.vm.model

    def save(self) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(
            json.dumps(asdict(self.vm.model), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_model(self) -> SettingsModel:
        return self.vm.model

    def update_runtime_defaults(
        self,
        *,
        axial_n: float,
        factor: float,
        threshold: float,
        check_code: str,
        db_name: str,
    ) -> SettingsModel:
        self.vm.update_runtime_defaults(
            axial_n=axial_n,
            factor=factor,
            threshold=threshold,
            check_code=check_code,
            db_name=db_name,
        )
        self.save()
        return self.vm.model
