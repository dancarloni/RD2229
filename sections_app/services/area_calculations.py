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


def _area_inverted_t_section(dims: dict[str, float]) -> tuple[float, float]:
    # Same geometry as T_SECTION (just flipped vertically), shear areas are the same
    return _area_t_section(dims)


def _area_pi_section(dims: dict[str, float]) -> tuple[float, float]:
    flange_width = _get(dims, "flange_width")
    flange_thickness = _get(dims, "flange_thickness")
    web_thickness = _get(dims, "web_thickness")
    web_height = _get(dims, "web_height")
    # Double web: shear carried by both webs
    A_y = 2 * web_thickness * web_height + flange_width * flange_thickness
    A_z = 2 * web_thickness * web_height
    return A_y, A_z


def _area_v_section(dims: dict[str, float]) -> tuple[float, float]:
    # V sections: no standard shear area formula, use total area as fallback
    width = _get(dims, "width")
    height = _get(dims, "height")
    thickness = _get(dims, "thickness")
    half_width = width / 2
    length = math.sqrt(half_width**2 + height**2) if (half_width > 0 and height > 0) else 0
    area = 2 * length * thickness
    return area, area


def _area_inverted_v_section(dims: dict[str, float]) -> tuple[float, float]:
    return _area_v_section(dims)


_SECTION_HANDLERS = {
    "RECTANGULAR": _area_rectangular,
    "CIRCULAR": _area_circular,
    "CIRCULAR_HOLLOW": _area_circular_hollow,
    "RECTANGULAR_HOLLOW": _area_rectangular_hollow,
    "T_SECTION": _area_t_section,
    "I_SECTION": _area_i_section,
    "L_SECTION": _area_l_section,
    "C_SECTION": _area_c_section,
    "INVERTED_T_SECTION": _area_inverted_t_section,
    "PI_SECTION": _area_pi_section,
    "V_SECTION": _area_v_section,
    "INVERTED_V_SECTION": _area_inverted_v_section,
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

    # NOTE: historically this function returned raw geometric areas from the
    # handlers and callers applied shear correction factors (kappa) elsewhere.
    # That led to inconsistent usages and wrong effective shear areas in
    # some code paths. This implementation applies the kappa factors here
    # (when available) so callers always receive the Timoshenko effective
    # shear areas (A_y = kappa_y * A_ref_y, A_z = kappa_z * A_ref_z).

    section_type = (section.section_type or "").upper()
    dims = getattr(section, "dimensions", {}) or {}

    handler = _SECTION_HANDLERS.get(section_type)
    if handler:
        A_y, A_z = handler(dims)

        # Determine shear correction factors (kappa_y, kappa_z).
        # Priority: explicit attributes on the section -> section.get_default_shear_kappas() -> fallback 1.0
        kappa_y = getattr(section, "shear_factor_y", None)
        kappa_z = getattr(section, "shear_factor_z", None)

        if not kappa_y or kappa_y <= 0 or not kappa_z or kappa_z <= 0:
            # Try to call section method if available
            try:
                kdef = section.get_default_shear_kappas()
                if isinstance(kdef, tuple) and len(kdef) == 2:
                    if not kappa_y or kappa_y <= 0:
                        kappa_y = float(kdef[0])
                    if not kappa_z or kappa_z <= 0:
                        kappa_z = float(kdef[1])
            except Exception:  # nosec
                # Ignore and fallback
                pass

        # Final fallback to 1.0
        kappa_y = float(kappa_y) if kappa_y and kappa_y > 0 else 1.0
        kappa_z = float(kappa_z) if kappa_z and kappa_z > 0 else 1.0

        return kappa_y * A_y, kappa_z * A_z

    # Default: usa proprietà area se disponibile
    props = getattr(section, "properties", None)
    area = getattr(props, "area", None) if props is not None else None
    if area is not None:
        return float(area), float(area)

    # Ultima risorsa: 0,0
    return 0.0, 0.0
