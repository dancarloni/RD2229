"""Minimal SettingsService shim for tests.

Provides `get_model()` returning an object with runtime defaults and
`update_runtime_defaults()` to mutate them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SettingsModel:
    recent_projects: list[str] | None = None
    default_axial_n: float = 120.0
    default_factor: float = 1.0
    default_threshold: float = 1000.0
    default_check_code: str = "MVP_REAL_MIN"
    default_db_name: str = "mvp_alpha.db"

    def __post_init__(self) -> None:
        if self.recent_projects is None:
            self.recent_projects = []


class SettingsService:
    def __init__(self, workspace_root: str | None = None) -> None:  # pragma: no cover - shim
        self._model = SettingsModel()

    def get_model(self) -> SettingsModel:
        return self._model

    def update_runtime_defaults(
        self,
        *,
        axial_n: float,
        factor: float,
        threshold: float,
        check_code: str,
        db_name: str,
    ) -> SettingsModel:
        self._model.default_axial_n = float(axial_n)
        self._model.default_factor = float(factor)
        self._model.default_threshold = float(threshold)
        self._model.default_check_code = check_code.strip() or "MVP_REAL_MIN"
        self._model.default_db_name = db_name.strip() or "mvp_alpha.db"
        return self._model


__all__ = ["SettingsService", "SettingsModel"]
