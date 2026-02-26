#!/usr/bin/env python3
"""
split_sections_app.py

Usage:
    python tools/split_sections_app.py [--src SECTIONS_APP] [--out SECTIONS_APP_REFACTORED]
                                 [--roots root1.py,modules/frc.py,...] [--dry-run]

Example:
    # dry-run with defaults (heuristic roots)
    python tools/split_sections_app.py --dry-run

Description / configuration:
- Edit the `DEFAULT_ROOTS_HEURISTIC` or pass `--roots` to select which root modules are considered.
- The script will:
    1) scan `--src` recursively for .py files,
    2) build an internal dependency graph by parsing imports with `ast`,
    3) compute transitive dependencies for each configured root module,
    4) copy selected files into `--out/<module_folder>/...` preserving relative paths,
    5) rewrite imports inside copied files so that references to copied modules become absolute imports \
        prefixed by the module folder name (e.g. `frc_module.services.repository`),
    6) include non-Python files (.json/.csv/.yml/.yaml) located in the same directories as selected .py files.

Assumptions:
- Package root directory is a simple folder (no installed package name); module names are derived \
  from file paths relative to `--src`.
- Non-Python support files are selected by extension and by being in directories of copied .py files.
- The script rewrites only imports that resolve to modules included in the copied set.

Notes on safety:
- The script writes output to a separate `--out` directory (default: SECTIONS_APP_REFACTORED) to avoid overwriting sources.
- Use `--dry-run` to preview actions without writing files.

"""

from __future__ import annotations

import argparse
import ast
import re
import shutil
from pathlib import Path

# ---------------------
# Configuration defaults
# ---------------------
DEFAULT_SRC = "SECTIONS_APP"
DEFAULT_OUT = "SECTIONS_APP_REFACTORED"
# Heuristic: default roots = all .py in top-level src dir + all .py in src/config/modules
DEFAULT_ROOTS_HEURISTIC = "heuristic"  # special value; see CLI processing

# Extensions for non-python support files to include when located in same dir as selected .py
SUPPORT_EXTS = {".json", ".csv", ".yml", ".yaml"}


# ---------------------
# Utilities
# ---------------------
def find_python_files(src_root: Path) -> list[Path]:
    """Return list of .py files under src_root excluding __pycache__ and .pyc."""
    py_files = []
    for p in src_root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        py_files.append(p)
    return py_files


def module_name_from_path(path: Path, src_root: Path) -> str:
    """Derive a module name relative to src_root, e.g. config.constants or modules.frc."""
    rel = path.relative_to(src_root)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def path_from_module_name(module_name: str, src_root: Path) -> Path | None:
    """Map a dotted module name to a file path under src_root (tries .py then __init__.py)."""
    candidate = src_root.joinpath(*module_name.split(".") + [".dummy"]).with_suffix(".py")
    if candidate.exists():
        return candidate
    # try package __init__.py
    init_candidate = src_root.joinpath(*module_name.split("."), "__init__.py")
    if init_candidate.exists():
        return init_candidate
    return None


def parse_imports(file_path: Path) -> list[tuple[str | None, int, list[str]]]:
    """
    Parse a python file and return a list of import records:
    - for `from X import ...` returns (module, level, [names]) where module may be None for `from . import name`
    - for `import X` returns (name, 0, [])
    The `level` corresponds to AST ImportFrom.level (0 for absolute).
    """
    with file_path.open("r", encoding="utf8") as f:
        src = f.read()
    try:
        tree = ast.parse(src)
    except Exception:
        return []
    records = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module  # may be None for 'from . import X'
            level = node.level  # 0 for absolute
            names = [alias.name for alias in node.names]
            records.append((mod, level, names))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                # name like 'config.constants' or 'os'
                records.append((alias.name, 0, []))
    return records


