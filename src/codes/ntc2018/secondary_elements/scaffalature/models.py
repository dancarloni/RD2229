from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class TipoScaffalatura(str, Enum):
    HEAVY_DUTY = "heavy_duty"
    LIGHT_DUTY = "light_duty"
    ARMADIO_TECNICO = "armadio_tecnico"
    ARCHIVIO = "archivio"


@dataclass
class ScaffalaturaSpec:
    tipo: TipoScaffalatura
    altezza_cm: float
    larghezza_cm: float
    profondita_cm: float
    massa_vuota_kg: float
    massa_contenuto_kg: float
    ancorata: bool
    tipo_ancoraggio: str | None = None

    def massa_totale_kg(self) -> float:
        return self.massa_vuota_kg + self.massa_contenuto_kg

    def baricentro_relativo(self) -> float:
        total = self.massa_totale_kg()
        if total == 0:
            return 0.5
        return self.altezza_cm / 2.0


@dataclass
class ContestoSLUScaffalatura:
    accelerazione_spettrale_g: float
    gamma_i: float = 1.0


@dataclass
class ContestoSLEScaffalatura:
    spostamento_relativo_cm: float


@dataclass
class RisultatoSLUScaffalatura:
    esito: bool
    domanda_sismica_kg: float
    capacita_ribaltamento_kg: float
    capacita_ancoraggi_kg: float
    meccanismo_critico: str
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        resistenza = (
            min(self.capacita_ribaltamento_kg, self.capacita_ancoraggi_kg)
            if self.capacita_ancoraggi_kg > 0
            else self.capacita_ribaltamento_kg
        )
        self.rapporto_domanda_resistenza = (
            self.domanda_sismica_kg / resistenza if resistenza > 0 else float("inf")
        )


@dataclass
class RisultatoSLEScaffalatura:
    stato_danno: StatoDannoSLE
    spostamento_relativo_cm: float
    spostamento_ammissibile_cm: float
    perdita_contenuto: bool
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
class RisultatoScaffalatura:
    spec: ScaffalaturaSpec
    risultato_slu: RisultatoSLUScaffalatura
    risultato_sle: RisultatoSLEScaffalatura
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {"tipo": self.spec.tipo.value},
            "slu": {"esito": self.risultato_slu.esito},
            "sle": {"stato_danno": self.risultato_sle.stato_danno.value},
            "passaggi": self.passaggi_calcolo,
        }
