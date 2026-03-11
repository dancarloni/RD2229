"""Storage adapter per elementi secondari.

Gestisce persistenza in-memory degli elementi secondari.
In futuro sostituibile con persistenza su file/DB.
"""

from __future__ import annotations

import uuid
from typing import Any

# Storage in-memory
_STORAGE: dict[str, dict[str, Any]] = {}


def save_secondary_element(record: dict[str, Any]) -> str:
    """Salva un elemento secondario e restituisce il suo ID.

    Se il record ha già un 'id', lo usa; altrimenti ne genera uno.
    """
    record_id = record.get("id") or str(uuid.uuid4())
    normalized = dict(record)
    normalized["id"] = record_id
    normalized.setdefault("element_type", record.get("element_type", "generic"))
    normalized.setdefault("norm_code", record.get("norm_code", "NTC2018"))
    normalized.setdefault("phase_id", record.get("phase_id"))
    normalized.setdefault("preset_id", record.get("preset_id"))
    normalized.setdefault("trace_id", record.get("trace_id"))
    normalized.setdefault("decision_log", record.get("decision_log", []))
    _STORAGE[record_id] = normalized
    return record_id


def load_secondary_element(record_id: str) -> dict[str, Any] | None:
    """Carica un elemento secondario per ID. Restituisce None se non trovato."""
    return _STORAGE.get(record_id)


def list_secondary_elements() -> list[str]:
    """Restituisce la lista degli ID degli elementi salvati."""
    return list(_STORAGE.keys())


def list_secondary_element_records(element_type: str | None = None) -> list[dict[str, Any]]:
    """Restituisce i record salvati, opzionalmente filtrati per tipo."""
    values = list(_STORAGE.values())
    if element_type is None:
        return values
    return [record for record in values if record.get("element_type") == element_type]


def delete_secondary_element(record_id: str) -> bool:
    """Rimuove un elemento. Restituisce True se trovato e rimosso."""
    if record_id in _STORAGE:
        del _STORAGE[record_id]
        return True
    return False


def clear_storage() -> None:
    """Svuota lo storage (utile per i test)."""
    _STORAGE.clear()
