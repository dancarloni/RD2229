from pathlib import Path
import ast
import pkgutil
import importlib


def test_no_tkinter_imports():
    # detect package root by importing rd2229
    import rd2229 as pkg

    pkg_path = Path(pkg.__file__).resolve().parent
    assert pkg_path.exists()

    bad = []
    for p in pkg_path.rglob("*.py"):
        # skip legacy folder
        if "ui_legacy" in str(p):
            continue
        try:
            src = p.read_text(encoding="utf8")
        except Exception:
            continue
        if "import tkinter" in src or "from tkinter" in src:
            bad.append(str(p))

    assert bad == [], f"Found tkinter imports in non-legacy modules: {bad}"
