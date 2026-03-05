"""Wind outputs – strutture dati per i risultati del calcolo del vento.

Contiene i modelli di output per: profilo velocità, pressioni su zone,
forze risultanti, attrito, combinazioni di carico.
"""

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
    """Pressioni su una zona della struttura (parete, copertura, pannello)."""

    zone_id: str = ""
    description: str = ""
    cpe: float = 0.0  # Coefficiente pressione esterna
    cpi: float = 0.0  # Coefficiente pressione interna
    we_kN_m2: float = 0.0  # Pressione esterna [kN/m²]
    wi_kN_m2: float = 0.0  # Pressione interna [kN/m²]
    net_kN_m2: float = 0.0  # Pressione netta (we - wi) [kN/m²]
    area_m2: float = 0.0  # Area della zona [m²]


@dataclass
class ZoneForce:
    """Forza risultante su una zona/elemento strutturale."""

    zone_id: str = ""
    F_kN: float = 0.0  # Forza risultante [kN]
    direction: str = ""  # "pressure", "suction", "uplift", "drag"
    tributary_area_m2: float = 0.0
    application_point_m: float = 0.0  # quota di applicazione [m]


@dataclass
class FrictionForce:
    """Forza di attrito del vento su una superficie."""

    surface_id: str = ""
    c_fr: float = 0.0
    area_m2: float = 0.0
    q_p_kN_m2: float = 0.0
    F_fr_kN: float = 0.0  # c_fr · q_p · A_fr [kN]


@dataclass
class WindCombination:
    """Combinazione di carico vento (SLU/SLE)."""

    combo_id: str = ""  # "SLU_1.5", "SLE_car", "SLE_freq", "SLE_qp"
    description: str = ""
    gamma_w: float = 1.5
    psi: float = 1.0
    pressures: list[PressureZoneResults] = field(default_factory=list)
    resultant_forces: list[ZoneForce] = field(default_factory=list)


@dataclass
class WindResults:
    """Risultati completi del calcolo delle azioni del vento.

    Attributes:
        method: Metodo normativo usato.
        v_b_ms: Velocità base di riferimento [m/s].
        v_ref_ms: Velocità di riferimento sito [m/s].
        q_b_kN_m2: Pressione cinetica di riferimento [kN/m²].
        velocity_profile: Profilo di velocità/pressione per quote crescenti.
        pressure_zones: Pressioni per zone della struttura.
        resultant_forces: Forze risultanti per zona.
        friction_forces: Forze di attrito.
        combinations: Combinazioni di carico (opzionale).
        topography_factor: Fattore topografico ct.
        structural_factor: Fattore strutturale cs·cd.
        wind_direction_deg: Direzione del vento analizzata [°].
        warnings: Avvisi non bloccanti.
        extra: Parametri intermedi per tracciabilità.
    """

    method: str = "NTC2018"
    v_b_ms: float = 0.0
    v_ref_ms: float = 0.0
    q_b_kN_m2: float = 0.0
    velocity_profile: list[WindProfilePoint] = field(default_factory=list)
    pressure_zones: list[PressureZoneResults] = field(default_factory=list)
    resultant_forces: list[ZoneForce] = field(default_factory=list)
    friction_forces: list[FrictionForce] = field(default_factory=list)
    combinations: list[WindCombination] = field(default_factory=list)
    topography_factor: float = 1.0
    structural_factor: float = 1.0
    wind_direction_deg: float | None = None
    warnings: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
