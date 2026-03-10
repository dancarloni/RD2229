"""Gestione regole normative geotecniche.

Progettato per essere esteso: ogni norma implementa la stessa
interfaccia e puo' essere sostituita senza cambiare i calcoli.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .models import CombinazioneDA1, NormaGeotecnica


@dataclass(frozen=True, slots=True)
class CoefficientiParzialiGeotecnici:
    """Coefficienti parziali per combinazione normativa."""

    gamma_m_phi: float
    gamma_m_c: float
    gamma_r: float


class NormaGeotecnicaBase(ABC):
    """Interfaccia astratta per implementazioni normative."""

    @property
    @abstractmethod
    def codice(self) -> NormaGeotecnica:
        """Codice norma esposto dall'implementazione."""

    @abstractmethod
    def coefficienti_da1(self, combinazione: CombinazioneDA1) -> CoefficientiParzialiGeotecnici:
        """Restituisce i coefficienti per DA1 set 1 / set 2."""


class NormaNTC2018Geotecnica(NormaGeotecnicaBase):
    """Implementazione iniziale NTC2018 per Fase P.

    Nota: i valori sono mantenuti configurabili e centralizzati per
    facilitare aggiornamenti successivi (estensione futura del modulo).
    """

    _COEFFICIENTI_DA1: dict[CombinazioneDA1, CoefficientiParzialiGeotecnici] = {
        CombinazioneDA1.SET1: CoefficientiParzialiGeotecnici(
            gamma_m_phi=1.0,
            gamma_m_c=1.0,
            gamma_r=1.40,
        ),
        CombinazioneDA1.SET2: CoefficientiParzialiGeotecnici(
            gamma_m_phi=1.25,
            gamma_m_c=1.25,
            gamma_r=1.40,
        ),
    }

    @property
    def codice(self) -> NormaGeotecnica:
        return NormaGeotecnica.NTC2018

    def coefficienti_da1(self, combinazione: CombinazioneDA1) -> CoefficientiParzialiGeotecnici:
        return self._COEFFICIENTI_DA1[combinazione]


class NormaEC7Geotecnica(NormaNTC2018Geotecnica):
    """Implementazione EC7 iniziale.

    In questa fase riusa i coefficienti default NTC per garantire
    continuita' operativa; verra' raffinata in step successivi.
    """

    @property
    def codice(self) -> NormaGeotecnica:
        return NormaGeotecnica.EC7


class NormaDM1988Geotecnica(NormaNTC2018Geotecnica):
    """Implementazione DM 11/03/1988 iniziale.

    Placeholder strutturato per estensione storica in fasi successive.
    """

    @property
    def codice(self) -> NormaGeotecnica:
        return NormaGeotecnica.DM_1988


def crea_norma_geotecnica(codice: NormaGeotecnica) -> NormaGeotecnicaBase:
    """Factory normativa geotecnica."""

    if codice == NormaGeotecnica.NTC2018:
        return NormaNTC2018Geotecnica()
    if codice == NormaGeotecnica.EC7:
        return NormaEC7Geotecnica()
    if codice == NormaGeotecnica.DM_1988:
        return NormaDM1988Geotecnica()
    raise ValueError(f"Norma non supportata: {codice}")
