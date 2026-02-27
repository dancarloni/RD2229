"""Unified registry for modern GUI features and plugin discovery."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from src.plugins import PluginRegistry, PluginSpec
from src.ui.modern.features.registry import FeatureSpec, clear, get_all, register

__all__ = [
    "FeatureSpec",
    "register",
    "get_all",
    "clear",
    "register_feature",
    "discover_plugin_specs",
]


def register_feature(spec: FeatureSpec) -> None:
    """Alias esplicito usato da chiamanti esterni."""
    register(spec)


_DEFAULT_PLUGIN_MODULES = [
    "src.plugins.info_plugin",
    "src.plugins.run_plugin",
    "src.plugins.export_plugin",
]


def discover_plugin_specs(extra_modules: list[str] | None = None) -> list[PluginSpec]:
    """Discover built-in and optional plugin specs from module names."""
    registry = PluginRegistry()
    module_names = [*_DEFAULT_PLUGIN_MODULES, *(extra_modules or [])]

    for module_name in module_names:
        try:
            module = import_module(module_name)
        except Exception:
            continue
        register_fn = getattr(module, "register", None)
        if callable(register_fn):
            try:
                register_fn(registry)
            except Exception:
                continue

    return registry.list_plugins()
