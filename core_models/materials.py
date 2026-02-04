from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class Material:
    name: str
    type: str  # e.g., 'concrete', 'steel'
    properties: Dict[str, float] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    
    def to_dict(self) -> Dict:
        """Converte il Material a dizionario per JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "properties": self.properties,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> Material:
        """Crea un Material da un dizionario JSON."""
        return Material(
            id=data.get("id", str(uuid4())),
            name=data.get("name", ""),
            type=data.get("type", ""),
            properties=data.get("properties", {}),
        )


class MaterialRepository:
    """Archivio in memoria dei materiali con persistenza JSON."""
    
    DEFAULT_JSON_FILE = "materials.json"

    def __init__(self, json_file: str = DEFAULT_JSON_FILE) -> None:
        self._materials: Dict[str, Material] = {}
        self._json_file = json_file
        
        # Carica i materiali dal file JSON se esiste
        self.load_from_file()

    def add(self, mat: Material) -> None:
        self._materials[mat.id] = mat
        logger.debug("Materiale aggiunto: %s (%s)", mat.id, mat.name)
        
        # Salva in file JSON
        self.save_to_file()

    def get_all(self) -> List[Material]:
        return list(self._materials.values())

    def find_by_name(self, name: str) -> Optional[Material]:
        for m in self._materials.values():
            if m.name == name:
                return m
        return None
    
    def find_by_id(self, material_id: str) -> Optional[Material]:
        return self._materials.get(material_id)
    
    def update(self, material_id: str, updated_material: Material) -> None:
        """Aggiorna un materiale esistente."""
        if material_id not in self._materials:
            logger.warning("Tentativo aggiornamento materiale non trovato: %s", material_id)
            raise KeyError(f"Materiale non trovato: {material_id}")
        
        # Preserva l'ID originale
        updated_material.id = material_id
        self._materials[material_id] = updated_material
        logger.debug("Materiale aggiornato: %s (%s)", material_id, updated_material.name)
        
        # Salva in file JSON
        self.save_to_file()
    
    def delete(self, material_id: str) -> None:
        """Elimina un materiale dal repository."""
        material = self._materials.pop(material_id, None)
        if material:
            logger.debug("Materiale eliminato: %s (%s)", material_id, material.name)
            
            # Salva in file JSON
            self.save_to_file()
    
    def clear(self) -> None:
        """Elimina tutti i materiali."""
        self._materials.clear()
        
        # Salva in file JSON
        self.save_to_file()
    
    def load_from_file(self) -> None:
        """Carica tutti i materiali dal file JSON.
        
        Se il file non esiste, il repository rimane vuoto.
        Se il file esiste ma è invalido, registra un errore.
        """
        if not os.path.isfile(self._json_file):
            logger.debug("File JSON %s non trovato, archivio vuoto", self._json_file)
            return
        
        try:
            with open(self._json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Ripristina i materiali dal JSON
            self._materials.clear()
            
            if not isinstance(data, list):
                logger.warning("File JSON %s non contiene una lista", self._json_file)
                return
            
            for idx, item in enumerate(data):
                try:
                    material = Material.from_dict(item)
                    self._materials[material.id] = material
                    logger.debug("Materiale caricato: %s (%s)", material.id, material.name)
                except Exception as e:
                    logger.exception("Errore caricamento materiale %d dal JSON: %s", idx, e)
            
            logger.info("Caricati %d materiali da %s", len(self._materials), self._json_file)
        except Exception as e:
            logger.exception("Errore lettura file JSON %s: %s", self._json_file, e)

    def save_to_file(self) -> None:
        """Salva tutti i materiali in un file JSON.
        
        Crea il file se non esiste, sovrascrive se esiste.
        """
        try:
            data = []
            for material in self._materials.values():
                material_dict = material.to_dict()
                data.append(material_dict)
            
            # Crea la directory se non esiste
            directory = os.path.dirname(self._json_file)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(self._json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("Salvati %d materiali in %s", len(data), self._json_file)
        except Exception as e:
            logger.exception("Errore salvataggio file JSON %s: %s", self._json_file, e)

