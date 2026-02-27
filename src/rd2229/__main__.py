"""Package runner: invokes the Qt app main entrypoint.

This allows `python -m rd2229` to start the new Qt shell when available.
"""

from __future__ import annotations

from .ui_qt import app


def main():
    return app.main()


if __name__ == "__main__":
    raise SystemExit(main())
