"""Feature registry per GUI moderna.

Mantiene API minima compatibile con i test (`register`, `get_all`, `clear`)
ed espone helper utili alla nuova dashboard operativa.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class FeatureSpec:
    feature_id: str = ""
    label: str = ""
    category: str = "generic"
    description: str = ""
    icon: str = "*"
    order: int = 100
    enabled: bool = True
    tooltip: str = ""
    action: Callable[[], Any] | None = None
    tags: tuple[str, ...] = ()

    def create_widget(
        self, parent: Any, *args: Any, **kwargs: Any
    ) -> Any:  # pragma: no cover - shim
        raise NotImplementedError()


_REGISTRY: list[FeatureSpec] = []


def register(spec: FeatureSpec) -> None:
    global _REGISTRY
    _REGISTRY = [s for s in _REGISTRY if s.feature_id != spec.feature_id]
    _REGISTRY.append(spec)
    _REGISTRY.sort(key=lambda s: s.order)


def get_all() -> list[FeatureSpec]:
    return list(_REGISTRY)


def get_enabled() -> list[FeatureSpec]:
    return [spec for spec in _REGISTRY if spec.enabled]


def get_by_id(feature_id: str) -> FeatureSpec | None:
    for spec in _REGISTRY:
        if spec.feature_id == feature_id:
            return spec
    return None


def clear() -> None:
    global _REGISTRY
    _REGISTRY = []


__all__ = [
    "FeatureSpec",
    "register",
    "get_all",
    "get_enabled",
    "get_by_id",
    "clear",
]
