#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path


def make_all_writable(root: Path):
    for p in root.rglob("*"):
        try:
            os.chmod(p, stat.S_IWRITE)
        except Exception:
            try:
                # try to set writable for directories
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except Exception:  # nosec
                pass


def main():
    repo = Path(__file__).resolve().parents[1]
    cache = repo / ".venv" / ".cache" / "pre-commit"
    if not cache.exists():
        print(f"No cache at {cache}")
        return 0
    try:
        make_all_writable(cache)
    except Exception as e:
        print("make_all_writable failed:", e)
    try:
        shutil.rmtree(cache)
        print(f"Removed cache {cache}")
        cache.mkdir(parents=True, exist_ok=True)
        print(f"Recreated empty cache {cache}")
        return 0
    except Exception as e:
        print(f"Failed to remove cache: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
