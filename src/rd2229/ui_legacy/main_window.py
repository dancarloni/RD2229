"""Shim for legacy main window (Tkinter).

This module lazily imports the original `ui.main_window` implementation when
the legacy UI flag is enabled.
"""

from __future__ import annotations

from importlib import import_module


def get_main_window(*args, **kwargs):
    mod = import_module("ui.main_window")
    return getattr(mod, "get_main_window")(*args, **kwargs)
