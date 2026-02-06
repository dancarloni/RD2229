from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from enum import Enum
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
    """Materiale storico con doppia notazione (moderna e RD 2229/39).

    MAPPING NOTAZIONI:
    ==================
    CALCESTRUZZO:
        Moderna     | Storica (RD 2229/39)  | Descrizione
        ------------|----------------------|---------------------------
        fck         | σ_c,28 (sigma_c28)   | Resistenza cubica a 28 gg
        fcd         | σ_c (sigma_c)        | Tensione ammissibile
        Ec          | E_c                  | Modulo elastico
        -           | τ_c0 (tau_c0)        | Taglio di servizio
        -           | τ_c1 (tau_c1)        | Taglio massimo
        -           | n                    | Coeff. omogeneizzazione (Es/Ec)

    ACCIAIO:
        Moderna     | Storica (RD 2229/39)  | Descrizione
        ------------|----------------------|---------------------------
        fyk         | σ_sn (sigma_sn)      | Tensione di snervamento
        fyd         | σ_s (sigma_s)        | Tensione ammissibile
        Es          | E_s                  | Modulo elastico (2.100.000 kg/cm²)

    COEFFICIENTI DI SICUREZZA (metodo TA):
        - γ_c = 1 (verifiche alle tensioni ammissibili)
        - γ_s = 1 (verifiche alle tensioni ammissibili)
        NB: gamma_c e gamma_s nel dataclass rappresentano il rapporto
        resistenza/tensione_ammissibile (circa 3 per cls, 2 per acciaio)

    Tutte le unità in kg/cm² (storico).
    """

    id: str
    name: str  # es. "CLS R 160 (RD 2229/39)"
    code: str  # es. "RD2229_R160"
    source: str  # es. "RD 2229/39", "ReLUIS STIL", ecc.
    type: HistoricalMaterialType

    # ============================================================
    # CALCESTRUZZO - Proprietà meccaniche [kg/cm²]
    # ============================================================
    # Notazione moderna | Alias storico RD 2229/39
    fck: Optional[float] = None  # resistenza caratteristica = σ_c,28 (cubica 28 gg)
    fcd: Optional[float] = None  # resistenza di calcolo = σ_c (tensione ammissibile)
    fctm: Optional[float] = None  # trazione media [kg/cm²]
    Ec: Optional[float] = None  # modulo elastico cls = E_c [kg/cm²]

    # Campi specifici RD 2229/39 per calcestruzzo
    tau_c0: Optional[float] = None  # τ_c0: taglio di servizio [kg/cm²]
    tau_c1: Optional[float] = None  # τ_c1: taglio massimo [kg/cm²]
    n: Optional[float] = None  # coefficiente di omogeneizzazione (Es/Ec)

    # ============================================================
    # ACCIAIO - Proprietà meccaniche [kg/cm²]
    # ============================================================
    # Notazione moderna | Alias storico RD 2229/39
    fyk: Optional[float] = None  # snervamento = σ_sn (tensione di snervamento)
    fyd: Optional[float] = None  # resistenza di calcolo = σ_s (tensione ammissibile)
    Es: Optional[float] = None  # modulo acciaio = E_s [kg/cm²]

    # ============================================================
    # Coefficienti di sicurezza (rapporto resistenza/ammissibile)
    # ============================================================
    gamma_c: Optional[float] = None  # cls: tipicamente ≈ 3 (fck/fcd)
    gamma_s: Optional[float] = None  # acciaio: tipicamente = 2 (fyk/fyd)

    notes: str = ""

    # ============================================================
    # ALIAS PROPERTY - Notazione storica RD 2229/39
    # ============================================================

    # --- Calcestruzzo ---
    @property
    def sigma_c28(self) -> Optional[float]:
        """σ_c,28: Resistenza cubica a rottura a 28 giorni [kg/cm²] (alias di fck)."""
        return self.fck

    @property
    def sigma_c(self) -> Optional[float]:
        """σ_c: Tensione ammissibile del calcestruzzo [kg/cm²] (alias di fcd)."""
        return self.fcd

    @property
    def tau_service(self) -> Optional[float]:
        """τ_c0: Tensione tangenziale di servizio [kg/cm²] (alias di tau_c0)."""
        return self.tau_c0

    @property
    def tau_max(self) -> Optional[float]:
        """τ_c1: Tensione tangenziale massima [kg/cm²] (alias di tau_c1)."""
        return self.tau_c1

    # --- Acciaio ---
    @property
    def sigma_sn(self) -> Optional[float]:
        """σ_sn: Tensione di snervamento acciaio [kg/cm²] (alias di fyk)."""
        return self.fyk

    @property
    def sigma_s(self) -> Optional[float]:
        """σ_s: Tensione ammissibile dell'acciaio [kg/cm²] (alias di fyd)."""
        return self.fyd

    def to_dict(self) -> dict:
        """Serializza il materiale in dizionario per JSON.

        Include sia i campi con notazione moderna che gli alias storici
        per facilitare l'interoperabilità.
        """
        d = asdict(self)
        d["type"] = self.type.value if isinstance(self.type, HistoricalMaterialType) else self.type
        # Aggiungi alias storici per retrocompatibilità e chiarezza
        d["sigma_c28"] = self.sigma_c28  # alias fck
        d["sigma_c"] = self.sigma_c  # alias fcd
        d["sigma_sn"] = self.sigma_sn  # alias fyk
        d["sigma_s"] = self.sigma_s  # alias fyd
        return d

    @staticmethod
    def from_dict(d: dict) -> "HistoricalMaterial":
        """Deserializza da dizionario, accettando sia notazione moderna che storica."""
        # Supporta sia notazione moderna (fck, fcd) che storica (sigma_c28, sigma_c)
        fck = d.get("fck") or d.get("sigma_c28")
        fcd = d.get("fcd") or d.get("sigma_c")
        fyk = d.get("fyk") or d.get("sigma_sn")
        fyd = d.get("fyd") or d.get("sigma_s")

        return HistoricalMaterial(
            id=d.get("id", str(uuid4())),
            name=d.get("name", ""),
            code=d.get("code", ""),
            source=d.get("source", ""),
            type=HistoricalMaterialType(d.get("type", HistoricalMaterialType.OTHER)),
            fck=fck,
            fcd=fcd,
            fctm=d.get("fctm"),
            Ec=d.get("Ec"),
            tau_c0=d.get("tau_c0") or d.get("tau_service"),
            tau_c1=d.get("tau_c1") or d.get("tau_max"),
            n=d.get("n"),
            fyk=fyk,
            fyd=fyd,
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
        # Load materials from file to populate internal list (if file exists)
        # This ensures that if a historical_materials.json is present it will be
        # read into self._materials for immediate use by search functions.
        try:
            self.load_from_file()
        except Exception:
            # If loading fails, _ensure_default_materials will have created defaults
            # and save_to_file will have written them; ignore errors here.
            pass

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
                logger.warning(
                    "Existing historical materials file %s unreadable: will recreate defaults",
                    self._file_path,
                )

        # Materiali base secondo RD 2229/39 (Regio Decreto 16 novembre 1939)
        # Valori tratti direttamente dalla normativa storica
        # Unità: tutte le tensioni in kg/cm²
        examples: List[HistoricalMaterial] = []

        # ============================================================
        # CALCESTRUZZI - RD 2229/39
        # ============================================================

        # CLS con cemento normale (Portland, alto forno, pozzolanico)
        # Resistenza minima 120 kg/cm², σ_c ammissibile 35-40 kg/cm²
        examples.append(
            HistoricalMaterial(
                id="RD2229_CLS_120_N",
                code="RD2229_CLS_120_N",
                name="CLS R120 Cemento Normale",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=120.0,  # σ_c,28: resistenza cubica minima a 28 gg [kg/cm²]
                fcd=35.0,  # σ_c: tensione ammissibile sez. sempl. compresse [kg/cm²]
                fctm=None,  # non specificato nel RD
                Ec=250000.0,  # E_c: modulo elastico convenzionale [kg/cm²]
                tau_c0=4.0,  # τ_c0: taglio di servizio [kg/cm²]
                tau_c1=14.0,  # τ_c1: taglio massimo [kg/cm²]
                n=10.0,  # coefficiente di omogeneizzazione Es/Ec
                gamma_c=3.0,  # rapporto σ_c28/σ_c ≈ 3
                notes="Cemento Portland normale (idraulico, alto forno, pozzolanico)",
            )
        )

        # CLS con cemento normale R 160
        examples.append(
            HistoricalMaterial(
                id="RD2229_CLS_160_N",
                code="RD2229_CLS_160_N",
                name="CLS R160 Cemento Normale",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=160.0,  # σ_c,28: resistenza cubica a 28 gg [kg/cm²]
                fcd=35.0,  # σ_c: tensione ammissibile sez. sempl. compresse [kg/cm²]
                fctm=None,
                Ec=250000.0,  # E_c: modulo elastico convenzionale [kg/cm²]
                tau_c0=4.0,  # τ_c0: taglio di servizio [kg/cm²]
                tau_c1=14.0,  # τ_c1: taglio massimo [kg/cm²]
                n=10.0,  # coefficiente di omogeneizzazione Es/Ec
                gamma_c=3.0,
                notes="Cemento Portland normale R160. Richiesto per acciaio dolce σ_s=1400 kg/cm²",
            )
        )

        # CLS con cemento ad alta resistenza R 160
        examples.append(
            HistoricalMaterial(
                id="RD2229_CLS_160_AR",
                code="RD2229_CLS_160_AR",
                name="CLS R160 Cemento Alta Resistenza",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=160.0,  # σ_c,28: resistenza cubica minima a 28 gg [kg/cm²]
                fcd=45.0,  # σ_c: tensione ammissibile sez. sempl. compresse [kg/cm²]
                fctm=None,
                Ec=300000.0,  # E_c: modulo elastico convenzionale [kg/cm²]
                tau_c0=6.0,  # τ_c0: taglio di servizio [kg/cm²]
                tau_c1=16.0,  # τ_c1: taglio massimo [kg/cm²]
                n=8.0,  # coefficiente di omogeneizzazione Es/Ec
                gamma_c=3.0,
                notes=(
                    "Cemento ad alta resistenza. "
                    "Richiesto per acciaio semiduro σ_s=1600-1800 kg/cm²"
                ),
            )
        )

        # CLS con cemento ad alta resistenza R 225
        examples.append(
            HistoricalMaterial(
                id="RD2229_CLS_225_AR",
                code="RD2229_CLS_225_AR",
                name="CLS R225 Cemento Alta Resistenza",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=225.0,  # σ_c,28: resistenza cubica a 28 gg [kg/cm²]
                fcd=50.0,  # σ_c: tensione ammissibile sez. inflesse [kg/cm²]
                fctm=None,
                Ec=300000.0,  # E_c: modulo elastico convenzionale [kg/cm²]
                tau_c0=6.0,  # τ_c0: taglio di servizio [kg/cm²]
                tau_c1=16.0,  # τ_c1: taglio massimo [kg/cm²]
                n=8.0,  # coefficiente di omogeneizzazione Es/Ec
                gamma_c=3.0,
                notes="Cemento ad alta resistenza R225. Richiesto per acciaio duro σ_s=2000 kg/cm²",
            )
        )

        # CLS con cemento alluminoso R 160
        examples.append(
            HistoricalMaterial(
                id="RD2229_CLS_160_AL",
                code="RD2229_CLS_160_AL",
                name="CLS R160 Cemento Alluminoso",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=160.0,  # σ_c,28: resistenza cubica minima a 28 gg [kg/cm²]
                fcd=45.0,  # σ_c: tensione ammissibile sez. sempl. compresse [kg/cm²]
                fctm=None,
                Ec=330000.0,  # E_c: modulo elastico convenzionale [kg/cm²]
                tau_c0=6.0,  # τ_c0: taglio di servizio [kg/cm²]
                tau_c1=16.0,  # τ_c1: taglio massimo [kg/cm²]
                n=6.0,  # coefficiente di omogeneizzazione Es/Ec
                gamma_c=3.0,
                notes="Cemento alluminoso. Rapida presa e alta resistenza iniziale",
            )
        )

        # CLS con cemento a lenta presa R 120
        examples.append(
            HistoricalMaterial(
                id="RD2229_CLS_120_LP",
                code="RD2229_CLS_120_LP",
                name="CLS R120 Cemento Lenta Presa",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.CONCRETE,
                fck=120.0,  # σ_c,28: resistenza cubica minima a 28 gg [kg/cm²]
                fcd=35.0,  # σ_c: tensione ammissibile [kg/cm²]
                fctm=None,
                Ec=200000.0,  # E_c: modulo elastico convenzionale [kg/cm²]
                tau_c0=6.0,  # τ_c0: taglio di servizio [kg/cm²]
                tau_c1=16.0,  # τ_c1: taglio massimo [kg/cm²]
                n=10.0,  # coefficiente di omogeneizzazione Es/Ec
                gamma_c=3.0,
                notes="Cemento a lenta presa. Modulo ridotto E_c=200000 kg/cm²",
            )
        )

        # ============================================================
        # ACCIAI DA ARMATURA - RD 2229/39
        # ============================================================

        # Acciaio dolce
        examples.append(
            HistoricalMaterial(
                id="RD2229_ACC_DOLCE",
                code="RD2229_ACC_DOLCE",
                name="Acciaio Dolce",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.STEEL,
                fyk=2800.0,  # σ_sn: tensione di snervamento [kg/cm²]
                fyd=1400.0,  # σ_s: tensione ammissibile a trazione [kg/cm²]
                Es=2100000.0,  # E_s: modulo elastico acciaio [kg/cm²]
                gamma_s=2.0,  # rapporto σ_sn/σ_s = 2
                notes="Acciaio dolce liscio. Richiede CLS con σ_c,28≥160 kg/cm². "
                "σ_s ≤ σ_sn/2 (non deve superare metà carico snervamento)",
            )
        )

        # Acciaio semiduro
        examples.append(
            HistoricalMaterial(
                id="RD2229_ACC_SEMIDURO",
                code="RD2229_ACC_SEMIDURO",
                name="Acciaio Semiduro",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.STEEL,
                fyk=3600.0,  # σ_sn: tensione di snervamento tipica [kg/cm²]
                fyd=1800.0,  # σ_s: tensione ammissibile (sez. rettangolari) [kg/cm²]
                Es=2100000.0,  # E_s: modulo elastico acciaio [kg/cm²]
                gamma_s=2.0,  # rapporto σ_sn/σ_s = 2
                notes="Acciaio semiduro. Richiede CLS alta resistenza σ_c,28≥160 kg/cm². "
                "σ_s = 1600 kg/cm² (sez. T) o 1800 kg/cm² (sez. rett.)",
            )
        )

        # Acciaio duro
        examples.append(
            HistoricalMaterial(
                id="RD2229_ACC_DURO",
                code="RD2229_ACC_DURO",
                name="Acciaio Duro",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.STEEL,
                fyk=4000.0,  # σ_sn: tensione di snervamento tipica [kg/cm²]
                fyd=2000.0,  # σ_s: tensione ammissibile massima [kg/cm²]
                Es=2100000.0,  # E_s: modulo elastico acciaio [kg/cm²]
                gamma_s=2.0,  # rapporto σ_sn/σ_s = 2
                notes="Acciaio duro. Richiede CLS alta resistenza σ_c,28≥225 kg/cm². "
                "σ_s = 1800 kg/cm² (sez. T) o 2000 kg/cm² (sez. rett.)",
            )
        )

        # ============================================================
        # ACCIAI PER STAFFE - RD 2229/39
        # ============================================================

        # Acciaio dolce per staffe (stesso dell'armatura longitudinale)
        examples.append(
            HistoricalMaterial(
                id="RD2229_STAFFA_DOLCE",
                code="RD2229_STAFFA_DOLCE",
                name="Acciaio Dolce per Staffe",
                source="RD 16/11/1939 n. 2229",
                type=HistoricalMaterialType.STIRRUP_STEEL,
                fyk=2800.0,  # σ_sn: tensione di snervamento [kg/cm²]
                fyd=1400.0,  # σ_s: tensione ammissibile [kg/cm²]
                Es=2100000.0,  # E_s: modulo elastico acciaio [kg/cm²]
                gamma_s=2.0,  # rapporto σ_sn/σ_s = 2
                notes="Acciaio dolce per staffe e legature. Tondo liscio φ6-φ10 tipici",
            )
        )

        # Install examples only if currently empty
        if not self._materials:
            self._materials.extend(examples)
            try:
                self.save_to_file()
                logger.info(
                    "Populated historical materials with default examples: %s", self._file_path
                )
            except Exception:
                logger.exception(
                    "Failed to save default historical materials to %s", self._file_path
                )

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
                logger.warning(
                    "Historical materials file %s does not contain a list", self._file_path
                )
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
            if self._file_path.parent.exists() is False and str(self._file_path.parent) != ".":
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
                            mtype = (
                                HistoricalMaterialType(type_raw)
                                if type_raw
                                else HistoricalMaterialType.OTHER
                            )
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
                                logger.warning(
                                    "CSV row %s: invalid numeric for %s: %r", idx, field, v
                                )
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
