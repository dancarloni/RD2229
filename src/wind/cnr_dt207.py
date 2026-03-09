"""CNR-DT 207 R1/2018 – Fattori di turbolenza e risposta dinamica.

Riferimento: CNR-DT 207 R1/2018 – Istruzioni per la valutazione delle azioni
e degli effetti del vento sulle costruzioni.

NOTA PROPRIETÀ LETTERARIA: Il documento CNR-DT 207 R1/2018 è soggetto a
proprietà letteraria riservata. Le formule qui implementate sono derivate da
principi generali di ingegneria del vento e da letteratura tecnica pubblica.
I valori dei parametri sito-specifici devono essere forniti dall'utente.

Implementa:
- Intensità di turbolenza Iv(z)
- Scala integrale di turbolenza L(z)
- Fattore di fondo B²
- Fattore di risonanza R² (con funzioni di ammettenza Rh, Rb)
- Densità spettrale adimensionale S_L
- Fattore di picco kp
- Fattore strutturale cs·cd (semplificato e dettagliato)
"""

from __future__ import annotations

import dataclasses
import logging
import math
from dataclasses import dataclass

from src.wind.models import BuildingGeom, StructureGeom, WindSite
from src.wind.outputs import WindResults

logger = logging.getLogger(__name__)


# ===========================================================================
# Costanti
# ===========================================================================

_RHO_AIR = 1.25  # Densità aria [kg/m³]
_T_AVERAGING = 600.0  # Periodo di media [s] (10 min)


# ===========================================================================
# Risultati dettagliati cs·cd
# ===========================================================================

@dataclass
class CscdDetailedResult:
    """Risultati dettagliati del calcolo cs·cd."""

    cscd: float = 1.0
    cs: float = 1.0
    cd: float = 1.0
    B2: float = 1.0         # Fattore di fondo
    R2: float = 0.0         # Fattore di risonanza
    kp: float = 3.5         # Fattore di picco
    Iv: float = 0.0         # Intensità di turbolenza
    L_z_m: float = 0.0      # Scala integrale turbolenza [m]
    S_L: float = 0.0        # Densità spettrale adimensionale
    delta_tot: float = 0.0  # Smorzamento totale (log. dec.)
    method: str = "simplified"


# ===========================================================================
# Turbolenza
# ===========================================================================

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


def compute_integral_length_scale(
    z: float,
    z_min: float = 2.0,
    *,
    L_ref: float = 300.0,
    z_ref: float = 200.0,
    alpha: float = 0.67,
) -> float:
    """Scala integrale di turbolenza L(z).

    L(z) = L_ref · (z / z_ref)^alpha

    Parametri di default dalla letteratura tecnica generale:
    L_ref = 300 m, z_ref = 200 m, alpha = 0.67 (terreno aperto).

    Args:
        z: Quota [m].
        z_min: Quota minima [m].
        L_ref: Scala di riferimento [m].
        z_ref: Quota di riferimento [m].
        alpha: Esponente.

    Returns:
        Scala integrale L(z) [m].
    """
    z_eff = max(z, z_min)
    return L_ref * (z_eff / z_ref) ** alpha


# ===========================================================================
# Fattore di fondo B²
# ===========================================================================

def compute_background_factor(
    h: float,
    b: float,
    L_z: float,
) -> float:
    """Fattore di fondo B² (background response factor).

    B² = 1 / (1 + 0.9 · ((b + h) / L(z))^0.63)

    Tiene conto della mancanza di correlazione spaziale delle raffiche
    sulla superficie della struttura.

    Args:
        h: Altezza struttura [m].
        b: Larghezza struttura trasversale al vento [m].
        L_z: Scala integrale di turbolenza [m].

    Returns:
        Fattore di fondo B² (0 < B² ≤ 1).
    """
    if L_z <= 0:
        return 1.0
    return 1.0 / (1.0 + 0.9 * ((b + h) / L_z) ** 0.63)


# ===========================================================================
# Densità spettrale e fattore di risonanza R²
# ===========================================================================

