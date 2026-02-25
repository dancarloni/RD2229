"""Minimal Qt application entrypoint used for smoke tests and `-m` execution.

If `PySide6` is missing, `main()` prints a user-friendly message and exits
with a non-zero code instead of raising a stack trace.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    try:
        import PySide6  # type: ignore
        from PySide6 import QtWidgets  # type: ignore
    except ModuleNotFoundError:
        msg = (
            "GUI dependency missing: to run the graphical interface install:\n"
            "  python -m pip install -e .[gui]\n"
            "Then run: rd2229 or python -m rd2229"
        )
        print(msg, file=sys.stderr)
        return 2

    # If running in test mode, do not start the Qt event loop
    if os.environ.get("RD2229_UI_TEST"):
        return 0

    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("rd2229")
    window.resize(800, 600)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
