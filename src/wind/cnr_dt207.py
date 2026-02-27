"""CNR-DT 207 R1/2018 – Fattori di turbolenza e risposta dinamica.

Riferimento: CNR-DT 207 R1/2018 – Istruzioni per la valutazione delle azioni
e degli effetti del vento sulle costruzioni.

NOTA PROPRIETÀ LETTERARIA: Il documento CNR-DT 207 R1/2018 è soggetto a
proprietà letteraria riservata. Le formule qui implementate sono derivate da
principi generali di ingegneria del vento e da letteratura tecnica pubblica.
I valori dei parametri sito-specifici devono essere forniti dall'utente.

TODO: Implementare calcolo risposta dinamica completo (fattore Cd)
      quando disponibili parametri strutturali (frequenza propria, smorzamento).
"""

from __future__ import annotations

import logging
import math

from src.wind.models import BuildingGeom, WindSite
from src.wind.outputs import WindResults

logger = logging.getLogger(__name__)


def compute_turbulence_intensity(
    z: float,
    z0: float,
    z_min: float,
    ki: float = 1.0,
) -> float:
    """Intensità di turbolenza Iv(z) (formula logaritmica standard).

    Iv(z) = ki / ln(z / z0) per z ≥ z_min, altrimenti Iv(z_min).

    Args:
        z: Quota [m].
        z0: Rugosità del terreno [m].
        z_min: Quota minima [m].
        ki: Fattore di turbolenza (default 1.0).

    Returns:
        Intensità di turbolenza [-].
    """
    z_eff = max(z, z_min)
    return ki / math.log(z_eff / z0)


def compute_peak_factor(
    turbulence_intensity: float,
    *,
    kp: float = 3.5,
) -> float:
    """Fattore di picco kp per la pressione di picco.

    In assenza di calcolo dinamico: usa kp = 3.5 (valore tipico per strutture
    non slanciose secondo letteratura tecnica).

    Args:
        turbulence_intensity: Intensità di turbolenza Iv(z).
        kp: Fattore di picco (default 3.5).

    Returns:
        Fattore di picco kp.
    """
    return kp


def enrich_results_with_cnr_dt207(
    wind_results: WindResults,
    site: WindSite,
    building: BuildingGeom,
    *,
    z0: float = 0.05,
    z_min: float = 2.0,
) -> WindResults:
    """Arricchisce i risultati con i fattori CNR-DT 207 R1/2018.

    Aggiunge intensità di turbolenza e fattori di picco all'extra dei risultati.
    Non sostituisce il profilo di velocità.

    Args:
        wind_results: Risultati base (da NTC2018 o EN1991-1-4).
        site: Parametri del sito.
        building: Geometria edificio.
        z0: Rugosità terreno [m].
        z_min: Quota minima [m].

    Returns:
        :class:`WindResults` arricchito (nuovo oggetto).
    """
    h = building.height_m
    z_ref = max(h, z_min)
    iv = compute_turbulence_intensity(z_ref, z0, z_min)
    kp = compute_peak_factor(iv)

    extra = {
        **wind_results.extra,
        "cnr_dt207": {
            "turbulence_intensity_at_h": round(iv, 4),
            "peak_factor_kp": kp,
            "z_ref_m": z_ref,
            "note": "Valori calcolati con formula logaritmica standard; "
            "verificare con parametri CNR-DT 207 R1/2018 per applicazione reale.",
        },
    }

    warnings = list(wind_results.warnings)
    warnings.append(
        "CNR-DT 207 R1/2018: fattori di risposta dinamica (Cd) non implementati. "
        "Inserire parametri dinamici (frequenza propria, smorzamento) per calcolo completo."
    )

    import dataclasses

    return dataclasses.replace(wind_results, extra=extra, warnings=warnings)
