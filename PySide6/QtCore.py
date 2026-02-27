"""Re-export QtCore names from PyQt6.QtCore for compatibility."""

from PyQt6 import QtCore as _pyqt6_qtcore

# Re-export most names
from PyQt6.QtCore import *  # noqa: F401,F403

# Provide Signal/Slot compatibility aliases expected by PySide6-using code
try:
    Signal = _pyqt6_qtcore.Signal  # type: ignore[attr-defined]
except Exception:
    # PyQt6 exposes pyqtSignal instead of Signal in some builds
    Signal = getattr(_pyqt6_qtcore, "pyqtSignal", None)

try:
    Slot = _pyqt6_qtcore.Slot  # type: ignore[attr-defined]
except Exception:
    Slot = getattr(_pyqt6_qtcore, "pyqtSlot", None)

__all__ = [name for name in dir() if not name.startswith("_")]
