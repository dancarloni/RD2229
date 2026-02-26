"""ResultsModel – output serializzabile della pipeline di calcolo.

Ogni istanza di :class:`ResultsModel` contiene:
    - ``ok``: esito globale (True se tutti gli elementi verificati sono OK)
    - ``elements``: lista di :class:`ElementResult` per ogni elemento
    - ``warnings``: avvisi non bloccanti generati durante la pipeline
    - ``trace``: traccia minimale dei passi della pipeline (non log completo)
    - ``timestamp``: ISO-8601 del momento del calcolo
    - ``schema_version_input``: versione dello schema del progetto in input

Serializzazione::

    import dataclasses, json
    data = dataclasses.asdict(results)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)

Funzione di export: :func:`export_results`.
"""

from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ElementResult:
    """Risultato di calcolo per un singolo elemento strutturale."""

    element_id: str = ""
    ok: bool = False
    # Metriche numeriche (dict str→float/str serializzabile)
    metrics: dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


@dataclass
class ResultsModel:
    """Risultati serializzabili della pipeline RD2229.

    Tutti i campi hanno defaults per permettere la costruzione incrementale
    durante la pipeline, anche in caso di input incompleto.
    """

    ok: bool = False
    elements: list[ElementResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Traccia minimale: lista di stringhe che descrivono i passi eseguiti
    trace: list[str] = field(default_factory=list)
    timestamp: str = ""
    schema_version_input: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def export_results(results: ResultsModel, path: str) -> None:
    """Serializza un :class:`ResultsModel` su file JSON.

    Usa scrittura atomica tramite file temporaneo.

    Args:
        results: Modello risultati da esportare.
        path: Percorso del file destinazione.
    """
    data = dataclasses.asdict(results)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
