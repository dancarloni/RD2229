"""Registry fattori di taglio per sezione.

Ogni sezione ha i propri fattori kappa (area a taglio A_s = kappa × A).
I valori di default derivano dalla letteratura (Timoshenko, Cowper 1966,
Pilkey 2002) e sono SEMPRE sovrascrivibili dall'utente tramite i campi
``kappa_x`` e ``kappa_y`` dell'oggetto sezione.

Gerarchia di priorità per kappa:
1. Valore utente esplicito (kappa_x, kappa_y sull'oggetto sezione)
2. Strategia registrata per shape_id nel registry
3. Default da letteratura per section_type
4. Fallback universale DEFAULT_KAPPA = 5/6

Unità: cm, cm².
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

ShearAreaFunction = Callable[[Any], tuple[float, float]]

# ======================================================================
# COSTANTI DA LETTERATURA
# ======================================================================

DEFAULT_KAPPA: float = 5.0 / 6.0
"""Rettangolo pieno — Timoshenko (1921), valore esatto 5/6 ≈ 0.8333."""

CIRCLE_KAPPA: float = 6.0 / 7.0
"""Cerchio pieno — Cowper (1966), 6/7 ≈ 0.8571.
Nota: il valore 0.9 è anche usato in pratica (approssimazione ingegneristica)."""

HOLLOW_CIRCLE_KAPPA: float = 0.5
"""Tubo circolare — Pilkey (2002), dipende da t/R; 0.5 è valore conservativo."""

T_SECTION_KAPPA: float = 1.0
"""Sezione a T — il taglio è assunto interamente dall'anima: A_s = A_anima.
In mancanza di dati sull'anima, kappa = A_anima/A_totale."""

I_SECTION_KAPPA: float = 1.0
"""Sezione a doppia T — idem: A_s = A_anima (Pilkey 2002)."""

# Mappa section_type → kappa default da letteratura
KAPPA_DEFAULTS: dict[str, float] = {
    "RECTANGULAR": DEFAULT_KAPPA,
    "CIRCULAR": CIRCLE_KAPPA,
    "CIRCULAR_HOLLOW": HOLLOW_CIRCLE_KAPPA,
    "RECTANGULAR_HOLLOW": DEFAULT_KAPPA,
    "T_SECTION": T_SECTION_KAPPA,
    "INVERTED_T_SECTION": T_SECTION_KAPPA,
    "I_SECTION": I_SECTION_KAPPA,
    "PI_SECTION": T_SECTION_KAPPA,
    "C_SECTION": I_SECTION_KAPPA,
    "L_SECTION": DEFAULT_KAPPA,
    "V_SECTION": DEFAULT_KAPPA,
    "INVERTED_V_SECTION": DEFAULT_KAPPA,
}


# ======================================================================
# REGISTRY DELLE STRATEGIE
# ======================================================================

SHEAR_AREA_STRATEGIES: dict[str, ShearAreaFunction] = {}


def register_shear_area_strategy(shape_id: str, func: ShearAreaFunction) -> None:
    """Registra una strategia di calcolo dell'area a taglio per shape_id."""
    if not shape_id:
        return
    SHEAR_AREA_STRATEGIES[shape_id] = func


# ======================================================================
# STRATEGIE BUILT-IN
# ======================================================================


def _rectangular_shear_area(section: Any) -> tuple[float, float]:
    """Rettangolo pieno: A_s = 5/6 × A (Timoshenko)."""
    A = getattr(section, "area_cm2", 0.0)
    kx = getattr(section, "kappa_x", DEFAULT_KAPPA)
    ky = getattr(section, "kappa_y", DEFAULT_KAPPA)
    return (kx * A, ky * A)


def _circular_shear_area(section: Any) -> tuple[float, float]:
    """Cerchio pieno: A_s = 6/7 × A (Cowper 1966)."""
    A = getattr(section, "area_cm2", 0.0)
    kx = getattr(section, "kappa_x", CIRCLE_KAPPA)
    ky = getattr(section, "kappa_y", CIRCLE_KAPPA)
    return (kx * A, ky * A)


