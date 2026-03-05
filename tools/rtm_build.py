"""tools/rtm_build.py – Regeneration tool for RTM and compliance docs.

Usage:
    python tools/rtm_build.py [--output-dir docs/RTM] [--module-dir docs/modules]

What this tool does (STATIC ANALYSIS ONLY – does NOT execute project code):
    1. Scans src/ to inventory modules (directories with __init__.py or .py files)
    2. Counts .py files per module
    3. Detects TODO/stub markers in .py files
    4. Finds test files that import from each module
    5. Finds normative references (NTC2018, DM96, etc.) in .py files
    6. Outputs a machine-readable module inventory JSON and regenerated RTM summary

Does NOT:
    - Import or execute any project module
    - Access the internet
    - Modify existing docs/modules/*.md files (add --update-modules to do that)

Exit codes: 0 = success, 1 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"
TESTS_LEGACY_DIR = REPO_ROOT / "tests_legacy"

NORMATIVE_KEYWORDS = [
    "NTC2018",
    "NTC 2018",
    "DM92",
    "DM 92",
    "DM96",
    "DM 96",
    "RD2229",
    "RD 2229",
    "EN1992",
    "EN 1992",
    "EN1991",
    "EN 1991",
    "CNR-DT 207",
    "CNR_DT207",
    "ISO 834",
    "ISO834",
    "Eurocodice",
    "Eurocode",
    "EC2",
    "EC8",
]

STUB_MARKERS = [
    "STUB",
    "TODO",
    "raise NotImplementedError",
    "SKELETON",
    "pass  # TODO",
    "# TODO",
]

STATUS_LEGEND = {
    "COMPLETO": "Entrypoint + test significativi + nessun TODO/stub core",
    "PARZIALE": "Funziona parzialmente o ha TODO/gap evidenti o test limitati",
    "INCOMPLETO": "Struttura esiste ma manca call path/test o placeholder chiave",
    "STUB": "Implementazione minimale / placeholder / tutti TODO",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_py_files(directory: Path) -> list[Path]:
    """Recursively find all .py files under *directory*."""
    return sorted(directory.rglob("*.py"))


def count_stub_markers(py_file: Path) -> int:
    """Count how many STUB/TODO/NotImplementedError lines are in a file."""
    try:
        content = py_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    count = 0
    for marker in STUB_MARKERS:
        count += content.count(marker)
    return count


def find_normative_refs(py_file: Path) -> list[str]:
    """Return list of normative keywords found in a .py file."""
    try:
        content = py_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    found = []
    for kw in NORMATIVE_KEYWORDS:
        if kw in content:
            found.append(kw)
    return sorted(set(found))


def find_tests_for_module(module_name: str, tests_root: Path) -> list[str]:
    """Find test files that contain 'from src.<module>' or 'import src.<module>'."""
    pattern_from = re.compile(
        rf"from\s+src\.{re.escape(module_name)}\b|import\s+src\.{re.escape(module_name)}\b"
    )
    pattern_direct = re.compile(
        rf"from\s+{re.escape(module_name)}\b|import\s+{re.escape(module_name)}\b"
    )
    results = []
    for test_file in sorted(tests_root.rglob("test_*.py")):
        try:
            content = test_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if pattern_from.search(content) or pattern_direct.search(content):
            try:
                rel = str(test_file.relative_to(REPO_ROOT))
            except ValueError:
                rel = str(test_file)
            results.append(rel)
    return results


def infer_status(module_name: str, py_files: list[Path], test_files: list[str]) -> str:
    """
    Heuristic-only status inference.
    IMPORTANT: this is a best-effort static analysis heuristic.
    Human review is required. See RTM_MASTER.md for verified statuses.
    """
    total_stub_count = sum(count_stub_markers(f) for f in py_files)
    total_lines = sum(
        len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        for f in py_files
        if f.exists()
    )
    has_tests = len(test_files) > 0

    if total_lines < 50 and total_stub_count > 2:
        return "STUB"
    if total_stub_count > 20 and not has_tests:
        return "STUB"
    if total_stub_count > 10 and not has_tests:
        return "INCOMPLETO"
    if total_stub_count > 5 or not has_tests:
        return "PARZIALE"
    return "COMPLETO"


# ---------------------------------------------------------------------------
# Main inventory builder
# ---------------------------------------------------------------------------


def build_module_inventory() -> list[dict]:
    """Scan src/ and build per-module inventory dict."""
    modules = []

    if not SRC_DIR.exists():
        print(f"ERROR: src/ not found at {SRC_DIR}", file=sys.stderr)
        return modules

    for item in sorted(SRC_DIR.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith("_") or item.name.startswith("."):
            continue

        py_files = find_py_files(item)
        if not py_files:
            continue

        # Normative refs across all .py files in module
        norm_refs: list[str] = []
        for pf in py_files:
            norm_refs.extend(find_normative_refs(pf))
        norm_refs = sorted(set(norm_refs))

        # Tests
        test_files = find_tests_for_module(item.name, TESTS_DIR)
        # Also check src/tests/
        src_tests_dir = SRC_DIR / "tests"
        if src_tests_dir.exists():
            test_files += find_tests_for_module(item.name, src_tests_dir)
        test_files = sorted(set(test_files))

        # Stub count
        stub_count = sum(count_stub_markers(f) for f in py_files)

        # Relative paths
        rel_py_files = []
        for pf in py_files:
            try:
                rel_py_files.append(str(pf.relative_to(REPO_ROOT)))
            except ValueError:
                rel_py_files.append(str(pf))

        inferred_status = infer_status(item.name, py_files, test_files)

        modules.append(
            {
                "name": item.name,
                "path": str(item.relative_to(REPO_ROOT)),
                "py_file_count": len(py_files),
                "py_files": rel_py_files,
                "stub_marker_count": stub_count,
                "test_files": test_files,
                "normative_refs": norm_refs,
                "inferred_status": inferred_status,
                "_note": "inferred_status is heuristic only – see RTM_MASTER.md for verified status",
            }
        )

    return modules


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_inventory_json(modules: list[dict], output_path: Path) -> None:
    """Write machine-readable inventory JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_generated": datetime.now(UTC).isoformat(),
        "_tool": "tools/rtm_build.py",
        "_note": "Static analysis only. inferred_status is heuristic. See RTM_MASTER.md.",
        "module_count": len(modules),
        "modules": modules,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"  Wrote {output_path.relative_to(REPO_ROOT)}")


