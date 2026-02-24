"""Minimal project store for migration phases.

Provides a tiny in-memory store used by the Qt shell and tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ProjectStore:
    projects: Dict[str, dict] = field(default_factory=dict)

    def add(self, name: str, data: dict) -> None:
        self.projects[name] = data

    def get(self, name: str) -> dict | None:
        return self.projects.get(name)

    def list(self) -> list[str]:
        return list(self.projects.keys())