def resolve_imported_module(from_module: str, import_mod: str | None, level: int) -> str | None:
    """
    Resolve an ImportFrom with possible relative level into an absolute module name
    relative to the package root (without leading package name).
    from_module: e.g. 'ui.module_selector'
    import_mod: e.g. 'services.repo' or None
    level: 0 absolute, >0 relative
    Returns dotted module name relative to src_root or None if cannot resolve.
    """
    if level == 0:
        # absolute import; import_mod might be None for "from import" invalid but treat carefully
        return import_mod
    # relative import: compute parent package of from_module by chopping 'level' elements
    parts = from_module.split(".") if from_module else []
    if level > len(parts) + 1:
        # goes above package root; ignore
        return None
    base_parts = parts[: max(0, len(parts) - level + 1)]
    if import_mod:
        return ".".join(base_parts + import_mod.split(".")) if base_parts else import_mod
    else:
        return ".".join(base_parts) if base_parts else None


# ---------------------
# Build dependency graph
# ---------------------
def build_dependency_graph(src_root: Path) -> tuple[dict[Path, set[Path]], dict[str, Path]]:
    """
    Return (graph, module_name_to_path)
    graph: mapping Path -> set(Path) where edges denote "file imports target"
    """
    py_files = find_python_files(src_root)
    module_to_path: dict[str, Path] = {}
    for p in py_files:
        module_to_path[module_name_from_path(p, src_root)] = p

    graph: dict[Path, set[Path]] = {p: set() for p in py_files}

    for p in py_files:
        from_mod = module_name_from_path(p, src_root)
        imports = parse_imports(p)
        for mod, level, names in imports:
            if level == 0 and mod is not None:
                # absolute ImportFrom; mod could be top-level like 'os' or 'config.constants'
                # if it starts with src_root folder name, strip it; but we store module names relative to src_root
                candidate = mod
            elif level == 0 and names == []:
                # import statement handled earlier as (name,0,[])
                candidate = mod
            else:
                # relative ImportFrom
                candidate = resolve_imported_module(from_mod, mod, level)
            if not candidate:
                continue
            # candidate may be like 'SECTIONS_APP.config' if absolute with package name; strip package root if present
            if candidate.startswith(src_root.name + "."):
                candidate = candidate[len(src_root.name) + 1 :]
            # try to map candidate to a path; also try progressively shorter prefixes (for modules importing packages)
            found = None
            parts = candidate.split(".")
            for i in range(len(parts), 0, -1):
                try_mod = ".".join(parts[:i])
                target_path = module_to_path.get(try_mod)
                if target_path:
                    found = target_path
                    break
            if found:
                graph[p].add(found)
    return graph, module_to_path


# ---------------------
# Collect files for a root module
# ---------------------
def collect_module_files(
    root_ident: str, src_root: Path, graph: dict[Path, set[Path]], module_map: dict[str, Path]
) -> set[Path]:
    """
    root_ident may be a file path relative to src_root (e.g. 'app.py' or 'config/modules/frc.py'),
    or a module name like 'modules.frc'.
    Return a set of Paths (files) forming the transitive closure of dependencies starting from root.
    """
    # Resolve root to path
    root_path: Path | None
    # If looks like a path (contains / or endswith .py)
    candidate_path = (src_root / root_ident).resolve()
    if candidate_path.exists() and candidate_path.is_file():
        root_path = candidate_path
    else:
        # try module name
        modname = root_ident
        if modname.startswith(src_root.name + "."):
            modname = modname[len(src_root.name) + 1 :]
        root_path = module_map.get(modname)
    if not root_path:
        raise FileNotFoundError(f"Root module '{root_ident}' not found under {src_root}")
    # DFS
    collected: set[Path] = set()
    stack = [root_path]
    while stack:
        cur = stack.pop()
        if cur in collected:
            continue
        collected.add(cur)
        for dep in graph.get(cur, []):
            if dep not in collected:
                stack.append(dep)
    return collected


# ---------------------
# Support files collection
# ---------------------
def collect_support_files(py_files: set[Path]) -> set[Path]:
    """Include files in same directories as py_files that match SUPPORT_EXTS."""
    dirs = {p.parent for p in py_files}
    result = set()
    for d in dirs:
        for ext in SUPPORT_EXTS:
            for p in d.glob(f"*{ext}"):
                result.add(p)
    return result


