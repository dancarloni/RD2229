"""Shim that exposes the legacy module selector UI when enabled.

This shim lazy-loads the original `ui.module_selector` only when called.
"""

from __future__ import annotations

from importlib import import_module


def _load():
    return import_module("ui.module_selector")


def show_selector(*args, **kwargs):
    mod = _load()
    return getattr(mod, "show_selector")(*args, **kwargs)
