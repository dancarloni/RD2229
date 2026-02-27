"""Notification center shim for legacy UI.

Forwards to `ui.notification_center` when legacy UI enabled.
"""

from __future__ import annotations

from importlib import import_module


def notify(*args, **kwargs):
    mod = import_module("ui.notification_center")
    return getattr(mod, "notify")(*args, **kwargs)