def write_rtm_summary(modules: list[dict], output_path: Path) -> None:
    """Write a regenerated RTM summary Markdown (auto-generated section)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# RTM – Riepilogo Auto-generato",
        "",
        f"> **Auto-generato da `tools/rtm_build.py`** — {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "> Stato 'inferred_status' è euristico (analisi statica). Verificare contro RTM_MASTER.md.",
        "",
        f"**Moduli rilevati**: {len(modules)}",
        "",
        "| Modulo | File .py | Marker STUB/TODO | Test trovati | Norme nel codice | Stato (euristico) |",
        "|--------|----------|-------------------|--------------|------------------|-------------------|",
    ]
    for m in modules:
        norms = ", ".join(m["normative_refs"]) if m["normative_refs"] else "—"
        tests_count = len(m["test_files"])
        lines.append(
            f"| `{m['name']}` | {m['py_file_count']} | {m['stub_marker_count']} | {tests_count} | {norms} | **{m['inferred_status']}** |"
        )

    lines += [
        "",
        "---",
        "",
        "## Occorrenze Normative (per modulo)",
        "",
    ]
    for m in modules:
        if m["normative_refs"]:
            lines.append(f"- **{m['name']}**: {', '.join(m['normative_refs'])}")

    lines += [
        "",
        "---",
        "",
        "*Per RTM completa con evidenze verificate manualmente: `docs/RTM/RTM_MASTER.md`*",
        "*Per docs per modulo: `docs/modules/<modulo>.md`*",
    ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Wrote {output_path.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        default="docs/RTM",
        help="Output directory for RTM summary (default: docs/RTM)",
    )
    parser.add_argument(
        "--inventory-json",
        default="docs/RTM/module_inventory.json",
        help="Path for machine-readable inventory JSON (default: docs/RTM/module_inventory.json)",
    )
    parser.add_argument(
        "--rtm-summary",
        default="docs/RTM/RTM_AUTOGENERATED.md",
        help="Path for auto-generated RTM summary (default: docs/RTM/RTM_AUTOGENERATED.md)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print("=== tools/rtm_build.py ===")
    print(f"Repo root : {REPO_ROOT}")
    print(f"Src dir   : {SRC_DIR}")
    print()

    print("Step 1/3: Scanning src/ for modules...")
    modules = build_module_inventory()
    print(f"  Found {len(modules)} modules")
    print()

    print("Step 2/3: Writing inventory JSON...")
    inv_path = REPO_ROOT / args.inventory_json
    write_inventory_json(modules, inv_path)
    print()

    print("Step 3/3: Writing auto-generated RTM summary...")
    rtm_path = REPO_ROOT / args.rtm_summary
    write_rtm_summary(modules, rtm_path)
    print()

    print("Done. Review:")
    print(f"  - {args.inventory_json}")
    print(f"  - {args.rtm_summary}")
    print()
    print("NOTE: inferred_status is heuristic. See docs/RTM/RTM_MASTER.md for verified status.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
