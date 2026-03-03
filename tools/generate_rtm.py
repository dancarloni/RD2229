#!/usr/bin/env python3
"""tools/generate_rtm.py – RTM generator: norm↔function↔test mapping with gap analysis.

Analyses:
  - ``docs/_norme/`` for registered normative extracts
  - ``src/`` for implemented functions/modules with normative references
  - ``tests/`` for test coverage evidence
  - ``README.md`` / ``docs/`` for documentation evidence

Produces in ``docs/RTM/``:
  - ``rtm.csv``        – machine-readable mapping table
  - ``rtm.json``       – full structured data with evidence
  - ``rtm_coverage.md``– human-readable coverage report with gap analysis

Evidence-only policy:
  This tool references ONLY what is demonstrably present in the codebase.
  No inventive claims, no assumptions. Gap = anything mentioned in norms
  but without a corresponding src/ function + tests/ test.

Usage::

    python tools/generate_rtm.py [--output-dir docs/RTM] [--norme-dir docs/_norme]

Exit codes: 0 = success, 1 = error.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
_TESTS = _ROOT / "tests"
_DOCS = _ROOT / "docs"

# Canonical norm IDs and their keyword aliases for source scanning
NORM_ALIASES: dict[str, list[str]] = {
    "NTC2018": ["NTC2018", "NTC 2018", "ntc2018", "ntc_2018"],
    "RD2229": ["RD2229", "RD 2229", "rd2229", "Regio Decreto 2229"],
    "DM96": ["DM96", "DM 96", "dm96", "DM_96"],
    "DM92": ["DM92", "DM 92", "dm92"],
    "EN1992": ["EN1992", "EN 1992", "Eurocode 2", "EC2", "en1992"],
    "EN1991": ["EN1991", "EN 1991", "Eurocode 1", "EC1", "en1991"],
    "ISO834": ["ISO 834", "ISO834", "iso834"],
}

STUB_MARKERS = ["TODO", "STUB", "raise NotImplementedError", "SKELETON", "# TODO"]


def _rel(path: Path) -> str:
    """Return path relative to _ROOT, or absolute string if not under _ROOT."""
    try:
        return str(path.relative_to(_ROOT))
    except ValueError:
        return str(path)


def _find_py_files(directory: Path) -> list[Path]:
    return sorted(directory.rglob("*.py")) if directory.exists() else []


def _count_stubs(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return sum(text.count(m) for m in STUB_MARKERS)
    except OSError:
        return 0


def _has_norm_refs(text: str, norm_id: str) -> bool:
    return any(alias in text for alias in NORM_ALIASES.get(norm_id, [norm_id]))


# ---------------------------------------------------------------------------
# Step 1 – Scan registered normative extracts
# ---------------------------------------------------------------------------


def scan_norm_extracts(norme_dir: Path) -> dict[str, dict]:
    """Return {norm_id: {clauses: [...], has_metadata: bool, extract_count: int}}."""
    result: dict[str, dict] = {}
    if not norme_dir.exists():
        return result
    for nd in sorted(norme_dir.iterdir()):
        if not nd.is_dir():
            continue
        norm_id = nd.name
        meta_path = nd / "metadata.json"
        meta = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        extracts_dir = nd / "extracts"
        extracts = sorted(extracts_dir.glob("*.md")) if extracts_dir.exists() else []

        result[norm_id] = {
            "has_metadata": meta_path.exists(),
            "title": meta.get("title", norm_id),
            "clauses": meta.get("clauses", []),
            "extract_files": [_rel(e) for e in extracts],
            "extract_count": len(extracts),
        }
    return result


# ---------------------------------------------------------------------------
# Step 2 – Scan src/ for function/module evidence
# ---------------------------------------------------------------------------


def scan_src_evidence(src_dir: Path) -> dict[str, dict]:
    """Return {norm_id: {modules: [...], function_count: int, stub_count: int}}."""
    result: dict[str, dict] = {nid: {"modules": [], "function_count": 0, "stub_count": 0} for nid in NORM_ALIASES}

    for py_file in _find_py_files(src_dir):
        # Skip legacy and __pycache__
        parts = py_file.parts
        if any(p in ("legacy", "__pycache__") for p in parts):
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        stub_count = sum(text.count(m) for m in STUB_MARKERS)
        # Count def/class definitions as function evidence
        defs = len(re.findall(r"^\s*(?:def|class)\s+\w+", text, re.MULTILINE))

        for norm_id in NORM_ALIASES:
            if _has_norm_refs(text, norm_id):
                try:
                    rel = str(py_file.relative_to(_ROOT))
                except ValueError:
                    rel = str(py_file)
                result[norm_id]["modules"].append(rel)
                result[norm_id]["function_count"] += defs
                result[norm_id]["stub_count"] += stub_count

    return result


# ---------------------------------------------------------------------------
# Step 3 – Scan tests/ for test evidence
# ---------------------------------------------------------------------------


def scan_test_evidence(tests_dir: Path) -> dict[str, dict]:
    """Return {norm_id: {test_files: [...], test_function_count: int}}."""
    result: dict[str, dict] = {nid: {"test_files": [], "test_function_count": 0} for nid in NORM_ALIASES}

    for tf in _find_py_files(tests_dir):
        if any(p in ("legacy_tkinter", "legacy_qt", "__pycache__") for p in tf.parts):
            continue
        try:
            text = tf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        test_defs = len(re.findall(r"^\s*def\s+test_\w+", text, re.MULTILINE))

        for norm_id in NORM_ALIASES:
            if _has_norm_refs(text, norm_id):
                try:
                    rel = str(tf.relative_to(_ROOT))
                except ValueError:
                    rel = str(tf)
                result[norm_id]["test_files"].append(rel)
                result[norm_id]["test_function_count"] += test_defs

    return result


# ---------------------------------------------------------------------------
# Step 4 – Scan docs/README for documentation evidence
# ---------------------------------------------------------------------------


def scan_doc_evidence() -> dict[str, list[str]]:
    """Return {norm_id: [doc_files_mentioning_norm]}."""
    result: dict[str, list[str]] = {nid: [] for nid in NORM_ALIASES}
    doc_files = list(_DOCS.rglob("*.md")) + list(_DOCS.rglob("*.rst"))
    readme = _ROOT / "README.md"
    if readme.exists():
        doc_files.append(readme)

    for df in doc_files:
        try:
            text = df.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for norm_id in NORM_ALIASES:
            if _has_norm_refs(text, norm_id):
                try:
                    rel = str(df.relative_to(_ROOT))
                except ValueError:
                    rel = str(df)
                if rel not in result[norm_id]:
                    result[norm_id].append(rel)

    return result


# ---------------------------------------------------------------------------
# Step 5 – Compute coverage scores and identify gaps
# ---------------------------------------------------------------------------


def compute_coverage(
    norme: dict[str, dict],
    src_ev: dict[str, dict],
    test_ev: dict[str, dict],
    doc_ev: dict[str, list[str]],
) -> list[dict]:
    """Compute per-norm coverage entries."""
    rows = []
    all_norms = set(NORM_ALIASES) | set(norme.keys())

    for norm_id in sorted(all_norms):
        ne = norme.get(norm_id, {})
        se = src_ev.get(norm_id, {})
        te = test_ev.get(norm_id, {})
        de = doc_ev.get(norm_id, [])

        has_extract = ne.get("extract_count", 0) > 0
        has_src = len(se.get("modules", [])) > 0
        has_tests = len(te.get("test_files", [])) > 0
        has_docs = len(de) > 0

        # Score: 25 pts each for extract, src, tests, docs
        score = sum([25 * has_extract, 25 * has_src, 25 * has_tests, 25 * has_docs])

        # Gap analysis
        gaps = []
        if not has_extract:
            gaps.append("no_normative_extract")
        if not has_src:
            gaps.append("no_src_implementation")
        if not has_tests:
            gaps.append("no_tests")
        if not has_docs:
            gaps.append("no_documentation")
        if has_src and se.get("stub_count", 0) > 10:
            gaps.append("high_stub_count")

        rows.append({
            "norm_id": norm_id,
            "title": ne.get("title", NORM_ALIASES.get(norm_id, [norm_id])[0] if norm_id in NORM_ALIASES else norm_id),
            "coverage_pct": score,
            "has_extract": has_extract,
            "extract_count": ne.get("extract_count", 0),
            "has_src": has_src,
            "src_module_count": len(se.get("modules", [])),
            "src_function_count": se.get("function_count", 0),
            "stub_count": se.get("stub_count", 0),
            "has_tests": has_tests,
            "test_file_count": len(te.get("test_files", [])),
            "test_function_count": te.get("test_function_count", 0),
            "has_docs": has_docs,
            "doc_file_count": len(de),
            "gaps": gaps,
            "src_modules": se.get("modules", []),
            "test_files": te.get("test_files", []),
            "doc_files": de,
            "extract_files": ne.get("extract_files", []),
        })

    return rows


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "norm_id", "title", "coverage_pct", "has_extract", "extract_count",
        "has_src", "src_module_count", "src_function_count", "stub_count",
        "has_tests", "test_file_count", "test_function_count",
        "has_docs", "doc_file_count", "gaps",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            r = dict(row)
            r["gaps"] = "; ".join(row.get("gaps", []))
            writer.writerow(r)
    print(f"  Wrote {_rel(path)}")


def write_json(rows: list[dict], path: Path, norme: dict, src_ev: dict, test_ev: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_generated": datetime.now(UTC).isoformat(),
        "_tool": "tools/generate_rtm.py",
        "_policy": "Evidence-only: references only what is demonstrably present in codebase.",
        "norm_count": len(rows),
        "rows": rows,
        "evidence_summary": {
            "norme_dir_exists": (_ROOT / "docs" / "_norme").exists(),
            "registered_norms": list(norme.keys()),
            "src_modules_scanned": str(_SRC),
            "tests_scanned": str(_TESTS),
        },
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  Wrote {_rel(path)}")


def write_coverage_md(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# RTM – Copertura Normativa (Evidence-Only)",
        "",
        f"> **Auto-generato da `tools/generate_rtm.py`** — {now}",
        "> Policy: solo evidenze verificabili nel codice/test/doc. Nessuna inferenza inventiva.",
        "",
        "## Sommario Copertura",
        "",
        "| Norma | Copertura % | Estratti | Src | Test | Doc | Gap |",
        "|-------|------------|----------|-----|------|-----|-----|",
    ]
    for r in rows:
        gaps = ", ".join(r["gaps"]) if r["gaps"] else "—"
        lines.append(
            f"| `{r['norm_id']}` | **{r['coverage_pct']}%** "
            f"| {'✓' if r['has_extract'] else '✗'} ({r['extract_count']}) "
            f"| {'✓' if r['has_src'] else '✗'} ({r['src_module_count']} moduli) "
            f"| {'✓' if r['has_tests'] else '✗'} ({r['test_file_count']} file) "
            f"| {'✓' if r['has_docs'] else '✗'} ({r['doc_file_count']}) "
            f"| {gaps} |"
        )

    lines += ["", "---", "", "## Dettaglio per Norma", ""]
    for r in rows:
        lines += [
            f"### {r['norm_id']} – {r['title']}",
            "",
            f"**Copertura**: {r['coverage_pct']}%",
            "",
        ]
        if r["src_modules"]:
            lines += ["**Moduli src/ che referenziano questa norma:**", ""]
            for m in r["src_modules"][:10]:
                lines.append(f"- `{m}`")
            if len(r["src_modules"]) > 10:
                lines.append(f"- *(e altri {len(r['src_modules']) - 10})*")
            lines.append("")
        if r["test_files"]:
            lines += ["**Test che referenziano questa norma:**", ""]
            for t in r["test_files"][:10]:
                lines.append(f"- `{t}`")
            if len(r["test_files"]) > 10:
                lines.append(f"- *(e altri {len(r['test_files']) - 10})*")
            lines.append("")
        if r["extract_files"]:
            lines += ["**Estratti disponibili:**", ""]
            for e in r["extract_files"]:
                lines.append(f"- `{e}`")
            lines.append("")
        if r["gaps"]:
            lines += ["**Gap identificati:**", ""]
            for g in r["gaps"]:
                lines.append(f"- ⚠️ `{g}`")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines += [
        "*RTM verificata manualmente: `docs/RTM/RTM_MASTER.md`*",
        "*Inventario moduli: `docs/RTM/module_inventory.json`*",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Wrote {_rel(path)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--output-dir", default="docs/RTM", help="Output directory (default: docs/RTM)")
    parser.add_argument("--norme-dir", default="docs/_norme", help="Normative extracts dir (default: docs/_norme)")
    parser.add_argument("--csv", default="docs/RTM/rtm.csv", help="CSV output path")
    parser.add_argument("--json", default="docs/RTM/rtm.json", help="JSON output path")
    parser.add_argument("--md", default="docs/RTM/rtm_coverage.md", help="Markdown output path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    norme_dir = _ROOT / args.norme_dir

    print("=== tools/generate_rtm.py ===")
    print(f"Repo root  : {_ROOT}")
    print(f"Norme dir  : {norme_dir}")
    print()

    print("Step 1/5: Scanning normative extracts...")
    norme = scan_norm_extracts(norme_dir)
    print(f"  Found {len(norme)} registered norms in {norme_dir}")

    print("Step 2/5: Scanning src/ for implementation evidence...")
    src_ev = scan_src_evidence(_SRC)

    print("Step 3/5: Scanning tests/ for test evidence...")
    test_ev = scan_test_evidence(_TESTS)

    print("Step 4/5: Scanning docs/ for documentation evidence...")
    doc_ev = scan_doc_evidence()

    print("Step 5/5: Computing coverage and writing outputs...")
    rows = compute_coverage(norme, src_ev, test_ev, doc_ev)

    csv_path = _ROOT / args.csv
    json_path = _ROOT / args.json
    md_path = _ROOT / args.md

    write_csv(rows, csv_path)
    write_json(rows, json_path, norme, src_ev, test_ev)
    write_coverage_md(rows, md_path)

    # Summary
    print()
    print("Coverage summary:")
    for r in rows:
        print(f"  {r['norm_id']:<12} {r['coverage_pct']:>3}%  gaps={r['gaps']}")
    print()
    print("NOTE: Evidence-only analysis. No LLM inference used.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
