"""Friction – forze di attrito del vento su superfici.

Calcola le forze di attrito F_fr = c_fr · q_p(z_e) · A_fr
secondo NTC2018 §3.3.4 / EN 1991-1-4 §7.5.

Tre classi di rugosità superficiale:
- SMOOTH (0.01): vetro, acciaio, calcestruzzo liscio
- ROUGH (0.02): laterizio, calcestruzzo grezzo
- VERY_ROUGH (0.04): lamiera grecata, ondulato
"""

from __future__ import annotations

import logging

from src.wind.models import FRICTION_CLASSES
from src.wind.outputs import FrictionForce
from src.wind.zone_loader import load_coefficient_file

logger = logging.getLogger(__name__)


def get_friction_coefficient(
    friction_class: str,
    *,
    override: float | None = None,
) -> float:
    """Coefficiente di attrito c_fr per la classe di rugosità.

    Args:
        friction_class: "SMOOTH", "ROUGH", "VERY_ROUGH".
        override: Override utente.

    Returns:
        Coefficiente c_fr.
    """
    if override is not None:
        return override

    c_fr = FRICTION_CLASSES.get(friction_class.upper())
    if c_fr is not None:
        return c_fr

    # Prova dal JSON
    data = load_coefficient_file("friction.json")
    classes = data.get("classes", {})
    entry = classes.get(friction_class.upper(), {})
    c_fr = entry.get("c_fr")
    if c_fr is not None:
        return c_fr

    logger.warning("Classe attrito '%s' non riconosciuta; uso SMOOTH (0.01).", friction_class)
    return 0.01


def compute_friction_force(
    q_p_kN_m2: float,
    friction_class: str,
    area_m2: float,
    *,
    surface_id: str = "",
    override_cfr: float | None = None,
) -> FrictionForce:
    """Calcola la forza di attrito su una superficie.

    F_fr = c_fr · q_p(z_e) · A_fr

    dove A_fr è l'area delle superfici parallele alla direzione del vento.

    Args:
        q_p_kN_m2: Pressione di picco alla quota di riferimento [kN/m²].
        friction_class: Classe di rugosità.
        area_m2: Area di attrito [m²].
        surface_id: Identificativo della superficie.
        override_cfr: Override del coefficiente c_fr.

    Returns:
        FrictionForce con i risultati.
    """
    c_fr = get_friction_coefficient(friction_class, override=override_cfr)
    F_fr = c_fr * q_p_kN_m2 * area_m2

    return FrictionForce(
        surface_id=surface_id or f"friction_{friction_class.lower()}",
        c_fr=c_fr,
        area_m2=area_m2,
        q_p_kN_m2=q_p_kN_m2,
        F_fr_kN=round(F_fr, 4),
    )


def compute_building_friction(
    h_m: float,
    b_m: float,
    d_m: float,
    q_p_kN_m2: float,
    friction_class: str = "SMOOTH",
    *,
    override_cfr: float | None = None,
) -> list[FrictionForce]:
    """Calcola le forze di attrito sulle superfici di un edificio.

    Le superfici soggette ad attrito sono quelle parallele al vento:
    - 2 pareti laterali (altezza × profondità)
    - Copertura (larghezza × profondità) se parallela al vento

    EC1 §7.5(3): l'attrito si considera solo se d > min(2h, 4b).

    Args:
        h_m: Altezza edificio [m].
        b_m: Larghezza perpendicolare al vento [m].
        d_m: Profondità parallela al vento [m].
        q_p_kN_m2: Pressione di picco [kN/m²].
        friction_class: Classe di rugosità.
        override_cfr: Override c_fr.

    Returns:
        Lista di FrictionForce (vuota se d ≤ min(2h, 4b)).
    """
    # Verifica se l'attrito è significativo
    d_limit = min(2.0 * h_m, 4.0 * b_m)
    if d_m <= d_limit:
        return []

    # Area soggetta ad attrito: solo la porzione oltre d_limit
    d_friction = d_m - d_limit
    forces = []

    # Pareti laterali (2 pareti)
    area_walls = 2.0 * h_m * d_friction
    forces.append(
        compute_friction_force(
            q_p_kN_m2,
            friction_class,
            area_walls,
            surface_id="walls_lateral",
            override_cfr=override_cfr,
        )
    )

    # Copertura
    area_roof = b_m * d_friction
    forces.append(
        compute_friction_force(
            q_p_kN_m2,
            friction_class,
            area_roof,
            surface_id="roof",
            override_cfr=override_cfr,
        )
    )

    return forces
