from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class SistemaFacciata(str, Enum):
    CURTAIN_WALL = "curtain_wall"
    VENTILATA = "ventilata"
    PANNELLO_PREFABBRICATO = "pannello_prefabbricato"
    RIVESTIMENTO_PESANTE = "rivestimento_pesante"


@dataclass
class FacciataSpec:
    sistema: SistemaFacciata
    modulo_luce_cm: float
    massa_superficiale_kg_m2: float
    tipo_sottostruttura: str
    tipo_ancoraggio: str
    area_m2: float = 50.0
    drift_capacita_perc: float | None = None

    def massa_totale_kg(self) -> float:
        return self.area_m2 * self.massa_superficiale_kg_m2


@dataclass
class ContestoSLUFacciata:
    accelerazione_spettrale_g: float
    pressione_vento_kpa: float = 0.0
    gamma_i: float = 1.0


@dataclass
class ContestoSLEFacciata:
    drift_calcolato_perc: float


@dataclass
class RisultatoSLUFacciata:
    esito: bool
    domanda_sismica_kg: float
    domanda_vento_kg: float
    domanda_combinata_kg: float
    resistenza_ancoraggi_kg: float
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_domanda_resistenza = (
            self.domanda_combinata_kg / self.resistenza_ancoraggi_kg
            if self.resistenza_ancoraggi_kg > 0
            else float("inf")
        )


@dataclass
class RisultatoSLEFacciata:
    stato_danno: StatoDannoSLE
    drift_calcolato_perc: float
    drift_ammissibile_perc: float
    danno_ai_giunti: bool
    rischio_martellamento: bool
    intervento_necessario: bool
    note: str
    rapporto_drift: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_drift = (
            self.drift_calcolato_perc / self.drift_ammissibile_perc
            if self.drift_ammissibile_perc > 0
            else float("inf")
        )


@dataclass
class RisultatoFacciata:
    spec: FacciataSpec
    risultato_slu: RisultatoSLUFacciata
    risultato_sle: RisultatoSLEFacciata
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {"sistema": self.spec.sistema.value, "area_m2": self.spec.area_m2},
            "slu": {
                "esito": self.risultato_slu.esito,
                "rapporto": round(self.risultato_slu.rapporto_domanda_resistenza, 4),
            },
            "sle": {
                "stato_danno": self.risultato_sle.stato_danno.value,
                "rapporto": round(self.risultato_sle.rapporto_drift, 4),
            },
            "passaggi": self.passaggi_calcolo,
        }
