"""Minimal Qt application entrypoint used for smoke tests and `-m` execution.

If `PySide6` is missing, `main()` prints a user-friendly message and exits
with a non-zero code instead of raising a stack trace.
"""

from __future__ import annotations

import os
import sys

from rd2229.ui_qt.pages.home import HomePage
from rd2229.ui_qt.pages.settings import SettingsPage
from rd2229.ui_qt.pages.verification import VerificationPage


def main() -> int:
    try:
        import PySide6  # type: ignore
        from PySide6 import QtWidgets  # type: ignore
        from PySide6.QtCore import Qt  # type: ignore
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
    window.resize(1180, 760)

    # Central area: left navigation + stacked pages on the right
    central = QtWidgets.QWidget()
    main_layout = QtWidgets.QHBoxLayout(central)

    # Navigation list
    nav = QtWidgets.QListWidget()
    nav.setFixedWidth(200)
    nav.addItems(["Home", "Verification", "Settings"])

    # Stacked pages
    stack = QtWidgets.QStackedWidget()

    home = HomePage()
    ver = VerificationPage()
    settings = SettingsPage()

    stack.addWidget(home)
    stack.addWidget(ver)
    stack.addWidget(settings)

    # Wire navigation selection
    def on_nav_changed(index: int) -> None:
        stack.setCurrentIndex(index)

    nav.currentRowChanged.connect(on_nav_changed)
    nav.setCurrentRow(0)

    main_layout.addWidget(nav)
    main_layout.addWidget(stack, 1)

    window.setCentralWidget(central)

    # Basic toolbar
    toolbar = window.addToolBar("Main")
    act_about = toolbar.addAction("About")
    act_about.triggered.connect(lambda: QtWidgets.QMessageBox.information(window, "About", "rd2229 — Qt UI (skeleton)"))

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
