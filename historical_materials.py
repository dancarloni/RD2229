from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class HistoricalMaterialType(str, Enum):
    CONCRETE = "concrete"
    STEEL = "steel"
    STIRRUP_STEEL = "stirrup_steel"
    OTHER = "other"


@dataclass
class HistoricalMaterial:
    id: str
    name: str                # es. "CLS R 160 (RD 2229/39)"
    code: str                # es. "RD2229_R160"
    source: str              # es. "RD 2229/39", "ReLUIS STIL", ecc.
    type: HistoricalMaterialType

    # Proprietà meccaniche principali (unità coerenti: kg/cm², ecc.)
    fck: Optional[float] = None      # resistenza caratteristica a compressione [kg/cm²]
    fcd: Optional[float] = None      # resistenza di calcolo compressione [kg/cm²]
    fctm: Optional[float] = None     # trazione media [kg/cm²]
    Ec: Optional[float] = None       # modulo cls [kg/cm²]

    fyk: Optional[float] = None      # snervamento acciaio [kg/cm²]
    fyd: Optional[float] = None      # resistenza di calcolo acciaio [kg/cm²]
    Es: Optional[float] = None       # modulo acciaio [kg/cm²]

    gamma_c: Optional[float] = None
    gamma_s: Optional[float] = None

    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value if isinstance(self.type, HistoricalMaterialType) else self.type
        return d

    @staticmethod
    def from_dict(d: dict) -> "HistoricalMaterial":
        return HistoricalMaterial(
            id=d.get("id", str(uuid4())),
            name=d.get("name", ""),
            code=d.get("code", ""),
            source=d.get("source", ""),
            type=HistoricalMaterialType(d.get("type", HistoricalMaterialType.OTHER)),
            fck=d.get("fck"),
            fcd=d.get("fcd"),
            fctm=d.get("fctm"),
            Ec=d.get("Ec"),
            fyk=d.get("fyk"),
            fyd=d.get("fyd"),
            Es=d.get("Es"),
            gamma_c=d.get("gamma_c"),
            gamma_s=d.get("gamma_s"),
            notes=d.get("notes", ""),
        )


