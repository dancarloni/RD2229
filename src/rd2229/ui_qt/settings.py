"""Settings view / viewmodel skeleton for Qt shell.

Lightweight container used by tests and later UI wiring.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingsModel:
    recent_projects: list[str] = None

    def __post_init__(self):
        if self.recent_projects is None:
            self.recent_projects = []


class SettingsViewModel:
    def __init__(self, model: SettingsModel | None = None) -> None:
        self.model = model or SettingsModel()

    def add_recent(self, project: str) -> None:
        if project not in self.model.recent_projects:
            self.model.recent_projects.append(project)
