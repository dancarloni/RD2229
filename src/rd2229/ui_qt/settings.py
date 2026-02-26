"""Settings view / viewmodel skeleton for Qt shell.

Lightweight container used by tests and later UI wiring.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingsModel:
    recent_projects: list[str] = None
    default_axial_n: float = 120.0
    default_factor: float = 1.0
    default_threshold: float = 1000.0
    default_check_code: str = "MVP_REAL_MIN"
    default_db_name: str = "mvp_alpha.db"

    def __post_init__(self):
        if self.recent_projects is None:
            self.recent_projects = []


class SettingsViewModel:
    def __init__(self, model: SettingsModel | None = None) -> None:
        self.model = model or SettingsModel()

    def add_recent(self, project: str) -> None:
        if project not in self.model.recent_projects:
            self.model.recent_projects.append(project)

    def update_runtime_defaults(
        self,
        *,
        axial_n: float,
        factor: float,
        threshold: float,
        check_code: str,
        db_name: str,
    ) -> None:
        self.model.default_axial_n = float(axial_n)
        self.model.default_factor = float(factor)
        self.model.default_threshold = float(threshold)
        self.model.default_check_code = check_code.strip() or "MVP_REAL_MIN"
        self.model.default_db_name = db_name.strip() or "mvp_alpha.db"
