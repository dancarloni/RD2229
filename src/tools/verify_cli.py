"""CLI per eseguire verifiche strutturali dalla riga di comando.

Pipeline: config → bootstrap → resolve_inputs → action_repo → report/export.

Utilizzo:
    python -m src.tools.verify_cli --config project.json --format html --output report.html
    python -m src.tools.verify_cli --config project.json --format csv --output results.csv
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from ..actions.action_repo import get_action, list_actions_for_norm
from ..codes.code_registry import bootstrap_codes
from ..elements.element_repo import ElementRepository
from ..elements.resolve_inputs import resolve_verification_inputs
from ..materials.material_repo import MaterialRepository
from ..report.renderer_html import HTMLReportRenderer
from ..report.renderer_md import MarkdownReportRenderer
from .export_results import export_to_csv, export_to_json

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parsing degli argomenti CLI."""
    parser = argparse.ArgumentParser(
        description="CLI verifica strutturale — RD2229 / NTC2018",
    )
    parser.add_argument("--config", type=str, default=None,
                        help="File di configurazione progetto (JSON)")
    parser.add_argument("--format", type=str, default="html",
                        choices=["html", "md", "json", "csv"],
                        help="Formato output: html, md, json, csv")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Percorso file di output")
    parser.add_argument("--norm", type=str, default=None,
                        help="Norma di riferimento (es. NTC2018, RD2229)")
    parser.add_argument("--checks", type=str, nargs="*", default=None,
                        help="Lista azioni da eseguire (es. flexure_check shear_check)")
    parser.add_argument("--elements", type=str, default=None,
                        help="File JSON con elementi strutturali")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args(argv)


def load_user_config(path: str) -> dict[str, Any]:
    """Carica configurazione utente da file JSON."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def bootstrap_all(user_conf: dict[str, Any]) -> dict[str, Any]:
    """Inizializza repository materiali ed elementi."""
    materials = MaterialRepository()
    materials.carica_defaults()

    elements = ElementRepository()

    # Carica elementi da file se specificato
    elements_path = user_conf.get("elements_file")
    if elements_path:
        elements.load_from_json(elements_path, materials)

    # Bootstrap normative
    try:
        bootstrap_codes("src/codes")
    except Exception:
        logger.debug("Bootstrap codes non disponibile, proseguo.")

    return {
        "materials": materials,
        "elements": elements,
    }


def run_verifications(
    resolved: dict[str, Any],
    check_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Esegue le verifiche sugli elementi risolti.

    Args:
        resolved: output di resolve_verification_inputs().
        check_ids: lista di azioni da eseguire (None = tutte per norma).

    Returns:
        Lista di risultati.
    """
    norm_code = resolved.get("norm_code", "NTC2018")
    normative = resolved.get("normative", {"norm_code": norm_code})
    settings = resolved.get("settings", {})
    elements = resolved.get("elements", [])

    # Determina checks da eseguire
    if check_ids:
        actions = [get_action(cid) for cid in check_ids]
        actions = [a for a in actions if a is not None]
    else:
        actions = list_actions_for_norm(norm_code)

    if not actions:
        logger.warning("Nessuna azione di verifica trovata per norma '%s'.", norm_code)
        return []

    results: list[dict[str, Any]] = []

    for element in elements:
        for action in actions:
            result = action.run(element, normative, settings)
            result["element_id"] = element.get("element_id", "-")
            results.append(result)

    return results


def run_cli(argv: list[str] | None = None) -> None:
    """Entry point CLI."""
    args = parse_args(argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Carica configurazione
    user_conf: dict[str, Any] = {}
    if args.config:
        user_conf = load_user_config(args.config)
    if args.norm:
        user_conf["norm_code"] = args.norm
    if args.elements:
        user_conf["elements_file"] = args.elements

    # Bootstrap
    repos = bootstrap_all(user_conf)
    materials = repos["materials"]
    elements = repos["elements"]

    # Risolve input
    resolved = resolve_verification_inputs(elements, materials, user_conf)

    # Esegue verifiche
    check_ids = args.checks or user_conf.get("checks")
    results = run_verifications(resolved, check_ids)
    resolved["results"] = results

    # Output
    output_path = args.output
    fmt = args.format

    if fmt == "json":
        if output_path:
            export_to_json(resolved, output_path)
            print(f"Risultati esportati in {output_path}")
        else:
            print(json.dumps(resolved, indent=2, ensure_ascii=False))
    elif fmt == "csv":
        if output_path:
            n = export_to_csv(resolved, output_path)
            print(f"Esportate {n} righe in {output_path}")
        else:
            print("Errore: --output richiesto per formato CSV.", file=sys.stderr)
            sys.exit(1)
    elif fmt == "md":
        renderer = MarkdownReportRenderer()
        report = renderer.render(resolved)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report Markdown generato in {output_path}")
        else:
            print(report)
    else:  # html
        renderer = HTMLReportRenderer()
        report = renderer.render(resolved)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report HTML generato in {output_path}")
        else:
            print(report)

    # Riepilogo
    total = len(results)
    passed = sum(1 for r in results if r.get("ok"))
    print(f"\nVerifiche: {passed}/{total} superate.")


if __name__ == "__main__":
    run_cli()
