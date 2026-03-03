#!/usr/bin/env python3
"""Generate per-module documentation stubs from docs/_generated/MODULE_INDEX.md.

For each module listed in MODULE_INDEX, creates (or skips if already present)
a file docs/modules/<module_name>.md based on docs/templates/MODULO_TEMPLATE.md.

Usage::

    python tools/generate_module_docs.py            # generate all missing docs
    python tools/generate_module_docs.py --force    # overwrite existing files
    python tools/generate_module_docs.py --dry-run  # show what would be generated

Rules
-----
- Never overwrite existing docs unless --force is given.
- Never invent data: all fields default to TBD unless mechanically derivable.
- Pure filesystem operation; no production code is imported.
"""

from __future__ import annotations

import argparse
import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_INDEX = ROOT / "docs" / "_generated" / "MODULE_INDEX.md"
TEMPLATE = ROOT / "docs" / "templates" / "MODULO_TEMPLATE.md"
OUT_DIR = ROOT / "docs" / "modules"

# Regex to parse a data row from MODULE_INDEX.md
# Columns: Modulo | Path | Tipo | File .py | Test rilevati | Stato | Note
_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*(\S+)\s*\|\s*(\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|$"
)


def _parse_module_index() -> list[dict]:
    """Parse MODULE_INDEX.md and return list of module dicts."""
    if not MODULE_INDEX.exists():
        raise FileNotFoundError(
            f"MODULE_INDEX not found: {MODULE_INDEX}\n"
            "Run `python tools/audit_repo.py` first."
        )
    modules = []
    for line in MODULE_INDEX.read_text(encoding="utf-8").splitlines():
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        name, path, type_, py_files, tests_raw, status, _note = (
            m.group(1),
            m.group(2),
            m.group(3),
            m.group(4),
            m.group(5).strip(),
            m.group(6).strip(),
            m.group(7).strip(),
        )
        # Parse test files from the backtick-quoted list
        test_files = re.findall(r"`([^`]+)`", tests_raw)
        modules.append(
            {
                "name": name,
                "path": path,
                "type": type_,
                "py_files": int(py_files),
                "test_files": test_files,
                "status": status,
            }
        )
    return modules


def _safe_filename(module_name: str) -> str:
    """Convert a module name to a safe filename (replace / and spaces)."""
    return module_name.replace("/", "_").replace(" ", "_").replace(".", "_")


def _render_stub(module: dict, now_dt: datetime.datetime) -> str:
    """Render a documentation stub for *module* from the template."""
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE}")

    name = module["name"]
    path = module["path"]
    type_ = module["type"]
    status = module["status"]
    py_files = module["py_files"]
    test_files = module["test_files"]

    # Build test table rows
    if test_files:
        test_rows = "\n".join(
            f"| `{tf}` | TBD | — |" for tf in test_files
        )
    else:
        test_rows = "| — | — | Nessun test rilevato meccanicamente. |"

    now = now_dt.strftime("%Y-%m-%d %H:%M UTC")
    now_date = now_dt.strftime("%Y-%m-%d")

    return f"""# Documentazione Modulo: `{name}`

> **Generato automaticamente** da `tools/generate_module_docs.py` — {now}
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `{name}` |
| **Path** | `{path}` |
| **Tipo** | {type_} |
| **File .py rilevati** | {py_files} |
| **Stato** | {status} |
| **Maintainer** | TBD |
| **Ultima revisione** | {now_date} |

---

## 2. Scopo

> Descrivere in 2-3 righe il *perché* esiste questo modulo e quale problema risolve.

TBD

---

## 3. File / Classi / Funzioni principali

> Elencare i simboli pubblici rilevanti. Non inventare: se non si conosce la firma esatta, annotare TBD.

| File | Classe/Funzione | Descrizione |
|------|-----------------|-------------|
| TBD | TBD | TBD |

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | TBD | TBD |
| Output | TBD | TBD |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
{test_rows}

---

## 6. Fonti normative

> Solo riferimenti a ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`. NESSUN testo copiato.

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| TBD | TBD | — |

---

## 7. Dipendenze interne

> Moduli `src/` da cui questo modulo dipende (import diretti).

- TBD

---

## 8. Note e TODO

- [ ] Compilare sezioni TBD
- [ ] Verificare test correlati
- [ ] Tracciare fonti normative di riferimento
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate docs/modules/<module>.md stubs from MODULE_INDEX"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing documentation files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without writing files",
    )
    args = parser.parse_args()

    now_dt = datetime.datetime.now(tz=datetime.UTC)
    modules = _parse_module_index()

    if not modules:
        print("No modules found in MODULE_INDEX. Run `python tools/audit_repo.py` first.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for mod in modules:
        filename = _safe_filename(mod["name"]) + ".md"
        out_path = OUT_DIR / filename

        if out_path.exists() and not args.force:
            if args.dry_run:
                print(f"  SKIP (exists): {out_path.relative_to(ROOT)}")
            skipped += 1
            continue

        already_exists = out_path.exists()
        content = _render_stub(mod, now_dt)

        if args.dry_run:
            action = "OVERWRITE" if already_exists else "CREATE"
            print(f"  {action}: {out_path.relative_to(ROOT)}")
        else:
            out_path.write_text(content, encoding="utf-8")
            action = "Overwritten" if already_exists else "Created"
            print(f"  {action}: {out_path.relative_to(ROOT)}")

        created += 1

    if args.dry_run:
        print(f"\nDry-run: {created} would be created/overwritten, {skipped} skipped.")
    else:
        print(f"\nDone: {created} files written, {skipped} skipped.")


if __name__ == "__main__":
    main()
