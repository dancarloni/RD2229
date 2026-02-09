#!/usr/bin/env python3
"""Esegue gli strumenti di lint/format usando l'interprete corrente (presumibilmente .venv).

Azioni:
 - rimuove la cache di pre-commit (se presente)
 - rimuove attributo sola lettura dai file del repo
 - esegue `black`, `isort`, `ruff format`, `ruff check`, `mypy`, `bandit`

Usa: .venv\\Scripts\\python.exe scripts\run_lint_from_venv.py
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess  # nosec
import sys
from pathlib import Path


def _on_rm_error(func, path, exc_info):
    # Called by shutil.rmtree on error; try to make writable and retry
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:  # nosec
        pass


def rmdir_force(p: Path):
    if not p.exists():
        return False
    try:
        shutil.rmtree(p, onerror=_on_rm_error)
        return True
    except Exception as e:
        print(f"Warning: cannot remove {p!s}: {e}")
        return False


def run(cmd, check=False):
    print(f"\n>>> Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)  # nosec
    print(proc.stdout)
    return proc.returncode


def main():
    repo_root = Path(__file__).resolve().parents[1]
    home = Path.home()

    # 1) remove pre-commit cache
    # Prefer an isolated cache inside the project .venv to avoid permission
    # issues with the user's global cache. Set PRE_COMMIT_HOME accordingly.
    venv_cache = repo_root / ".venv" / ".cache" / "pre-commit"
    venv_cache.mkdir(parents=True, exist_ok=True)
    os.environ["PRE_COMMIT_HOME"] = str(venv_cache)
    print(f"Using PRE_COMMIT_HOME={venv_cache}")

    # Remove any existing user-level cache as a best-effort (optional)
    user_cache = home / ".cache" / "pre-commit"
    if user_cache.exists():
        try:
            print(f"Removing user pre-commit cache: {user_cache}")
            rmdir_force(user_cache)
        except Exception as e:
            print(f"Warning: could not remove user cache: {e}")
    else:
        print("No user pre-commit cache found")

    # 2) remove read-only attribute via attrib (works on Windows)
    # 2) remove read-only attribute recursively from repo files
    try:
        cmd = ["cmd", "/c", "attrib", "-R", str(repo_root / "*.*"), "/S"]
        subprocess.run(cmd, check=False)  # nosec
        print("Cleared read-only attributes (attrib -R)")
    except Exception as e:
        print("Warning: attrib failed:", e)

    # Ensure all files in venv_cache are writable to avoid WinError 5 during hook
    try:
        for p in venv_cache.rglob("*"):
            try:
                mode = p.stat().st_mode
                os.chmod(p, mode | stat.S_IWRITE)
            except Exception:  # nosec
                pass
        print("Ensured pre-commit cache files are writable")
    except Exception:  # nosec
        pass

    # 3) run formatters and linters using current interpreter
    py = sys.executable

    steps = [
        [py, "-m", "black", "."],
        [py, "-m", "isort", "."],
        [py, "-m", "ruff", "format", "."],
        [py, "-m", "ruff", "check", "."],
        [py, "-m", "mypy", "src", "config"],
        [py, "-m", "bandit", "-r", "."],
    ]

    results = {}
    for cmd in steps:
        rc = run(cmd)
        results[" ".join(cmd[2:])] = rc

    print("\nSummary:")
    for k, v in results.items():
        print(f" - {k}: returncode={v}")

    # Run pre-commit at the end using the isolated PRE_COMMIT_HOME inside .venv
    rc = run([py, "-m", "pre_commit", "run", "--all-files"])
    results["pre-commit run --all-files"] = rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
