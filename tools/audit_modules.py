#!/usr/bin/env python3
"""Audit tool: scan src/ and tests/ to produce a Markdown module matrix.

Usage::

    python tools/audit_modules.py              # prints to stdout
    python tools/audit_modules.py -o docs/ARCHITETTURA_MODULI.md  # write to file

The output contains only mechanically-verified information:
  - module path (real filesystem path)
  - python files count
  - matching test files (if any)
  - notes column left empty / "TBD" for manual review
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"


def _find_test_files(module_name: str) -> list[str]:
    """Return test file names that likely cover *module_name*."""
    hits: list[str] = []
    for tf in sorted(TESTS.rglob("test_*.py")):
        # heuristic: test file name contains the module name
        stem = tf.stem.replace("test_", "")
        if module_name.replace("/", "_") in stem or stem in module_name:
            hits.append(str(tf.relative_to(ROOT)))
    return hits


def _count_py(path: Path) -> int:
    return sum(1 for _ in path.rglob("*.py"))


def audit() -> str:
    """Return the Markdown audit report."""
    now = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    try:
        import subprocess

        commit = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        commit = "unknown"

    lines: list[str] = []
    lines.append(f"> **Auditato al commit `{commit}` — {now}**")
    lines.append("")
    lines.append("| Modulo | Path | File .py | Test correlati | Note |")
    lines.append("|--------|------|----------|----------------|------|")

    for d in sorted(SRC.iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue
        rel = str(d.relative_to(ROOT))
        py_count = _count_py(d)
        if py_count == 0:
            continue
        test_files = _find_test_files(d.name)
        test_col = ", ".join(f"`{t}`" for t in test_files[:3])
        if len(test_files) > 3:
            test_col += f" (+{len(test_files) - 3})"
        if not test_col:
            test_col = "—"
        lines.append(f"| `{d.name}` | `{rel}/` | {py_count} | {test_col} | TBD |")

    # Also list top-level .py files in src/
    top_py = sorted(SRC.glob("*.py"))
    if top_py:
        for fp in top_py:
            rel = str(fp.relative_to(ROOT))
            lines.append(f"| `{fp.name}` | `{rel}` | 1 | — | top-level file |")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit src/ modules vs tests/")
    parser.add_argument("-o", "--output", help="Write output to file instead of stdout")
    args = parser.parse_args()

    report = audit()
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
