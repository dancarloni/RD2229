"""Feature registry shim preserved for tests.

Provides a minimal `FeatureSpec` and registry functions expected by
tests that import `src.ui.modern.features.registry`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FeatureSpec:
    feature_id: str = ""
    label: str = ""
    icon: str = "📋"
    order: int = 100
    enabled: bool = True
    tooltip: str = ""

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


def clear() -> None:
    global _REGISTRY
    _REGISTRY = []


__all__ = ["FeatureSpec", "register", "get_all", "clear"]
