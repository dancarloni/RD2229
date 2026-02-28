"""Compatibility shim for legacy import path.

This module re-exports the legacy GUI app found in
`src.legacy.ui.verification_table_app` so older imports of
`src.legacy.verification_table` continue to work. Keep a thin shim to avoid
syntax errors during test collection.
"""

from importlib import import_module


def _load():
    return import_module("src.legacy.ui.verification_table_app")


_mod = None


def __getattr__(name: str):
    global _mod
    if _mod is None:
        _mod = _load()
    return getattr(_mod, name)


def __dir__():
    if _mod is None:
        return ["__name__"]
    return [n for n in dir(_mod) if not n.startswith("_")]
