"""Minimal plugin registry used by the Qt shell.

Registers simple callables by name for later dynamic extension.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

_REGISTRY: dict[str, Callable] = {}
_SPEC_REGISTRY: dict[str, ModuleSpec] = {}


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    name: str
    version: str
    entrypoints: dict[str, str] = field(default_factory=dict)
    capabilities: dict[str, list[str]] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    data_contracts: dict[str, Any] = field(default_factory=dict)


def is_spec_compatible(spec: ModuleSpec) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    if not spec.id.strip():
        warnings.append("missing-module-id")
    if not spec.version.strip():
        warnings.append("missing-module-version")
    if "engine" not in spec.entrypoints and spec.capabilities.get("checks"):
        warnings.append("missing-engine-entrypoint")
    return (len(warnings) == 0, warnings)


def register(name: str, fn: Callable) -> None:
    _REGISTRY[name] = fn


def get(name: str) -> Callable | None:
    return _REGISTRY.get(name)


def list_plugins() -> list[str]:
    return list(_REGISTRY.keys())


def register_spec(spec: ModuleSpec) -> None:
    _SPEC_REGISTRY[spec.id] = spec


def get_spec(module_id: str) -> ModuleSpec | None:
    return _SPEC_REGISTRY.get(module_id)


def list_specs() -> list[str]:
    return list(_SPEC_REGISTRY.keys())


def list_incompatible_specs() -> dict[str, list[str]]:
    incompatible: dict[str, list[str]] = {}
    for spec_id, spec in _SPEC_REGISTRY.items():
        ok, warnings = is_spec_compatible(spec)
        if not ok:
            incompatible[spec_id] = warnings
    return incompatible
