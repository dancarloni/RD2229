import importlib
import pytest


def test_ui_qt_app_import_and_main(monkeypatch):
    pytest.importorskip("PySide6", reason="PySide6 not installed; Qt smoke skipped")
    monkeypatch.setenv("RD2229_UI_TEST", "1")
    mod = importlib.import_module("rd2229.ui_qt.app")
    assert hasattr(mod, "main")
    res = mod.main()
    assert res == 0
