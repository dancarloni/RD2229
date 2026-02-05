"""MaterialsRepository: gestione in-memory dei materiali con load/save .jsonm

Questo wrapper utilizza le utility esistenti in `tools.materials_manager`
per il parsing e i campi derivati, ma mantiene i materiali in memoria fino a
quando l'utente richiede esplicitamente il salvataggio (`save_to_jsonm`).

EventBus viene notificato dopo operazioni che mutano l'archivio in memoria
in modo che le UI (es. `VerificationTableWindow`) possano aggiornare i suggerimenti.
"""
from __future__ import annotations

import json
import logging
from typing import List, Dict, Optional
from tkinter import messagebox

from tools import materials_manager
try:
    from sections_app.services.event_bus import EventBus, MATERIALS_CLEARED, MATERIALS_ADDED, MATERIALS_UPDATED, MATERIALS_DELETED
except Exception:
    EventBus = None
    MATERIALS_CLEARED = MATERIALS_ADDED = MATERIALS_UPDATED = MATERIALS_DELETED = None

logger = logging.getLogger(__name__)


class MaterialsRepository:
    """Repository in-memory per materiali con load/save in formato .jsonm.

    - `load_from_jsonm(path)`: carica file .jsonm (lista di materiali) in memoria
    - `save_to_jsonm(path)`: salva l'elenco corrente in un file .jsonm
    - CRUD in memoria: `add`, `update`, `delete`
    Le operazioni non scrivono su disco automaticamente: l'utente deve chiamare
    `save_to_jsonm` (es. dal pulsante "Salva lista materiali").
    """

    def __init__(self) -> None:
        self._materials: List[Dict] = []
        self.path: Optional[str] = None

    def load_from_jsonm(self, path: str) -> List[Dict]:
        if not path.lower().endswith('.jsonm'):
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
                        bus.emit(MATERIALS_ADDED, material_id=m.get('id') or m.get('name'), material_name=m.get('name'))
                except Exception:
                    logger.exception("Error emitting EventBus events after load_from_jsonm")
            return self._materials
        except Exception as e:
            logger.exception("Failed loading materials from %s: %s", path, e)
            raise

    def save_to_jsonm(self, path: str) -> None:
        if not path.lower().endswith('.jsonm'):
            path = path + '.jsonm'
        try:
            # Use materials_manager.save_materials to keep file format consistent
            materials_manager.save_materials(self._materials, path)
            self.path = path
        except Exception:
            logger.exception("Error saving materials to %s", path)
            raise

    def get_all(self) -> List[Dict]:
        return [m.copy() for m in self._materials]

    def get_by_name(self, name: str) -> Optional[Dict]:
        for m in self._materials:
            if m.get('name') == name:
                return m.copy()
        return None

    def add(self, material: Dict) -> None:
        # Check duplicate by name
        if any(m.get('name') == material.get('name') for m in self._materials):
            raise ValueError(f"Material with name '{material.get('name')}' already exists")
        # Ensure derived fields (use helper from materials_manager)
        try:
            materials_manager._ensure_derived_fields(material)
        except Exception:
            # best-effort: ignore errors in derived field computation
            pass
        self._materials.append(material.copy())
        if EventBus is not None:
            try:
                EventBus().emit(MATERIALS_ADDED, material_id=material.get('id') or material.get('name'), material_name=material.get('name'))
            except Exception:
                logger.exception("Error emitting MATERIALS_ADDED")

    def update(self, name: str, updates: Dict) -> None:
        for i, m in enumerate(self._materials):
            if m.get('name') == name:
                new = {**m, **updates}
                try:
                    materials_manager._ensure_derived_fields(new)
                except Exception:
                    pass
                self._materials[i] = new
                if EventBus is not None:
                    try:
                        EventBus().emit(MATERIALS_UPDATED, material_id=new.get('id') or new.get('name'), material_name=new.get('name'))
                    except Exception:
                        logger.exception("Error emitting MATERIALS_UPDATED")
                return
        raise KeyError(f"Material with name '{name}' not found")

    def delete(self, name: str) -> None:
        new = [m for m in self._materials if m.get('name') != name]
        if len(new) == len(self._materials):
            raise KeyError(f"Material with name '{name}' not found")
        # find deleted ids
        deleted = [m for m in self._materials if m.get('name') == name]
        self._materials = new
        if EventBus is not None:
            try:
                for d in deleted:
                    EventBus().emit(MATERIALS_DELETED, material_id=d.get('id') or d.get('name'), material_name=d.get('name'))
            except Exception:
                logger.exception("Error emitting MATERIALS_DELETED")