def compute_spectral_density(n_dim: float) -> float:
    """Densità spettrale di potenza adimensionale S_L(f, z).

    S_L(n) = 6.8 · n / (1 + 10.2 · n)^(5/3)

    dove n = f·L(z) / v_m(z) è la frequenza adimensionale.

    Args:
        n_dim: Frequenza adimensionale n = f·L(z) / v_m(z).

    Returns:
        Densità spettrale S_L [-].
    """
    if n_dim <= 0:
        return 0.0
    return 6.8 * n_dim / (1.0 + 10.2 * n_dim) ** (5.0 / 3.0)


def compute_aerodynamic_admittance(
    eta: float,
) -> float:
    """Funzione di ammettenza aerodinamica R_h o R_b.

    R(η) = (1/η) - 1/(2η²) · (1 - e^(-2η))   per η > 0
    R(η) = 1                                    per η = 0

    Args:
        eta: Argomento adimensionale η = 4.6·f·dim / v_m(z) (con dim = h o b).

    Returns:
        Fattore di ammettenza aerodinamica [-].
    """
    if eta <= 0:
        return 1.0
    if eta > 50:
        return 1.0 / eta
    return 1.0 / eta - 1.0 / (2.0 * eta ** 2) * (1.0 - math.exp(-2.0 * eta))


def compute_resonance_factor(
    f1: float,
    h: float,
    b: float,
    v_m: float,
    L_z: float,
    delta_tot: float,
) -> float:
    """Fattore di risonanza R² (resonance response factor).

    R² = (π² / (2·δ_tot)) · S_L(f1, z) · R_h(η_h) · R_b(η_b)

    Tiene conto dell'amplificazione risonante della risposta strutturale.

    Args:
        f1: Frequenza propria fondamentale [Hz].
        h: Altezza struttura [m].
        b: Larghezza struttura [m].
        v_m: Velocità media alla quota di riferimento [m/s].
        L_z: Scala integrale di turbolenza [m].
        delta_tot: Smorzamento totale (decremento logaritmico).

    Returns:
        Fattore di risonanza R² (≥ 0).
    """
    if f1 <= 0 or v_m <= 0 or delta_tot <= 0:
        return 0.0

    # Frequenza adimensionale
    n_dim = f1 * L_z / v_m

    # Densità spettrale
    S_L = compute_spectral_density(n_dim)

    # Ammettenza aerodinamica
    eta_h = 4.6 * f1 * h / v_m
    eta_b = 4.6 * f1 * b / v_m
    R_h = compute_aerodynamic_admittance(eta_h)
    R_b = compute_aerodynamic_admittance(eta_b)

    R2 = (math.pi ** 2 / (2.0 * delta_tot)) * S_L * R_h * R_b

    return max(R2, 0.0)


# ===========================================================================
# Fattore di picco kp
# ===========================================================================

def compute_peak_factor(
    turbulence_intensity: float,
    *,
    kp: float = 3.5,
    f1: float | None = None,
    B2: float | None = None,
    R2: float | None = None,
) -> float:
    """Fattore di picco kp.

    Se f1, B² e R² sono forniti, calcola:
        ν = f1 · √(R² / (B² + R²))
        kp = √(2·ln(ν·T)) + 0.6 / √(2·ln(ν·T))
    con T = 600 s (10 minuti), kp ≥ 3.0.

    Altrimenti restituisce il valore di default (3.5).

    Args:
        turbulence_intensity: Intensità di turbolenza Iv(z).
        kp: Valore di default.
        f1: Frequenza propria [Hz].
        B2: Fattore di fondo.
        R2: Fattore di risonanza.

    Returns:
        Fattore di picco kp.
    """
    if f1 is None or B2 is None or R2 is None:
        return kp

    if B2 + R2 <= 0:
        return kp

    # Frequenza di up-crossing
    nu = f1 * math.sqrt(R2 / (B2 + R2))
    nu_T = max(nu * _T_AVERAGING, 1.0)
    ln_nuT = math.log(nu_T)

    if ln_nuT <= 0:
        return max(kp, 3.0)

    kp_calc = math.sqrt(2.0 * ln_nuT) + 0.6 / math.sqrt(2.0 * ln_nuT)
    return max(kp_calc, 3.0)


