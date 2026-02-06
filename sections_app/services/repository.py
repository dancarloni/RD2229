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

# Percorso JSON di default usato dalle API helper e dal repository
DEFAULT_JSON_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'sec_repository', 'sec_repository.jsons'))

class SectionRepository:
    """Archivio in memoria delle sezioni con persistenza JSON."""

    DEFAULT_JSON_FILE = DEFAULT_JSON_FILE

    def __init__(self, json_file: Optional[str] = None, auto_migrate: Optional[bool] = None) -> None:
        """
        Se `json_file` è None → usiamo il file canonico `DEFAULT_JSON_FILE` e
        abilitiamo la migrazione automatica da `sections.json` a `sec_repository/...jsons`
        (a meno che l'env var `RD2229_NO_AUTO_MIGRATE` sia attiva).

        Se `json_file` è esplicito (es. 'sections.json') → lo rispettiamo e non
        eseguiamo migrazioni automatiche.
        """
        self._sections: Dict[str, Section] = {}
        self._keys: Dict[tuple, str] = {}

        # Decidi se la migrazione automatica è abilitata (default: True)
        if auto_migrate is None:
            no_migrate = os.environ.get("RD2229_NO_AUTO_MIGRATE", "").lower()
            auto_migrate = not (no_migrate in ("1", "true", "yes"))

        # Se l'utente ha passato un path esplicito, lo usiamo così com'è
        self._explicit_json_file = json_file is not None
        if json_file is not None:
            self._json_file = json_file
            self._file_path = Path(json_file)
        else:
            # Usare il canonical come fallback, ma provare prima a migrare qualsiasi legacy
            canonical = Path(self.DEFAULT_JSON_FILE)
            self._json_file = str(canonical)
            self._file_path = canonical
            if auto_migrate:
                # Cerca `sections.json` in posizioni legacy (cwd, root progetto)
                project_root = Path(__file__).resolve().parents[2]
                candidates = [Path("sections.json").resolve(), (project_root / "sections.json").resolve()]
                migrated = False
                for cand in candidates:
                    if cand.exists():
                        try:
                            # Backup legacy
                            bak = cand.with_suffix(cand.suffix + ".bak")
                            shutil.copy2(cand, bak)
                            with cand.open("r", encoding="utf-8") as f:
                                data = json.load(f)

                            # Preferisci creare un canonical locale nella stessa cartella del legacy
                            local_canonical = cand.parent / "sec_repository" / "sec_repository.jsons"
                            if not local_canonical.parent.exists():
                                local_canonical.parent.mkdir(parents=True, exist_ok=True)

                            # Scrivi il file canonical locale (se non esiste già)
                            if not local_canonical.exists():
                                with local_canonical.open("w", encoding="utf-8") as f:
                                    json.dump(data, f, indent=2, ensure_ascii=False)

                            # Aggiorna file path attivo per questo repository in modo che punti al locale
                            self._json_file = str(local_canonical)
                            self._file_path = local_canonical

                            logger.info("Migrato legacy %s -> %s (backup: %s)", cand, local_canonical, bak)

                            # Se possibile, mostra una messagebox informativa (non bloccante)
                            try:
                                from tkinter import messagebox
                                messagebox.showinfo(
                                    "Migrazione sezioni",
                                    f"Il file legacy '{cand.name}' è stato migrato in '{local_canonical}'.\nBackup creato come '{bak.name}'."
                                )
                            except Exception:
                                # Headless o ambiente non-GUI: silenziamo la messagebox
                                pass

                            migrated = True
                        except Exception:
                            logger.exception("Errore durante la migrazione di %s", cand)
                        break
                if not migrated:
                    logger.debug("Nessun file legacy trovato per la migrazione; user default canonical: %s", canonical)

        # Percorsi per backup
        self._backup_path = self._file_path.with_name(f"{self._file_path.stem}_backup{self._file_path.suffix}")

        # Carica le sezioni dal file JSON se esiste
        self.load_from_file()

        # Se il file locale (es. migrazione) non ha prodotto sezioni valide,
        # prova a caricare il file canonical globale come fallback, SOLO se
        # l'utente non ha passato un percorso esplicito (compatibilità con test)
        try:
            if (
                not self._sections
                and not getattr(self, "_explicit_json_file", False)
                and Path(self.DEFAULT_JSON_FILE).exists()
                and self._file_path.resolve() != Path(self.DEFAULT_JSON_FILE).resolve()
            ):
                logger.warning(
                    "File locale %s non ha prodotto sezioni valide; provo a caricare il canonical globale %s",
                    self._file_path, Path(self.DEFAULT_JSON_FILE)
                )
                self._file_path = Path(self.DEFAULT_JSON_FILE)
                self._json_file = str(self._file_path)
                self.load_from_file()
        except Exception:
            logger.exception("Errore durante il tentativo di fallback al canonical globale")

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
            
            # Scrivi su file temporaneo preservando l'estensione originale
            tmp_path = Path(str(self._file_path) + ".tmp")
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
            if suffix not in ['.json', '.jsons', '.csv']:
                # Aggiungi .jsons di default (format canonical)
                dest_path = dest_path.with_suffix('.jsons')
                suffix = '.jsons'
                logger.info("Estensione mancante o non valida, uso .jsons: %s", dest_path)
            
            # Crea directory di destinazione se necessaria
            if dest_path.parent.exists() is False and str(dest_path.parent) != '.':
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug("Creata directory: %s", dest_path.parent)
            
            # Ottieni tutte le sezioni
            sections = self.get_all_sections()
            
            if suffix in ('.json', '.jsons'):
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


