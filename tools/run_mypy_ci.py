"""Run mypy using explicit package bases mapping for CI-like runs.

Usage:
    python tools/run_mypy_ci.py

This ensures mypy sees `src` as the package base and avoids duplicate-module errors
in local editable installs where the repo root appears on sys.path.
"""
from __future__ import annotations

import sys
from mypy import api


def main() -> int:
    args = ["--config-file", "mypy.ini", "--explicit-package-bases", "src=.", "src"]
    stdout, stderr, exit_status = api.run(args)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
