"""Effetti aeroelastici – base per CNR-DT 207 R1/2018 Appendici O e P.

Modulo preparatorio per il calcolo degli effetti aeroelastici:
- Distacco di vortici (vortex shedding) — Appendice O
- Galloping, flutter, divergenza — Appendice P

Stato: PLACEHOLDER — le funzioni forniscono stime iniziali e flag di
verifica. L'implementazione completa richiede dati modali della struttura.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ===========================================================================
# Modelli dati
# ===========================================================================

@dataclass
class VortexSheddingResult:
    """Risultati della verifica a distacco di vortici (App. O).

    Attributes:
        is_susceptible: True se la struttura è suscettibile a vortex shedding.
        v_cr_ms: Velocità critica di distacco vortici [m/s].
        St: Numero di Strouhal.
        Re_cr: Reynolds critico stimato.
        y_max_m: Ampiezza massima stimata delle oscillazioni [m].
        check_ratio: v_cr / v_mean — se < 1.25 la struttura è a rischio.
        warnings: Avvisi e note.
    """

    is_susceptible: bool = False
    v_cr_ms: float = 0.0
    St: float = 0.2
    Re_cr: float = 0.0
    y_max_m: float = 0.0
    check_ratio: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass
class GallopingResult:
    """Risultati della verifica al galloping (App. P).

    Attributes:
        is_susceptible: True se la sezione è suscettibile al galloping.
        v_cg_ms: Velocità critica di galloping [m/s].
        a_G: Fattore di instabilità aerodinamica (∂cL/∂α + cD).
        check_ratio: v_cg / v_mean — se < 1.25 la sezione è a rischio.
        warnings: Avvisi e note.
    """

    is_susceptible: bool = False
    v_cg_ms: float = 0.0
    a_G: float = 0.0
    check_ratio: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass
class AeroelasticCheckResult:
    """Risultati complessivi delle verifiche aeroelastiche."""

    vortex_shedding: VortexSheddingResult = field(default_factory=VortexSheddingResult)
    galloping: GallopingResult = field(default_factory=GallopingResult)
    requires_detailed_analysis: bool = False
    warnings: list[str] = field(default_factory=list)


# ===========================================================================
# Numeri di Strouhal — CNR-DT 207 Tab. O.I
# ===========================================================================

# Strouhal number per sezioni tipiche
STROUHAL_NUMBERS: dict[str, float] = {
    "circular": 0.18,
    "square": 0.12,
    "rectangular_2_1": 0.06,     # b/d = 2
    "rectangular_1_2": 0.16,     # b/d = 0.5
    "H_section": 0.12,
    "I_section": 0.14,
    "L_section": 0.14,
    "plate": 0.14,
    "hexagonal": 0.12,
    "octagonal": 0.15,
}

# Sezioni suscettibili a galloping (∂cL/∂α < 0 → instabile)
GALLOPING_SUSCEPTIBLE_SECTIONS = frozenset({
    "square",
    "rectangular_2_1",
    "D_section",
    "L_section",
    "ice_coated_circular",
})


# ===========================================================================
# Verifica distacco vortici — CNR-DT 207 Appendice O
# ===========================================================================

def compute_critical_wind_speed(
    n1_hz: float,
    b_m: float,
    St: float = 0.18,
) -> float:
    """Calcola la velocità critica di distacco vortici.

    v_cr = n1 · b / St

    dove n1 è la frequenza propria del primo modo, b è la dimensione
    trasversale al vento, St è il numero di Strouhal.

    Args:
        n1_hz: Frequenza propria del primo modo [Hz].
        b_m: Dimensione trasversale al vento [m].
        St: Numero di Strouhal (default 0.18 per cilindro circolare).

    Returns:
        Velocità critica [m/s].
    """
    if St <= 0 or n1_hz <= 0:
        return 0.0
    return round(n1_hz * b_m / St, 2)


def get_strouhal_number(section_type: str) -> float:
    """Restituisce il numero di Strouhal per il tipo di sezione.

    Args:
        section_type: Tipo di sezione (es. "circular", "square", "plate").

    Returns:
        Numero di Strouhal St.
    """
    return STROUHAL_NUMBERS.get(section_type.lower(), 0.18)


def check_vortex_shedding(
    n1_hz: float,
    b_m: float,
    v_mean_ms: float,
    *,
    section_type: str = "circular",
    height_m: float = 0.0,
    damping_log_dec: float = 0.05,
    mass_per_length_kg_m: float = 0.0,
) -> VortexSheddingResult:
    """Verifica preliminare a distacco di vortici (CNR-DT 207 App. O).

    La struttura è suscettibile se v_cr < 1.25 · v_mean.

    Args:
        n1_hz: Frequenza propria primo modo [Hz].
        b_m: Dimensione trasversale al vento [m].
        v_mean_ms: Velocità media del vento alla sommità [m/s].
        section_type: Tipo di sezione trasversale.
        height_m: Altezza struttura [m] (per stima Reynolds).
        damping_log_dec: Decremento logaritmico di smorzamento δ.
        mass_per_length_kg_m: Massa per unità di lunghezza [kg/m].

    Returns:
        VortexSheddingResult con esito della verifica.
    """
    St = get_strouhal_number(section_type)
    v_cr = compute_critical_wind_speed(n1_hz, b_m, St)

    warnings: list[str] = []

    if v_cr <= 0 or v_mean_ms <= 0:
        warnings.append("Dati insufficienti per verifica vortex shedding.")
        return VortexSheddingResult(warnings=warnings)

    check_ratio = v_cr / v_mean_ms
    is_susceptible = check_ratio < 1.25

    # Reynolds critico stimato
    nu_air = 1.5e-5  # viscosità cinematica aria [m²/s]
    Re_cr = round(v_cr * b_m / nu_air, 0) if b_m > 0 else 0.0

    # Stima ampiezza oscillazioni (metodo semplificato CNR-DT 207 O.3)
    y_max = 0.0
    if is_susceptible and mass_per_length_kg_m > 0 and damping_log_dec > 0:
        # Scruton number Sc = 2·δ·m / (ρ·b²)
        rho_air = 1.25  # kg/m³
        Sc = 2.0 * damping_log_dec * mass_per_length_kg_m / (rho_air * b_m ** 2)

        # Stima semplificata: y_max/b ≈ K_w · c_lat / (Sc · St²)
        # Con K_w ≈ 0.5 (fattore di correlazione), c_lat ≈ 0.2 (cilindro)
        c_lat = 0.2 if section_type == "circular" else 0.5
        K_w = 0.5

        if Sc > 0:
            y_over_b = K_w * c_lat / (Sc * St ** 2)
            y_max = round(y_over_b * b_m, 4)
            warnings.append(
                f"Scruton number Sc = {Sc:.1f}; "
                f"ampiezza stimata y_max = {y_max * 1000:.1f} mm "
                f"(stima semplificata, verificare con App. O dettagliata)."
            )

    if is_susceptible:
        warnings.append(
            f"v_cr = {v_cr:.1f} m/s < 1.25·v_mean = {1.25 * v_mean_ms:.1f} m/s → "
            "struttura suscettibile a distacco di vortici."
        )
    else:
        warnings.append(
            f"v_cr = {v_cr:.1f} m/s ≥ 1.25·v_mean = {1.25 * v_mean_ms:.1f} m/s → "
            "verifica vortex shedding soddisfatta."
        )

    return VortexSheddingResult(
        is_susceptible=is_susceptible,
        v_cr_ms=v_cr,
        St=St,
        Re_cr=Re_cr,
        y_max_m=y_max,
        check_ratio=round(check_ratio, 3),
        warnings=warnings,
    )


# ===========================================================================
# Verifica galloping — CNR-DT 207 Appendice P
# ===========================================================================

def check_galloping(
    n1_hz: float,
    b_m: float,
    v_mean_ms: float,
    *,
    section_type: str = "circular",
    mass_per_length_kg_m: float = 0.0,
    damping_log_dec: float = 0.05,
    a_G: float | None = None,
) -> GallopingResult:
    """Verifica preliminare al galloping (CNR-DT 207 App. P).

    v_cg = 2·Sc·n1·b / a_G

    dove Sc è il numero di Scruton e a_G è il fattore di instabilità.

    La struttura è suscettibile se v_cg < 1.25 · v_mean.

    Args:
        n1_hz: Frequenza propria primo modo [Hz].
        b_m: Dimensione trasversale [m].
        v_mean_ms: Velocità media alla sommità [m/s].
        section_type: Tipo di sezione.
        mass_per_length_kg_m: Massa per unità di lunghezza [kg/m].
        damping_log_dec: Decremento logaritmico δ.
        a_G: Fattore di instabilità (override). Se None, stima da sezione.

    Returns:
        GallopingResult con esito della verifica.
    """
    warnings: list[str] = []

    # Verifica se la sezione è suscettibile
    is_type_susceptible = section_type.lower() in GALLOPING_SUSCEPTIBLE_SECTIONS
    if not is_type_susceptible and a_G is None:
        warnings.append(
            f"Sezione '{section_type}' non tipicamente suscettibile a galloping."
        )
        return GallopingResult(
            is_susceptible=False,
            warnings=warnings,
        )

    # Fattore di instabilità
    if a_G is None:
        # Valori indicativi per sezioni tipiche
        a_G_table: dict[str, float] = {
            "square": 2.7,
            "rectangular_2_1": 0.5,
            "D_section": 1.0,
            "L_section": 3.0,
            "ice_coated_circular": 1.0,
        }
        a_G = a_G_table.get(section_type.lower(), 2.0)

    if mass_per_length_kg_m <= 0 or damping_log_dec <= 0 or b_m <= 0:
        warnings.append(
            "Dati insufficienti (massa, smorzamento o dimensione) "
            "per calcolo velocità critica di galloping."
        )
        return GallopingResult(
            is_susceptible=is_type_susceptible,
            a_G=a_G,
            warnings=warnings,
        )

    rho_air = 1.25  # kg/m³
    Sc = 2.0 * damping_log_dec * mass_per_length_kg_m / (rho_air * b_m ** 2)

    # Velocità critica di galloping
    v_cg = 2.0 * Sc * n1_hz * b_m / a_G if a_G > 0 else 0.0
    v_cg = round(v_cg, 2)

    check_ratio = v_cg / v_mean_ms if v_mean_ms > 0 else float("inf")
    is_susceptible = check_ratio < 1.25

    if is_susceptible:
        warnings.append(
            f"v_cg = {v_cg:.1f} m/s < 1.25·v_mean = {1.25 * v_mean_ms:.1f} m/s → "
            "struttura suscettibile a galloping."
        )
    else:
        warnings.append(
            f"v_cg = {v_cg:.1f} m/s ≥ 1.25·v_mean = {1.25 * v_mean_ms:.1f} m/s → "
            "verifica galloping soddisfatta."
        )

    return GallopingResult(
        is_susceptible=is_susceptible,
        v_cg_ms=v_cg,
        a_G=a_G,
        check_ratio=round(check_ratio, 3),
        warnings=warnings,
    )


# ===========================================================================
# Verifica complessiva
# ===========================================================================

def check_aeroelastic_effects(
    n1_hz: float,
    b_m: float,
    v_mean_ms: float,
    *,
    section_type: str = "circular",
    height_m: float = 0.0,
    mass_per_length_kg_m: float = 0.0,
    damping_log_dec: float = 0.05,
) -> AeroelasticCheckResult:
    """Verifica complessiva degli effetti aeroelastici (CNR-DT 207 App. O+P).

    Esegue le verifiche a:
    1. Distacco di vortici (vortex shedding)
    2. Galloping

    Args:
        n1_hz: Frequenza propria primo modo [Hz].
        b_m: Dimensione trasversale al vento [m].
        v_mean_ms: Velocità media del vento alla sommità [m/s].
        section_type: Tipo di sezione trasversale.
        height_m: Altezza struttura [m].
        mass_per_length_kg_m: Massa per unità di lunghezza [kg/m].
        damping_log_dec: Decremento logaritmico di smorzamento δ.

    Returns:
        AeroelasticCheckResult con risultati di tutte le verifiche.
    """
    vs = check_vortex_shedding(
        n1_hz, b_m, v_mean_ms,
        section_type=section_type,
        height_m=height_m,
        damping_log_dec=damping_log_dec,
        mass_per_length_kg_m=mass_per_length_kg_m,
    )

    gal = check_galloping(
        n1_hz, b_m, v_mean_ms,
        section_type=section_type,
        mass_per_length_kg_m=mass_per_length_kg_m,
        damping_log_dec=damping_log_dec,
    )

    requires_detailed = vs.is_susceptible or gal.is_susceptible
    warnings = []

    if requires_detailed:
        warnings.append(
            "Struttura suscettibile a effetti aeroelastici: "
            "è necessaria un'analisi dettagliata secondo CNR-DT 207 App. O/P."
        )

    return AeroelasticCheckResult(
        vortex_shedding=vs,
        galloping=gal,
        requires_detailed_analysis=requires_detailed,
        warnings=warnings,
    )
