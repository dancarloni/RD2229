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

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def read_config(path: str = ".rd2229_config.yaml") -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        logger.debug("yaml not installed, using defaults")
        return {}

    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except (FileNotFoundError, getattr(__import__("yaml"), "YAMLError", Exception)) as exc:  # type: ignore
        logger.debug("No config found at %s, using defaults: %s", path, exc)
        return {}


def ensure_init(path: str | Path, doc: str | None = None) -> None:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    init_file = p / "__init__.py"
    if not init_file.exists():
        with init_file.open("w", encoding="utf-8") as fh:
            if doc:
                fh.write(f'"""{doc}\n"""\n')
            else:
                fh.write('"""\n"""\n')


def mirror_modules(calculations_root: str, verifications_root: str) -> list[str]:
    ops: list[str] = []
    calc_root = Path(calculations_root)
    ver_root = Path(verifications_root)

    if not calc_root.is_dir():
        raise FileNotFoundError(f"Calculations path non trovato: {calculations_root}")

    ensure_init(ver_root, doc="Verifiche sincronizzate automaticamente con calculations")

    for entry in sorted(calc_root.iterdir(), key=lambda p: p.name):
        src_path = entry
        dest_path = ver_root / entry.name

        if src_path.is_dir():
            ensure_init(dest_path, doc=f"Verifiche per {entry.name} (placeholder)")
            ops.append(f"created package: {dest_path}")
        elif entry.name.endswith(".py"):
            # creare modulo corrispondente in verifications root
            ver_root.mkdir(parents=True, exist_ok=True)
            dest_file = ver_root / entry.name
            if not dest_file.exists():
                with dest_file.open("w", encoding="utf-8") as fh:
                    fh.write(f"# Verifica placeholder per modulo {entry.name}\n")
                ops.append(f"created module: {dest_file}")

    return ops


def main(_argv: list[str] | None = None) -> int:
    cfg = read_config()
    calculations = cfg.get("calculations_path", "src/rd2229/calculations")
    verifications = cfg.get("verifications_path", "src/rd2229/verifications")

    calculations = str(Path(calculations).resolve())
    verifications = str(Path(verifications).resolve())

    try:
        ops = mirror_modules(calculations, verifications)
    except FileNotFoundError as exc:
        logger.error("Errore: %s", exc)
        return 2

    if ops:
        logger.info("Sincronizzazione completata. Operazioni eseguite:")
        for o in ops:
            logger.info(" - %s", o)
    else:
        logger.info("Nessuna modifica necessaria. verifications è già allineato.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
