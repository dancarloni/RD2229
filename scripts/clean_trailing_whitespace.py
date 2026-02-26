#!/usr/bin/env python3
r"""Rimuove spazi finali e garantisce newline finale per file testuali.

Usare con l'interprete della `.venv`:
  .venv\Scripts\python.exe scripts\clean_trailing_whitespace.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", ".venv", ".venv_old", "__pycache__", "node_modules", ".cache"}
EXTS = {".py", ".md", ".txt", ".rst", ".ini", ".cfg", ".json", ".yml", ".yaml", ".toml", ".csv"}


def should_process(p: Path) -> bool:
    if any(part in EXCLUDE for part in p.parts):
        return False
    if p.is_file() and p.suffix.lower() in EXTS:
        return True
    return False


def fix_file(p: Path) -> bool:
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return False
    lines = text.splitlines()
    new_lines = [ln.rstrip(" \t") for ln in lines]
    new_text = "\n".join(new_lines) + ("\n" if new_lines else "")
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for p in ROOT.rglob("*"):
        if should_process(p):
            if fix_file(p):
                print(f"Fixed: {p.relative_to(ROOT)}")
                changed += 1
    print(f"Files changed: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
