import builtins
import importlib
import sys


def test_entrypoint_graceful_no_pyside(monkeypatch, capsys):
    # Import module (does not import PySide6 at top-level)
    mod = importlib.import_module("rd2229.ui_qt.app")

    # Monkeypatch builtins.__import__ to raise ModuleNotFoundError for PySide6
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("PySide6"):
            raise ModuleNotFoundError("No PySide6")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        res = mod.main()
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)

    captured = capsys.readouterr()
    assert res == 2
    assert "python -m pip install -e .[gui]" in captured.err
