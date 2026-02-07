from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Importa EventBus con try/except per evitare circular imports
try:
    from sections_app.services.event_bus import (
        MATERIALS_ADDED,
        MATERIALS_CLEARED,
        MATERIALS_DELETED,
        MATERIALS_UPDATED,
        EventBus,
    )

    HAS_EVENT_BUS = True
except ImportError:
    HAS_EVENT_BUS = False


@dataclass
class Material:
    name: str
    type: str  # e.g., 'concrete', 'steel'
    code: str = (
        ""  # ✅ NUOVO: codice del materiale (es. "C100", "A500") - permette ricerca per codice
    )
    properties: Dict[str, float] = field(default_factory=dict)
    # FRC (Fiber Reinforced Composite) optional parameters
    frc_enabled: bool = False
    frc_fFts: Optional[float] = None  # tensile strength (design) of fibers
    frc_fFtu: Optional[float] = None  # ultimate tensile strength of fibers
    frc_eps_fu: Optional[float] = None  # ultimate strain of fibers
    frc_note: Optional[str] = None  # free-text note or source
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict:
        """Converte il Material a dizionario per JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "code": self.code,  # ✅ Persisti codice nel JSON
            "properties": self.properties,
            # FRC fields (optional)
            "frc_enabled": self.frc_enabled,
            "frc_fFts": self.frc_fFts,
            "frc_fFtu": self.frc_fFtu,
            "frc_eps_fu": self.frc_eps_fu,
            "frc_note": self.frc_note,
        }

    @staticmethod
    def from_dict(data: Dict) -> Material:
        """Crea un Material da un dizionario JSON."""
        return Material(
            id=data.get("id", str(uuid4())),
            name=data.get("name", ""),
            type=data.get("type", ""),
            code=data.get("code", ""),  # ✅ Carica codice da JSON
            properties=data.get("properties", {}),
            frc_enabled=data.get("frc_enabled", False),
            frc_fFts=data.get("frc_fFts"),
            frc_fFtu=data.get("frc_fFtu"),
            frc_eps_fu=data.get("frc_eps_fu"),
            frc_note=data.get("frc_note"),
        )


# Historical materials module is provided in `historical_materials.py` as a
# single authoritative source
try:
    from historical_materials import HistoricalMaterial as _HistoricalMaterial_external
    from historical_materials import (
        HistoricalMaterialLibrary as _HistoricalMaterialLibrary_external,
    )

    HistoricalMaterial = _HistoricalMaterial_external
    HistoricalMaterialLibrary = _HistoricalMaterialLibrary_external
except Exception:
    # Fallback definitions (should not normally be used)
    @dataclass
    class _HistoricalMaterial:
        code: str
        name: str
        fck: Optional[float] = None
        fcd: Optional[float] = None
        fyk: Optional[float] = None
        fyd: Optional[float] = None
        Ec: Optional[float] = None
        Es: Optional[float] = None
        gamma_c: Optional[float] = None
        gamma_s: Optional[float] = None
        source: Optional[str] = None
        notes: Optional[str] = None

        def to_dict(self) -> Dict:
            return {
                "code": self.code,
                "name": self.name,
                "fck": self.fck,
                "fcd": self.fcd,
                "fyk": self.fyk,
                "fyd": self.fyd,
                "Ec": self.Ec,
                "Es": self.Es,
                "gamma_c": self.gamma_c,
                "gamma_s": self.gamma_s,
                "source": self.source,
                "notes": self.notes,
            }

        @staticmethod
        def from_dict(d: Dict) -> "_HistoricalMaterial":
            return _HistoricalMaterial(
                code=d.get("code", ""),
                name=d.get("name", ""),
                fck=d.get("fck"),
                fcd=d.get("fcd"),
                fyk=d.get("fyk"),
                fyd=d.get("fyd"),
                Ec=d.get("Ec"),
                Es=d.get("Es"),
                gamma_c=d.get("gamma_c"),
                gamma_s=d.get("gamma_s"),
                source=d.get("source"),
                notes=d.get("notes"),
            )

    class _HistoricalMaterialLibrary:
        def __init__(self, path: str | Path | None = None):
            self._file_path = Path(path or "historical_materials.json")
            self._materials: List[_HistoricalMaterial] = []

        def load_from_file(self) -> None:
            self._materials.clear()
            if not self._file_path.exists():
                return
            try:
                with self._file_path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                if not isinstance(raw, list):
                    logger.warning(
                        "Historical materials file %s does not contain a list", self._file_path
                    )
                    return
                for idx, item in enumerate(raw):
                    try:
                        self._materials.append(_HistoricalMaterial.from_dict(item))
                    except Exception:
                        logger.exception("Error parsing historical material %s", idx)
            except Exception:
                logger.exception("Error loading historical materials from %s", self._file_path)

        def save_to_file(self) -> None:
            try:
                if self._file_path.parent.exists() is False and str(self._file_path.parent) != ".":
                    self._file_path.parent.mkdir(parents=True, exist_ok=True)
                tmp = self._file_path.with_suffix(self._file_path.suffix + ".tmp")
                with tmp.open("w", encoding="utf-8") as f:
                    json.dump(
                        [m.to_dict() for m in self._materials], f, indent=2, ensure_ascii=False
                    )
                tmp.replace(self._file_path)
            except Exception:
                logger.exception("Error saving historical materials to %s", self._file_path)

        def get_all(self) -> List[_HistoricalMaterial]:
            return list(self._materials)

        def add(self, material: "_HistoricalMaterial") -> None:
            existing = self.find_by_code(material.code)
            if existing:
                self._materials = [m for m in self._materials if m.code != material.code]
            self._materials.append(material)
            self.save_to_file()

        def find_by_code(self, code: str) -> Optional["_HistoricalMaterial"]:
            for m in self._materials:
                if m.code == code:
                    return m
            return None


# Expose canonical names for runtime compatibility (use fallback only if needed)
try:
    HistoricalMaterial
except NameError:
    HistoricalMaterial = _HistoricalMaterial  # type: ignore

try:
    HistoricalMaterialLibrary
except NameError:
    HistoricalMaterialLibrary = _HistoricalMaterialLibrary  # type: ignore


class MaterialRepository:
    """Archivio in memoria dei materiali con persistenza JSON."""

    DEFAULT_JSON_FILE = "materials.json"

    def __init__(self, json_file: str = DEFAULT_JSON_FILE) -> None:
        self._materials: Dict[str, Material] = {}
        self._json_file = json_file
        # Flag per repository in-memory (es. json_file=":memory:") usato nei test
        self._in_memory = json_file == ":memory:"

        # Percorsi per backup
        self._file_path = Path(json_file)
        self._backup_path = self._file_path.with_name(
            f"{self._file_path.stem}_backup{self._file_path.suffix}"
        )

        # Carica i materiali dal file JSON se esiste (se non siamo in-memory)
        if not self._in_memory:
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

    def import_historical_material(self, hist: "HistoricalMaterial") -> Material:
        """Crea un oggetto Material a partire da un HistoricalMaterial senza
        aggiungerlo automaticamente all'archivio.

        ✅ Mantiene il `code` dalla fonte storica per permettere ricerca
        per codice.
        """
        props: Dict[str, float] = {}
        keys = [
            "fck",
            "fcd",
            "fyk",
            "fyd",
            "Ec",
            "Es",
            "gamma_c",
            "gamma_s",
        ]
        for key in keys:
            val = getattr(hist, key, None)
            if val is not None:
                props[key] = val
        mat_type = (
            "concrete"
            if getattr(hist, "fck", None) is not None
            else ("steel" if getattr(hist, "fyk", None) is not None else "historical")
        )
        # ✅ Preserva il code dalla fonte storica
        mat = Material(
            name=hist.name,
            type=mat_type,
            code=getattr(hist, "code", ""),  # ✅ Usa code da HistoricalMaterial
            properties=props,
        )
        return mat

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
            EventBus().emit(
                MATERIALS_UPDATED, material_id=material_id, material_name=updated_material.name
            )

    def delete(self, material_id: str) -> None:
        """Elimina un materiale dal repository."""
        material = self._materials.pop(material_id, None)
        if material:
            logger.debug("Materiale eliminato: %s (%s)", material_id, material.name)

            # Salva in file JSON
            self.save_to_file()

            # Emetti evento se disponibile
            if HAS_EVENT_BUS:
                EventBus().emit(
                    MATERIALS_DELETED, material_id=material_id, material_name=material.name
                )

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
        # Se il repository è in-memory (test special case), non facciamo I/O
        if getattr(self, "_in_memory", False):
            self._materials.clear()
            return
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
        except Exception:
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
                    logger.debug(
                        "Materiale caricato da backup: %s (%s)", material.id, material.name
                    )
                except Exception as e:
                    logger.exception("Errore caricamento materiale %d dal backup: %s", idx, e)

            logger.warning(
                "Caricati %d materiali dal backup %s (file principale danneggiato)",
                len(self._materials),
                self._backup_path,
            )
            return
        except Exception:
            logger.exception("Errore anche nel caricamento del backup %s", self._backup_path)

        # 3) Se tutto fallisce, archivio vuoto
        logger.warning(
            "Impossibile caricare archivio materiali da %s né da %s: inizializzo archivio vuoto",
            self._file_path,
            self._backup_path,
        )
        self._materials.clear()

    def save_to_file(self) -> None:
        """Salva tutti i materiali in un file JSON con backup automatico.

        Strategia di sicurezza:
        1. Se il file principale esiste, crea backup (materials_backup.json)
        2. Scrive su file temporaneo (.json.tmp)
        3. Rename atomico del file temporaneo sul file principale
        """
        # Se repository in-memory (es. json_file=":memory:"), non facciamo I/O
        if getattr(self, "_in_memory", False):
            return
        try:
            data = []
            for material in self._materials.values():
                material_dict = material.to_dict()
                data.append(material_dict)

            # Crea la directory se non esiste
            if self._file_path.parent.exists() is False and str(self._file_path.parent) != ".":
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
                logger.debug(
                    "Salvati %d materiali in %s (backup: %s)",
                    len(data),
                    self._file_path,
                    self._backup_path,
                )
            except Exception:
                logger.exception("Errore nel salvataggio del file materiali")
                # Elimina file temporaneo se esiste
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
                raise
        except Exception as e:
            logger.exception("Errore salvataggio file JSON %s: %s", self._json_file, e)

    def export_backup(self, destination: Path | str) -> None:
        """Esporta l'archivio materiali nel percorso indicato.
        Non modifica il file principale né il backup interno.
        Se destination ha estensione .json, salva JSON.

        Args:
            destination: Percorso del file di destinazione (Path o str).
                        Se l'estensione è .json → salva in formato JSON
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
            if suffix != ".json":
                # Aggiungi .json di default
                dest_path = dest_path.with_suffix(".json")
                suffix = ".json"
                logger.info("Estensione mancante o non valida, uso .json: %s", dest_path)

            # Crea directory di destinazione se necessaria
            if dest_path.parent.exists() is False and str(dest_path.parent) != ".":
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug("Creata directory: %s", dest_path.parent)

            # Ottieni tutti i materiali
            materials = self.get_all()

            # Esporta in JSON
            data = [material.to_dict() for material in materials]
            with dest_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Esportati %d materiali in JSON: %s", len(materials), dest_path)

        except (OSError, IOError) as e:
            logger.exception(
                "Errore I/O durante esportazione backup materiali in %s: %s", destination, e
            )
            raise IOError(f"Impossibile esportare backup materiali in {destination}: {e}") from e
        except Exception as e:
            logger.exception(
                "Errore durante esportazione backup materiali in %s: %s", destination, e
            )
            raise ValueError(f"Errore esportazione backup materiali: {e}") from e
