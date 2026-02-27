"""GUI entrypoint for RD2229 modern interface."""

from __future__ import annotations

from src.ui.modern.app import main as modern_main


def main() -> int:
    return modern_main()


if __name__ == "__main__":
    raise SystemExit(main())
