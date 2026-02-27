#!/usr/bin/env python3
"""Cleanup helper: try to remove .exe files in .venv pre-commit cache.

This attempts to make files writable and delete them. It reports any files
that could not be removed so the user can run an elevated cleanup if needed.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path


def make_writable(p: Path) -> bool:
    try:
        mode = p.stat().st_mode
        p.chmod(mode | stat.S_IWRITE)
        return True
    except Exception:
        try:
            os.chmod(p, stat.S_IWRITE)
            return True
        except Exception:
            return False


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    venv_cache = repo / ".venv" / ".cache" / "pre-commit"
    if not venv_cache.exists():
        print(f"No venv pre-commit cache at {venv_cache}")
        return 0

    failed: list[Path] = []
    removed = 0
    for p in venv_cache.rglob("*"):
        if p.is_file() and p.suffix.lower() == ".exe":
            try:
                if not make_writable(p):
                    print(f"Could not make writable: {p}")
                p.unlink()
                removed += 1
            except Exception as e:
                print(f"Failed to remove {p}: {e}")
                failed.append(p)

    print(f"Removed {removed} .exe files from {venv_cache}")
    if failed:
        print("Files that could not be removed (require elevation):")
        for p in failed:
            print(" - ", p)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
