"""Plugin contracts and registry for RD2229.

Defines PluginSpec, ActionSpec, ParamSpec dataclasses and the
PluginRegistry class used to discover and manage plugins.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ParamSpec",
    "ActionSpec",
    "PluginSpec",
    "PluginRegistry",
    "BasePlugin",
]

from src.plugins.base import BasePlugin


@dataclass
class ParamSpec:
    """Specification for a single action parameter."""

    name: str
    label: str
    type: str = "string"  # string, int, float, bool, file, dir
    required: bool = False
    default: Any = None
    description: str = ""


@dataclass
class ActionSpec:
    """Specification for a plugin action."""

    id: str
    label: str
    handler: Callable[..., Any] | None = None
    params: list[ParamSpec] = field(default_factory=list)
    description: str = ""
    icon: str = ""


@dataclass
class PluginSpec:
    """Full specification for a plugin."""

    id: str
    title: str
    version: str = "0.1.0"
    category: str = "general"
    icon: str = ""
    description: str = ""
    actions: list[ActionSpec] = field(default_factory=list)


class PluginRegistry:
    """Registry that holds loaded PluginSpec instances."""

    def __init__(self) -> None:
        self._plugins: dict[str, PluginSpec] = {}

    def register(self, spec: PluginSpec) -> None:
        """Register a plugin spec."""
        self._plugins[spec.id] = spec

    def get(self, plugin_id: str) -> PluginSpec | None:
        """Return plugin by id, or None."""
        return self._plugins.get(plugin_id)

    def list_plugins(self) -> list[PluginSpec]:
        """Return all registered plugins."""
        return list(self._plugins.values())

    def clear(self) -> None:
        """Remove all registered plugins."""
        self._plugins.clear()
