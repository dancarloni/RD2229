"""
export_results.py

Utility per esportare i risultati delle verifiche in vari formati:

- JSON
- CSV
- TABELLE (per uso interno)
- Integrazione con report HTML / MD / PDF

Il modulo NON effettua verifiche: riceve i dati finali strutturati.
Fa parte della pipeline:

    repo → resolve_inputs → action_repo → report → exporter

Questo file è STUB S2:
- Struttura completa
- Docstring estese
- Nessuna implementazione reale
"""

import csv
import json
from typing import Any


def export_to_json(data: dict[str, Any], path: str) -> None:
    """
    Esporta i risultati in JSON.

    TODO Copilot:
    - Validare struttura dati.
    - Aggiungere indentazione configurabile.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_to_csv(data: dict[str, Any], path: str) -> None:
    """
    Esporta i risultati in CSV.

    Il CSV include tipicamente:
    - element_id
    - action_id
    - ok/non ok
    - messaggi principali

    TODO:
    - Validare presenza campi
    - Gestire errori
    """

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["element_id", "action_id", "ok", "message"])

        # TODO Copilot:
        # - Iterare su data["results"]
        # - Scrivere righe pertinenti
        writer.writerow(["stub_element", "stub_action", True, "no data (stub)"])


# ======================================================================
# FINE FILE export_results.py
# ======================================================================
