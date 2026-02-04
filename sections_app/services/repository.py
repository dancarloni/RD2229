from __future__ import annotations

import csv
import json
import logging
import os
from typing import Dict, Iterable, List, Optional

from sections_app.models.sections import CSV_HEADERS, Section, create_section_from_dict

logger = logging.getLogger(__name__)


class SectionRepository:
    """Archivio in memoria delle sezioni con persistenza JSON."""

    DEFAULT_JSON_FILE = "sections.json"

    def __init__(self, json_file: str = DEFAULT_JSON_FILE) -> None:
        self._sections: Dict[str, Section] = {}
        self._keys: Dict[tuple, str] = {}
        self._json_file = json_file
        
        # Carica le sezioni dal file JSON se esiste
        self.load_from_file()

    def add_section(self, section: Section) -> bool:
        """Aggiunge una sezione se non duplicata. Ritorna True se aggiunta.

        Prima di aggiungere, si prova a calcolare tutte le proprietà geometriche.
        Se il calcolo fallisce, la sezione non viene salvata.
        """
        # Calcola proprietà (se fallisce non si salva)
        try:
            section.compute_properties()
        except Exception as e:
            logger.exception("Calcolo proprietà fallito: %s", e)
            return False

        key = section.logical_key()
        if key in self._keys:
            logger.debug("Sezione duplicata ignorata: %s", key)
            return False
        self._sections[section.id] = section
        self._keys[key] = section.id
        logger.debug("Sezione aggiunta: %s", section.id)
        
        # Salva in file JSON
        self.save_to_file()
        return True

    def update_section(self, section_id: str, updated_section: Section) -> None:
        """Aggiorna una sezione esistente.

        Se la sezione non esiste, solleva KeyError. Se la nuova chiave logica entra in conflitto
        con un'altra sezione esistente (diversa da quella aggiornata), solleva ValueError per evitare duplicati.

        Inoltre, prima dell'aggiornamento, esegue `compute_properties()` sulla sezione aggiornata
        e blocca l'aggiornamento se il calcolo fallisce.
        """
        logger.debug("Updating section %s with %s", section_id, updated_section)
        if section_id not in self._sections:
            logger.warning("Attempted update on non-existing section: %s", section_id)
            raise KeyError(f"Sezione non trovata: {section_id}")

        # Calcolo proprietà prima di procedere
        try:
            updated_section.compute_properties()
        except Exception as e:
            logger.exception("Calcolo proprietà fallito durante update per %s: %s", section_id, e)
            raise

        # Controlla conflitti sulla chiave logica
        new_key = updated_section.logical_key()
        existing = self._keys.get(new_key)
        if existing is not None and existing != section_id:
            logger.warning(
                "Update would create duplicate logical key %s for section %s (conflicts with %s)",
                new_key,
                section_id,
                existing,
            )
            raise ValueError("Aggiornamento invalido: crea duplicato di una sezione esistente")

        old_section = self._sections[section_id]
        old_key = old_section.logical_key()
        # Rimuovi vecchia chiave e aggiorna
        self._keys.pop(old_key, None)

        updated_section.id = section_id
        self._sections[section_id] = updated_section
        self._keys[new_key] = section_id
        logger.debug("Sezione aggiornata: %s", section_id)
        
        # Salva in file JSON
        self.save_to_file()

    def delete_section(self, section_id: str) -> None:
        """Elimina una sezione dall'archivio."""
        section = self._sections.pop(section_id, None)
        if section:
            self._keys.pop(section.logical_key(), None)
            logger.debug("Sezione eliminata: %s", section_id)
            
            # Salva in file JSON
            self.save_to_file()

    def get_all_sections(self) -> List[Section]:
        return list(self._sections.values())

    def find_by_id(self, section_id: str) -> Optional[Section]:
        return self._sections.get(section_id)

    def clear(self) -> None:
        self._sections.clear()
        self._keys.clear()
        
        # Salva in file JSON
        self.save_to_file()

    def load_from_file(self) -> None:
        """Carica tutte le sezioni dal file JSON.
        
        Se il file non esiste, il repository rimane vuoto.
        Se il file esiste ma è invalido, registra un errore.
        """
        if not os.path.isfile(self._json_file):
            logger.debug("File JSON %s non trovato, archivio vuoto", self._json_file)
            return
        
        try:
            with open(self._json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Ripristina le sezioni dal JSON
            self._sections.clear()
            self._keys.clear()
            
            if not isinstance(data, list):
                logger.warning("File JSON %s non contiene una lista", self._json_file)
                return
            
            for idx, item in enumerate(data):
                try:
                    section = create_section_from_dict(item)
                    section.compute_properties()
                    
                    # Ripristina l'ID originale dal JSON
                    if "id" in item and item["id"]:
                        section.id = item["id"]
                    
                    self._sections[section.id] = section
                    key = section.logical_key()
                    self._keys[key] = section.id
                    logger.debug("Sezione caricata: %s (%s)", section.id, section.name)
                except Exception as e:
                    logger.exception("Errore caricamento sezione %d dal JSON: %s", idx, e)
            
            logger.info("Caricate %d sezioni da %s", len(self._sections), self._json_file)
        except Exception as e:
            logger.exception("Errore lettura file JSON %s: %s", self._json_file, e)

    def save_to_file(self) -> None:
        """Salva tutte le sezioni in un file JSON.
        
        Crea il file se non esiste, sovrascrive se esiste.
        """
        try:
            data = []
            for section in self._sections.values():
                section_dict = section.to_dict()
                data.append(section_dict)
            
            # Crea la directory se non esiste
            directory = os.path.dirname(self._json_file)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(self._json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("Salvate %d sezioni in %s", len(data), self._json_file)
        except Exception as e:
            logger.exception("Errore salvataggio file JSON %s: %s", self._json_file, e)


class CsvSectionSerializer:
    """Gestione import/export CSV con log dettagliato."""

    def export_to_csv(self, file_path: str, sections: Iterable[Section], delimiter: str = ";") -> None:
        """Esporta tutte le colonne presenti nelle dict ritornate da Section.to_dict()."""
        rows = 0
        # Determina dinamicamente tutte le chiavi in ordine preservando id/name/section_type all'inizio
        fieldnames = ["id", "name", "section_type"]
        for section in sections:
            for k in section.to_dict().keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            for section in sections:
                # Convertiamo None in stringa vuota per il CSV
                row = {k: ("" if v is None else v) for k, v in section.to_dict().items()}
                writer.writerow(row)
                rows += 1
        logger.debug("Esportate %s righe in %s", rows, file_path)

    def import_from_csv(self, file_path: str, delimiter: str = ";") -> List[Section]:
        sections: List[Section] = []
        with open(file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            for idx, row in enumerate(reader, start=2):
                if not row or all(not (value or "").strip() for value in row.values()):
                    logger.debug("Riga vuota saltata: %s", idx)
                    continue
                try:
                    section = create_section_from_dict(row)
                    section.compute_properties()
                    sections.append(section)
                except Exception:
                    logger.exception("Errore import riga %s: %s", idx, row)
        logger.debug("Importate %s righe da %s", len(sections), file_path)
        return sections