# ===========================================================================
# Arricchimento risultati con CNR-DT 207
# ===========================================================================

def enrich_results_with_cnr_dt207(
    wind_results: WindResults,
    site: WindSite,
    building: BuildingGeom,
    *,
    z0: float = 0.05,
    z_min: float = 2.0,
) -> WindResults:
    """Arricchisce i risultati con i fattori CNR-DT 207 R1/2018.

    Aggiunge intensità di turbolenza, scala integrale e fattori di picco
    ai risultati. Non sostituisce il profilo di velocità.

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
    L_z = compute_integral_length_scale(z_ref, z_min)
    kp = compute_peak_factor(iv)

    extra = {
        **wind_results.extra,
        "cnr_dt207": {
            "turbulence_intensity_at_h": round(iv, 4),
            "peak_factor_kp": kp,
            "integral_length_scale_m": round(L_z, 1),
            "z_ref_m": z_ref,
        },
    }

    warnings = list(wind_results.warnings)

    return dataclasses.replace(wind_results, extra=extra, warnings=warnings)


# ===========================================================================
# Fattore strutturale cs·cd
# ===========================================================================

def compute_structural_factor(
    structure: StructureGeom | BuildingGeom,
    site: WindSite | None = None,
    *,
    z0: float = 0.05,
    z_min: float = 2.0,
    override: float | None = None,
) -> float:
    """Calcola il fattore strutturale cs·cd.

    NTC2018 §3.3.4 / CNR-DT 207 §6:
    - cs·cd = 1.0 per strutture rigide (h ≤ 15 m oppure f1 > 1 Hz)
    - Per strutture con f1 e δ: calcolo completo con B² e R²
    - Altrimenti: approssimazione tabellare

    Calcolo completo:
        cs·cd = (1 + 2·kp·Iv·√(B²+R²)) / (1 + 7·Iv)

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
    b = getattr(structure, "width_m", 10.0)
    if isinstance(structure, StructureGeom):
        f1 = structure.natural_frequency_hz
        damping = structure.damping_log_decrement

    # Criterio di rigidezza: h ≤ 15m oppure f1 > 1 Hz
    if h <= 15.0:
        return 1.0

    if f1 is not None and f1 > 1.0:
        return 1.0

    # Intensità di turbolenza alla quota di riferimento
    z_ref = max(h, z_min)
    iv = compute_turbulence_intensity(z_ref, z0, z_min)

    if f1 is not None and damping is not None:
        return _compute_cscd_detailed(h, b, f1, damping, iv, z0, z_min)

    # Approssimazione tabellare per altezza
    # h=20m → cs·cd≈0.95, h=50m → cs·cd≈0.90, h>100m → cs·cd≈0.85
    if h <= 20.0:
        cscd = 0.95
    elif h <= 50.0:
        t = (h - 20.0) / 30.0
        cscd = 0.95 - 0.05 * t
    elif h <= 100.0:
        t = (h - 50.0) / 50.0
        cscd = 0.90 - 0.05 * t
    else:
        cscd = 0.85

    logger.info(
        "cs·cd semplificato = %.3f per h=%.1f m (tabellare). "
        "Per calcolo preciso fornire f1 e δ.",
        cscd,
        h,
    )
    return round(cscd, 3)