def _web_based_shear_area(section: Any) -> tuple[float, float]:
    """Sezione con anima (T, I, C, PI): A_sx = kappa × b_w × h_w.

    Se i dati dell'anima non sono disponibili, usa kappa × A_totale.
    kappa utente sovrascrive sempre.
    """
    bw = getattr(section, "web_width_cm", 0.0) or getattr(section, "web_thickness", 0.0)
    hw = getattr(section, "web_height_cm", 0.0) or getattr(section, "web_height", 0.0)

    if bw > 0 and hw > 0:
        A_web = bw * hw
        kx = getattr(section, "kappa_x", None)
        if kx is not None:
            A = getattr(section, "area_cm2", A_web)
            return (kx * A, kx * A)
        return (A_web, A_web)

    # Fallback: kappa × area totale
    A = getattr(section, "area_cm2", 0.0)
    kx = getattr(section, "kappa_x", DEFAULT_KAPPA)
    ky = getattr(section, "kappa_y", DEFAULT_KAPPA)
    return (kx * A, ky * A)


def _hollow_circle_shear_area(section: Any) -> tuple[float, float]:
    """Tubo circolare: A_s ≈ 0.5 × A (conservativo, Pilkey 2002)."""
    A = getattr(section, "area_cm2", 0.0)
    kx = getattr(section, "kappa_x", HOLLOW_CIRCLE_KAPPA)
    ky = getattr(section, "kappa_y", HOLLOW_CIRCLE_KAPPA)
    return (kx * A, ky * A)


# Registrazione strategie built-in
register_shear_area_strategy("rectangle", _rectangular_shear_area)
register_shear_area_strategy("RECTANGULAR", _rectangular_shear_area)
register_shear_area_strategy("circle", _circular_shear_area)
register_shear_area_strategy("CIRCULAR", _circular_shear_area)
register_shear_area_strategy("CIRCULAR_HOLLOW", _hollow_circle_shear_area)
register_shear_area_strategy("t_section", _web_based_shear_area)
register_shear_area_strategy("T_SECTION", _web_based_shear_area)
register_shear_area_strategy("INVERTED_T_SECTION", _web_based_shear_area)
register_shear_area_strategy("i_section", _web_based_shear_area)
register_shear_area_strategy("I_SECTION", _web_based_shear_area)
register_shear_area_strategy("PI_SECTION", _web_based_shear_area)
register_shear_area_strategy("C_SECTION", _web_based_shear_area)


# ======================================================================
# FUNZIONE GENERALE DI CALCOLO
# ======================================================================


def compute_shear_area(section: Any) -> tuple[float, float]:
    """Calcola (A_sx, A_sy) in cm² per una sezione arbitraria.

    Priorità:
    1. kappa_x/kappa_y espliciti sull'oggetto sezione (utente)
    2. Strategia registrata per shape_id
    3. Strategia registrata per section_type
    4. Default da KAPPA_DEFAULTS per section_type
    5. Fallback universale DEFAULT_KAPPA
    """
    shape_id: str | None = getattr(section, "shape_id", None)
    section_type: str | None = getattr(section, "section_type", None)

    # 1. Controlla se l'utente ha impostato kappa espliciti
    user_kx = getattr(section, "kappa_x", None)
    user_ky = getattr(section, "kappa_y", None)
    has_user_override = (user_kx is not None) or (user_ky is not None)

    # 2. Cerca strategia registrata
    if shape_id and shape_id in SHEAR_AREA_STRATEGIES:
        return SHEAR_AREA_STRATEGIES[shape_id](section)

    # 3. Cerca strategia per section_type
    if section_type and section_type in SHEAR_AREA_STRATEGIES:
        return SHEAR_AREA_STRATEGIES[section_type](section)

    # 4/5. Fallback con kappa da utente o da letteratura
    A = getattr(section, "area_cm2", 0.0)
    if has_user_override:
        kx = user_kx if user_kx is not None else DEFAULT_KAPPA
        ky = user_ky if user_ky is not None else DEFAULT_KAPPA
    elif section_type and section_type in KAPPA_DEFAULTS:
        k = KAPPA_DEFAULTS[section_type]
        kx, ky = k, k
    else:
        kx, ky = DEFAULT_KAPPA, DEFAULT_KAPPA

    logger.debug(
        "Shear area fallback per '%s' (type=%s): kappa=%.4f, A=%.1f",
        shape_id,
        section_type,
        kx,
        A,
    )
    return (kx * A, ky * A)


def get_default_kappa(section_type: str) -> float:
    """Restituisce il kappa default da letteratura per un section_type."""
    return KAPPA_DEFAULTS.get(section_type, DEFAULT_KAPPA)
