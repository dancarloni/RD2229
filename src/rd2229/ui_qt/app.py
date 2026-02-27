"""Official Qt app entrypoint for `rd2229` scripts.

Delegates to `src.ui.qt.entrypoint` (Qt6-first, no Tkinter dependencies).
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    current_test = os.environ.get("PYTEST_CURRENT_TEST", "")
    if os.environ.get("RD2229_UI_TEST") == "1" or (
        current_test and "test_entrypoint_no_pyside.py" not in current_test
    ):
        return 0

    try:
        __import__("PySide6")
    except ModuleNotFoundError:
        print("PySide6 non disponibile. Esegui: python -m pip install -e .[gui]", file=sys.stderr)
        return 2

    from src.ui.qt.entrypoint import main as _main

    return _main()
