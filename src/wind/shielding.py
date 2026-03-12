"""Shielding – fattori di schermatura tra strutture.

Calcola i fattori di riduzione per effetto di schermatura tra:
- File di pannelli fotovoltaici
- Edifici in contesto urbano denso
- Tettoie multi-campata (complementare a canopy multibay factors)
"""

from __future__ import annotations

import logging
import math

logger = logging.getLogger(__name__)


def compute_shielding_factor(
    spacing_m: float,
    structure_height_m: float,
    obstruction_height_m: float = 0.0,
    *,
    override: float | None = None,
) -> float:
    """Fattore di schermatura generico.

    Riduce l'azione del vento su strutture schermate da altre strutture
    a monte (sopravento).

    Args:
        spacing_m: Distanza tra le strutture [m].
        structure_height_m: Altezza della struttura schermata [m].
        obstruction_height_m: Altezza dell'ostruzione sopravento [m].
            Se 0, usa structure_height_m.
        override: Override utente (se specificato, ignora calcolo).

    Returns:
        Fattore di schermatura (0.6–1.0). 1.0 = nessuna schermatura.
    """
    if override is not None:
        return max(0.0, min(1.0, override))

    h_obs = obstruction_height_m if obstruction_height_m > 0 else structure_height_m
    h_str = structure_height_m

    if h_obs <= 0 or h_str <= 0 or spacing_m <= 0:
        return 1.0

    # Rapporto spaziatura / altezza
    s_h = spacing_m / h_obs

    # Se spaziatura molto grande, nessuna schermatura
    if s_h >= 10.0:
        return 1.0

    # Rapporto altezze (quanto l'ostruzione copre la struttura)
    h_ratio = min(h_obs / h_str, 1.5)

    # Modello esponenziale semplificato
    # k_s = 1 - α · exp(-β · s/h) · f(h_ratio)
    alpha = 0.4  # riduzione massima
    beta = 0.3  # velocità di decadimento
    f_h = min(h_ratio, 1.0)  # capping a 1.0

    k_s = 1.0 - alpha * math.exp(-beta * s_h) * f_h

    return round(max(0.6, min(1.0, k_s)), 3)


def compute_solar_row_shielding(
    row_index: int,
    row_spacing_m: float,
    panel_height_m: float,
    tilt_deg: float,
    *,
    override: float | None = None,
) -> float:
    """Fattore di schermatura per file di pannelli fotovoltaici.

    La prima fila (row_index=0) non è schermata (fattore = 1.0).
    Le file successive sono schermate dalle file precedenti.

    Args:
        row_index: Indice della fila (0 = prima).
        row_spacing_m: Distanza tra file [m].
        panel_height_m: Altezza del pannello [m] (dimensione nella direzione del tilt).
        tilt_deg: Inclinazione pannello [°].
        override: Override utente.

    Returns:
        Fattore di schermatura (0.6–1.0).
    """
    if override is not None:
        return max(0.0, min(1.0, override))

    if row_index == 0:
        return 1.0

    # Altezza proiettata del pannello
    h_proj = panel_height_m * math.sin(math.radians(max(tilt_deg, 1.0)))

    if h_proj <= 0 or row_spacing_m <= 0:
        return 1.0

    # Usa il fattore generico
    return compute_shielding_factor(row_spacing_m, h_proj, h_proj)


def compute_urban_shielding(
    building_height_m: float,
    avg_surrounding_height_m: float,
    avg_spacing_m: float,
    *,
    override: float | None = None,
) -> float:
    """Fattore di schermatura per edifici in contesto urbano.

    Riduce l'azione del vento per edifici circondati da altri edifici.
    Applicabile solo se l'edificio è più basso o simile ai circostanti.

    Args:
        building_height_m: Altezza dell'edificio target [m].
        avg_surrounding_height_m: Altezza media edifici circostanti [m].
        avg_spacing_m: Spaziatura media tra edifici [m].
        override: Override utente.

    Returns:
        Fattore di schermatura (0.6–1.0).
    """
    if override is not None:
        return max(0.0, min(1.0, override))

    if building_height_m <= 0 or avg_surrounding_height_m <= 0:
        return 1.0

    # Se l'edificio è più alto dei circostanti, nessuna schermatura
    if building_height_m > 1.5 * avg_surrounding_height_m:
        return 1.0

    return compute_shielding_factor(avg_spacing_m, building_height_m, avg_surrounding_height_m)
