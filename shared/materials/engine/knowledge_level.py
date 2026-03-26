"""
Knowledge Levels (Livelli di Conoscenza) e Confidence Factors (FC).

Implementa il sistema LC/FC per strutture esistenti secondo NTC2018 §C8.5.4.

Ogni livello di conoscenza comporta:
- Una riduzione sistematica delle resistenze (diviso FC)
- Una descrizione delle indagini necessarie
- Un fattore di confidenza specifico

Questo sistema si applica a verifiche di strutture esistenti (es. adeguamento sismico)
per tener conto dell'incertezza nei dati di ingresso.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class KnowledgeLevelType(str, Enum):
    """Livelli di conoscenza per strutture esistenti (NTC2018)."""

    LC1 = "LC1"  # Conoscenza limitata
    LC2 = "LC2"  # Conoscenza adeguata
    LC3 = "LC3"  # Conoscenza accurata


@dataclass
class KnowledgeLevel:
    """
    Rappresentazione di un livello di conoscenza con fattore di confidenza.

    Usato per strutture esistenti quando si hanno dubbi sui parametri meccanici
    dei materiali (resistenza, modulo elastico, etc.).
    """

    level: KnowledgeLevelType  # LC1, LC2, LC3
    fc: float  # Fattore di confidenza (1.35, 1.20, 1.00)
    description: str  # Descrizione breve
    required_inspections: list[str] = None  # ["rilievo geometrico", "indagini materiali", ...]

    def __post_init__(self):
        if self.required_inspections is None:
            self.required_inspections = []

    def apply_to_strength(self, f_m: float) -> float:
        """
        Applica il fattore di confidenza a una resistenza.

        La resistenza di progetto con LC/FC si ottiene:
            f_d = (f_m / FC) / γ_m

        Questo metodo applica solo il fattore FC, dividendo per il fattore.

        Args:
            f_m: Resistenza media [kg/cm²]

        Returns:
            Resistenza ridotta [kg/cm²]
        """
        return f_m / self.fc

    def to_dict(self) -> dict:
        """Serializza per salvataggio."""
        return {
            "level": self.level.value,
            "fc": self.fc,
            "description": self.description,
            "required_inspections": self.required_inspections,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeLevel":
        """Ricrea dal serializzato."""
        return cls(
            level=KnowledgeLevelType(data["level"]),
            fc=data["fc"],
            description=data["description"],
            required_inspections=data.get("required_inspections", []),
        )


class KnowledgeLevelFactory:
    """Factory per creare livelli di conoscenza standardizzati (NTC2018)."""

    @staticmethod
    def create_lc1() -> KnowledgeLevel:
        """LC1 - Conoscenza limitata."""
        return KnowledgeLevel(
            level=KnowledgeLevelType.LC1,
            fc=1.35,
            description="Conoscenza limitata: rilievo geometrico e catasto",
            required_inspections=[
                "Rilievo geometrico basilare",
                "Informazioni da catasto/cartografia",
                "Nessuna indagine materiali",
            ],
        )

    @staticmethod
    def create_lc2() -> KnowledgeLevel:
        """LC2 - Conoscenza adeguata."""
        return KnowledgeLevel(
            level=KnowledgeLevelType.LC2,
            fc=1.20,
            description="Conoscenza adeguata: rilievo + indagini non invasive",
            required_inspections=[
                "Rilievo geometrico dettagliato",
                "Indagini non invasive (sonic, Schmidt, ecc.)",
                "Prove di laboratorio su campioni",
                "Documentazione storica disponibile",
            ],
        )

    @staticmethod
    def create_lc3() -> KnowledgeLevel:
        """LC3 - Conoscenza accurata."""
        return KnowledgeLevel(
            level=KnowledgeLevelType.LC3,
            fc=1.00,
            description="Conoscenza accurata: rilievo completo + indagini invasive",
            required_inspections=[
                "Rilievo geometrico completo e preciso",
                "Indagini invasive (carotaggi, microscopiche, ecc.)",
                "Prove di laboratorio su campioni certificati",
                "Documentazione tecnica originale disponibile",
                "Verifiche di compatibilità strutturale",
            ],
        )

    @staticmethod
    def get_by_level(level: KnowledgeLevelType) -> KnowledgeLevel:
        """Recupera livello per tipo."""
        if level == KnowledgeLevelType.LC1:
            return KnowledgeLevelFactory.create_lc1()
        elif level == KnowledgeLevelType.LC2:
            return KnowledgeLevelFactory.create_lc2()
        elif level == KnowledgeLevelType.LC3:
            return KnowledgeLevelFactory.create_lc3()
        else:
            raise ValueError(f"Livello sconosciuto: {level}")

    @staticmethod
    def get_by_fc(fc: float) -> Optional[KnowledgeLevel]:
        """Recupera livello per fattore di confidenza."""
        if fc == 1.35:
            return KnowledgeLevelFactory.create_lc1()
        elif fc == 1.20:
            return KnowledgeLevelFactory.create_lc2()
        elif fc == 1.00:
            return KnowledgeLevelFactory.create_lc3()
        else:
            return None


__all__ = [
    "KnowledgeLevelType",
    "KnowledgeLevel",
    "KnowledgeLevelFactory",
]
