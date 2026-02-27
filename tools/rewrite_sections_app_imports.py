#!/usr/bin/env python3
"""
rewrite_sections_app_imports.py

Automatically rewrite imports that reference `sections_app.*` inside
`softw_components` to the actual module names present under `softw_components`.

Usage:
    python tools/rewrite_sections_app_imports.py [--dir softw_components] [--dry-run]

Behaviour:
- Scans `--dir` for Python modules and builds a map of module names -> paths.
- For each import/import-from that starts with `sections_app` tries to find a
  unique replacement module under `softw_components` whose module name endswith
  the same suffix. If found, replaces the import token with the new module name.
- If multiple candidates exist, chooses the longest match (most specific).
- Writes files in-place unless `--dry-run` is given.

"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


def find_python_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def module_name_from_path(path: Path, src_root: Path) -> str:
    rel = path.relative_to(src_root)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_imports(path: Path) -> list[tuple[str, int | None, list[str]]]:
    # returns list of (module, level, names) where module may be None for 'from . import'
    try:
        src = path.read_text(encoding="utf8")
        tree = ast.parse(src)
    except Exception:
        return []
    records = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                records.append((alias.name, 0, []))
        elif isinstance(node, ast.ImportFrom):
            records.append((node.module, node.level, [a.name for a in node.names]))
    return records


def build_module_map(root: Path) -> dict[str, Path]:
    files = find_python_files(root)
    return {module_name_from_path(p, root): p for p in files}


def find_replacement(module_map: dict[str, Path], original: str) -> str | None:
    # original like 'sections_app.services.repository' or 'sections_app'
    if not original.startswith("sections_app"):
        return None
    if original == "sections_app":
        # find candidate that matches top-level package content, prefer 'sections_app_module' if exists
        candidates = [m for m in module_map.keys() if m.endswith("__init__") or m.count(".") == 0]
    else:
        suffix = original[len("sections_app.") :]
        candidates = [m for m in module_map.keys() if m.endswith(suffix)]
    if not candidates:
        return None
    # choose longest (most specific) module name to prefer deeper matches
    candidates.sort(key=lambda s: -len(s))
    return candidates[0]


def rewrite_file(path: Path, mapping: dict[str, str]) -> tuple[bool, list[tuple[str, str]]]:
    text = path.read_text(encoding="utf8")
    new_text = text
    performed = []
    # replace in from-import first
    for orig, new in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        # from X import ...
        pattern_from = re.compile(rf"(^|\n)(\s*from\s+){re.escape(orig)}(\b)", flags=re.MULTILINE)
        new_text, n1 = pattern_from.subn(rf"\1\2{new}\3", new_text)
        if n1:
            performed.append((orig, new))
        # import X
        pattern_import = re.compile(rf"(^|\n)(\s*import\s+.*)\b{re.escape(orig)}\b", flags=re.MULTILINE)
        new_text, n2 = pattern_import.subn(lambda m: m.group(1) + m.group(2).replace(orig, new), new_text)
        if n2:
            performed.append((orig, new))
    if new_text != text:
        path.write_text(new_text, encoding="utf8")
        return True, performed
    return False, []


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="softw_components")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    root = Path(args.dir)
    if not root.exists():
        raise SystemExit(f"Directory {root} not found")

    module_map = build_module_map(root)
    print(f"Found {len(module_map)} modules under {root}")

    files = find_python_files(root)
    total_changes = 0
    for f in files:
        records = parse_imports(f)
        mapping = {}
        for mod, level, names in records:
            if not mod:
                continue
            if mod.startswith("sections_app"):
                repl = find_replacement(module_map, mod)
                if repl and repl != mod:
                    mapping[mod] = repl
        if mapping:
            print(f"File: {f} -> replacements: {mapping}")
            if not args.dry_run:
                changed, perf = rewrite_file(f, mapping)
                if changed:
                    total_changes += 1
                    print(f"  Rewrote {f}: {perf}")

    print(f"Done. Files changed: {total_changes}")


if __name__ == "__main__":
    main()
