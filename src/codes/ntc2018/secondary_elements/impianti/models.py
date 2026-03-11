from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class CategoriaImpianto(str, Enum):
    TUBAZIONE_SOSPESA = "tubazione_sospesa"
    CANALE_ARIA = "canale_aria"
    APPARECCHIATURA = "apparecchiatura"
    QUADRO_ELETTRICO = "quadro_elettrico"
    SISTEMA_SPRINKLER = "sistema_sprinkler"


class TipoSupporto(str, Enum):
    SOSPENSIONE = "sospensione"
    APPOGGIO = "appoggio"
    STAFFAGGIO = "staffaggio"
    INCOLLAGGIO = "incollaggio"


@dataclass
class ImpiantoSpec:
    categoria: CategoriaImpianto
    massa_kg: float
    quota_cm: float
    tipo_supporto: TipoSupporto
    numero_ancoraggi: int
    presenza_giunto_flessibile: bool
    classe_funzione: str | None = None
    resistenza_supporto_kn: float | None = None
    lunghezza_percorso_m: float = 1.0

    def massa_totale_kg(self) -> float:
        return self.massa_kg

    def domanda_per_ancoraggio_kg(self) -> float:
        if self.numero_ancoraggi <= 0:
            return 0.0
        return self.massa_kg / self.numero_ancoraggi


@dataclass
class ContestoSLUImpianto:
    accelerazione_spettrale_g: float
    gamma_i: float = 1.0


@dataclass
class ContestoSLEImpianto:
    spostamento_relativo_cm: float


@dataclass
class RisultatoSLUImpianto:
    esito: bool
    domanda_totale_kg: float
    resistenza_supporti_kg: float
    capacita_continuita_funzionale: bool
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_domanda_resistenza = (
            self.domanda_totale_kg / self.resistenza_supporti_kg
            if self.resistenza_supporti_kg > 0
            else float("inf")
        )


@dataclass
class RisultatoSLEImpianto:
    stato_danno: StatoDannoSLE
    spostamento_relativo_cm: float
    spostamento_ammissibile_cm: float
    collisione_rischio: bool
    perdita_funzionalita: bool
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
class RisultatoImpianto:
    spec: ImpiantoSpec
    risultato_slu: RisultatoSLUImpianto
    risultato_sle: RisultatoSLEImpianto
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec": {
                "categoria": self.spec.categoria.value,
                "massa_kg": self.spec.massa_kg,
                "quota_cm": self.spec.quota_cm,
                "numero_ancoraggi": self.spec.numero_ancoraggi,
            },
            "slu": {
                "esito": self.risultato_slu.esito,
                "domanda_totale_kg": self.risultato_slu.domanda_totale_kg,
                "resistenza_supporti_kg": self.risultato_slu.resistenza_supporti_kg,
                "rapporto": round(self.risultato_slu.rapporto_domanda_resistenza, 4),
            },
            "sle": {
                "stato_danno": self.risultato_sle.stato_danno.value,
                "spostamento_relativo_cm": self.risultato_sle.spostamento_relativo_cm,
                "rapporto": round(self.risultato_sle.rapporto_spostamento, 4),
            },
            "passaggi_calcolo": self.passaggi_calcolo,
        }
