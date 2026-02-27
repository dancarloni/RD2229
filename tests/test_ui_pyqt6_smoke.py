"""Smoke tests for the PyQt6 GUI entry point (src.ui.modern.app:main)."""

from __future__ import annotations

import importlib
import sys

import pytest


def test_pyqt6_main_test_mode(monkeypatch):
    """When RD2229_UI_TEST is set, main() should return 0 without starting the event loop."""
    pytest.importorskip("PyQt6", reason="PyQt6 not installed; PyQt6 smoke skipped")
    monkeypatch.setenv("RD2229_UI_TEST", "1")
    mod = importlib.import_module("src.ui.modern.app")
    importlib.reload(mod)
    result = mod.main()
    assert result == 0


def test_pyqt6_main_missing_pyqt6(monkeypatch, capsys):
    """When PyQt6 is not importable, main() should print an error message and return 2."""
    # Block PyQt6 by inserting None into sys.modules for the QtWidgets import
    monkeypatch.setitem(sys.modules, "PyQt6", None)  # type: ignore[arg-type]
    monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", None)  # type: ignore[arg-type]

    mod = importlib.import_module("src.ui.modern.app")
    importlib.reload(mod)
    result = mod.main()

    assert result == 2
    captured = capsys.readouterr()
    assert "PyQt6" in captured.err
