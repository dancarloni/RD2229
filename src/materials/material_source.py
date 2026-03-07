"""
Modello strutturato delle fonti normative dei materiali (MaterialSource) per RD2229.
Definisce:
- MaterialSource: dataclass principale per la fonte normativa
- MetodoCalcolo: enum per il metodo di calcolo (TA, SL, SP, SPER)
- MaterialNormRef: dataclass per riferimenti puntuali a norma/articolo/tabella/parametro
Tutto in italiano, Unicode per simboli, serializzazione JSON nativa.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MetodoCalcolo(str, Enum):
    TA = "TA"  # Tensioni Ammissibili
    SL = "SL"  # Stati Limite
    SP = "SP"  # Sperimentale
    SPER = "SPER"  # Sperimentale/Prove


@dataclass
class MaterialSource:
    id: str
    name: str
    year: int
    calculation_method: MetodoCalcolo
    is_historical: bool
    reference: str
    description: str
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["calculation_method"] = self.calculation_method.value
        return d

    @staticmethod
    def from_dict(data: dict) -> "MaterialSource":
        return MaterialSource(
            id=data["id"],
            name=data["name"],
            year=int(data.get("year") or 0),
            calculation_method=MetodoCalcolo(data["calculation_method"]),
            is_historical=bool(data["is_historical"]),
            reference=data["reference"],
            description=data["description"],
            notes=data.get("notes", ""),
        )


@dataclass
class MaterialNormRef:
    norma_id: str
    articolo: str
    tabella: Optional[str] = None
    formula: Optional[str] = None
    parametro: Optional[str] = None
    descrizione_it: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "MaterialNormRef":
        return MaterialNormRef(
            norma_id=data["norma_id"],
            articolo=data["articolo"],
            tabella=data.get("tabella"),
            formula=data.get("formula"),
            parametro=data.get("parametro"),
            descrizione_it=data.get("descrizione_it", ""),
        )
