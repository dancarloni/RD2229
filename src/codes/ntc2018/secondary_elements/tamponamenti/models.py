"""
Modelli dati per tamponamenti secondari (Fase S1).

NTC2018 §7.2.3 — Criteri di verifica per elementi e componenti non strutturali.
Completamento 2026-03-11, sessione Copilot (utente: DanieleCarloni).

Supporta:
- Vincoli multipli (incastro, cerniera, appoggio, controventi elastici)
- Ancoraggi dettagliati (vite, tassello, saldatura) con curve SLU/SLE
- Stato danno 4-livelli (assente, locale, diffuso, insicurezza)
- Compatibilità deformativa con drift interpiano
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoVincolo(Enum):
    """Tipi di vincolo per tamponamento."""

    INCASTRO = "incastro_perfetto"
    CERNIERA_ORIZZONTALE = "cerniera_orizzontale"
    APPOGGIO_LIBERO = "appoggio_libero"
    CONTROVENTO_ELASTICO = "controvento_elastico_laterale"


class TipoAncoraggio(Enum):
    """Tipi di ancoraggio e fissaggio."""

    VITE_METALLO = "vite_metallo_filettata"
    TASSELLO_CHIMICO = "tassello_chimico_resina"
    TASSELLO_MECCANICO = "tassello_meccanico_espansione"
    SALDATURA = "saldatura_a_cordone"


class StatoDannoSLE(Enum):
    """Scala stati di danno per SLE — NTC2018 §C7.2 (riferimento)."""

    ASSENTE = "assente"  # Drift < 50% capacità
    LOCALE = "locale"  # 50% < drift < 75% capacità; danno localizzato ai giunti
    DIFFUSO = "diffuso"  # 75% < drift < 100% capacità; danno generalizzato
    INSICUREZZA = "insicurezza"  # Drift >= 100%; richiede intervento strutturale


@dataclass
class SpecAncoraggio:
    """Specifica di un fissaggio (vite, tassello, saldatura)."""

    tipo: TipoAncoraggio
    diametro_mm: float  # ∅ in mm
    materiale: str  # es. "acciaio C45", "resina epossidica", "saldatura d'angolo"
    resistenza_trazione_mpa: float  # f_t,k
    resistenza_taglio_mpa: float  # f_v,k
    numero_fissaggi: int  # Per filare di ancoraggio
    interasse_mm: Optional[float] = None  # Distanza tra è fissaggi consecutivi
    profondita_ancoraggio_mm: Optional[float] = None  # Per tasselli meccanici/chimici
    spessore_acciaio_mm: Optional[float] = None  # Per saldature


@dataclass
class TamponamentoSpec:
    """
    Specifica completa di un tamponamento secondo NTC2018 §7.2.3.

    Parametri geometrici:
    - altezza, larghezza, spessore, massa superficiale

    Parametri di vincolo:
    - vincolo superiore, inferiore (multipli)
    - controventi laterali (elastici)

    Parametri di ancoraggio:
    - lista dettagliata di fissaggi (vite, tassello, saldatura)

    Parametri di deformabilità:
    - drift_capacita_perc: % di drift massimo ammissibile (default 1.5%)
    """

    # Geometria
    altezza_cm: float
    larghezza_cm: float
    spessore_cm: float
    massa_superficiale_kg_m2: float

    # Tipologia e materiale
    tipologia: str  # es. "muratura tradizionale", "cls prefabbricato", "laterizio"
    resistenza_compressione_mpa: Optional[float] = None  # Per verifiche interne
    resistenza_taglio_mpa: Optional[float] = None

    # Vincoli
    vincolo_superiore: TipoVincolo = TipoVincolo.INCASTRO
    vincolo_inferiore: TipoVincolo = TipoVincolo.INCASTRO
    controvento_laterale: bool = False  # Presente/assente
    rigidezza_controvento_elastico_kg_cm: Optional[float] = None  # k per molla laterale

    # Ancoraggi (lista di fissaggi)
    ancoraggi: list[SpecAncoraggio] = field(default_factory=list)

    # Deformabilità
    drift_capacita_perc: float = 1.5  # % di h, default 1.5% (NTC2018)

    # Apertule e forometria
    area_aperture_cm2: float = 0.0
    numero_aperture: int = 0

    # Q&A decisione 2026-03-11: memorizzare decisioni architetturali
    note_decisionali: str = ""

    def drift_capacita_cm(self) -> float:
        """Capacità deformativa in cm."""
        return self.altezza_cm * self.drift_capacita_perc / 100.0

    def area_lorda_cm2(self) -> float:
        """Area lorda pannello."""
        return self.altezza_cm * self.larghezza_cm

    def area_netta_cm2(self) -> float:
        """Area netta (area lorda - aperture)."""
        return self.area_lorda_cm2() - self.area_aperture_cm2

    def massa_totale_kg(self) -> float:
        """Massa totale pannello."""
        return self.massa_superficiale_kg_m2 * self.area_lorda_cm2() / 10000.0

    def numero_ancoraggi_totali(self) -> int:
        """Numero totale di fissaggi."""
        return sum(a.numero_fissaggi for a in self.ancoraggi)


@dataclass
class RisultatoSLU:
    """Risultato della verifica SLU (stato limite ultimo)."""

    esito: bool  # True = verificato, False = non verificato
    domanda_fuori_piano_kg: float
    resistenza_pannello_kg: float
    resistenza_ancoraggi_kg: float
    rapporto_domanda_resistenza: float = field(init=False)
    margine_sicurezza_perc: float = field(init=False)
    meccanismo_critico: str = ""  # es. "ribaltamento_fuori_piano", "rottura_ancoraggio"

    def __post_init__(self):
        if self.resistenza_pannello_kg > 0:
            self.rapporto_domanda_resistenza = (
                self.domanda_fuori_piano_kg / self.resistenza_pannello_kg
            )
            self.margine_sicurezza_perc = max(0, (1 - self.rapporto_domanda_resistenza) * 100)
        else:
            self.rapporto_domanda_resistenza = float("inf")
            self.margine_sicurezza_perc = -999.9


@dataclass
class RisultatoSLE:
    """Risultato della verifica SLE (stato limite di esercizio)."""

    stato_danno: StatoDannoSLE
    drift_calcolato_perc: float
    drift_capacita_perc: float
    rapporto_drift: float = field(init=False)
    danno_ai_giunti: bool = False
    danno_al_pannello: bool = False
    intervento_necessario: bool = False
    note_sle: str = ""

    def __post_init__(self):
        if self.drift_capacita_perc > 0:
            self.rapporto_drift = self.drift_calcolato_perc / self.drift_capacita_perc
        else:
            self.rapporto_drift = float("inf")


@dataclass
class RisultatoTamponamento:
    """Risultato combinato SLU + SLE per tamponamento."""

    spec: TamponamentoSpec
    risultato_slu: RisultatoSLU
    risultato_sle: RisultatoSLE
    passaggi_calcolo: list[str] = field(default_factory=list)

    def esito_complessivo(self) -> bool:
        """True se sia SLU che SLE sono verificati."""
        return self.risultato_slu.esito and (
            self.risultato_sle.stato_danno != StatoDannoSLE.INSICUREZZA
        )

    def to_dict(self) -> dict:
        """Serializzazione per report."""
        return {
            "tipologia": self.spec.tipologia,
            "geometria": {
                "altezza_cm": self.spec.altezza_cm,
                "larghezza_cm": self.spec.larghezza_cm,
                "spessore_cm": self.spec.spessore_cm,
                "area_netta_cm2": self.spec.area_netta_cm2(),
            },
            "slu": {
                "esito": self.risultato_slu.esito,
                "domanda_kg": self.risultato_slu.domanda_fuori_piano_kg,
                "resistenza_kg": self.risultato_slu.resistenza_pannello_kg,
                "rapporto": round(self.risultato_slu.rapporto_domanda_resistenza, 3),
                "margine_perc": round(self.risultato_slu.margine_sicurezza_perc, 1),
                "meccanismo_critico": self.risultato_slu.meccanismo_critico,
            },
            "sle": {
                "stato_danno": self.risultato_sle.stato_danno.value,
                "drift_calcolato_perc": round(self.risultato_sle.drift_calcolato_perc, 2),
                "drift_capacita_perc": round(self.risultato_sle.drift_capacita_perc, 2),
                "rapporto_drift": round(self.risultato_sle.rapporto_drift, 3),
                "danno_giunti": self.risultato_sle.danno_ai_giunti,
                "danno_pannello": self.risultato_sle.danno_al_pannello,
                "intervento_necessario": self.risultato_sle.intervento_necessario,
            },
            "esito_complessivo": self.esito_complessivo(),
            "passaggi": self.passaggi_calcolo,
        }
