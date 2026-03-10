"""Modelli dati geotecnici per la Fase P.

Il modulo e' pensato per crescita progressiva: ogni sotto-dominio
(fondazioni superficiali, cedimenti, pali, muri, liquefazione)
puo' estendere questi contratti senza rompere le API esistenti.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .utils import kg_cm2_to_kpa, kpa_to_kg_cm2


class UnitaTensione(str, Enum):
    """Unita di tensione supportate per input/output geotecnico."""

    KG_CM2 = "kg/cm2"
    KPA = "kPa"


class NormaGeotecnica(str, Enum):
    """Codici normativi geotecnici gestiti dal package."""

    NTC2018 = "NTC2018"
    EC7 = "EC7"
    DM_1988 = "DM_11_03_1988"


class ApproccioSLU(str, Enum):
    """Approccio di progetto SLU geotecnico."""

    DA1 = "DA1"


class CombinazioneDA1(str, Enum):
    """Combinazioni previste da DA1."""

    SET1 = "SET1"
    SET2 = "SET2"


class CorrelazioneSPTCPT(str, Enum):
    """Correlazioni disponibili per stima geotecnica da prove in sito."""

    MEYERHOF = "MEYERHOF"
    ROBERTSON_CAMPANELLA = "ROBERTSON_CAMPANELLA"


@dataclass(slots=True)
class ParametriTerreno:
    """Parametri di base del terreno.

    Le tensioni vengono memorizzate nell'unita indicata da
    ``unita_tensione`` e convertite su richiesta.
    """

    gamma_kg_m3: float
    phi_gradi: float
    coesione: float = 0.0
    modulo_elastico: float = 0.0
    coeff_poisson: float = 0.30
    c_u: float = 0.0
    indice_vuoti_e0: float = 0.8
    indice_compressione_cc: float = 0.2
    unita_tensione: UnitaTensione = UnitaTensione.KG_CM2

    def __post_init__(self) -> None:
        if self.gamma_kg_m3 <= 0:
            raise ValueError("gamma_kg_m3 deve essere > 0")
        if not (0.0 <= self.phi_gradi < 90.0):
            raise ValueError("phi_gradi deve essere compreso tra 0 e 90")
        if not (0.0 <= self.coeff_poisson < 0.5):
            raise ValueError("coeff_poisson deve essere compreso tra 0 e 0.5")

    @property
    def coesione_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.coesione)
        return self.coesione

    @property
    def modulo_elastico_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.modulo_elastico)
        return self.modulo_elastico

    @property
    def c_u_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.c_u)
        return self.c_u


@dataclass(slots=True)
class GeometriaFondazione:
    """Geometria fondazione superficiale (in cm)."""

    larghezza_b_cm: float
    lunghezza_l_cm: float
    profondita_piano_posa_cm: float
    eccentricita_b_cm: float = 0.0
    eccentricita_l_cm: float = 0.0

    def __post_init__(self) -> None:
        if self.larghezza_b_cm <= 0 or self.lunghezza_l_cm <= 0:
            raise ValueError("Le dimensioni B e L devono essere > 0")
        if self.profondita_piano_posa_cm < 0:
            raise ValueError("La profondita di posa deve essere >= 0")


@dataclass(slots=True)
class CaricoFondazione:
    """Carichi di progetto agenti sulla fondazione."""

    n_verticale_kg: float
    h_orizzontale_kg: float = 0.0


@dataclass(slots=True)
class InputPortanzaFondazione:
    """Input principale per verifica di portanza fondazioni superficiali."""

    terreno: ParametriTerreno
    geometria: GeometriaFondazione
    carico: CaricoFondazione
    pressione_agente: float
    unita_pressione_agente: UnitaTensione = UnitaTensione.KG_CM2
    norma: NormaGeotecnica = NormaGeotecnica.NTC2018
    approccio_slu: ApproccioSLU = ApproccioSLU.DA1
    combinazioni_da1: tuple[CombinazioneDA1, ...] = (
        CombinazioneDA1.SET1,
        CombinazioneDA1.SET2,
    )
    correlazione_default: CorrelazioneSPTCPT = CorrelazioneSPTCPT.ROBERTSON_CAMPANELLA

    @property
    def pressione_agente_kg_cm2(self) -> float:
        if self.unita_pressione_agente == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.pressione_agente)
        return self.pressione_agente


@dataclass(slots=True)
class InputCedimenti:
    """Input per valutazione cedimenti P.2."""

    pressione_media: float
    larghezza_fondazione_cm: float
    modulo_elastico_terreno: float
    coeff_poisson: float
    fattore_influenza_i_rho: float = 1.0
    spessore_strato_consolidante_cm: float = 0.0
    indice_compressione_cc: float = 0.0
    indice_vuoti_e0: float = 0.0
    sigma_eff_iniziale: float = 0.0
    sigma_eff_finale: float = 0.0
    unita_tensione: UnitaTensione = UnitaTensione.KG_CM2

    def __post_init__(self) -> None:
        if self.larghezza_fondazione_cm <= 0:
            raise ValueError("larghezza_fondazione_cm deve essere > 0")
        if self.modulo_elastico_terreno <= 0:
            raise ValueError("modulo_elastico_terreno deve essere > 0")
        if not (0.0 <= self.coeff_poisson < 0.5):
            raise ValueError("coeff_poisson deve essere compreso tra 0 e 0.5")

    def pressione_media_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.pressione_media)
        return self.pressione_media

    def modulo_elastico_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.modulo_elastico_terreno)
        return self.modulo_elastico_terreno

    def sigma_eff_iniziale_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.sigma_eff_iniziale)
        return self.sigma_eff_iniziale

    def sigma_eff_finale_kg_cm2(self) -> float:
        if self.unita_tensione == UnitaTensione.KPA:
            return kpa_to_kg_cm2(self.sigma_eff_finale)
        return self.sigma_eff_finale


@dataclass(slots=True)
class RisultatoVerificaSLU:
    """Esito verifica SLU singola combinazione."""

    combinazione: CombinazioneDA1
    q_ed_kg_cm2: float
    q_rd_kg_cm2: float
    rapporto_utilizzo: float
    verificato: bool
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, float | str | bool | list[str]]:
        return {
            "combinazione": self.combinazione.value,
            "q_ed_kg_cm2": self.q_ed_kg_cm2,
            "q_rd_kg_cm2": self.q_rd_kg_cm2,
            "rapporto_utilizzo": self.rapporto_utilizzo,
            "verificato": self.verificato,
            "passaggi_calcolo": self.passaggi_calcolo,
        }


@dataclass(slots=True)
class RisultatoPortanzaFondazione:
    """Output completo della verifica di portanza."""

    risultati_slu: list[RisultatoVerificaSLU]
    combinazione_governante: CombinazioneDA1
    verificato_globale: bool
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "risultati_slu": [r.to_dict() for r in self.risultati_slu],
            "combinazione_governante": self.combinazione_governante.value,
            "verificato_globale": self.verificato_globale,
            "passaggi_calcolo": self.passaggi_calcolo,
        }


@dataclass(slots=True)
class RisultatoCedimenti:
    """Output valutazione cedimenti P.2."""

    cedimento_immediato_cm: float
    cedimento_consolidazione_cm: float
    cedimento_totale_cm: float
    passaggi_calcolo: list[str] = field(default_factory=list)

    @property
    def cedimento_totale_mm(self) -> float:
        return self.cedimento_totale_cm * 10.0

    def to_dict(self) -> dict[str, float | list[str]]:
        return {
            "cedimento_immediato_cm": self.cedimento_immediato_cm,
            "cedimento_consolidazione_cm": self.cedimento_consolidazione_cm,
            "cedimento_totale_cm": self.cedimento_totale_cm,
            "cedimento_totale_mm": self.cedimento_totale_mm,
            "passaggi_calcolo": self.passaggi_calcolo,
        }


def tensione_to_kpa(valore_kg_cm2: float) -> float:
    """Helper di utilita per report/UI geotecnica."""

    return kg_cm2_to_kpa(valore_kg_cm2)
