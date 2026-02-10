#!/usr/bin/env python3
"""
verify_softw_components.py

Checks internal import dependencies for the `libs.app_module` directory.

Usage:
    python tools/verify_softw_components.py [--dir libs.app_module]

This script parses Python files under the given directory, builds a map of local
modules (dotted names -> file paths) and reports any import statements that
refer to local modules that are missing in the directory.

It does NOT attempt to import third-party packages or check installed deps;
it only verifies local/module-level consistency inside `libs.app_module`.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


def find_python_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def module_name_from_path(path: Path, src_root: Path) -> str:
    rel = path.relative_to(src_root)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_imports(file_path: Path) -> list[ast.AST]:
    try:
        text = file_path.read_text(encoding="utf8")
        tree = ast.parse(text)
        return [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    except Exception:
        return []


def resolve_relative(from_mod: str, level: int, module: str | None) -> str | None:
    # from_mod: e.g. 'app_module.ui.module_selector'
    if level == 0:
        return module
    parts = from_mod.split(".") if from_mod else []
    if level > len(parts) + 1:
        return None
    base = parts[: max(0, len(parts) - level + 1)]
    if module:
        return ".".join(base + module.split(".")) if base else module
    return ".".join(base) if base else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="libs.app_module")
    args = p.parse_args()
    root = Path(args.dir)
    if not root.exists():
        raise SystemExit(f"Directory {root} not found")

    py_files = find_python_files(root)
    module_map: dict[str, Path] = {module_name_from_path(p, root): p for p in py_files}

    missing: dict[Path, set[str]] = {}
    external: dict[Path, set[str]] = {}

    for p in py_files:
        modname = module_name_from_path(p, root)
        nodes = parse_imports(p)
        for node in nodes:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    top = name.split(".")[0]
                    # if top is a local module, check existence
                    if top in module_map:
                        # try resolving progressively longer prefixes
                        parts = name.split(".")
                        found = False
                        for i in range(len(parts), 0, -1):
                            candidate = ".".join(parts[:i])
                            if candidate in module_map:
                                found = True
                                break
                        if not found:
                            missing.setdefault(p, set()).add(name)
                    else:
                        external.setdefault(p, set()).add(name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                level = node.level
                resolved = resolve_relative(modname, level, module)
                if not resolved:
                    # cannot resolve (likely imports beyond package root)
                    external.setdefault(p, set()).add(f"from {'.' * level}{module or ''}")
                    continue
                top = resolved.split(".")[0]
                if top in module_map:
                    # check if resolved or prefix exists
                    parts = resolved.split(".")
                    found = False
                    for i in range(len(parts), 0, -1):
                        candidate = ".".join(parts[:i])
                        if candidate in module_map:
                            found = True
                            break
                    if not found:
                        missing.setdefault(p, set()).add(resolved)
                else:
                    external.setdefault(p, set()).add(f"from {resolved}")

    # Report
    print(f"Scanned {len(py_files)} python files under {root}")
    if missing:
        print("\nMissing local modules referenced:")
        for fp, names in missing.items():
            print(f" - {fp}: {sorted(names)}")
    else:
        print("\nNo missing local modules detected.")

    print("\nExamples of non-local/third-party imports (not checked):")
    cnt = 0
    for fp, names in external.items():
        print(f" - {fp}: {sorted(list(names)[:5])}")
        cnt += 1
        if cnt >= 20:
            break

    print("\nSummary:")
    print(f" - local modules: {len(module_map)}")
    print(f" - files with missing local refs: {len(missing)}")
    print(f" - files with external imports: {len(external)}")


if __name__ == "__main__":
    main()