# ---------------------
# Copying and rewriting
# ---------------------
def prepare_module_folder_name(root_path: Path) -> str:
    """Derive a folder name for module root. Use file stem, or last module part if nested."""
    if root_path.name == "__init__.py":
        # use parent folder name
        return root_path.parent.name + "_module"
    else:
        return root_path.stem + "_module"


def build_rewrite_mapping(
    collected: set[Path], src_root: Path, module_folder: str
) -> dict[str, str]:
    """
    For each original module name (relative to src_root) in collected set, create mapping:
    original_module -> new_module_name prefixed with module_folder.
    Example: 'services.repository' -> 'frc_module.services.repository'
    """
    mapping: dict[str, str] = {}
    for p in collected:
        mod = module_name_from_path(p, src_root)
        if not mod:
            continue
        new_mod = module_folder + "." + mod if mod else module_folder
        mapping[mod] = new_mod
    return mapping


def rewrite_imports_in_text(
    src_text: str, mapping: dict[str, str]
) -> tuple[str, list[tuple[str, str]]]:
    """
    Replace import and from-import module names present in mapping keys with mapping values.
    Returns new text and a list of (old, new) replacements performed.
    Approach: longest-first token replacement using regex on import/from statements.
    """
    # sort keys longest-first to avoid partial replacements
    keys_sorted = sorted(mapping.keys(), key=lambda s: -len(s))
    replacements = []
    new_text = src_text

    # Build regex patterns for `from X import` and `import X` occurrences.
    # We'll look for word boundaries to avoid substrings.
    for old_mod in keys_sorted:
        new_mod = mapping[old_mod]
        # from-import pattern: from <old_mod> (possibly followed by .sub) - but we match exact module only
        # Use negative lookbehind to ensure it's a separate token
        pattern_from = re.compile(
            rf"(^|\n)(\s*from\s+){re.escape(old_mod)}(\b)", flags=re.MULTILINE
        )
        new_text, n1 = pattern_from.subn(rf"\1\2{new_mod}\3", new_text)
        if n1:
            replacements.append((old_mod, new_mod))

        # import statement pattern: import <old_mod> (possibly with commas and aliases)
        # We will replace occurrences of the exact module name after 'import' or after commas
        # Simpler: replace tokens like '\bold_mod\b' that appear in import lines.
        # To avoid touching other contexts, operate only inside import lines.
        def replace_in_import_line(line: str):
            # replace token occurrences in the line
            token_pat = re.compile(rf"\b{re.escape(old_mod)}\b")
            new_line, nn = token_pat.subn(new_mod, line)
            if nn:
                replacements.append((old_mod, new_mod))
            return new_line

        pattern_import_line = re.compile(r"(^|\n)(\s*import\s+[^\n]+)", flags=re.MULTILINE)
        new_text = pattern_import_line.sub(
            lambda m: m.group(1) + replace_in_import_line(m.group(2)), new_text
        )

    # Deduplicate replacements
    deduped = []
    seen = set()
    for a, b in replacements:
        if (a, b) not in seen:
            deduped.append((a, b))
            seen.add((a, b))
    return new_text, deduped


