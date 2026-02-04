from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Importa EventBus con try/except per evitare circular imports
try:
    from sections_app.services.event_bus import EventBus, MATERIALS_ADDED, MATERIALS_UPDATED, MATERIALS_DELETED, MATERIALS_CLEARED
    HAS_EVENT_BUS = True
except ImportError:
    HAS_EVENT_BUS = False


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
        
        # Percorsi per backup
        self._file_path = Path(json_file)
        self._backup_path = self._file_path.with_name(f"{self._file_path.stem}_backup{self._file_path.suffix}")
        
        # Carica i materiali dal file JSON se esiste
        self.load_from_file()

    def add(self, mat: Material) -> None:
        self._materials[mat.id] = mat
        logger.debug("Materiale aggiunto: %s (%s)", mat.id, mat.name)
        
        # Salva in file JSON
        self.save_to_file()
        
        # Emetti evento se disponibile
        if HAS_EVENT_BUS:
            EventBus().emit(MATERIALS_ADDED, material_id=mat.id, material_name=mat.name)

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
        
        # Emetti evento se disponibile
        if HAS_EVENT_BUS:
            EventBus().emit(MATERIALS_UPDATED, material_id=material_id, material_name=updated_material.name)
    
    def delete(self, material_id: str) -> None:
        """Elimina un materiale dal repository."""
        material = self._materials.pop(material_id, None)
        if material:
            logger.debug("Materiale eliminato: %s (%s)", material_id, material.name)
            
            # Salva in file JSON
            self.save_to_file()
            
            # Emetti evento se disponibile
            if HAS_EVENT_BUS:
                EventBus().emit(MATERIALS_DELETED, material_id=material_id, material_name=material.name)
    
    def clear(self) -> None:
        """Elimina tutti i materiali."""
        self._materials.clear()
        
        # Salva in file JSON
        self.save_to_file()
        
        # Emetti evento se disponibile
        if HAS_EVENT_BUS:
            EventBus().emit(MATERIALS_CLEARED)
    
    def load_from_file(self) -> None:
        """Carica i materiali dal file principale, oppure dal backup se il principale è corrotto.
        
        Strategia di recovery:
        1. Tenta di caricare dal file principale
        2. Se fallisce, tenta di caricare dal backup
        3. Se anche il backup fallisce, parte con archivio vuoto
        """
        self._materials.clear()
        
        def _load(path: Path) -> list:
            """Helper per caricare dati da un file JSON."""
            if not path.exists():
                return []
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        
        # 1) Prova a leggere il file principale
        try:
            raw_data = _load(self._file_path)
            if not isinstance(raw_data, list):
                logger.warning("File JSON %s non contiene una lista", self._file_path)
                raise ValueError("File JSON non contiene una lista")
            
            # Carica i materiali
            for idx, item in enumerate(raw_data):
                try:
                    material = Material.from_dict(item)
                    self._materials[material.id] = material
                    logger.debug("Materiale caricato: %s (%s)", material.id, material.name)
                except Exception as e:
                    logger.exception("Errore caricamento materiale %d dal JSON: %s", idx, e)
            
            logger.info("Caricati %d materiali da %s", len(self._materials), self._file_path)
            return
        except Exception as e:
            logger.exception("Errore nel caricamento di %s, provo il backup", self._file_path)
        
        # 2) Se fallisce, prova il backup
        try:
            raw_data = _load(self._backup_path)
            if not isinstance(raw_data, list):
                logger.warning("File backup JSON %s non contiene una lista", self._backup_path)
                raise ValueError("File backup JSON non contiene una lista")
            
            # Carica i materiali dal backup
            for idx, item in enumerate(raw_data):
                try:
                    material = Material.from_dict(item)
                    self._materials[material.id] = material
                    logger.debug("Materiale caricato da backup: %s (%s)", material.id, material.name)
                except Exception as e:
                    logger.exception("Errore caricamento materiale %d dal backup: %s", idx, e)
            
            logger.warning(
                "Caricati %d materiali dal backup %s (file principale danneggiato)",
                len(self._materials), self._backup_path
            )
            return
        except Exception as e:
            logger.exception("Errore anche nel caricamento del backup %s", self._backup_path)
        
        # 3) Se tutto fallisce, archivio vuoto
        logger.warning(
            "Impossibile caricare archivio materiali da %s né da %s: inizializzo archivio vuoto",
            self._file_path, self._backup_path
        )
        self._materials.clear()

    def save_to_file(self) -> None:
        """Salva tutti i materiali in un file JSON con backup automatico.
        
        Strategia di sicurezza:
        1. Se il file principale esiste, crea backup (materials_backup.json)
        2. Scrive su file temporaneo (.json.tmp)
        3. Rename atomico del file temporaneo sul file principale
        """
        try:
            data = []
            for material in self._materials.values():
                material_dict = material.to_dict()
                data.append(material_dict)
            
            # Crea la directory se non esiste
            if self._file_path.parent.exists() is False and str(self._file_path.parent) != '.':
                self._file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Crea backup del file esistente
            if self._file_path.exists():
                try:
                    shutil.copy2(self._file_path, self._backup_path)
                    logger.debug("Backup creato: %s", self._backup_path)
                except Exception as exc:
                    logger.warning("Impossibile creare backup di %s: %s", self._file_path, exc)
            
            # Scrivi su file temporaneo
            tmp_path = self._file_path.with_suffix(".json.tmp")
            try:
                with tmp_path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Rename atomico
                tmp_path.replace(self._file_path)
                logger.debug("Salvati %d materiali in %s (backup: %s)", len(data), self._file_path, self._backup_path)
            except Exception:
                logger.exception("Errore nel salvataggio del file materiali")
                # Elimina file temporaneo se esiste
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
                raise
        except Exception as e:
            logger.exception("Errore salvataggio file JSON %s: %s", self._json_file, e)

