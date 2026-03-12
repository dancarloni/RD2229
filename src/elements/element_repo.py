"""Repository degli elementi strutturali.

Responsabilità:
- Creazione e registrazione elementi
- Caricamento da file JSON
- Collegamento con repository materiali e registry sezioni
- Serializzazione/deserializzazione
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..calc.section_registry import get_section_metadata
from ..materials.material_repo import MaterialRepository
from .element_model import Element

logger = logging.getLogger(__name__)


class ElementRepository:
    """Repository per la gestione degli elementi strutturali."""

    def __init__(self) -> None:
        self._elements: dict[str, Element] = {}

    def __len__(self) -> int:
        return len(self._elements)

    def add_element(self, element: Element) -> None:
        """Aggiunge un elemento al repository."""
        if element.element_id in self._elements:
            logger.debug("Sovrascrittura elemento '%s'.", element.element_id)
        self._elements[element.element_id] = element

    def get(self, element_id: str) -> Element | None:
        """Recupera un elemento per ID."""
        return self._elements.get(element_id)

    def list_all(self) -> list[Element]:
        """Restituisce tutti gli elementi."""
        return list(self._elements.values())

    def list_by_type(self, element_type: str) -> list[Element]:
        """Restituisce gli elementi di un dato tipo."""
        return [e for e in self._elements.values() if e.type == element_type]

    def remove(self, element_id: str) -> bool:
        """Rimuove un elemento. Restituisce True se trovato."""
        if element_id in self._elements:
            del self._elements[element_id]
            return True
        return False

    def assign_material(
        self,
        element_id: str,
        material_id: str,
        material_repo: MaterialRepository,
    ) -> bool:
        """Assegna un materiale a un elemento. Restituisce True se riuscito."""
        el = self.get(element_id)
        mat = material_repo.get(material_id)
        if el is None:
            logger.warning("Elemento '%s' non trovato.", element_id)
            return False
        if mat is None:
            logger.warning("Materiale '%s' non trovato.", material_id)
            return False
        el.material = mat
        return True

    def assign_section(self, element_id: str, section_id: str) -> bool:
        """Assegna la sezione tramite registry globale. Restituisce True se riuscito."""
        el = self.get(element_id)
        if el is None:
            logger.warning("Elemento '%s' non trovato.", element_id)
            return False
        metadata = get_section_metadata(section_id)
        if metadata is None:
            logger.warning("Sezione '%s' non trovata nel registry.", section_id)
            return False
        el.section = metadata
        return True

    def load_from_json(self, path: str, material_repo: MaterialRepository) -> int:
        """Carica elementi da file JSON.

        Formato atteso: lista di dizionari con chiave "element_id".
        Restituisce il numero di elementi caricati.
        """
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            items = data.get("elements", [])
        elif isinstance(data, list):
            items = data
        else:
            logger.warning("Formato JSON non riconosciuto in '%s'.", path)
            return 0

        count = 0
        for item in items:
            if not isinstance(item, dict) or "element_id" not in item:
                logger.warning("Elemento senza element_id, ignorato.")
                continue

            mat_id = item.get("material")
            material = material_repo.get(mat_id) if mat_id else None

            section_id = item.get("section_id")
            if section_id:
                section = get_section_metadata(section_id)
                item["section"] = section

            el = Element.from_dict(item, material=material)
            self.add_element(el)
            count += 1

        logger.info("Caricati %d elementi da '%s'.", count, path)
        return count

    def save_to_json(self, path: str) -> None:
        """Salva tutti gli elementi in un file JSON."""
        data = [el.to_dict() for el in self.list_all()]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"elements": data}, f, indent=2, ensure_ascii=False)
        logger.info("Salvati %d elementi in '%s'.", len(data), path)

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Restituisce tutti gli elementi come lista di dizionari."""
        return [el.to_dict() for el in self.list_all()]
