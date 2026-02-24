"""Wind models – modelli dati per le azioni del vento.

Supporta NTC 2018 (§3.3), EN 1991-1-4 e CNR-DT 207 R1/2018.
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
        reference_wind_speed_ms: Velocità di riferimento del vento [m/s].
            Se None, calcolata dal metodo normativo.
        extra: Parametri aggiuntivi specifici del metodo.
    """

    altitude_m: float = 0.0
    terrain_category: str = "II"
    topography: str = "flat"
    reference_wind_speed_ms: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Terrain:
    """Parametri del terreno per il calcolo del profilo di velocità."""

    # Rugosità z0 [m] (altezza di rugosità)
    z0_m: float = 0.05
    # Altezza minima di applicazione del profilo [m]
    z_min_m: float = 2.0
    # Fattore orografico (default 1.0 = terreno piano)
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
