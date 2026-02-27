"""Package runner.

Starts the Qt GUI entrypoint by default and falls back to CLI when Qt is
not available.
"""

from __future__ import annotations

from src.cli.entrypoint import main as cli_main
from src.rd2229.ui_qt.app import main as qt_main


def main():
    """Invoke Qt GUI by default; fallback to CLI if Qt dependencies are missing."""
    try:
        return qt_main()
    except ImportError:
        return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
