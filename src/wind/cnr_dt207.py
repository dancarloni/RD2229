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

from src.wind.models import BuildingGeom, StructureGeom, WindSite
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


# ---------------------------------------------------------------------------
# Fattore strutturale cs·cd — semplificato
# ---------------------------------------------------------------------------

def compute_structural_factor(
    structure: StructureGeom | BuildingGeom,
    site: WindSite | None = None,
    *,
    z0: float = 0.05,
    z_min: float = 2.0,
    override: float | None = None,
) -> float:
    """Calcola il fattore strutturale cs·cd (semplificato).

    NTC2018 §3.3.4 / CNR-DT 207 §6:
    - cs·cd = 1.0 per strutture rigide (h ≤ 15 m oppure f1 > 1 Hz)
    - Per strutture flessibili: approssimazione tabellare

    Il calcolo completo richiede:
        cs·cd = (1 + 2·kp·Iv·√(B²+R²)) / (1 + 7·Iv)
    dove B² = fattore di fondo, R² = fattore di risonanza.

    Qui si implementa il metodo semplificato; lo schema completo
    è predisposto per future estensioni.

    Args:
        structure: Geometria della struttura.
        site: Parametri del sito (per turbolenza).
        z0: Rugosità terreno [m].
        z_min: Quota minima [m].
        override: Override utente.

    Returns:
        Fattore cs·cd (tipicamente 0.85–1.1).
    """
    if override is not None:
        return override

    h = structure.height_m

    # Parametri dinamici (se disponibili)
    f1 = None
    damping = None
    if isinstance(structure, StructureGeom):
        f1 = structure.natural_frequency_hz
        damping = structure.damping_log_decrement

    # Criterio di rigidezza: h ≤ 15m oppure f1 > 1 Hz
    if h <= 15.0:
        return 1.0

    if f1 is not None and f1 > 1.0:
        return 1.0

    # Strutture flessibili: approssimazione semplificata
    # Basata su altezza e intensità di turbolenza
    z_ref = max(h, z_min)
    iv = compute_turbulence_intensity(z_ref, z0, z_min)

    if f1 is not None and damping is not None:
        # Schema per futuro calcolo completo
        return _compute_cscd_detailed(h, f1, damping, iv, z0, z_min)

    # Approssimazione tabellare per altezza
    # Basata su tendenze generali da letteratura:
    # h=20m → cs·cd≈0.95, h=50m → cs·cd≈0.90, h>100m → cs·cd≈0.85
    if h <= 20.0:
        cscd = 0.95
    elif h <= 50.0:
        t = (h - 20.0) / 30.0
        cscd = 0.95 - 0.05 * t  # 0.95 → 0.90
    elif h <= 100.0:
        t = (h - 50.0) / 50.0
        cscd = 0.90 - 0.05 * t  # 0.90 → 0.85
    else:
        cscd = 0.85

    logger.info(
        "cs·cd semplificato = %.3f per h=%.1f m (tabellare). "
        "Per calcolo preciso fornire f1 e δ.",
        cscd,
        h,
    )
    return round(cscd, 3)


def _compute_cscd_detailed(
    h: float,
    f1: float,
    damping_log_dec: float,
    iv: float,
    z0: float,
    z_min: float,
) -> float:
    """Schema per calcolo completo cs·cd — CNR-DT 207 §6.

    cs·cd = (1 + 2·kp·Iv·√(B²+R²)) / (1 + 7·Iv)

    TODO: Implementazione completa con:
    - B² = fattore di fondo (background factor)
    - R² = fattore di risonanza (resonance factor)
    - kp = fattore di picco (peak factor)
    - S_L = funzione di densità spettrale
    - Dimensioni di correlazione del vento

    Per ora: approssimazione basata su f1 e smorzamento.
    """
    # Smorzamento totale δ_s (logaritmico)
    delta_s = damping_log_dec

    # B² approssimato (fattore di fondo)
    # B² ≈ 1 / (1 + 0.9 · (b+h)/(L(z_ref)))^0.63
    # Con L(z_ref) ≈ 300 · (z_ref/200)^0.67 (scala integrale turbolenza)
    z_ref = max(h, z_min)
    L_z = 300.0 * (z_ref / 200.0) ** 0.67
    B2 = 1.0 / (1.0 + 0.9 * (h / L_z) ** 0.63)

    # R² approssimato (fattore di risonanza)
    # R² ≈ (π / (2·δ_tot)) · S_L(f1, z_ref) · R_h · R_b
    # Semplificazione: R² ≈ π²/(2·δ_s) · f1 · S_L / (...)
    # Per ora: stima semplificata
    n1 = f1 * L_z / (max(z_ref, 1.0) * iv * 25.0 + 1.0)
    S_L = 6.8 * n1 / (1.0 + 10.2 * n1) ** (5.0 / 3.0)

    # δ_tot ≈ δ_s + δ_a (smorzamento aerodinamico)
    delta_a = 0.01  # stima conservativa
    delta_tot = delta_s + delta_a

    R2 = math.pi / (2.0 * max(delta_tot, 0.01)) * S_L * 0.5  # approssimazione

    # kp = √(2·ln(ν·T)) + 0.6/√(2·ln(ν·T))
    # ν = f1 · √(R²/(B²+R²)), T = 600 s
    nu = f1 * math.sqrt(R2 / max(B2 + R2, 0.001))
    nu_T = max(nu * 600.0, 1.0)
    ln_nuT = math.log(nu_T)
    kp = math.sqrt(2.0 * ln_nuT) + 0.6 / math.sqrt(max(2.0 * ln_nuT, 0.1))
    kp = max(kp, 3.0)  # minimo 3.0

    # cs·cd
    numerator = 1.0 + 2.0 * kp * iv * math.sqrt(B2 + R2)
    denominator = 1.0 + 7.0 * iv
    cscd = numerator / denominator

    # Limiti ragionevoli
    cscd = max(0.85, min(1.1, cscd))

    logger.info(
        "cs·cd dettagliato = %.3f (B²=%.3f, R²=%.3f, kp=%.2f, f1=%.2f Hz, δ=%.3f).",
        cscd, B2, R2, kp, f1, delta_s,
    )
    return round(cscd, 3)
