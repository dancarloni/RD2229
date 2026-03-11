from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..common import StatoDannoSLE


class SistemaTramezzo(str, Enum):
    CARTONGESSO_STANDARD = "cartongesso_standard"
    CARTONGESSO_DOPPIA_LASTRA = "cartongesso_doppia_lastra"
    LATERIZIO_FORATO = "laterizio_forato"
    SISTEMA_MISTO = "sistema_misto"


class VincoloSuperiore(str, Enum):
    RIGIDO = "rigido"
    SCORREVOLE = "scorrevole"
    ELASTICO = "elastico"


@dataclass
class TramezzoSpec:
    sistema: SistemaTramezzo
    altezza_cm: float
    lunghezza_cm: float
    spessore_cm: float
    peso_lineare_kg_m: float
    vincolo_superiore: VincoloSuperiore = VincoloSuperiore.RIGIDO
    guida_superiore_scorrimento: bool = False
    ancorato_lateralmente: bool = True
    drift_capacita_perc: float = 1.0
    area_aperture_cm2: float = 0.0
    numero_aperture: int = 0
    impianti_integrati: bool = False
    resistenza_fuori_piano_kg: float | None = None
    resistenza_ancoraggi_kg: float | None = None

    def area_lorda_cm2(self) -> float:
        return self.altezza_cm * self.lunghezza_cm

    def area_netta_cm2(self) -> float:
        return max(0.0, self.area_lorda_cm2() - self.area_aperture_cm2)

    def massa_totale_kg(self) -> float:
        return self.peso_lineare_kg_m * (self.lunghezza_cm / 100.0)


@dataclass
class ContestoSLUTramezzo:
    accelerazione_spettrale_g: float
    gamma_i: float = 1.0


@dataclass
class ContestoSLETramezzo:
    drift_calcolato_perc: float


@dataclass
class RisultatoSLUTramezzo:
    esito: bool
    domanda_fuori_piano_kg: float
    resistenza_fuori_piano_kg: float
    resistenza_ancoraggi_kg: float
    meccanismo_critico: str
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        resistenza = min(self.resistenza_fuori_piano_kg, self.resistenza_ancoraggi_kg)
        self.rapporto_domanda_resistenza = (
            self.domanda_fuori_piano_kg / resistenza if resistenza > 0 else float("inf")
        )


@dataclass
class RisultatoSLETramezzo:
    stato_danno: StatoDannoSLE
    drift_calcolato_perc: float
    drift_capacita_perc: float
    danno_ai_giunti: bool
    danno_al_pannello: bool
    intervento_necessario: bool
    note: str
    rapporto_drift: float = field(init=False)

    def __post_init__(self) -> None:
        self.rapporto_drift = (
            self.drift_calcolato_perc / self.drift_capacita_perc
            if self.drift_capacita_perc > 0
            else float("inf")
        )


@dataclass
class RisultatoTramezzo:
    spec: TramezzoSpec
    risultato_slu: RisultatoSLUTramezzo
    risultato_sle: RisultatoSLETramezzo
    passaggi_calcolo: list[str] = field(default_factory=list)

    def esito_complessivo(self) -> bool:
        return self.risultato_slu.esito and not self.risultato_sle.intervento_necessario

    def to_dict(self) -> dict:
        return {
            "element_type": "tramezzi",
            "sistema": self.spec.sistema.value,
            "slu": {
                "esito": self.risultato_slu.esito,
                "domanda_fuori_piano_kg": round(self.risultato_slu.domanda_fuori_piano_kg, 2),
                "resistenza_fuori_piano_kg": round(self.risultato_slu.resistenza_fuori_piano_kg, 2),
                "resistenza_ancoraggi_kg": round(self.risultato_slu.resistenza_ancoraggi_kg, 2),
                "rapporto": round(self.risultato_slu.rapporto_domanda_resistenza, 3),
                "meccanismo_critico": self.risultato_slu.meccanismo_critico,
            },
            "sle": {
                "stato_danno": self.risultato_sle.stato_danno.value,
                "drift_calcolato_perc": round(self.risultato_sle.drift_calcolato_perc, 3),
                "drift_capacita_perc": round(self.risultato_sle.drift_capacita_perc, 3),
                "rapporto_drift": round(self.risultato_sle.rapporto_drift, 3),
                "intervento_necessario": self.risultato_sle.intervento_necessario,
            },
            "passaggi": list(self.passaggi_calcolo),
        }
