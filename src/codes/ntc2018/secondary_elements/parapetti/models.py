from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class TipoParapetto(str, Enum):
    CONTINUO_MURATURA = "continuo_muratura"
    CONTINUO_ACCIAIO = "continuo_acciaio"
    MONTANTI_ACCIAIO = "montanti_acciaio"
    VETRATO = "vetrato"
    MISTO_ACCIAIO_VETRO = "misto_acciaio_vetro"
    RECINZIONE_METALLICA = "recinzione_metallica"


class TipoAncoraggio(str, Enum):
    BASE_CONTINUA = "base_continua"
    TASSELLI_PUNTUALI = "tasselli_puntuali"
    CHIMICO = "chimico"
    CORDOLO_INTEGRATO = "cordolo_integrato"


@dataclass
class ParapettoSpec:
    tipo: TipoParapetto
    altezza_cm: float
    lunghezza_cm: float
    massa_lineare_kg_m: float
    tipo_ancoraggio: TipoAncoraggio
    resistenza_ancoraggio_kn: float | None = None
    interasse_montanti_cm: float | None = None
    spessore_parete_cm: float | None = None
    numero_montanti: int | None = None
    area_aperture_cm2: float = 0.0
    comportamento_fragile: bool = False
    vincoli_laterali: bool = True

    def area_lorda_cm2(self) -> float:
        return self.altezza_cm * self.lunghezza_cm

    def area_netta_cm2(self) -> float:
        return max(0.0, self.area_lorda_cm2() - self.area_aperture_cm2)

    def massa_totale_kg(self) -> float:
        return self.massa_lineare_kg_m * (self.lunghezza_cm / 100.0)


@dataclass
class ContestoSLUParapetto:
    accelerazione_spettrale_g: float
    carico_orizzontale_servizio_kg: float
    gamma_i: float = 1.0


@dataclass
class ContestoSLEParapetto:
    spostamento_bordo_cm: float


@dataclass
class RisultatoSLUParapetto:
    esito: bool
    domanda_sismica_kg: float
    domanda_servizio_kg: float
    domanda_combinata_kg: float
    resistenza_ancoraggio_kg: float
    meccanismo_critico: str
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_domanda_resistenza = (
            self.domanda_combinata_kg / self.resistenza_ancoraggio_kg
            if self.resistenza_ancoraggio_kg > 0
            else float("inf")
        )


@dataclass
class RisultatoSLEParapetto:
    stato_danno: StatoDannoSLE
    spostamento_bordo_cm: float
    spostamento_ammissibile_cm: float
    danno_ai_giunti: bool
    integrita_pannelli: bool
    intervento_necessario: bool
    note: str
    rapporto_spostamento: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_spostamento = (
            self.spostamento_bordo_cm / self.spostamento_ammissibile_cm
            if self.spostamento_ammissibile_cm > 0
            else float("inf")
        )


@dataclass
class RisultatoParapetto:
    spec: ParapettoSpec
    risultato_slu: RisultatoSLUParapetto
    risultato_sle: RisultatoSLEParapetto
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {
                "tipo": self.spec.tipo.value,
                "altezza_cm": self.spec.altezza_cm,
                "lunghezza_cm": self.spec.lunghezza_cm,
                "massa_lineare_kg_m": self.spec.massa_lineare_kg_m,
                "tipo_ancoraggio": self.spec.tipo_ancoraggio.value,
            },
            "slu": {
                "esito": self.risultato_slu.esito,
                "domanda_sismica_kg": self.risultato_slu.domanda_sismica_kg,
                "domanda_servizio_kg": self.risultato_slu.domanda_servizio_kg,
                "domanda_combinata_kg": self.risultato_slu.domanda_combinata_kg,
                "resistenza_ancoraggio_kg": self.risultato_slu.resistenza_ancoraggio_kg,
                "rapporto": round(self.risultato_slu.rapporto_domanda_resistenza, 4),
                "meccanismo_critico": self.risultato_slu.meccanismo_critico,
            },
            "sle": {
                "stato_danno": self.risultato_sle.stato_danno.value,
                "spostamento_bordo_cm": self.risultato_sle.spostamento_bordo_cm,
                "spostamento_ammissibile_cm": self.risultato_sle.spostamento_ammissibile_cm,
                "rapporto": round(self.risultato_sle.rapporto_spostamento, 4),
                "danno_ai_giunti": self.risultato_sle.danno_ai_giunti,
                "integrita_pannelli": self.risultato_sle.integrita_pannelli,
                "intervento_necessario": self.risultato_sle.intervento_necessario,
            },
            "passaggi_calcolo": self.passaggi_calcolo,
        }
