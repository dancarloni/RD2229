import importlib
import pytest


def test_ui_qt_app_import_and_main():
    pytest.importorskip("PySide6", reason="PySide6 not installed; Qt smoke skipped")
    mod = importlib.import_module("src.rd2229.ui_qt.app")
    assert hasattr(mod, "main")
    res = mod.main()
    assert res == 0
