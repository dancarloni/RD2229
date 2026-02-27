"""Wind outputs – strutture dati per i risultati del calcolo del vento."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WindProfilePoint:
    """Punto del profilo di velocità/pressione a quota z."""

    z_m: float
    v_m_s: float  # Velocità media [m/s]
    q_kN_m2: float  # Pressione cinetica [kN/m²]


@dataclass
class PressureZoneResults:
    """Pressioni su una zona della struttura (parete, copertura)."""

    zone_id: str = ""
    description: str = ""
    cpe: float = 0.0  # Coefficiente pressione esterna
    cpi: float = 0.0  # Coefficiente pressione interna
    we_kN_m2: float = 0.0  # Pressione esterna [kN/m²]
    wi_kN_m2: float = 0.0  # Pressione interna [kN/m²]
    net_kN_m2: float = 0.0  # Pressione netta (we - wi) [kN/m²]


@dataclass
class WindResults:
    """Risultati completi del calcolo delle azioni del vento.

    Attributes:
        method: Metodo normativo usato ("NTC2018", "EN1991_1_4", "CNR_DT207", "hybrid").
        v_b_ms: Velocità base di riferimento [m/s].
        v_ref_ms: Velocità di riferimento sito [m/s].
        q_b_kN_m2: Pressione cinetica di riferimento [kN/m²].
        velocity_profile: Profilo di velocità/pressione per quote crescenti.
        pressure_zones: Pressioni per zone della struttura.
        warnings: Avvisi non bloccanti.
        extra: Parametri intermedi per tracciabilità.
    """

    method: str = "NTC2018"
    v_b_ms: float = 0.0
    v_ref_ms: float = 0.0
    q_b_kN_m2: float = 0.0
    velocity_profile: list[WindProfilePoint] = field(default_factory=list)
    pressure_zones: list[PressureZoneResults] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
