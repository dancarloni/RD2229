"""Shim for historical verification main window (Tkinter).

Lazily imports `ui.historical_main_window`.
"""

from __future__ import annotations

from importlib import import_module


def create_historical_window(*args, **kwargs):
    mod = import_module("ui.historical_main_window")
    return getattr(mod, "create_historical_window")(*args, **kwargs)
