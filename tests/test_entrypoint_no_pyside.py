import builtins
import importlib
import os
import sys
from pathlib import Path


def test_entrypoint_graceful_no_pyside(monkeypatch, capsys):
    # ensure package import path: add src/ to sys.path if needed
    try:
        import rd2229  # noqa: F401
    except ModuleNotFoundError:
        root = Path(__file__).resolve().parents[1]
        src_path = str(root / "src")
        if os.path.isdir(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)

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
