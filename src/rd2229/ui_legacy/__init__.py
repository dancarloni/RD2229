"""Guarded legacy UI package inside the real package.

Importing this package will raise unless the environment variable
`RD2229_LEGACY_UI` is set to a truthy value. This ensures legacy Tkinter
components are opt-in during the PySide6 migration.
"""

from __future__ import annotations

import os

_ENABLED = os.environ.get("RD2229_LEGACY_UI", "0") not in ("0", "", "false", "False")

if not _ENABLED:  # pragma: no cover - only enabled in legacy runs
    raise ImportError(
        "Legacy UI is disabled. Set RD2229_LEGACY_UI=1 to enable legacy Tkinter modules."
    )

__all__ = [
    "module_selector",
    "main_window",
    "historical_main_window",
    "notification_center",
    "section_manager",
]
