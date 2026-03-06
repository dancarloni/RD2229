"""Utility per esportare i risultati delle verifiche in vari formati.

Formati supportati: JSON, CSV.
Pipeline: repo → resolve_inputs → action_repo → report → exporter
"""

from __future__ import annotations

import csv
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def export_to_json(data: dict[str, Any], path: str, indent: int = 2) -> None:
    """Esporta i risultati in JSON.

    Args:
        data: struttura completa con results, elements, ecc.
        path: percorso file di output.
        indent: indentazione JSON (default 2).
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    logger.info("Esportato JSON in '%s'.", path)


def export_to_csv(data: dict[str, Any], path: str) -> int:
    """Esporta i risultati in CSV.

    Colonne: element_id, action_id, ok, utilization, message.

    Args:
        data: deve contenere "results" (lista di dict con action_id, ok, messages, partials).
        path: percorso file di output.

    Returns:
        Numero di righe scritte.
    """
    results = data.get("results", [])

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["element_id", "action_id", "ok", "utilization", "message"])

        rows = 0
        for r in results:
            element_id = r.get("element_id", r.get("partials", {}).get("element_id", "-"))
            action_id = r.get("action_id", "-")
            ok = r.get("ok", False)
            utilization = r.get("partials", {}).get("utilization", "-")
            messages = "; ".join(r.get("messages", []))
            writer.writerow([element_id, action_id, ok, utilization, messages])
            rows += 1

    logger.info("Esportato CSV in '%s' (%d righe).", path, rows)
    return rows


def results_to_table(results: list[dict[str, Any]]) -> list[list[str]]:
    """Converte i risultati in formato tabella (lista di righe).

    Utile per formattazione interna o visualizzazione CLI.
    """
    header = ["#", "Verifica", "Esito", "Utilizzazione", "Note"]
    rows = [header]

    for i, r in enumerate(results, 1):
        action_id = r.get("action_id", "-")
        ok = "OK" if r.get("ok") else "NON VERIFICATO"
        util = r.get("partials", {}).get("utilization", "-")
        if isinstance(util, float):
            util = f"{util:.3f}"
        msgs = "; ".join(r.get("messages", [])[:1])
        rows.append([str(i), action_id, ok, str(util), msgs])

    return rows
