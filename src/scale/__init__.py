"""Modulo scale - Fase V.

API pubblica per verifiche di rampe in c.a. e metalliche.
"""

from .scale import (
    GeometriaRampa,
    ProfiloAcciaioScala,
    RisultatoScala,
    RisultatoVerifica,
    calcola_carico_variabile_default,
    calcola_coefficiente_neve,
    profilo_ipe200_s275,
    verifica_scala_ca,
    verifica_scala_metallica,
)

__all__ = [
    "GeometriaRampa",
    "ProfiloAcciaioScala",
    "RisultatoScala",
    "RisultatoVerifica",
    "calcola_carico_variabile_default",
    "calcola_coefficiente_neve",
    "profilo_ipe200_s275",
    "verifica_scala_ca",
    "verifica_scala_metallica",
]
