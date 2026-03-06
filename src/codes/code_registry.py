"""Registry normativo del software.

Mappa le normative disponibili (NTC2018, EC2, EC8, ...) collegando:
- parametri numerici (JSON → params/)
- clausole, paragrafi, limiti normativi (YAML → clauses/)

Fornisce accesso unificato a coefficienti di sicurezza, combinazione,
limiti di tensione e parametri di duttilità.

Unità: cm, kg/cm², kg/m³.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# ======================================================================
# REGISTRY PER LE NORMATIVE DISPONIBILI
# ======================================================================

CODE_REGISTRY: dict[str, dict[str, Any]] = {}


# ======================================================================
# FUNZIONI DI CARICAMENTO
# ======================================================================


def load_code_params(name: str, path: str) -> dict[str, Any]:
    """Carica i parametri normativi (JSON) per una normativa."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        logger.debug("Parametri '%s' caricati da '%s'.", name, path)
        return data
    except FileNotFoundError:
        logger.warning("File parametri non trovato per '%s': '%s'.", name, path)
        return {}
    except json.JSONDecodeError as exc:
        logger.warning("Errore JSON in '%s': %s.", path, exc)
        return {}


def load_code_clauses(name: str, path: str) -> dict[str, Any]:
    """Carica le clausole normative (YAML) per una normativa."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.debug("Clausole '%s' caricate da '%s'.", name, path)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        logger.debug("File clausole non trovato per '%s': '%s'.", name, path)
        return {}
    except yaml.YAMLError as exc:
        logger.warning("Errore YAML in '%s': %s.", path, exc)
        return {}


# ======================================================================
# REGISTRAZIONE E ACCESSO
# ======================================================================


def register_code(code_name: str, params: dict[str, Any], clauses: dict[str, Any]) -> None:
    """Registra una normativa nel registry."""
    if not code_name:
        logger.warning("code_name vuoto: normativa ignorata.")
        return
    CODE_REGISTRY[code_name] = {
        "params": params,
        "clauses": clauses,
    }
    logger.debug("Normativa '%s' registrata.", code_name)


def get_code(code_name: str) -> dict[str, Any] | None:
    """Recupera una normativa dal registry."""
    return CODE_REGISTRY.get(code_name)


def get_code_param(code_name: str, key: str, default: Any = None) -> Any:
    """Accesso diretto a un singolo parametro di una normativa.

    Supporta chiavi annidate con notazione a punto: 'materials.gamma_c'.
    """
    entry = CODE_REGISTRY.get(code_name)
    if entry is None:
        return default
    params = entry.get("params", {})

    # Navigazione con dot-notation
    parts = key.split(".")
    current: Any = params
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return default
        if current is None:
            return default
    return current


def get_code_clause(code_name: str, section_path: str) -> Any:
    """Accesso a una clausola per path (es. 'materials.concrete.limit_states').

    Restituisce None se non trovata.
    """
    entry = CODE_REGISTRY.get(code_name)
    if entry is None:
        return None
    clauses = entry.get("clauses", {})

    parts = section_path.split(".")
    current: Any = clauses
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


def list_codes() -> list[str]:
    """Restituisce la lista delle normative registrate."""
    return list(CODE_REGISTRY.keys())


def clear_registry() -> None:
    """Svuota il registry (utile per i test)."""
    CODE_REGISTRY.clear()


# ======================================================================
# BOOTSTRAP
# ======================================================================


def bootstrap_codes(base_path: str) -> int:
    """Carica tutte le normative da params/*.json e clauses/*.yml.

    Per ogni file JSON in params/, cerca il corrispondente .yml in clauses/.
    Restituisce il numero di normative caricate.
    """
    params_dir = os.path.join(base_path, "params")
    clauses_dir = os.path.join(base_path, "clauses")

    if not os.path.isdir(params_dir):
        logger.warning("Directory params non trovata: '%s'.", params_dir)
        return 0

    count = 0
    for filename in sorted(os.listdir(params_dir)):
        if not filename.endswith(".json"):
            continue

        code_name = filename[:-5]  # rimuovi .json
        params_path = os.path.join(params_dir, filename)
        params = load_code_params(code_name, params_path)

        # Cerca clausole corrispondenti (.yml o .yaml)
        clauses: dict[str, Any] = {}
        for ext in (".yml", ".yaml"):
            clause_path = os.path.join(clauses_dir, code_name + ext)
            if os.path.isfile(clause_path):
                clauses = load_code_clauses(code_name, clause_path)
                break

        register_code(code_name, params, clauses)
        count += 1

    logger.info("Bootstrap normative: %d caricate da '%s'.", count, base_path)
    return count
