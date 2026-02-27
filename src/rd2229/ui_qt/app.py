"""Minimal Qt application entrypoint used for smoke tests and `-m` execution.

`main()` performs a light import of PySide6 and returns 0 on success.
If PySide6 is not available it raises ImportError so tests can skip.
"""

from __future__ import annotations

def main() -> int:
    try:
        # only import Qt to ensure it's available; do not start event loop here
        import PySide6  # noqa: F401
        from PySide6 import QtWidgets  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on environment
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
