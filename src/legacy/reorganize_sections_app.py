#!/usr/bin/env python3
"""
reorganize_sections_app.py

Reorganize SECTIONS_APP into per-module folders based on dependency analysis.

Usage examples
--------------
  Dry-run (prints plan without writing any files):
    python reorganize_sections_app.py --root sections_app --out SECTIONS_APP_REFACTORED --dry-run

  Real run:
    python reorganize_sections_app.py --root sections_app --out SECTIONS_APP_REFACTORED

  Process only specific modules:
    python reorganize_sections_app.py --root sections_app --out SECTIONS_APP_REFACTORED --modules geometry historical

Configuration
-------------
  Edit ROOT_MODULES below to control which modules are extracted.
  Each entry is the basename (without .py) of a file in sections_app/modules/.

How it works
------------
  1. Scans all .py files in sections_app and builds a dependency graph using AST
     import analysis.  Module names are computed WITH the package prefix
     (e.g. "sections_app.ui.main_window") so that absolute imports resolve correctly.
  2. For each root module, collects the transitive dependency set via BFS.
  3. Copies the file set into an output folder preserving the internal directory
     structure (e.g. SECTIONS_APP_REFACTORED/geometry/ui/main_window.py).
  4. Rewrites absolute imports: replaces "sections_app." with "<module_name>."
     in all copied Python files.  Relative imports are left unchanged because
     the internal structure is preserved.
  5. Filters __init__.py files so they only reference sub-modules/packages that
     were actually copied.
  6. Copies resource files (.json, .csv, ...) referenced by the module's code.

Requires Python 3.8+ (uses ast node end_lineno).
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import shutil
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURATION — edit these to match your project
# ---------------------------------------------------------------------------

# Root modules to extract (basenames of .py files in sections_app/modules/).
ROOT_MODULES: list[str] = [
    "frc",
    "historical",
    "geometry",
    "verification",
    "material",
    "debug",
]

# The package name as it appears in import statements.
PACKAGE_NAME = "sections_app"

# File extensions treated as copyable resources.
RESOURCE_EXTS: set[str] = {".json", ".csv", ".txt", ".yaml", ".yml", ".ini"}

# Directories to skip during scanning.
IGNORE_DIRS: set[str] = {"__pycache__", ".mypy_cache", ".pytest_cache"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DepGraph:
    """Container for the results of dependency graph construction."""

    graph: dict[Path, set[Path]] = field(default_factory=lambda: defaultdict(set))
    modname_to_path: dict[str, Path] = field(default_factory=dict)
    path_to_modname: dict[Path, str] = field(default_factory=dict)
    file_to_literals: dict[Path, set[str]] = field(default_factory=lambda: defaultdict(set))


# ---------------------------------------------------------------------------
# Phase 1 — Build dependency graph
# ---------------------------------------------------------------------------


def find_python_files(root: Path) -> list[Path]:
    """Return all .py files under *root*, skipping ignored directories."""
    result: list[Path] = []
    for p in root.rglob("*.py"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        result.append(p)
    return result


def module_name_from_path(root: Path, p: Path, package_name: str) -> str:
    """Compute the dotted module name INCLUDING the package prefix.

    Examples (assuming package_name="sections_app"):
      root/ui/main_window.py  -> "sections_app.ui.main_window"
      root/domain/__init__.py -> "sections_app.domain"
      root/__init__.py        -> "sections_app"
    """
    rel = p.relative_to(root)
    parts = list(rel.with_suffix("").parts)
    # __init__ represents the package itself, not a sub-module
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if parts:
        return package_name + "." + ".".join(parts)
    return package_name


def _parse_imports_and_literals(filepath: Path) -> tuple[set[str], set[str]]:
    """Parse a Python file with AST and return (import_strings, string_literals)."""
    imports: set[str] = set()
    literals: set[str] = set()
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return imports, literals
    try:
        tree = ast.parse(text)
    except Exception:
        return imports, literals

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = getattr(node, "level", 0) or 0

            if level > 0:
                # Relative import — encode as leading dots so we can resolve later
                prefix = "." * level
                full = prefix + module if module else prefix
            else:
                full = module

            if full:
                imports.add(full)
            # Also record module.name variants (the imported name might be a sub-module)
            for alias in node.names:
                if alias.name and module:
                    imports.add(full + "." + alias.name if level == 0 else full + "." + alias.name)

        # Collect string literals for resource detection
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)

    return imports, literals


def _resolve_relative_import(imp: str, src_modname: str, is_package: bool = False) -> str:
    """Convert a relative import string (with leading dots) to an absolute one.

    For regular modules (e.g. ``services/area_calculations.py`` whose modname is
    ``sections_app.services.area_calculations``), level=1 means "this package"
    which strips the last segment to get ``sections_app.services``.

    For ``__init__.py`` files (e.g. ``domain/__init__.py`` whose modname is
    ``sections_app.domain``), the module IS the package, so level=1 stays in the
    same package (no stripping).  Set *is_package=True* for this case.

    Examples:
      imp="..domain.base", src_modname="sections_app.services.area_calculations"
      -> "sections_app.domain.base"

      imp=".base", src_modname="sections_app.domain", is_package=True
      -> "sections_app.domain.base"
    """
    level = len(imp) - len(imp.lstrip("."))
    rest = imp[level:]
    parts = src_modname.split(".")
    # For __init__.py the module IS the package, so effective level is one less
    effective_level = max(level - 1, 0) if is_package else level
    if effective_level > len(parts):
        return ""  # invalid relative import
    base = parts[:-effective_level] if effective_level else parts
    if rest:
        return ".".join(base) + "." + rest
    return ".".join(base)


def build_dependency_graph(root: Path, package_name: str) -> DepGraph:
    """Scan all .py files under *root* and build a dependency graph.

    Module names are computed WITH the package prefix so that absolute imports
    like ``from sections_app.ui.main_window import MainWindow`` resolve via
    exact match.
    """
    dg = DepGraph()
    py_files = find_python_files(root)

    # Step 1: Register every .py file as a module name
    for p in py_files:
        modname = module_name_from_path(root, p, package_name)
        dg.modname_to_path[modname] = p
        dg.path_to_modname[p] = modname

    # Step 2: Parse imports and literals from every file
    file_to_imports: dict[Path, set[str]] = {}
    for p in py_files:
        imports, literals = _parse_imports_and_literals(p)
        file_to_imports[p] = imports
        dg.file_to_literals[p] = literals

    # Step 3: Resolve import strings to file paths and build graph edges
    def resolve(imp: str, src_modname: str, is_package: bool = False) -> Path | None:
        # Handle relative imports
        if imp.startswith("."):
            imp = _resolve_relative_import(imp, src_modname, is_package=is_package)
            if not imp:
                return None

        # Only consider imports within our package
        if not imp.startswith(package_name):
            return None

        # Try exact match
        if imp in dg.modname_to_path:
            return dg.modname_to_path[imp]

        # The last segment might be a class/function name, not a module.
        # Strip it and retry.  E.g. "sections_app.models.sections.Section"
        # -> try "sections_app.models.sections"
        dot = imp.rfind(".")
        if dot > 0:
            parent = imp[:dot]
            if parent in dg.modname_to_path:
                return dg.modname_to_path[parent]

        return None

    for p, imports in file_to_imports.items():
        src_modname = dg.path_to_modname[p]
        is_pkg = p.name == "__init__.py"
        for imp in imports:
            target = resolve(imp, src_modname, is_package=is_pkg)
            if target and target != p:
                dg.graph[p].add(target)

    return dg


# ---------------------------------------------------------------------------
# Phase 2 — Collect per-module dependency sets
# ---------------------------------------------------------------------------


def collect_module_dependencies(
    root: Path,
    dg: DepGraph,
    module_basename: str,
) -> set[Path]:
    """Return the transitive closure of files that *module_basename* depends on.

    Also ensures that every package directory containing at least one included
    file has its ``__init__.py`` added to the set (so the output is a valid
    Python package tree).
    """
    module_file = root / "modules" / f"{module_basename}.py"
    if not module_file.exists():
        raise FileNotFoundError(f"Module file for '{module_basename}' not found at {module_file}")

    # BFS for transitive dependencies.
    # After the initial BFS, add required __init__.py files and continue BFS
    # from them so that their dependencies are also included (e.g. domain/__init__.py
    # imports domain/shapes.py which should be pulled into the set).
    result: set[Path] = set()
    queue: deque[Path] = deque([module_file])

    while queue:
        cur = queue.popleft()
        if cur in result:
            continue
        result.add(cur)
        for dep in dg.graph.get(cur, ()):
            if dep not in result:
                queue.append(dep)

    # Add __init__.py files for every package that has included files,
    # then continue BFS from them to pull their own dependencies.
    changed = True
    while changed:
        changed = False
        init_files_to_add: set[Path] = set()
        for p in result:
            d = p.parent
            while d != root and d != root.parent:
                init_py = d / "__init__.py"
                if init_py.exists() and init_py not in result:
                    init_files_to_add.add(init_py)
                d = d.parent
        root_init = root / "__init__.py"
        if root_init.exists() and root_init not in result:
            init_files_to_add.add(root_init)

        for init_file in init_files_to_add:
            if init_file not in result:
                changed = True
                queue.append(init_file)
        # Run BFS from the newly added __init__.py files
        while queue:
            cur = queue.popleft()
            if cur in result:
                continue
            result.add(cur)
            changed = True
            for dep in dg.graph.get(cur, ()):
                if dep not in result:
                    queue.append(dep)

    return result


# ---------------------------------------------------------------------------
# Phase 3 — Detect resources and copy files
# ---------------------------------------------------------------------------


def detect_resource_files(
    root: Path,
    file_set: set[Path],
    file_to_literals: dict[Path, set[str]],
) -> set[Path]:
    """Find resource files (.json, .csv, etc.) referenced by *file_set*.

    Searches for string literals in the code that match filenames of existing
    resource files under *root*.
    """
    resources: set[Path] = set()

    # Gather all resource files that exist under root
    all_resources: dict[str, list[Path]] = defaultdict(list)
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in RESOURCE_EXTS:
            if not any(part in IGNORE_DIRS for part in p.parts):
                all_resources[p.name].append(p)

    for py_file in file_set:
        if py_file.suffix != ".py":
            continue
        literals = file_to_literals.get(py_file, set())
        for lit in literals:
            # Skip long strings (likely not filenames)
            if len(lit) > 200 or "\n" in lit:
                continue
            basename = Path(lit).name
            if basename in all_resources:
                for res_path in all_resources[basename]:
                    resources.add(res_path)

    return resources


def copy_module_tree(
    root: Path,
    out_root: Path,
    module_basename: str,
    file_set: set[Path],
    resource_set: set[Path],
    dry_run: bool,
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]]]:
    """Copy Python files and resources into the output directory.

    Returns (python_mappings, resource_mappings) where each is a list of
    (source, destination) tuples.
    """
    out_dir = out_root / module_basename
    py_mappings: list[tuple[Path, Path]] = []
    res_mappings: list[tuple[Path, Path]] = []

    # Copy Python files
    for src in sorted(file_set):
        rel = src.relative_to(root)
        dest = out_dir / rel
        py_mappings.append((src, dest))
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    # Copy resource files
    for src in sorted(resource_set):
        try:
            rel = src.relative_to(root)
        except ValueError:
            rel = Path(src.name)
        dest = out_dir / rel
        res_mappings.append((src, dest))
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    return py_mappings, res_mappings


# ---------------------------------------------------------------------------
# Phase 4 — Rewrite imports in copied files
# ---------------------------------------------------------------------------


def rewrite_imports_in_file(
    filepath: Path,
    old_package: str,
    new_package: str,
    dry_run: bool,
) -> list[tuple[str, str]]:
    """Rewrite absolute imports in *filepath* from *old_package* to *new_package*.

    Uses AST to locate import statements (including multi-line ones) and
    performs targeted text replacement on the source lines.

    Returns a list of (old_line_block, new_line_block) for reporting.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        tree = ast.parse(text)
    except Exception:
        return []

    lines = text.split("\n")
    # Collect spans that need rewriting: (start_line_0idx, end_line_0idx)
    # We process them in reverse order so line indices stay valid after edits
    spans_to_rewrite: list[tuple[int, int]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        # Determine if this import references our package
        needs_rewrite = False
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name and alias.name.startswith(old_package):
                    needs_rewrite = True
                    break
        else:  # ImportFrom
            level = getattr(node, "level", 0) or 0
            module = node.module or ""
            if level == 0 and module.startswith(old_package):
                needs_rewrite = True

        if not needs_rewrite:
            continue

        start = node.lineno - 1  # AST uses 1-based
        end = getattr(node, "end_lineno", node.lineno) - 1
        spans_to_rewrite.append((start, end))

    if not spans_to_rewrite:
        return []

    rewrites: list[tuple[str, str]] = []

    # Process in reverse order to preserve line indices
    for start, end in sorted(spans_to_rewrite, reverse=True):
        old_block = "\n".join(lines[start : end + 1])
        # Replace the package name in the block.
        # Use word-boundary-aware replacement to avoid partial matches.
        # "sections_app." -> "geometry." and bare "sections_app" at word boundary
        new_block = old_block.replace(old_package + ".", new_package + ".")
        # Also handle bare package reference (e.g., "import sections_app")
        new_block = re.sub(
            rf"\b{re.escape(old_package)}\b",
            new_package,
            new_block,
        )

        if new_block != old_block:
            lines[start : end + 1] = new_block.split("\n")
            rewrites.append((old_block, new_block))

    if rewrites and not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return rewrites


# ---------------------------------------------------------------------------
# Phase 5 — Filter __init__.py files
# ---------------------------------------------------------------------------


def filter_init_file(
    source_path: Path,
    dest_path: Path,
    available_source_files: set[Path],
    dry_run: bool,
) -> list[str]:
    """Adjust an __init__.py so it only imports sub-modules that exist in the output.

    *source_path* is the original file (always readable).
    *dest_path* is the output location (written only when not dry_run).
    *available_source_files* is the set of source .py files included in the module,
    used to check which sibling modules/packages exist.

    Returns a list of descriptions of changes made (for reporting).
    """
    try:
        text = source_path.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        tree = ast.parse(text)
    except Exception:
        return []

    init_dir = source_path.parent
    lines = text.split("\n")
    changes: list[str] = []
    removals: list[tuple[int, int]] = []  # (start_0idx, end_0idx) of lines to remove

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if not isinstance(node, ast.ImportFrom):
            continue

        level = getattr(node, "level", 0) or 0
        module = node.module or ""

        # We only care about relative imports from this __init__.py
        if level == 0:
            continue

        # Determine what file(s) this import references
        # "from .constants import X" references constants.py in same dir
        # "from . import config" references config/ or config.py in same dir
        all_targets_missing = True
        if module:
            # "from .module_name import ..." -> look for module_name.py or module_name/
            target_py = init_dir / (module.replace(".", os.sep) + ".py")
            target_pkg = init_dir / module.replace(".", os.sep) / "__init__.py"
            if target_py in available_source_files or target_pkg in available_source_files:
                all_targets_missing = False
        else:
            # "from . import name1, name2" -> check each name
            missing_names = []
            present_names = []
            for alias in node.names:
                name = alias.name
                target_py = init_dir / (name + ".py")
                target_pkg = init_dir / name / "__init__.py"
                if target_py in available_source_files or target_pkg in available_source_files:
                    present_names.append(alias)
                    all_targets_missing = False
                else:
                    missing_names.append(alias)

            # If some names are missing but others present, rebuild the import line
            if missing_names and present_names:
                start = node.lineno - 1
                end = getattr(node, "end_lineno", node.lineno) - 1
                old_block = "\n".join(lines[start : end + 1])
                # Rebuild: from . import present1, present2
                name_strs = []
                for alias in present_names:
                    if alias.asname:
                        name_strs.append(f"{alias.name} as {alias.asname}")
                    else:
                        name_strs.append(alias.name)
                new_line = f"from . import {', '.join(name_strs)}"
                lines[start : end + 1] = [new_line]
                changes.append(f"Filtered import: {old_block.strip()} -> {new_line.strip()}")
                continue

        if all_targets_missing:
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno) - 1
            old_block = "\n".join(lines[start : end + 1]).strip()
            removals.append((start, end))
            changes.append(f"Removed import: {old_block}")

    # Also filter __all__ if present
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    # Rebuild __all__ to only include names that are still importable
                    if isinstance(node.value, ast.List):
                        remaining = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                name = elt.value
                                # Check if the name corresponds to a file or is defined
                                # in a file that exists
                                target_py = init_dir / (name + ".py")
                                target_pkg = init_dir / name / "__init__.py"
                                if target_py in available_source_files or target_pkg in available_source_files:
                                    remaining.append(name)
                                else:
                                    # The name might be a class/function re-exported from
                                    # a sub-module.  Keep it if there's any valid import
                                    # remaining that could provide it.
                                    remaining.append(name)
                            else:
                                remaining.append(str(getattr(elt, "value", elt)))

                        start = node.lineno - 1
                        end = getattr(node, "end_lineno", node.lineno) - 1
                        # We don't aggressively filter __all__ since names may come
                        # from imports that survived filtering.  Only remove it if
                        # completely empty.

    # Apply removals in reverse order
    for start, end in sorted(removals, reverse=True):
        removed = lines[start : end + 1]
        # Replace with a comment
        indent = len(removed[0]) - len(removed[0].lstrip()) if removed else 0
        lines[start : end + 1] = [" " * indent + "# (removed: not included in this module)"]

    if changes and not dry_run:
        dest_path.write_text("\n".join(lines), encoding="utf-8")

    return changes


