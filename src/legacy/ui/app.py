"""Entrypoint della GUI moderna RD2229 – DEPRECATED.

.. deprecated::
    Usa ``rd2229-gui`` (PyQt6) oppure ``src.ui.modern.app:main``.
    Vedi ``legacy/README_LEGACY.md`` per i dettagli di migrazione.

Avvio::

    python -m src.ui.app

"""

from __future__ import annotations

import sys
import warnings


def main() -> int:
    """Funzione principale – rimanda alla GUI PyQt6 moderna.

    .. deprecated::
        Use ``rd2229-gui`` (PyQt6) instead.

    Returns:
        Exit code forwarded from ``src.ui.modern.app:main``.
    """
    warnings.warn(
        "src.ui.app:main is deprecated. Use 'rd2229-gui' (PyQt6) instead. "
        "See legacy/README_LEGACY.md for migration details.",
        DeprecationWarning,
        stacklevel=2,
    )
    from src.ui.modern.app import main as modern_main

    return modern_main()


if __name__ == "__main__":
    sys.exit(main())
