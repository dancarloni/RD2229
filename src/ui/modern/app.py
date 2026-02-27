"""Compatibility PyQt6 app entrypoint used by smoke tests."""

from __future__ import annotations

import os
import sys


def main() -> int:
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
    except ModuleNotFoundError:
        print("PyQt6 non disponibile. Installa le dipendenze GUI.", file=sys.stderr)
        return 2

    if os.environ.get("RD2229_UI_TEST") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return 0

    app = QApplication.instance() or QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("RD2229")
    window.show()
    return app.exec()