# ========================================================================
# 🔧 FUNZIONI HELPER PER GESTIONE JSON (API SEMPLIFICATA)
# ========================================================================
# Questi wrapper forniscono un'interfaccia semplice e chiara per
# caricare/salvare sezioni da/verso file JSON, senza dover istanziare
# direttamente il repository.
#
# Uso consigliato:
# - Per operazioni semplici e standalone (script, test, utility)
# - Quando non serve gestire eventi o mantenere stato in memoria
#
# Per l'applicazione principale, usa direttamente `SectionRepository`
# che offre caching, eventi, backup automatico e validazione.
# ========================================================================


def load_sections_from_json(json_file: str = DEFAULT_JSON_FILE) -> list[dict]:
    """
    Carica tutte le sezioni da un file JSON.
    
    Funzione di utilità che semplifica il caricamento delle sezioni
    quando non serve un'istanza persistente del repository.
    
    Args:
        json_file: Percorso del file JSON da leggere (default: "sections.json")
    
    Returns:
        Lista di dizionari rappresentanti le sezioni.
        Ogni dizionario contiene tutti i campi della sezione:
        - Campi geometrici (id, name, section_type, width, height, ecc.)
        - Proprietà calcolate (area, Ix, Iy, x_G, y_G, ecc.)
        - Note e metadati
    
    Gestione errori:
        - File non esistente → restituisce lista vuota
        - JSON malformato → logga l'errore e restituisce lista vuota
        - Sezioni con errori di validazione → vengono saltate
    
    Esempio d'uso:
        sections = load_sections_from_json("sections.json")
        for section_data in sections:
            print(f"{section_data['name']}: {section_data['area']} cm²")
    """
    try:
        repo = SectionRepository(json_file)
        sections_list = repo.get_all_sections()
        # Converte oggetti Section in dizionari
        return [section.to_dict() for section in sections_list]
    except Exception as e:
        logger.exception("Errore nel caricamento sezioni da %s: %s", json_file, e)
        return []


def save_sections_to_json(sections: list[dict], json_file: str = DEFAULT_JSON_FILE) -> None:
    """
    Salva una lista di sezioni in un file JSON.
    
    Funzione di utilità che semplifica il salvataggio quando non serve
    un'istanza persistente del repository.
    
    NOTA IMPORTANTE:
    Questa funzione SOVRASCRIVE completamente il file JSON esistente.
    Per aggiungere/modificare singole sezioni, usa `SectionRepository`.
    
    Args:
        sections: Lista di dizionari rappresentanti le sezioni.
                  Ogni dizionario deve contenere almeno:
                  - "name": nome della sezione
                  - "section_type": tipo (es. "RECTANGULAR", "T_SECTION", ecc.)
                  - campi geometrici specifici per il tipo
        json_file: Percorso del file JSON dove salvare (default: "sections.json")
    
    Gestione errori:
        - Sezioni non valide → vengono saltate con log warning
        - Errori di I/O → solleva IOError
        - Errori di validazione → solleva ValueError
    
    Strategia di salvataggio sicuro:
        1. Crea backup del file esistente
        2. Scrive su file temporaneo
        3. Rename atomico del file temporaneo sul file principale
    
    Esempio d'uso:
        sections = [
            {
                "name": "Sezione rettangolare 30x50",
                "section_type": "RECTANGULAR",
                "width": 30.0,
                "height": 50.0,
                "note": "Trave principale"
            }
        ]
        save_sections_to_json(sections, "sections.json")
    """
    try:
        # Crea repository e svuota l'archivio
        repo = SectionRepository(json_file)
        repo.clear()
        
        # Aggiunge tutte le sezioni dalla lista
        added_count = 0
        for section_data in sections:
            try:
                # Crea oggetto Section dal dizionario
                section = create_section_from_dict(section_data)
                # Calcola proprietà e valida
                section.compute_properties()
                # Preserva l'ID se presente nel dizionario originale
                if "id" in section_data and section_data["id"]:
                    section.id = section_data["id"]
                # Aggiunge al repository (che salva automaticamente)
                if repo.add_section(section):
                    added_count += 1
            except Exception as e:
                logger.warning(
                    "Sezione non valida saltata durante salvataggio: %s - Errore: %s",
                    section_data.get("name", "sconosciuta"),
                    e
                )
        
        logger.info("Salvate %d sezioni su %d in %s", added_count, len(sections), json_file)
        
    except Exception as e:
        logger.exception("Errore nel salvataggio sezioni in %s: %s", json_file, e)
        raise

