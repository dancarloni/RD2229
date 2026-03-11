from __future__ import annotations

from enum import Enum


class StatoDannoSLE(str, Enum):
    ASSENTE = "assente"
    LOCALE = "locale"
    DIFFUSO = "diffuso"
    INSICUREZZA = "insicurezza"


def calcola_forza_sismica_locale(
    massa_kg: float, accelerazione_spettrale_g: float, gamma_i: float = 1.0
) -> float:
    """Restituisce la forza sismica locale equivalente in kgf circa.

    Il modello e volutamente coerente con il pattern S1: usa un input spettrale
    espresso in multipli di g e restituisce una domanda equivalente proporzionale
    alla massa dell'elemento.
    """
    return max(0.0, massa_kg * accelerazione_spettrale_g * gamma_i)


def classifica_danno_da_rapporto(
    rapporto_domanda_capacita: float,
) -> tuple[StatoDannoSLE, bool, bool, bool, str]:
    """Classifica il danno SLE in quattro livelli, coerente con S1."""
    if rapporto_domanda_capacita < 0.50:
        return (
            StatoDannoSLE.ASSENTE,
            False,
            False,
            False,
            "Domanda deformativa ampiamente entro la capacita del sistema.",
        )
    if rapporto_domanda_capacita < 0.75:
        return (
            StatoDannoSLE.LOCALE,
            True,
            False,
            False,
            "Danno localizzato su giunti, fissaggi o punti singolari.",
        )
    if rapporto_domanda_capacita < 1.00:
        return (
            StatoDannoSLE.DIFFUSO,
            True,
            True,
            False,
            "Danno diffuso con perdita parziale di funzionalita del tramezzo.",
        )
    return (
        StatoDannoSLE.INSICUREZZA,
        True,
        True,
        True,
        "Capacita superata: rischio di distacco, espulsione locale o perdita di servizio.",
    )
