"""Utilita geotecniche condivise.

Il package usa kg/cm2 come unita interna per le tensioni.
Le conversioni verso kPa sono esplicite e centralizzate qui.
"""

from __future__ import annotations

import math

KG_CM2_TO_KPA = 98.0665
KPA_TO_KG_CM2 = 1.0 / KG_CM2_TO_KPA


def kg_cm2_to_kpa(valore: float) -> float:
    """Converte una tensione da kg/cm2 a kPa."""

    return valore * KG_CM2_TO_KPA


def kpa_to_kg_cm2(valore: float) -> float:
    """Converte una tensione da kPa a kg/cm2."""

    return valore * KPA_TO_KG_CM2


def sovraccarico_geostatico_kg_cm2(gamma_kg_m3: float, profondita_cm: float) -> float:
    """Calcola q = gamma * D nel sistema interno kg/cm2.

    gamma e' atteso in kg/m3 e la profondita in cm.
    """

    profondita_m = profondita_cm / 100.0
    q_kg_m2 = gamma_kg_m3 * profondita_m
    return q_kg_m2 / 10000.0


def riduci_tan_phi(phi_gradi: float, gamma_m_phi: float) -> float:
    """Riduce phi con approccio su tan(phi) / gamma_M."""

    if gamma_m_phi <= 0:
        raise ValueError("gamma_m_phi deve essere > 0")
    tan_phi = math.tan(math.radians(phi_gradi))
    tan_phi_ridotto = tan_phi / gamma_m_phi
    return math.degrees(math.atan(tan_phi_ridotto))


def clamp_non_negativo(valore: float) -> float:
    """Taglia valori negativi a zero."""

    return max(valore, 0.0)
