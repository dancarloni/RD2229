"""Qt-based module selector compatibility entrypoint.

Replaces the old Tkinter implementation in active runtime paths.
Legacy Tkinter implementation remains under `src.legacy.ui.module_selector`.
"""

from __future__ import annotations

from src.ui.qt.module_selector import ModuleSelectorWindow


class ModuleSelectorController:
    """Compatibility placeholder retained for legacy imports."""


class ModuleSelectorWindowCompat(ModuleSelectorWindow):
    """Backward-compatible alias of the Qt selector window."""


def show_selector() -> int:
    """Start the Qt selector using the official GUI entrypoint."""
    from src.ui.qt.entrypoint import main

    return main()


# Backward-compatible symbol name used by older imports
ModuleSelectorWindow = ModuleSelectorWindowCompat
