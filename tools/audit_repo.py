#!/usr/bin/env python3
"""Audit tool: mechanically scan the repo and produce objective inventory docs.

Deliverables generated
----------------------
- docs/_generated/REPO_INVENTORY.md   – full repo overview
- docs/_generated/MODULE_INDEX.md     – table: module → path → status → tests → notes

Usage::

    python tools/audit_repo.py            # write to docs/_generated/
    python tools/audit_repo.py --stdout   # print both reports to stdout

Rules
-----
- NEVER invent information.  If something is not verifiable, mark as TBD or
  NON PRESENTE.
- No computation, no imports of production code.  Pure filesystem scan.
"""

from __future__ import annotations

import argparse
import datetime
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
WORKFLOWS = ROOT / ".github" / "workflows"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def _now_utc() -> str:
    return datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")


def _count_py(path: Path) -> int:
    return sum(1 for _ in path.rglob("*.py") if "__pycache__" not in str(_))


def _find_test_files(module_name: str) -> list[str]:
    """Heuristic: test files whose stem contains the module name (or vice-versa)."""
    hits: list[str] = []
    safe = module_name.replace("/", "_").replace("-", "_")
    for tf in sorted(TESTS.rglob("test_*.py")):
        stem = tf.stem.replace("test_", "")
        if safe in stem or stem in safe:
            hits.append(str(tf.relative_to(ROOT)))
    return hits


