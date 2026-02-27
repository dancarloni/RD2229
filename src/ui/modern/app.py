"""PyQt6 GUI entry point for RD2229.

Avvio::

    python -m src.ui.modern.app
    rd2229-gui          # after installation

Richiede PyQt6::

    pip install "rd2229[gui]"

Se PyQt6 non è installato il modulo stampa un messaggio utile ed esce con
codice 2 senza crashare.  Se la variabile d'ambiente ``RD2229_UI_TEST`` è
impostata, l'event loop non viene avviato e la funzione restituisce 0
immediatamente (utile per smoke-test in CI headless).
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    """Avvia la GUI PyQt6.

    Returns:
        0  – successo (o test mode)
        1  – errore di runtime
        2  – PyQt6 non installato
    """
    try:
        from PyQt6.QtWidgets import QApplication  # noqa: F401
    except ImportError:
        print(
            "Errore: PyQt6 non è installato.\n"
            "Installa la dipendenza opzionale GUI:\n"
            "    pip install 'rd2229[gui]'\n"
            "oppure direttamente:\n"
            "    pip install 'PyQt6>=6.4'",
            file=sys.stderr,
        )
        return 2

    # Allow CI smoke-tests without starting the event loop
    if os.environ.get("RD2229_UI_TEST"):
        return 0

    try:
        from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

        app = QApplication.instance() or QApplication(sys.argv)

        window = QMainWindow()
        window.setWindowTitle("RD2229 v0.1.0")
        window.resize(900, 600)
        label = QLabel("RD2229 — Structural Engineering Calculations", window)
        label.setStyleSheet("font-size: 18px; padding: 20px;")
        window.setCentralWidget(label)
        window.show()

        return app.exec()  # type: ignore[return-value]
    except Exception as exc:
        print(f"GUI error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
