#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path


def on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
    except Exception:  # nosec
        pass
    try:
        func(path)
    except Exception:  # nosec
        pass


def main():
    repo = Path(__file__).resolve().parents[1]
    target = repo / ".venv" / ".cache" / "pre-commit" / "reposi0py3sf"
    if not target.exists():
        print(f"Target does not exist: {target}")
        return 0
    try:
        shutil.rmtree(target, onerror=on_rm_error)
        print(f"Removed {target}")
        return 0
    except Exception as e:
        print(f"Failed to remove {target}: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
