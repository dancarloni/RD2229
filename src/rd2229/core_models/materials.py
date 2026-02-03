from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class Material:
    name: str
    type: str  # e.g., 'concrete', 'steel'
    properties: Dict[str, float] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))


class MaterialRepository:
    def __init__(self) -> None:
        self._materials: Dict[str, Material] = {}

    def add(self, mat: Material) -> None:
        self._materials[mat.id] = mat

    def get_all(self) -> List[Material]:
        return list(self._materials.values())

    def find_by_name(self, name: str) -> Optional[Material]:
        for m in self._materials.values():
            if m.name == name:
                return m
        return None
