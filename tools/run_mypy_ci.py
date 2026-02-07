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
    # Prefer calling mypy via the CLI to avoid argument parsing quirks on Windows.
    cmd_variants = [
        # Try combined form first (most robust for CLI parsers):
        [sys.executable, "-m", "mypy", "--config-file", "mypy.ini", "--explicit-package-bases=src=.", "src"],
        # Fallback: separate args (older mypy or different parsers may accept this)
        [sys.executable, "-m", "mypy", "--config-file", "mypy.ini", "--explicit-package-bases", "src=.", "src"],
    ]

    for cmd in cmd_variants:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            if proc.stdout:
                print(proc.stdout)
            return 0
        # If output indicates unknown arg parsing, try the next variant
        if "ignored explicit argument" in (proc.stderr or "") or "can't read file 'src=." in (proc.stderr or ""):
            # try next variant
            continue
        # Otherwise, print whatever mypy returned and return the exit code
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode

    # If all variants failed due to parsing issues, return last exit code with stderr
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
