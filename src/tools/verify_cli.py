"""
verify_cli.py

Strumento CLI (Command Line Interface) per eseguire verifiche
strutturali dalla riga di comando.

OBIETTIVI:
- Permettere l'esecuzione automatica delle verifiche senza GUI.
- Caricare repository materiali, elementi e normative.
- Invocare resolve_inputs() per generare gli input finali.
- Attivare una pipeline di verifiche basata su action_repo.
- Generare un report (HTML/MD) tramite i renderer del package report.

UTILIZZO ATTESO (futuro):
    python verify_cli.py --config config/user_conf.yml

FUNZIONI PRINCIPALI:
- parse_args()
- load_user_config()
- bootstrap_all()
- run_verifications()
- export_report()

Questo file è uno STUB S2:
- Nessuna implementazione reale della pipeline
- Struttura e TODO per Copilot Plan
"""

import argparse
import json
from typing import Any

from ..codes.code_registry import bootstrap_codes
from ..elements.element_repo import ElementRepository
from ..elements.resolve_inputs import resolve_verification_inputs
from ..materials.material_repo import MaterialRepository
from ..report.renderer_html import HTMLReportRenderer
from ..report.renderer_md import MarkdownReportRenderer


def parse_args():
    """
    Parsing degli argomenti CLI.

    TODO Copilot:
    - Aggiungere opzioni per:
        --config file.yml
        --output out.html
        --format html/md
    """
    parser = argparse.ArgumentParser(description="CLI verifica strutturale (stub).")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--format", type=str, default="html")
    return parser.parse_args()


def load_user_config(path: str) -> dict[str, Any]:
    """
    Carica configurazione utente da file JSON/YAML.

    TODO Copilot:
    - Supportare YAML.
    - Validare dati.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def bootstrap_all() -> dict[str, Any]:
    """
    Inizializza repository e normative.

    TODO:
    - Caricare materiali da legacy.
    - Caricare sezioni da legacy.
    - Inizializzare registry normative.
    - Load base path from config/app.yml instead of hardcoding
    """

    materials = MaterialRepository()
    elements = ElementRepository()

    # Boot normative — TODO: load path from config/app.yml
    bootstrap_codes("src/codes")

    return {
        "materials": materials,
        "elements": elements,
    }


def run_cli() -> None:
    """
    Entry point CLI.

    TODO Copilot:
    - Implementare pipeline completa.
    """
    args = parse_args()

    # Carica user config
    if args.config:
        user_conf = load_user_config(args.config)
    else:
        user_conf = {}

    # Bootstrap
    repos = bootstrap_all()
    materials = repos["materials"]
    elements = repos["elements"]

    # Risolve input
    resolved = resolve_verification_inputs(elements, materials, user_conf)

    # Report
    if args.format == "html":
        renderer = HTMLReportRenderer("src/report/templates/template.html")
        out = renderer.render(resolved)
        print(out)
    else:
        renderer = MarkdownReportRenderer("src/report/templates/template.md")
        out = renderer.render(resolved)
        print(out)

    print("\n[CLI Stub] Verifica completata (stub).\n")


if __name__ == "__main__":
    run_cli()


# ======================================================================
# FINE FILE verify_cli.py
# ======================================================================
