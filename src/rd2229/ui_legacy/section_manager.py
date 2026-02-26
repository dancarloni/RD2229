"""Section manager shim for legacy UI.

Lazy-loads `ui.section_manager` to prevent Tkinter imports at package import.
"""

from __future__ import annotations

from importlib import import_module


def list_sections(*args, **kwargs):
    mod = import_module("ui.section_manager")
    return getattr(mod, "list_sections")(*args, **kwargs)


def add_section(*args, **kwargs):
    mod = import_module("ui.section_manager")
    return getattr(mod, "add_section")(*args, **kwargs)
