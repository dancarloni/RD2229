from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
from uuid import uuid4


@dataclass
class LoadCase:
    name: str
    description: str = ""
    values: Dict[str, float] = field(default_factory=dict)  # e.g., {'N':0, 'Mx':0, 'My':0}
    id: str = field(default_factory=lambda: str(uuid4()))


class LoadRepository:
    def __init__(self) -> None:
        self._loads: Dict[str, LoadCase] = {}

    def add(self, load: LoadCase) -> None:
        self._loads[load.id] = load

    def get_all(self) -> List[LoadCase]:
        return list(self._loads.values())

    def find_by_name(self, name: str) -> LoadCase | None:
        for load in self._loads.values():
            if load.name == name:
                return load
        return None
