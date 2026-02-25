from pathlib import Path
import ast
import pkgutil
import importlib
import sys
import os


def test_no_tkinter_imports():
    # ensure package import path: add src/ to sys.path if needed
    try:
        import rd2229 as pkg
    except ModuleNotFoundError:
        # attempt to locate src/ directory upwards
        p = Path(__file__).resolve()
        for _ in range(6):
            p = p.parent
            candidate = p / "src"
            if candidate.is_dir():
                src_path = str(candidate)
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                break
        import rd2229 as pkg

    pkg_file = getattr(pkg, "__file__", None)
    if pkg_file:
        pkg_path = Path(pkg_file).resolve().parent
    else:
        import importlib.util

        spec = importlib.util.find_spec("rd2229")
        if spec and spec.submodule_search_locations:
            pkg_path = Path(spec.submodule_search_locations[0])
        else:
            raise RuntimeError("Cannot locate rd2229 package path")
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
