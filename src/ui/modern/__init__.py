"""Pacchetto src.ui.modern – GUI moderna PySide6 per RD2229.

Struttura:
    - :mod:`src.ui.modern.app` – entrypoint principale (``python -m src.ui.app``)
    - :mod:`src.ui.modern.main_window` – QMainWindow + layout base
    - :mod:`src.ui.modern.navigation` – sidebar + stacked navigation
    - :mod:`src.ui.modern.features` – feature registry e base FeatureSpec
    - :mod:`src.ui.modern.viewmodels` – logica UI (no calcolo)
    - :mod:`src.ui.modern.services` – adapter verso core/repository
    - :mod:`src.ui.modern.workers` – esecuzione pipeline in background

Dipendenza opzionale::

    pip install "rd2229[gui]"   # aggiunge PySide6>=6.6
"""
