"""MaterialsRepository: gestione in-memory dei materiali con load/save .jsonm.

Questo wrapper utilizza le utility esistenti in `tools.materials_manager`
per il parsing e i campi derivati, ma mantiene i materiali in memoria fino a
quando l'utente richiede esplicitamente il salvataggio (`save_to_jsonm`).

EventBus viene notificato dopo operazioni che mutano l'archivio in memoria
in modo che le UI (es. `VerificationTableWindow`) possano aggiornare i suggerimenti.
"""

from __future__ import annotations

import logging
from typing import Any

from tools import materials_manager

# Defaults in case event bus is unavailable (e.g., in tests)
EventBus = None
MATERIALS_ADDED = "materials_added"
MATERIALS_UPDATED = "materials_updated"
MATERIALS_DELETED = "materials_deleted"
MATERIALS_CLEARED = "materials_cleared"

try:
    # Import EventBus class only when available; constants above remain valid
    from sections_app.services.event_bus import EventBus as _EventBus

    EventBus = _EventBus
except ImportError:
    # Running without the UI stack is acceptable; use defaults
    pass

logger: logging.Logger = logging.getLogger(__name__)


class MaterialsRepository:
    """Repository in-memory per materiali con load/save in formato .jsonm.

    - `load_from_jsonm(path)`: carica file .jsonm (lista di materiali) in memoria
    - `save_to_jsonm(path)`: salva l'elenco corrente in un file .jsonm
    - CRUD in memoria: `add`, `update`, `delete`
    Le operazioni non scrivono su disco automaticamente: l'utente deve chiamare
    `save_to_jsonm` (es. dal pulsante "Salva lista materiali").
    """

    def __init__(self) -> None:
        self._materials: list[dict[str, Any]] = []
        self.path: str | None = None

    def load_from_jsonm(self, path: str) -> list[dict[str, Any]]:
        if not path.lower().endswith(".jsonm"):
            raise ValueError("Material file must have .jsonm extension")
        try:
            mats = materials_manager.load_materials(path)
            # store in-memory
            self._materials = [m.copy() for m in mats]
            self.path = path
            # notify listeners
            if EventBus is not None:
                try:
                    bus = EventBus()
                    bus.emit(MATERIALS_CLEARED)
                    for m in self._materials:
                        bus.emit(
                            MATERIALS_ADDED,
                            material_id=m.get("id") or m.get("name"),
                            material_name=m.get("name"),
                        )
                except Exception as exc:  # noqa: B902
                    logger.exception(
                        "Error emitting EventBus events after load_from_jsonm: %s", exc
                    )
            return self._materials
        except Exception as exc:  # noqa: B902
            logger.exception("Failed loading materials from %s: %s", path, exc)
            raise

    def save_to_jsonm(self, path: str) -> None:
        if not path.lower().endswith(".jsonm"):
            path = path + ".jsonm"
        try:
            # Use materials_manager.save_materials to keep file format consistent
            materials_manager.save_materials(self._materials, path)
            self.path = path
        except Exception as exc:  # noqa: B902
            logger.exception("Error saving materials to %s: %s", path, exc)
            raise

    def get_all(self) -> list[dict[str, Any]]:
        return [m.copy() for m in self._materials]

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        for m in self._materials:
            if m.get("name") == name:
                return m.copy()
        return None

    def add(self, material: dict[str, Any]) -> None:
        # Check duplicate by name
        if any(m.get("name") == material.get("name") for m in self._materials):
            raise ValueError(f"Material with name '{material.get('name')}' already exists")
        # Ensure derived fields (use public helper from materials_manager)
        try:
            # Prefer public wrapper to avoid accessing protected members
            materials_manager.ensure_derived_fields(material)
        except Exception as exc:  # noqa: B902
            # best-effort: ignore errors in derived field computation
            logger.debug("Derived field computation failed: %s", exc)
        self._materials.append(material.copy())
        if EventBus is not None:
            try:
                EventBus().emit(
                    MATERIALS_ADDED,
                    material_id=material.get("id") or material.get("name"),
                    material_name=material.get("name"),
                )
            except Exception as exc:  # noqa: B902
                logger.exception("Error emitting MATERIALS_ADDED: %s", exc)

    def update(self, name: str, updates: dict[str, Any]) -> None:
        for i, m in enumerate(self._materials):
            if m.get("name") == name:
                new = {**m, **updates}
                try:
                    materials_manager.ensure_derived_fields(new)
                except Exception as exc:  # noqa: B902
                    logger.debug("Derived field computation failed during update: %s", exc)
                self._materials[i] = new
                if EventBus is not None:
                    try:
                        EventBus().emit(
                            MATERIALS_UPDATED,
                            material_id=new.get("id") or new.get("name"),
                            material_name=new.get("name"),
                        )
                    except Exception as exc:  # noqa: B902
                        logger.exception("Error emitting MATERIALS_UPDATED: %s", exc)
                return
        raise KeyError(f"Material with name '{name}' not found")

    def delete(self, name: str) -> None:
        new = [m for m in self._materials if m.get("name") != name]
        if len(new) == len(self._materials):
            raise KeyError(f"Material with name '{name}' not found")
        # find deleted ids
        deleted = [m for m in self._materials if m.get("name") == name]
        self._materials = new
        if EventBus is not None:
            try:
                for d in deleted:
                    EventBus().emit(
                        MATERIALS_DELETED,
                        material_id=d.get("id") or d.get("name"),
                        material_name=d.get("name"),
                    )
            except Exception as exc:  # noqa: B902
                logger.exception("Error emitting MATERIALS_DELETED: %s", exc)