def _src_packages() -> list[dict]:
    """Return list of dicts describing each package under src/."""
    packages = []
    for d in sorted(SRC.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith(("_", ".")):
            continue
        py_count = _count_py(d)
        if py_count == 0:
            continue
        test_files = _find_test_files(d.name)
        has_init = (d / "__init__.py").exists()
        packages.append(
            {
                "name": d.name,
                "path": str(d.relative_to(ROOT)),
                "py_files": py_count,
                "has_init": has_init,
                "test_files": test_files,
                "type": "package" if has_init else "namespace",
            }
        )
    # top-level .py files in src/
    for fp in sorted(SRC.glob("*.py")):
        if fp.name.startswith("_"):
            continue
        packages.append(
            {
                "name": fp.name,
                "path": str(fp.relative_to(ROOT)),
                "py_files": 1,
                "has_init": False,
                "test_files": _find_test_files(fp.stem),
                "type": "module",
            }
        )
    return packages


def _ci_workflows() -> list[dict]:
    """Return list of dicts describing CI workflow files."""
    if not WORKFLOWS.exists():
        return []
    workflows = []
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        workflows.append(
            {
                "name": wf.name,
                "path": str(wf.relative_to(ROOT)),
                "size_lines": len(wf.read_text(encoding="utf-8").splitlines()),
            }
        )
    return workflows


def _tools_scripts() -> list[str]:
    tools_dir = ROOT / "tools"
    if not tools_dir.exists():
        return []
    return [str(p.relative_to(ROOT)) for p in sorted(tools_dir.glob("*.py"))]


def _tests_summary() -> dict:
    test_files = list(TESTS.rglob("test_*.py"))
    return {
        "total": len(test_files),
        "files": [str(f.relative_to(ROOT)) for f in sorted(test_files)],
    }


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------

def _status_from_package(pkg: dict) -> str:
    """Derive a coarse status label from filesystem evidence only."""
    if pkg["py_files"] == 0:
        return "NON PRESENTE"
    if not pkg["has_init"] and pkg["type"] != "module":
        return "STUB"
    if pkg["test_files"]:
        return "PARZIALE"
    return "INCOMPLETO"


def build_repo_inventory(commit: str, now: str) -> str:
    packages = _src_packages()
    workflows = _ci_workflows()
    tools = _tools_scripts()
    tests_summary = _tests_summary()

    lines: list[str] = []
    lines += [
        "# REPO_INVENTORY",
        "",
        f"> Generato automaticamente da `tools/audit_repo.py` — commit `{commit}` — {now}",
        "> Questo file è di sola lettura. Non modificare manualmente.",
        "",
        "---",
        "",
        "## 1. Pacchetti/Moduli in `src/`",
        "",
        f"Totale pacchetti/moduli rilevati: **{len(packages)}**",
        "",
    ]
    for pkg in packages:
        lines.append(f"- `{pkg['path']}` ({pkg['type']}, {pkg['py_files']} file .py)")

    lines += [
        "",
        "---",
        "",
        "## 2. Test",
        "",
        f"File di test in `tests/`: **{tests_summary['total']}**",
        "",
    ]
    for tf in tests_summary["files"]:
        lines.append(f"- `{tf}`")

    lines += [
        "",
        "---",
        "",
        "## 3. CI Workflows",
        "",
        f"Workflow in `.github/workflows/`: **{len(workflows)}**",
        "",
    ]
    for wf in workflows:
        lines.append(
            f"- `{wf['path']}` ({wf['size_lines']} righe)"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. Tools / Scripts",
        "",
        f"Script in `tools/`: **{len(tools)}**",
        "",
    ]
    for t in tools:
        lines.append(f"- `{t}`")

    lines += [
        "",
        "---",
        "",
        "## 5. Entry points (da pyproject.toml)",
        "",
        "> Rilevamento meccanico limitato. Consultare `pyproject.toml` per la lista completa.",
        "",
    ]

    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        in_scripts = False
        for line in content.splitlines():
            stripped = line.strip()
            if "[project.scripts]" in stripped or "[project.entry-points" in stripped:
                in_scripts = True
            elif in_scripts and stripped.startswith("[") and "[project.scripts]" not in stripped:
                in_scripts = False
            elif in_scripts and "=" in stripped and not stripped.startswith("#"):
                lines.append(f"  - `{stripped}`")

    lines.append("")
    return "\n".join(lines)


def build_module_index(commit: str, now: str) -> str:
    packages = _src_packages()

    lines: list[str] = []
    lines += [
        "# MODULE_INDEX",
        "",
        f"> Generato automaticamente da `tools/audit_repo.py` — commit `{commit}` — {now}",
        "> Questo file è di sola lettura. Non modificare manualmente.",
        "",
        "| Modulo | Path | Tipo | File .py | Test rilevati | Stato | Note |",
        "|--------|------|------|----------|---------------|-------|------|",
    ]

    for pkg in packages:
        test_col = ", ".join(f"`{t}`" for t in pkg["test_files"][:2])
        if len(pkg["test_files"]) > 2:
            test_col += f" (+{len(pkg['test_files']) - 2})"
        if not test_col:
            test_col = "—"
        status = _status_from_package(pkg)
        lines.append(
            f"| `{pkg['name']}` | `{pkg['path']}` | {pkg['type']} | {pkg['py_files']} | {test_col} | {status} | TBD |"
        )

    lines += [
        "",
        "---",
        "",
        "## Legenda stati",
        "",
        "| Stato | Significato |",
        "|-------|-------------|",
        "| COMPLETO | Modulo con implementazione verificabile, test presenti e documentazione. |",
        "| PARZIALE | Modulo implementato ma test o documentazione mancanti/incompleti. |",
        "| INCOMPLETO | Modulo presente ma implementazione parziale o non verificabile. |",
        "| STUB | Directory o file presente ma senza `__init__.py` o contenuto significativo. |",
        "| NON PRESENTE | Nessun file Python rilevato. |",
        "",
        "> **Nota**: gli stati sono derivati meccanicamente da euristiche su file system.",
        "> La verifica manuale è necessaria per una classificazione definitiva.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan the repo and generate REPO_INVENTORY.md and MODULE_INDEX.md"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print both reports to stdout instead of writing to docs/_generated/",
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "docs" / "_generated"),
        help="Output directory (default: docs/_generated/)",
    )
    args = parser.parse_args()

    commit = _git_commit()
    now = _now_utc()

    inventory = build_repo_inventory(commit, now)
    module_index = build_module_index(commit, now)

    if args.stdout:
        print("=" * 60)
        print("REPO_INVENTORY")
        print("=" * 60)
        print(inventory)
        print()
        print("=" * 60)
        print("MODULE_INDEX")
        print("=" * 60)
        print(module_index)
    else:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        inv_path = out_dir / "REPO_INVENTORY.md"
        inv_path.write_text(inventory + "\n", encoding="utf-8")
        print(f"Written: {inv_path}")

        idx_path = out_dir / "MODULE_INDEX.md"
        idx_path.write_text(module_index + "\n", encoding="utf-8")
        print(f"Written: {idx_path}")


if __name__ == "__main__":
    main()
