"""Run mypy using explicit package bases mapping for CI-like runs.

Usage:
    python tools/run_mypy_ci.py

This ensures mypy sees `src` as the package base and avoids duplicate-module errors
in local editable installs where the repo root appears on sys.path.
"""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    # Run mypy with explicit-package-bases so that src/ is treated as the package root.
    cmd = [
        sys.executable,
        "-m",
        "mypy",
        "--config-file",
        "mypy.ini",
        "--explicit-package-bases",
        "src",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
