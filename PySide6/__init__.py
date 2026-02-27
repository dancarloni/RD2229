"""Compatibility shim package exposing a subset of PySide6 API via PyQt6.

This allows existing code that imports `PySide6` to run using `PyQt6`.
Only the modules required by the MCP simulator are re-exported here.
"""

from __future__ import annotations

# This package intentionally left minimal; submodules provide specific
# re-exports (QtCore, QtWidgets, QtTest, QtGui if needed).
__all__ = ["QtCore", "QtWidgets", "QtTest", "QtGui"]
