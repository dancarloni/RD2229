"""Entrypoint della GUI moderna RD2229 (PySide6).

Avvio::

    python -m src.ui.app

Richiede PySide6::

    pip install "rd2229[gui]"
    # oppure
    pip install PySide6>=6.6

Se PySide6 non è installato il modulo stampa un messaggio utile ed esce
con codice 1 senza crashare.
"""

from __future__ import annotations

import sys


def main() -> int:
    """Funzione principale – avvia la GUI moderna.

    Returns:
        Exit code (0 = successo, 1 = errore/PySide6 mancante).
    """
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print(
            "Errore: PySide6 non è installato.\n"
            "Installa la dipendenza opzionale GUI:\n"
            "    pip install 'rd2229[gui]'\n"
            "oppure direttamente:\n"
            "    pip install 'PySide6>=6.6'",
            file=sys.stderr,
        )
        return 1

    # Registra le schede built-in
    from src.ui.modern.features.builtin_features import register_builtin_features
    register_builtin_features()

    # Apri la finestra principale
    from src.ui.modern.main_window import ModernMainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    window = ModernMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
