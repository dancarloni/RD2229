"""Entrypoint della GUI moderna RD2229 (PySide6) – DEPRECATED.

.. deprecated::
    Usa ``rd2229-gui`` (PyQt6) oppure ``src.ui.modern.app:main``.
    Vedi ``legacy/README_LEGACY.md`` per i dettagli di migrazione.

Avvio::

    python -m src.ui.app

Richiede PySide6::

    pip install PySide6>=6.6

Se PySide6 non è installato il modulo stampa un messaggio utile ed esce
con codice 1 senza crashare.
"""

from __future__ import annotations

import sys
import warnings


def main() -> int:
    """Funzione principale – avvia la GUI moderna (PySide6 legacy).

    .. deprecated::
        Use ``rd2229-gui`` (PyQt6) instead.

    Returns:
        Exit code (0 = successo, 1 = errore/PySide6 mancante).
    """
    warnings.warn(
        "src.ui.app:main is deprecated. Use 'rd2229-gui' (PyQt6) instead. "
        "See legacy/README_LEGACY.md for migration details.",
        DeprecationWarning,
        stacklevel=2,
    )
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
