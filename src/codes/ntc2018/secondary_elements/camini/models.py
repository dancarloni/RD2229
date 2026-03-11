from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class TipoCamino(str, Enum):
    MURATURA = "muratura"
    ACCIAIO = "acciaio"
    PREFABBRICATO = "prefabbricato"
    COMPOSITO = "composito"


@dataclass
class CaminoSpec:
    tipo: TipoCamino
    altezza_cm: float
    massa_totale_kg: float
    vincolo_base: str
    controventato: bool
    rigidezza_equivalente_kg_cm: float | None = None

    def periodo_proprio_s(self) -> float:
        if not self.rigidezza_equivalente_kg_cm or self.rigidezza_equivalente_kg_cm == 0:
            return 0.3 * (self.altezza_cm / 100.0) ** 0.5
        g_cm_s2 = 981.0
        return (
            2.0
            * 3.14159
            * ((self.massa_totale_kg / self.rigidezza_equivalente_kg_cm) / g_cm_s2) ** 0.5
        )


@dataclass
class ContestoSLUCamino:
    accelerazione_spettrale_g: float
    gamma_i: float = 1.0


@dataclass
class ContestoSLECamino:
    spostamento_sommitale_cm: float


@dataclass
class RisultatoSLUCamino:
    esito: bool
    domanda_sismica_kg: float
    resistenza_base_kg: float
    capacita_stabilita: bool
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_domanda_resistenza = (
            self.domanda_sismica_kg / self.resistenza_base_kg
            if self.resistenza_base_kg > 0
            else float("inf")
        )


@dataclass
class RisultatoSLECamino:
    stato_danno: StatoDannoSLE
    spostamento_sommitale_cm: float
    spostamento_ammissibile_cm: float
    danno_risonanza: bool
    intervento_necessario: bool
    note: str
    rapporto_spostamento: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_spostamento = (
            self.spostamento_sommitale_cm / self.spostamento_ammissibile_cm
            if self.spostamento_ammissibile_cm > 0
            else float("inf")
        )


@dataclass
class RisultatoCamino:
    spec: CaminoSpec
    risultato_slu: RisultatoSLUCamino
    risultato_sle: RisultatoSLECamino
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {"tipo": self.spec.tipo.value, "altezza_cm": self.spec.altezza_cm},
            "slu": {"esito": self.risultato_slu.esito},
            "sle": {"stato_danno": self.risultato_sle.stato_danno.value},
            "passaggi": self.passaggi_calcolo,
        }
