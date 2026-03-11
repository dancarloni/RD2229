from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class TipoControsoffitto(str, Enum):
    MODULARE_GESSO = "modulare_gesso"
    LASTRA_CONTINUA = "lastra_continua"
    TECNICO_APERTO = "tecnico_aperto"
    SISTEMA_MISTO = "sistema_misto"


@dataclass
class ControsoffittoSpec:
    tipo: TipoControsoffitto
    area_m2: float
    massa_superficiale_kg_m2: float
    passo_pendini_cm: float
    presenza_controventi: bool
    gioco_perimetrale_mm: float
    numero_pendini: int | None = None
    lunghezza_controventi_m: float | None = None

    def massa_totale_kg(self) -> float:
        return self.area_m2 * self.massa_superficiale_kg_m2

    def domanda_per_pendino_kg(self) -> float:
        if not self.numero_pendini or self.numero_pendini == 0:
            return 0.0
        return self.massa_totale_kg() / self.numero_pendini


@dataclass
class ContestoSLUControsoffitto:
    accelerazione_spettrale_g: float
    gamma_i: float = 1.0


@dataclass
class ContestoSLEControsoffitto:
    drift_calcolato_perc: float


@dataclass
class RisultatoSLUControsoffitto:
    esito: bool
    domanda_totale_kg: float
    resistenza_pendini_kg: float
    resistenza_controventi_kg: float
    capacita_gioco_perimetrale: bool
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        resistenza = (
            min(self.resistenza_pendini_kg, self.resistenza_controventi_kg)
            if self.resistenza_controventi_kg > 0
            else self.resistenza_pendini_kg
        )
        self.rapporto_domanda_resistenza = (
            self.domanda_totale_kg / resistenza if resistenza > 0 else float("inf")
        )


@dataclass
class RisultatoSLEControsoffitto:
    stato_danno: StatoDannoSLE
    drift_calcolato_perc: float
    drift_ammissibile_perc: float
    perdita_appoggio_rischio: bool
    danno_bordo: bool
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
class RisultatoControsoffitto:
    spec: ControsoffittoSpec
    risultato_slu: RisultatoSLUControsoffitto
    risultato_sle: RisultatoSLEControsoffitto
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {
                "tipo": self.spec.tipo.value,
                "area_m2": self.spec.area_m2,
                "massa_superficiale_kg_m2": self.spec.massa_superficiale_kg_m2,
                "passo_pendini_cm": self.spec.passo_pendini_cm,
                "presenza_controventi": self.spec.presenza_controventi,
            },
            "slu": {
                "esito": self.risultato_slu.esito,
                "domanda_totale_kg": self.risultato_slu.domanda_totale_kg,
                "resistenza_pendini_kg": self.risultato_slu.resistenza_pendini_kg,
                "rapporto": round(self.risultato_slu.rapporto_domanda_resistenza, 4),
            },
            "sle": {
                "stato_danno": self.risultato_sle.stato_danno.value,
                "drift_calcolato_perc": self.risultato_sle.drift_calcolato_perc,
                "rapporto": round(self.risultato_sle.rapporto_drift, 4),
            },
            "passaggi_calcolo": self.passaggi_calcolo,
        }
