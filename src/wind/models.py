"""Wind models – modelli dati per le azioni del vento.

Supporta NTC 2018 (§3.3), EN 1991-1-4 e CNR-DT 207 R1/2018.
Gestisce edifici e strutture speciali (tettoie, insegne, pannelli FV).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WindSite:
    """Parametri del sito per le azioni del vento.

    Attributes:
        altitude_m: Altitudine sul livello del mare [m].
        terrain_category: Categoria di esposizione del terreno.
            - NTC2018: "I", "II", "III", "IV", "V"
            - EN 1991-1-4: "0", "I", "II", "III", "IV"
        topography: Tipo di topografia ("flat", "hill", "ridge", "valley").
        topography_params: Parametri topografici dettagliati per calcolo ct.
        reference_wind_speed_ms: Velocità di riferimento del vento [m/s].
            Se None, calcolata dal metodo normativo.
        zone_id: Zona geografica NTC2018 (1-9) per lookup automatico vb0.
        wind_directions: Direzioni del vento da analizzare.
        extra: Parametri aggiuntivi specifici del metodo.
    """

    altitude_m: float = 0.0
    terrain_category: str = "II"
    topography: str = "flat"
    topography_params: TopographyParams | None = None
    reference_wind_speed_ms: float | None = None
    zone_id: str | None = None
    wind_directions: list[WindDirection] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Terrain:
    """Parametri del terreno per il calcolo del profilo di velocità."""

    z0_m: float = 0.05
    z_min_m: float = 2.0
    orography_factor: float = 1.0


@dataclass
class BuildingGeom:
    """Geometria base dell'edificio per il calcolo delle pressioni di vento.

    Attributes:
        height_m: Altezza totale dell'edificio [m].
        width_m: Larghezza in pianta nella direzione del vento [m].
        depth_m: Profondità in pianta perpendicolare al vento [m].
    """

    height_m: float = 10.0
    width_m: float = 10.0
    depth_m: float = 10.0


# ---------------------------------------------------------------------------
# Modelli estesi per strutture speciali e parametri avanzati
# ---------------------------------------------------------------------------

# Tipologie di struttura supportate
STRUCTURE_TYPES = (
    "BUILDING",  # Edificio a pianta rettangolare
    "CANOPY_MONO",  # Tettoia a falda unica (monopitch)
    "CANOPY_DUO",  # Tettoia a due falde (duopitch)
    "CANOPY_TROUGH",  # Tettoia a V invertita
    "CANOPY_MULTI",  # Tettoia multi-campata
    "SHELTER",  # Pensilina (addossata a edificio)
    "SIGN",  # Insegna / pannello pubblicitario
    "SIGN_LATTICE",  # Insegna su struttura reticolare
    "SOLAR_GROUND",  # Pannello FV a terra
    "SOLAR_FLAT_ROOF",  # Pannello FV su tetto piano
    "SOLAR_PITCHED_ROOF",  # Pannello FV su tetto inclinato
    "SOLAR_TRACKER",  # Pannello FV su inseguitore monoassiale
    "WALL_FREE",  # Muro isolato / parapetto
    "FENCE",  # Recinzione
)

# Classi di rugosità superficiale per attrito
FRICTION_CLASSES = {
    "SMOOTH": 0.01,  # Vetro, acciaio, cls liscio
    "ROUGH": 0.02,  # Laterizio, cls grezzo
    "VERY_ROUGH": 0.04,  # Lamiera grecata, ondulato
}


@dataclass
class StructureGeom:
    """Geometria generalizzata per qualsiasi struttura esposta al vento.

    Estende BuildingGeom con parametri per strutture speciali.
    """

    structure_type: str = "BUILDING"
    height_m: float = 10.0
    width_m: float = 10.0
    depth_m: float = 10.0

    # Copertura / inclinazione
    roof_angle_deg: float = 0.0
    panel_tilt_deg: float = 0.0

    # Tettoie
    blockage_ratio: float = 0.0  # φ: 0=aperta, 1=completamente chiusa sotto

    # Insegne / recinzioni
    solidity_ratio: float = 1.0  # rapporto pieni/vuoti (1.0=piena)

    # Posizione
    ground_clearance_m: float = 0.0
    attached_to_building: bool = False

    # Per forze risultanti
    tributary_area_m2: float | None = None

    # Pannelli FV
    panel_rows: int = 1
    row_spacing_m: float = 0.0  # distanza tra file

    # Rugosità superficiale per attrito
    friction_class: str = "SMOOTH"

    # Parametri dinamici per cs·cd (opzionali)
    natural_frequency_hz: float | None = None
    damping_log_decrement: float | None = None

    extra: dict[str, Any] = field(default_factory=dict)

    def to_building_geom(self) -> BuildingGeom:
        """Converte a BuildingGeom per compatibilità con codice esistente."""
        return BuildingGeom(
            height_m=self.height_m,
            width_m=self.width_m,
            depth_m=self.depth_m,
        )


@dataclass
class TopographyParams:
    """Parametri topografici per il calcolo del fattore ct.

    NTC2018 §3.3.3 / EC1 §4.3.3 / EC1 Annex A.3.
    """

    topo_type: str = "flat"  # flat, hill, ridge, escarpment, valley
    slope_upwind_deg: float = 0.0
    crest_height_m: float = 0.0
    x_from_crest_m: float = 0.0
    lu_m: float = 0.0  # lunghezza caratteristica sopravento
    ld_m: float = 0.0  # lunghezza caratteristica sottovento


@dataclass
class WindDirection:
    """Direzione del vento da analizzare."""

    angle_deg: float = 0.0  # 0=Nord, 90=Est, 180=Sud, 270=Ovest
    label: str = ""


@dataclass
class InternalPressureConfig:
    """Configurazione per il calcolo della pressione interna cp_i.

    Attributes:
        method: "simplified" (±0.2) o "detailed" (funzione di μ).
        mu: Rapporto area aperture sopravento / area totale aperture.
        dominant_opening: True se c'è un'apertura dominante.
    """

    method: str = "simplified"
    mu: float | None = None
    dominant_opening: bool = False