# ---------------------------------------------------------------------------
# Phase 6 — Orchestration
# ---------------------------------------------------------------------------


def run_reorganization(
    root_path: str,
    out_path: str,
    modules: list[str],
    package_name: str,
    dry_run: bool,
) -> None:
    """Main orchestration: build graph, extract modules, rewrite imports."""
    root = Path(root_path).resolve()
    out_root = Path(out_path).resolve()

    if not root.exists() or not root.is_dir():
        print(f"Error: root path {root} not found or not a directory.", file=sys.stderr)
        return

    prefix = "DRY-RUN: " if dry_run else ""

    # --- Phase 1: Build dependency graph ---
    print(f"{prefix}Building dependency graph for {root} ...")
    dg = build_dependency_graph(root, package_name)
    print(f"  Found {len(dg.modname_to_path)} Python modules")
    print(f"  Found {sum(len(v) for v in dg.graph.values())} dependency edges")

    # --- Phase 2 & 3: Process each module ---
    print(f"\n{prefix}Processing {len(modules)} root module(s): {', '.join(modules)}")

    for mod in modules:
        print(f"\n{'='*60}")
        print(f"  Module: {mod}")
        print(f"{'='*60}")

        # Collect transitive dependencies
        try:
            file_set = collect_module_dependencies(root, dg, mod)
        except FileNotFoundError as e:
            print(f"  WARNING: {e}", file=sys.stderr)
            continue

        # Detect resource files
        resource_set = detect_resource_files(root, file_set, dg.file_to_literals)

        print(f"  Python files: {len(file_set)}")
        print(f"  Resource files: {len(resource_set)}")

        # List files
        for f in sorted(file_set):
            rel = f.relative_to(root)
            print(f"    .py  {rel}")
        for f in sorted(resource_set):
            try:
                rel = f.relative_to(root)
            except ValueError:
                rel = f.name
            print(f"    res  {rel}")

        # Clean output directory for this module (if not dry-run)
        mod_out = out_root / mod
        if not dry_run and mod_out.exists():
            shutil.rmtree(mod_out)

        # Copy files
        py_mappings, res_mappings = copy_module_tree(root, out_root, mod, file_set, resource_set, dry_run)

        # Rewrite imports in copied files
        print("\n  Import rewrites:")
        total_rewrites = 0
        for src, dest in py_mappings:
            source_to_read = src if dry_run else dest
            rewrites = rewrite_imports_in_file(source_to_read, package_name, mod, dry_run)
            for old_block, new_block in rewrites:
                total_rewrites += 1
                # Show a compact version
                old_first = old_block.split("\n")[0].strip()
                new_first = new_block.split("\n")[0].strip()
                rel = src.relative_to(root)
                print(f"    {rel}")
                print(f"      - {old_first}")
                print(f"      + {new_first}")
        print(f"  Total import rewrites: {total_rewrites}")

        # Filter __init__.py files
        # Use source paths for availability checks (consistent in both dry-run and real mode)
        print("\n  __init__.py filtering:")
        for src, dest in py_mappings:
            if dest.name == "__init__.py":
                changes = filter_init_file(src, dest, file_set, dry_run)
                if changes:
                    rel = src.relative_to(root)
                    for ch in changes:
                        print(f"    {rel}: {ch}")

    print(f"\n{'='*60}")
    print(f"{prefix}Done. Output in: {out_root}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorganize sections_app into per-module folders.")
    parser.add_argument(
        "--root",
        required=True,
        help="Path to sections_app root directory",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output root directory (will contain a sub-folder per module)",
    )
    parser.add_argument(
        "--modules",
        nargs="*",
        help="Module basenames to extract (overrides ROOT_MODULES)",
    )
    parser.add_argument(
        "--package-name",
        default=PACKAGE_NAME,
        help=f"Original package name used in imports (default: {PACKAGE_NAME})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without writing any files",
    )
    args = parser.parse_args()

    mods = args.modules if args.modules else ROOT_MODULES
    run_reorganization(args.root, args.out, mods, args.package_name, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
