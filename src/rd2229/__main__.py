"""Package runner: invokes the Qt app main entrypoint.

This allows `python -m rd2229` to start the new Qt shell when available.
"""

from __future__ import annotations

from src.cli.entrypoint import main as cli_main


def main():
    """Package runner: invoke CLI main by default after GUI removal."""
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
