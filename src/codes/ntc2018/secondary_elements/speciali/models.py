from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class FamigliaSpeciale(str, Enum):
    INSEGNA_BANDIERA = "insegna_bandiera"
    CANCELLO_SCORREVOLE = "cancello_scorrevole"
    PANNELLO_SOSPESO = "pannello_sospeso"
    MENSOLA_LEGGERA = "mensola_leggera"
    CHIUSURA_TECNICA = "chiusura_tecnica"


@dataclass
class ComponenteSpecialeSpec:
    famiglia: FamigliaSpeciale
    massa_kg: float
    schema_statico: str
    esposizione_esterna: bool
    tipo_supporto: str
    grado_mobilita: str
    supporti_numero: int = 1

    def massa_totale_kg(self) -> float:
        return self.massa_kg


@dataclass
class ContestoSLUSpeciale:
    accelerazione_spettrale_g: float
    pressione_vento_kpa: float = 0.0
    gamma_i: float = 1.0


@dataclass
class ContestoSLESpeciale:
    spostamento_relativo_cm: float


@dataclass
class RisultatoSLUSpeciale:
    esito: bool
    domanda_totale_kg: float
    resistenza_supporto_kg: float
    interferenza_funzionale: bool
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_domanda_resistenza = (
            self.domanda_totale_kg / self.resistenza_supporto_kg
            if self.resistenza_supporto_kg > 0
            else float("inf")
        )


@dataclass
class RisultatoSLESpeciale:
    stato_danno: StatoDannoSLE
    spostamento_relativo_cm: float
    spostamento_ammissibile_cm: float
    danni_locali: bool
    intervento_necessario: bool
    note: str
    rapporto_spostamento: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_spostamento = (
            self.spostamento_relativo_cm / self.spostamento_ammissibile_cm
            if self.spostamento_ammissibile_cm > 0
            else float("inf")
        )


@dataclass
class RisultatoComponenteSpeciale:
    spec: ComponenteSpecialeSpec
    risultato_slu: RisultatoSLUSpeciale
    risultato_sle: RisultatoSLESpeciale
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {"famiglia": self.spec.famiglia.value, "massa_kg": self.spec.massa_kg},
            "slu": {"esito": self.risultato_slu.esito},
            "sle": {"stato_danno": self.risultato_sle.stato_danno.value},
            "passaggi": self.passaggi_calcolo,
        }
