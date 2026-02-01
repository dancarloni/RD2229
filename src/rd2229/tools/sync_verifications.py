"""Script per sincronizzare automaticamente `verifications/` con `calculations/`.

Comportamento:
- legge `.rd2229_config.yaml` se presente per trovare i percorsi
- scorre `calculations/` e crea i corrispondenti package/moduli in
  `verifications/` se non esistono (placeholder `__init__.py`)
- gestisce sia sottopackage che semplici moduli `.py`

Uso:
    python -m rd2229.tools.sync_verifications

Lo script è idempotente e stampa un riassunto delle operazioni.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List


def read_config(path: str = ".rd2229_config.yaml") -> Dict:
    try:
        import yaml  # type: ignore

        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}


def ensure_init(path: str, doc: str = None) -> None:
    os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w", encoding="utf-8") as fh:
            if doc:
                fh.write(f'"""{doc}\n"""\n')
            else:
                fh.write("""""""\n)


def mirror_modules(calculations_root: str, verifications_root: str) -> List[str]:
    ops: List[str] = []
    if not os.path.isdir(calculations_root):
        raise FileNotFoundError(f"Calculations path non trovato: {calculations_root}")

    ensure_init(verifications_root, doc="Verifiche sincronizzate automaticamente con calculations")

    for entry in sorted(os.listdir(calculations_root)):
        src_path = os.path.join(calculations_root, entry)
        dest_path = os.path.join(verifications_root, entry)

        if os.path.isdir(src_path):
            ensure_init(dest_path, doc=f"Verifiche per {entry} (placeholder)")
            ops.append(f"created package: {dest_path}")
        elif entry.endswith(".py"):
            # creare modulo corrispondente in verifications root
            os.makedirs(verifications_root, exist_ok=True)
            dest_file = os.path.join(verifications_root, entry)
            if not os.path.exists(dest_file):
                with open(dest_file, "w", encoding="utf-8") as fh:
                    fh.write(f"""# Verifica placeholder per modulo {entry}\n""")
                ops.append(f"created module: {dest_file}")

    return ops


def main(argv: List[str] | None = None) -> int:
    cfg = read_config()
    calculations = cfg.get("calculations_path", "src/rd2229/calculations")
    verifications = cfg.get("verifications_path", "src/rd2229/verifications")

    calculations = os.path.abspath(calculations)
    verifications = os.path.abspath(verifications)

    try:
        ops = mirror_modules(calculations, verifications)
    except FileNotFoundError as exc:
        print(f"Errore: {exc}")
        return 2

    if ops:
        print("Sincronizzazione completata. Operazioni eseguite:")
        for o in ops:
            print(" -", o)
    else:
        print("Nessuna modifica necessaria. verifications è già allineato.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