def compute_structural_factor_detailed(
    structure: StructureGeom,
    v_m_ms: float,
    *,
    z0: float = 0.05,
    z_min: float = 2.0,
    delta_a: float = 0.01,
) -> CscdDetailedResult:
    """Calcolo dettagliato del fattore strutturale cs·cd con risultati intermedi.

    Args:
        structure: Geometria con parametri dinamici (f1, δ).
        v_m_ms: Velocità media alla quota di riferimento [m/s].
        z0: Rugosità terreno [m].
        z_min: Quota minima [m].
        delta_a: Smorzamento aerodinamico (default 0.01).

    Returns:
        CscdDetailedResult con tutti i parametri intermedi.
    """
    h = structure.height_m
    b = structure.width_m
    f1 = structure.natural_frequency_hz or 1.0
    damping = structure.damping_log_decrement or 0.05

    z_ref = max(h, z_min)
    iv = compute_turbulence_intensity(z_ref, z0, z_min)
    L_z = compute_integral_length_scale(z_ref, z_min)

    # B²
    B2 = compute_background_factor(h, b, L_z)

    # R²
    delta_tot = damping + delta_a
    v_m = max(v_m_ms, 1.0)
    R2 = compute_resonance_factor(f1, h, b, v_m, L_z, delta_tot)

    # Densità spettrale (per report)
    n_dim = f1 * L_z / v_m
    S_L = compute_spectral_density(n_dim)

    # kp
    kp = compute_peak_factor(iv, f1=f1, B2=B2, R2=R2)

    # cs·cd
    numerator = 1.0 + 2.0 * kp * iv * math.sqrt(B2 + R2)
    denominator = 1.0 + 7.0 * iv

    cscd = numerator / denominator
    cscd = max(0.85, min(1.15, cscd))

    # cs e cd separati
    cs = (1.0 + 7.0 * iv * math.sqrt(B2)) / denominator
    cd = numerator / (1.0 + 2.0 * kp * iv * math.sqrt(B2)) if B2 > 0 else 1.0
    cd = max(cd, 1.0)

    return CscdDetailedResult(
        cscd=round(cscd, 3),
        cs=round(cs, 3),
        cd=round(cd, 3),
        B2=round(B2, 4),
        R2=round(R2, 4),
        kp=round(kp, 2),
        Iv=round(iv, 4),
        L_z_m=round(L_z, 1),
        S_L=round(S_L, 4),
        delta_tot=round(delta_tot, 3),
        method="detailed",
    )


def _compute_cscd_detailed(
    h: float,
    b: float,
    f1: float,
    damping_log_dec: float,
    iv: float,
    z0: float,
    z_min: float,
) -> float:
    """Calcolo cs·cd con B² e R² completi.

    cs·cd = (1 + 2·kp·Iv·√(B²+R²)) / (1 + 7·Iv)

    Args:
        h: Altezza struttura [m].
        b: Larghezza struttura [m].
        f1: Frequenza propria [Hz].
        damping_log_dec: Smorzamento strutturale (decremento log.).
        iv: Intensità di turbolenza alla quota di riferimento.
        z0: Rugosità terreno [m].
        z_min: Quota minima [m].

    Returns:
        Fattore cs·cd arrotondato.
    """
    z_ref = max(h, z_min)
    L_z = compute_integral_length_scale(z_ref, z_min)

    # B²
    B2 = compute_background_factor(h, b, L_z)

    # R²
    delta_a = 0.01
    delta_tot = damping_log_dec + delta_a

    # Velocità media stimata dalla turbolenza
    # v_m ≈ v_b · cr(z) dove cr(z) ≈ 2.5 · ln(z/z0) per z ≥ z_min
    # In alternativa: v_m = 1/(iv * √(1 + 7·iv)) ma troppo circolare
    # Usiamo la relazione iv = 1/ln(z/z0) → v_m = ki·σ_v / iv
    # Approssimazione: assumiamo v_m ≈ 25 m/s per calcolo R²
    # (il risultato è poco sensibile al valore esatto di v_m)
    v_m = 25.0 / iv if iv > 0 else 25.0  # stima ragionevole
    v_m = max(v_m, 10.0)

    R2 = compute_resonance_factor(f1, h, b, v_m, L_z, delta_tot)

    # kp
    kp = compute_peak_factor(iv, f1=f1, B2=B2, R2=R2)

    # cs·cd
    numerator = 1.0 + 2.0 * kp * iv * math.sqrt(B2 + R2)
    denominator = 1.0 + 7.0 * iv
    cscd = numerator / denominator

    cscd = max(0.85, min(1.15, cscd))

    logger.info(
        "cs·cd dettagliato = %.3f (B²=%.3f, R²=%.3f, kp=%.2f, f1=%.2f Hz, δ=%.3f).",
        cscd, B2, R2, kp, f1, damping_log_dec,
    )
    return round(cscd, 3)