def copy_and_rewrite(
    collected_py: set[Path],
    support_files: set[Path],
    src_root: Path,
    out_root: Path,
    module_folder: str,
    dry_run: bool,
) -> list[str]:
    """
    Copy files under out_root/module_folder/<relative paths>.
    Rewrite imports in copied .py files according to mapping.
    Returns a log list of actions (strings) describing operations or planned operations.
    """
    log = []
    mapping = build_rewrite_mapping(collected_py, src_root, module_folder)

    for p in sorted(collected_py):
        rel = p.relative_to(src_root)
        target = out_root / module_folder / rel
        log.append(f"Will copy: {p} -> {target}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            # read and rewrite imports
            with target.open("r", encoding="utf8") as f:
                text = f.read()
            new_text, replacements = rewrite_imports_in_text(text, mapping)
            if replacements:
                log.append(f" Rewriting imports in {target}: {replacements}")
                with target.open("w", encoding="utf8") as f:
                    f.write(new_text)
            else:
                log.append(f" No import rewrites needed in {target}")

    for p in sorted(support_files):
        rel = p.relative_to(src_root)
        target = out_root / module_folder / rel
        log.append(f"Will copy support file: {p} -> {target}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
    return log


# ---------------------
# CLI and orchestration
# ---------------------
def discover_default_roots(src_root: Path) -> list[str]:
    """Heuristic: .py files in src_root (not in subdirs) plus .py in src_root/config/modules."""
    roots = []
    for p in src_root.glob("*.py"):
        if p.name.endswith(".py"):
            roots.append(str(p.relative_to(src_root)))
    modules_dir = src_root / "config" / "modules"
    if modules_dir.exists():
        for p in modules_dir.glob("*.py"):
            roots.append(str(p.relative_to(src_root)))
    return roots


def run(args):
    src_root = Path(args.src).resolve()
    out_root = Path(args.out).resolve()
    dry_run = args.dry_run
    if not src_root.exists():
        raise SystemExit(f"Source directory {src_root} not found")

    # decide roots
    if args.roots:
        # accept comma-separated list or a single value
        provided = [r.strip() for r in args.roots.split(",") if r.strip()]
        if len(provided) == 1 and provided[0].lower() == DEFAULT_ROOTS_HEURISTIC:
            roots = discover_default_roots(src_root)
        else:
            roots = provided
    else:
        roots = discover_default_roots(src_root)

    print(f"Source: {src_root}")
    print(f"Output: {out_root} (dry-run={dry_run})")
    print(f"Root modules: {roots}")

    # build dependency graph
    graph, module_map = build_dependency_graph(src_root)
    # For convenience, present mapping of module -> file
    print(f"Discovered {len(module_map)} Python modules under {src_root.name}")

    # For each root, collect files and copy
    for root_ident in roots:
        try:
            collected_py = collect_module_files(root_ident, src_root, graph, module_map)
        except FileNotFoundError as ex:
            print(f"Skipping root {root_ident}: {ex}")
            continue
        support_files = collect_support_files(collected_py)
        # derive folder name
        # if root_ident is a path relative to src, resolve to path
        root_path = (src_root / root_ident).resolve() if (src_root / root_ident).exists() else None
        if not root_path:
            # try via module map
            modname = root_ident
            if modname.startswith(src_root.name + "."):
                modname = modname[len(src_root.name) + 1 :]
            root_path = module_map.get(modname)
        module_folder = (
            prepare_module_folder_name(root_path)
            if root_path
            else Path(root_ident).stem + "_module"
        )
        print(f"\nModule root '{root_ident}' -> folder '{module_folder}'")
        print(f" Found {len(collected_py)} python files and {len(support_files)} support files")
        actions = copy_and_rewrite(
            collected_py, support_files, src_root, out_root, module_folder, dry_run
        )
        for a in actions:
            print("  " + a)


# ---------------------
# Entry point
# ---------------------
def main():
    parser = argparse.ArgumentParser(
        description="Split SECTIONS_APP into module-specific folders by dependency analysis."
    )
    parser.add_argument(
        "--src", default=DEFAULT_SRC, help="Source package directory (default: SECTIONS_APP)"
    )
    parser.add_argument(
        "--out", default=DEFAULT_OUT, help="Output directory (default: SECTIONS_APP_REFACTORED)"
    )
    parser.add_argument(
        "--roots",
        default=None,
        help=(
            f"Comma-separated root modules (file paths relative to src or module names). "
            f"Use '{DEFAULT_ROOTS_HEURISTIC}' to apply heuristic."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show planned actions without copying/writing files"
    )
    parsed = parser.parse_args()
    run(parsed)


if __name__ == "__main__":
    main()
