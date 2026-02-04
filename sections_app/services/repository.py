from __future__ import annotations

import csv
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from sections_app.models.sections import CSV_HEADERS, Section, create_section_from_dict
from sections_app.services.event_bus import EventBus, SECTIONS_ADDED, SECTIONS_UPDATED, SECTIONS_DELETED, SECTIONS_CLEARED

logger = logging.getLogger(__name__)


class SectionRepository:
    """Archivio in memoria delle sezioni con persistenza JSON."""

    DEFAULT_JSON_FILE = "sections.json"

    def __init__(self, json_file: str = DEFAULT_JSON_FILE) -> None:
        self._sections: Dict[str, Section] = {}
        self._keys: Dict[tuple, str] = {}
        self._json_file = json_file
        
        # Percorsi per backup
        self._file_path = Path(json_file)
        self._backup_path = self._file_path.with_name(f"{self._file_path.stem}_backup{self._file_path.suffix}")
        
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
        
        # Emetti evento
        EventBus().emit(SECTIONS_ADDED, section_id=section.id, section_name=section.name)
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
        
        # Emetti evento
        EventBus().emit(SECTIONS_UPDATED, section_id=section_id, section_name=updated_section.name)

    def delete_section(self, section_id: str) -> None:
        """Elimina una sezione dall'archivio."""
        section = self._sections.pop(section_id, None)
        if section:
            self._keys.pop(section.logical_key(), None)
            logger.debug("Sezione eliminata: %s", section_id)
            
            # Salva in file JSON
            self.save_to_file()
            
            # Emetti evento
            EventBus().emit(SECTIONS_DELETED, section_id=section_id, section_name=section.name)

    def get_all_sections(self) -> List[Section]:
        return list(self._sections.values())

    def find_by_id(self, section_id: str) -> Optional[Section]:
        return self._sections.get(section_id)

    def clear(self) -> None:
        self._sections.clear()
        self._keys.clear()
        
        # Salva in file JSON
        self.save_to_file()
        
        # Emetti evento
        EventBus().emit(SECTIONS_CLEARED)

    def load_from_file(self) -> None:
        """Carica le sezioni dal file principale, oppure dal backup se il principale è corrotto.
        
        Strategia di recovery:
        1. Tenta di caricare dal file principale
        2. Se fallisce, tenta di caricare dal backup
        3. Se anche il backup fallisce, parte con archivio vuoto
        """
        self._sections.clear()
        self._keys.clear()
        
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
            
            # Carica le sezioni
            for idx, item in enumerate(raw_data):
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
            
            logger.info("Caricate %d sezioni da %s", len(self._sections), self._file_path)
            return
        except Exception as e:
            logger.exception("Errore nel caricamento di %s, provo il backup", self._file_path)
        
        # 2) Se fallisce, prova il backup
        try:
            raw_data = _load(self._backup_path)
            if not isinstance(raw_data, list):
                logger.warning("File backup JSON %s non contiene una lista", self._backup_path)
                raise ValueError("File backup JSON non contiene una lista")
            
            # Carica le sezioni dal backup
            for idx, item in enumerate(raw_data):
                try:
                    section = create_section_from_dict(item)
                    section.compute_properties()
                    
                    # Ripristina l'ID originale dal JSON
                    if "id" in item and item["id"]:
                        section.id = item["id"]
                    
                    self._sections[section.id] = section
                    key = section.logical_key()
                    self._keys[key] = section.id
                    logger.debug("Sezione caricata da backup: %s (%s)", section.id, section.name)
                except Exception as e:
                    logger.exception("Errore caricamento sezione %d dal backup: %s", idx, e)
            
            logger.warning(
                "Caricate %d sezioni dal backup %s (file principale danneggiato)",
                len(self._sections), self._backup_path
            )
            return
        except Exception as e:
            logger.exception("Errore anche nel caricamento del backup %s", self._backup_path)
        
        # 3) Se tutto fallisce, archivio vuoto
        logger.warning(
            "Impossibile caricare archivio sezioni da %s né da %s: inizializzo archivio vuoto",
            self._file_path, self._backup_path
        )
        self._sections.clear()
        self._keys.clear()

    def save_to_file(self) -> None:
        """Salva tutte le sezioni in un file JSON con backup automatico.
        
        Strategia di sicurezza:
        1. Se il file principale esiste, crea backup (sections_backup.json)
        2. Scrive su file temporaneo (.json.tmp)
        3. Rename atomico del file temporaneo sul file principale
        """
        try:
            data = []
            for section in self._sections.values():
                section_dict = section.to_dict()
                data.append(section_dict)
            
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
                logger.debug("Salvate %d sezioni in %s (backup: %s)", len(data), self._file_path, self._backup_path)
            except Exception:
                logger.exception("Errore nel salvataggio del file sezioni")
                # Elimina file temporaneo se esiste
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
                raise
        except Exception as e:
            logger.exception("Errore salvataggio file JSON %s: %s", self._json_file, e)

    def export_backup(self, destination: Path | str) -> None:
        """
        Esporta l'archivio sezioni nel percorso indicato.
        Non modifica il file principale né il backup interno.
        Se destination ha estensione .json, salva JSON; se .csv, salva CSV.
        
        Args:
            destination: Percorso del file di destinazione (Path o str).
                        Se l'estensione è .json → salva in formato JSON
                        Se l'estensione è .csv → salva in formato CSV
                        Se mancante o diversa → aggiunge .json di default
        
        Raises:
            ValueError: Se la destinazione non è valida
            IOError: Se c'è un errore di scrittura del file
        """
        try:
            # Converti a Path
            dest_path = Path(destination) if not isinstance(destination, Path) else destination
            
            # Determina estensione e normalizza
            suffix = dest_path.suffix.lower()
            if suffix not in ['.json', '.csv']:
                # Aggiungi .json di default
                dest_path = dest_path.with_suffix('.json')
                suffix = '.json'
                logger.info("Estensione mancante o non valida, uso .json: %s", dest_path)
            
            # Crea directory di destinazione se necessaria
            if dest_path.parent.exists() is False and str(dest_path.parent) != '.':
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug("Creata directory: %s", dest_path.parent)
            
            # Ottieni tutte le sezioni
            sections = self.get_all_sections()
            
            if suffix == '.json':
                # Esporta in JSON
                data = [section.to_dict() for section in sections]
                with dest_path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info("Esportate %d sezioni in JSON: %s", len(sections), dest_path)
                
            elif suffix == '.csv':
                # Esporta in CSV usando CsvSectionSerializer
                serializer = CsvSectionSerializer()
                serializer.export_to_csv(str(dest_path), sections)
                logger.info("Esportate %d sezioni in CSV: %s", len(sections), dest_path)
            
        except (OSError, IOError) as e:
            logger.exception("Errore I/O durante esportazione backup in %s: %s", destination, e)
            raise IOError(f"Impossibile esportare backup in {destination}: {e}") from e
        except Exception as e:
            logger.exception("Errore durante esportazione backup in %s: %s", destination, e)
            raise ValueError(f"Errore esportazione backup: {e}") from e


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

