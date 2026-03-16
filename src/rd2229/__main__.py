"""Package runner.

Starts the modern Qt GUI entrypoint by default and falls back to CLI when
GUI dependencies are not available.
"""

from __future__ import annotations

from src.cli.entrypoint import main as cli_main
from src.ui.modern.app import main as modern_gui_main


def main():
    """Invoke modern GUI by default; fallback to CLI if GUI dependencies are missing."""
    try:
        return modern_gui_main()
    except ImportError:
        return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
