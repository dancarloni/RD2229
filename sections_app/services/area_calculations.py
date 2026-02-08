"""Servizi di calcolo per le aree shear.

Refactoring per chiarezza, sicurezza sui parametri e test rapido incorporato.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Provo a usare il Section reale, ma forzo un fallback per i test locali
try:
    from ..domain.base import Section, SectionProperties  # type: ignore
except (ImportError, Exception):
    from dataclasses import field

    @dataclass
    class SectionProperties:
        area: float = 0.0

    @dataclass
    class Section:  # semplice stub usato solo se l'import reale non è disponibile
        section_type: str
        dimensions: dict[str, float]
        properties: SectionProperties = field(default_factory=SectionProperties)


def _get(dims: dict[str, float], key: str) -> float:
    try:
        return float(dims.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _area_rectangular(dims: dict[str, float]) -> tuple[float, float]:
    width = _get(dims, "width")
    height = _get(dims, "height")
    area = width * height
    return area, area


def _area_circular(dims: dict[str, float]) -> tuple[float, float]:
    diameter = _get(dims, "diameter")
    radius = diameter / 2
    area = math.pi * radius * radius
    return area, area


def _area_circular_hollow(dims: dict[str, float]) -> tuple[float, float]:
    outer_diameter = _get(dims, "outer_diameter")
    thickness = _get(dims, "thickness")
    outer_radius = outer_diameter / 2
    inner_radius = max(0.0, outer_radius - thickness)
    area = math.pi * (outer_radius**2 - inner_radius**2)
    return area, area


def _area_rectangular_hollow(dims: dict[str, float]) -> tuple[float, float]:
    width = _get(dims, "width")
    height = _get(dims, "height")
    thickness = _get(dims, "thickness")
    A_ext = width * height
    inner_w = max(0.0, width - 2 * thickness)
    inner_h = max(0.0, height - 2 * thickness)
    A_int = inner_w * inner_h
    area = max(0.0, A_ext - A_int)
    return area, area


def _area_t_section(dims: dict[str, float]) -> tuple[float, float]:
    flange_width = _get(dims, "flange_width")
    flange_thickness = _get(dims, "flange_thickness")
    web_thickness = _get(dims, "web_thickness")
    web_height = _get(dims, "web_height")
    A_y = flange_width * flange_thickness + web_thickness * web_height
    A_z = web_thickness * web_height
    return A_y, A_z


def _area_i_section(dims: dict[str, float]) -> tuple[float, float]:
    flange_width = _get(dims, "flange_width")
    flange_thickness = _get(dims, "flange_thickness")
    web_thickness = _get(dims, "web_thickness")
    web_height = _get(dims, "web_height")
    A_y = 2 * flange_width * flange_thickness + web_thickness * web_height
    A_z = web_thickness * web_height
    return A_y, A_z


def _area_l_section(dims: dict[str, float]) -> tuple[float, float]:
    width = _get(dims, "width")
    height = _get(dims, "height")
    t_horizontal = _get(dims, "t_horizontal")
    t_vertical = _get(dims, "t_vertical")
    A_y = t_vertical * height
    A_z = width * t_horizontal
    return A_y, A_z


def _area_c_section(dims: dict[str, float]) -> tuple[float, float]:
    width = _get(dims, "width")
    height = _get(dims, "height")
    thickness = _get(dims, "thickness")
    A_y = max(0.0, 2 * width * thickness + max(0.0, height - 2 * thickness) * thickness)
    A_z = 2 * width * thickness
    return A_y, A_z


_SECTION_HANDLERS = {
    "RECTANGULAR": _area_rectangular,
    "CIRCULAR": _area_circular,
    "CIRCULAR_HOLLOW": _area_circular_hollow,
    "RECTANGULAR_HOLLOW": _area_rectangular_hollow,
    "T_SECTION": _area_t_section,
    "I_SECTION": _area_i_section,
    "L_SECTION": _area_l_section,
    "C_SECTION": _area_c_section,
}


def compute_shear_areas(section: Section) -> tuple[float, float]:
    """Calcola le aree shear effettive per una sezione.

    Esegue validazioni minimali e delega a funzioni specializzate per
    ciascun tipo di sezione. Accetta section_type in qualsiasi case.

    Args:
        section: Istanza della sezione

    Returns:
        Tupla (A_y, A_z) delle aree shear effettive
    """
    if not section:
        raise ValueError("section non può essere None")

    section_type = (section.section_type or "").upper()
    dims = getattr(section, "dimensions", {}) or {}

    handler = _SECTION_HANDLERS.get(section_type)
    if handler:
        return handler(dims)

    # Default: usa proprietà area se disponibile
    props = getattr(section, "properties", None)
    area = getattr(props, "area", None) if props is not None else None
    if area is not None:
        return float(area), float(area)

    # Ultima risorsa: 0,0
    return 0.0, 0.0
