"""Minimal plugin registry used by the Qt shell.

Registers simple callables by name for later dynamic extension.
"""

from __future__ import annotations

from typing import Callable, Dict

_REGISTRY: Dict[str, Callable] = {}

def register(name: str, fn: Callable) -> None:
    _REGISTRY[name] = fn

def get(name: str) -> Callable | None:
    return _REGISTRY.get(name)

def list_plugins() -> list[str]:
    return list(_REGISTRY.keys())