class HistoricalMaterialLibrary:
    """Archivio storico di materiali salvato in JSON.

    Implementazione semplice con load/save e gestione sicura dei file.
    """

    def __init__(self, path: str | Path | None = None):
        self._file_path = Path(path or "historical_materials.json")
        self._materials: List[HistoricalMaterial] = []
        # Ensure a sensible default set of historical materials exists on first use
        # (populated with example values and TODO notes for the user to replace with
        # authoritative values from RD 2229/39 or external datasets like ReLUIS/STIL)
        self._ensure_default_materials()

    def _ensure_default_materials(self) -> None:
        """
        Populate the library with a small set of example historical materials
        if the JSON file does not exist or is empty. The numeric values are
        illustrative; a developer or user should replace them with exact values
        from RD 2229/39 or other historical datasets.
        """
        # If a file exists and contains data, do nothing
        if self._file_path.exists():
            try:
                with self._file_path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, list) and raw:
                    return
            except Exception:
                # If the file exists but is not readable/valid JSON, we'll overwrite it
                logger.warning("Existing historical materials file %s unreadable: will recreate defaults", self._file_path)

        # Prepare default illustrative materials
        examples: List[HistoricalMaterial] = []

        # Example concrete from RD 2229/39 (values are placeholders - TODO)
        examples.append(
            HistoricalMaterial(
                id="RD2229_R160",
                code="RD2229_R160",
                name="CLS R 160 (RD 2229/39)",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=16.0,  # TODO: insert exact fck from RD 2229/39 table
                fcd=10.0,  # TODO: compute/insert fcd (design value)
                fctm=1.0,  # TODO: traction mean example
                Ec=300000.0,  # TODO: replace with authoritative value
                gamma_c=1.4,  # typical safety factor example
                notes="TODO: Inserire valori esatti da RD 2229/39 (pdf)"
            )
        )

        # Example steel (historic)
        examples.append(
            HistoricalMaterial(
                id="HIST_STEEL_FEB38",
                code="HIST_STEEL_FEB38",
                name="Acciaio FeB38 storico",
                source="Norme storiche / ReLUIS",
                type=HistoricalMaterialType.STEEL,
                fyk=380.0,  # placeholder
                fyd=300.0,  # placeholder design value
                Es=2100000.0,  # example modulus (kg/cm²)
                gamma_s=1.15,  # example safety factor
                notes="TODO: calibrare su dataset storico (es. ReLUIS, STIL)"
            )
        )

        # Example from an online archive (placeholder)
        examples.append(
            HistoricalMaterial(
                id="RELUIS_EXAMPLE_1",
                code="RELUIS_C_EX1",
                name="CLS ReLUIS Example",
                source="ReLUIS STIL",
                type=HistoricalMaterialType.CONCRETE,
                fck=20.0,
                fcd=13.0,
                Ec=320000.0,
                gamma_c=1.4,
                notes="Example entry from ReLUIS export - TODO: replace with actual dataset values"
            )
        )

        # Install examples only if currently empty
        if not self._materials:
            self._materials.extend(examples)
            try:
                self.save_to_file()
                logger.info("Populated historical materials with default examples: %s", self._file_path)
            except Exception:
                logger.exception("Failed to save default historical materials to %s", self._file_path)
    def load_from_file(self) -> None:
        self._materials.clear()
        if not self._file_path.exists():
            # Ensure defaults and save
            self._ensure_default_materials()
            return
        try:
            with self._file_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, list):
                logger.warning("Historical materials file %s does not contain a list", self._file_path)
                # Replace with defaults
                self._ensure_default_materials()
                return
            if not raw:
                # Empty list -> populate defaults
                self._ensure_default_materials()
                return
            for idx, item in enumerate(raw):
                try:
                    self._materials.append(HistoricalMaterial.from_dict(item))
                except Exception:
                    logger.exception("Error parsing historical material %s", idx)
        except Exception:
            logger.exception("Error loading historical materials from %s", self._file_path)
            # Attempt to recreate defaults if loading fails
            self._ensure_default_materials()

    def save_to_file(self) -> None:
        try:
            if self._file_path.parent.exists() is False and str(self._file_path.parent) != '.':
                self._file_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._file_path.with_suffix(self._file_path.suffix + ".tmp")
            with tmp.open("w", encoding="utf-8") as f:
                json.dump([m.to_dict() for m in self._materials], f, indent=2, ensure_ascii=False)
            tmp.replace(self._file_path)
        except Exception:
            logger.exception("Error saving historical materials to %s", self._file_path)

    def get_all(self) -> List[HistoricalMaterial]:
        return list(self._materials)

    def add(self, material: HistoricalMaterial) -> None:
        # replace existing with same code
        existing = self.find_by_code(material.code)
        if existing:
            self._materials = [m for m in self._materials if m.code != material.code]
        self._materials.append(material)
        self.save_to_file()

    def find_by_code(self, code: str) -> Optional[HistoricalMaterial]:
        for m in self._materials:
            if m.code == code:
                return m
        return None

    def import_from_csv(self, file_path: str | Path, delimiter: str = ";") -> int:
        """
        Importa materiali storici da un CSV.
        - Ogni riga -> un HistoricalMaterial.
        - Se esiste già un materiale con stesso 'code', aggiornalo.
        - Altrimenti aggiungilo.
        Ritorna il numero di materiali importati/aggiornati.
        """
        import csv

        fp = Path(file_path)
        if not fp.exists():
            logger.warning("CSV file for import not found: %s", fp)
            return 0

        added_or_updated = 0
        try:
            with fp.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                # Expected headers (case-insensitive)
                for idx, row in enumerate(reader, start=2):
                    if not row or all((v or "").strip() == "" for v in row.values()):
                        logger.debug("Skipping empty CSV row %s", idx)
                        continue
                    try:
                        code = (row.get("code") or row.get("Code") or "").strip()
                        if not code:
                            logger.warning("Skipping CSV row %s: missing code", idx)
                            continue
                        name = (row.get("name") or row.get("Name") or "").strip()
                        source = (row.get("source") or row.get("Source") or "").strip()

                        # Basic validation: require both code and name
                        if not name:
                            logger.warning("Skipping CSV row %s: missing name", idx)
                            continue

                        type_raw = (row.get("type") or row.get("Type") or "").strip().lower()
                        try:
                            mtype = HistoricalMaterialType(type_raw) if type_raw else HistoricalMaterialType.OTHER
                        except Exception:
                            # tolerant mapping
                            if "concr" in type_raw or "cls" in type_raw:
                                mtype = HistoricalMaterialType.CONCRETE
                            elif "steel" in type_raw or "acc" in type_raw:
                                mtype = HistoricalMaterialType.STEEL
                            else:
                                mtype = HistoricalMaterialType.OTHER

                        def _num(field: str):
                            v = (row.get(field) or "").strip()
                            if v == "":
                                return None
                            try:
                                return float(v.replace(",", "."))
                            except Exception:
                                logger.warning("CSV row %s: invalid numeric for %s: %r", idx, field, v)
                                return None

                        hist = HistoricalMaterial(
                            id=code,
                            code=code,
                            name=name,
                            source=source,
                            type=mtype,
                            fck=_num("fck"),
                            fcd=_num("fcd"),
                            fctm=_num("fctm"),
                            Ec=_num("Ec"),
                            fyk=_num("fyk"),
                            fyd=_num("fyd"),
                            Es=_num("Es"),
                            gamma_c=_num("gamma_c"),
                            gamma_s=_num("gamma_s"),
                            notes=(row.get("notes") or row.get("Notes") or "").strip(),
                        )

                        existing = self.find_by_code(code)
                        if existing:
                            # update fields
                            self._materials = [m for m in self._materials if m.code != code]
                            self._materials.append(hist)
                        else:
                            self._materials.append(hist)
                        added_or_updated += 1
                    except Exception:
                        logger.exception("Error processing CSV row %s", idx)
                        continue
            # Save changes
            self.save_to_file()
            logger.debug("Imported %d historical materials from %s", added_or_updated, fp)
            return added_or_updated
        except Exception:
            logger.exception("Failed to import historical materials from CSV %s", fp)
            return added_or_updated
