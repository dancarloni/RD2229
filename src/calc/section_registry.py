"""Registry delle sezioni geometriche.

Memorizza metadati geometrici (area, inerzia, moduli, kappa) per sezioni
note. Integra con:
- ``src/core_calculus/section_calculations.py`` per calcoli completi (polygon-based)
- ``src/methods/section_fiber.py`` per proprietà fibra (width_at_depth)
- ``src/calc/shear_area_registry.py`` per aree a taglio

Per sezioni generiche, usa ``compute_section_properties_from_geometry()``
dal modulo core. Questo registry offre un livello di accesso rapido a
sezioni preregistrate o caricate da legacy JSON.

Unità: cm, cm², cm⁴.
"""

from __future__ import annotations

import json
import logging
import math
import os
from typing import Any

logger = logging.getLogger(__name__)

SECTION_REGISTRY: dict[str, dict[str, Any]] = {}


def register_section(shape_id: str, metadata: dict[str, Any]) -> None:
    """Registra una sezione nel registry. shape_id deve essere non vuoto."""
    if not shape_id:
        logger.warning("shape_id vuoto: sezione ignorata.")
        return
    if shape_id in SECTION_REGISTRY:
        logger.debug("Sovrascrittura sezione '%s'.", shape_id)
    SECTION_REGISTRY[shape_id] = metadata


def get_section_metadata(shape_id: str) -> dict[str, Any] | None:
    """Restituisce il metadata associato alla sezione."""
    return SECTION_REGISTRY.get(shape_id)


def list_sections() -> list[str]:
    """Restituisce tutti gli shape_id registrati."""
    return list(SECTION_REGISTRY.keys())


def remove_section(shape_id: str) -> bool:
    """Rimuove una sezione. Restituisce True se trovata."""
    if shape_id in SECTION_REGISTRY:
        del SECTION_REGISTRY[shape_id]
        return True
    return False


def clear_registry() -> None:
    """Svuota il registry (utile per i test)."""
    SECTION_REGISTRY.clear()


# ======================================================================
# CALCOLO PROPRIETÀ PER FORME BASE
# ======================================================================


def compute_rectangular(b_cm: float, h_cm: float) -> dict[str, Any]:
    """Proprietà geometriche di una sezione rettangolare [cm]."""
    A = b_cm * h_cm
    Ix = b_cm * h_cm**3 / 12.0
    Iy = h_cm * b_cm**3 / 12.0
    Wx = Ix / (h_cm / 2.0) if h_cm > 0 else 0.0
    Wy = Iy / (b_cm / 2.0) if b_cm > 0 else 0.0

    return {
        "id": f"Rect-{b_cm:.0f}x{h_cm:.0f}",
        "section_type": "RECTANGULAR",
        "width_cm": b_cm, "height_cm": h_cm,
        "area_cm2": A,
        "Ix": round(Ix, 2), "Iy": round(Iy, 2),
        "Wx": round(Wx, 2), "Wy": round(Wy, 2),
        "inertia_cm4": {"Ix": round(Ix, 2), "Iy": round(Iy, 2)},
        "kappa_x": 5.0 / 6.0, "kappa_y": 5.0 / 6.0,
        "x_G": b_cm / 2.0, "y_G": h_cm / 2.0,
    }


def compute_circular(d_cm: float) -> dict[str, Any]:
    """Proprietà geometriche di una sezione circolare [cm]."""
    r = d_cm / 2.0
    A = math.pi * r**2
    I = math.pi * r**4 / 4.0
    W = math.pi * r**3 / 4.0

    return {
        "id": f"Circle-D{d_cm:.0f}",
        "section_type": "CIRCULAR",
        "diameter_cm": d_cm,
        "width_cm": d_cm, "height_cm": d_cm,
        "area_cm2": round(A, 2),
        "Ix": round(I, 2), "Iy": round(I, 2),
        "Wx": round(W, 2), "Wy": round(W, 2),
        "inertia_cm4": {"Ix": round(I, 2), "Iy": round(I, 2)},
        "kappa_x": 0.9, "kappa_y": 0.9,
        "x_G": r, "y_G": r,
    }


def compute_t_section(
    b_f_cm: float, h_f_cm: float, b_w_cm: float, h_w_cm: float,
) -> dict[str, Any]:
    """Proprietà geometriche di una sezione a T [cm]."""
    h_tot = h_f_cm + h_w_cm
    A_f = b_f_cm * h_f_cm
    A_w = b_w_cm * h_w_cm
    A = A_f + A_w

    y_f = h_w_cm + h_f_cm / 2.0
    y_w = h_w_cm / 2.0
    y_G = (A_f * y_f + A_w * y_w) / A if A > 0 else h_tot / 2.0

    Ix_f = b_f_cm * h_f_cm**3 / 12.0 + A_f * (y_f - y_G)**2
    Ix_w = b_w_cm * h_w_cm**3 / 12.0 + A_w * (y_w - y_G)**2
    Ix = Ix_f + Ix_w
    Iy = h_f_cm * b_f_cm**3 / 12.0 + h_w_cm * b_w_cm**3 / 12.0

    Wx_sup = Ix / (h_tot - y_G) if (h_tot - y_G) > 0 else 0.0
    Wx_inf = Ix / y_G if y_G > 0 else 0.0

    # Kappa taglio anima
    kappa_web = (b_w_cm * h_w_cm) / A if A > 0 else 5.0 / 6.0

    return {
        "id": f"T-{b_f_cm:.0f}x{h_tot:.0f}",
        "section_type": "T_SECTION",
        "width_cm": b_f_cm, "height_cm": h_tot,
        "flange_width_cm": b_f_cm, "flange_thickness_cm": h_f_cm,
        "web_width_cm": b_w_cm, "web_height_cm": h_w_cm,
        "area_cm2": round(A, 2),
        "Ix": round(Ix, 2), "Iy": round(Iy, 2),
        "Wx_sup": round(Wx_sup, 2), "Wx_inf": round(Wx_inf, 2),
        "inertia_cm4": {"Ix": round(Ix, 2), "Iy": round(Iy, 2)},
        "kappa_x": round(kappa_web, 4), "kappa_y": 5.0 / 6.0,
        "x_G": b_f_cm / 2.0, "y_G": round(y_G, 2),
    }


def compute_i_section(
    b_f_cm: float, h_f_cm: float, b_w_cm: float, h_w_cm: float,
) -> dict[str, Any]:
    """Proprietà geometriche di una sezione a doppia T (I) simmetrica [cm]."""
    h_tot = 2 * h_f_cm + h_w_cm
    A_f = b_f_cm * h_f_cm
    A_w = b_w_cm * h_w_cm
    A = 2 * A_f + A_w
    y_G = h_tot / 2.0

    d_f = h_w_cm / 2.0 + h_f_cm / 2.0
    Ix = (b_w_cm * h_w_cm**3 / 12.0 +
          2 * (b_f_cm * h_f_cm**3 / 12.0 + A_f * d_f**2))
    Iy = (h_w_cm * b_w_cm**3 / 12.0 +
          2 * h_f_cm * b_f_cm**3 / 12.0)
    Wx = Ix / (h_tot / 2.0) if h_tot > 0 else 0.0

    kappa_web = (b_w_cm * h_w_cm) / A if A > 0 else 5.0 / 6.0

    return {
        "id": f"I-{b_f_cm:.0f}x{h_tot:.0f}",
        "section_type": "I_SECTION",
        "width_cm": b_f_cm, "height_cm": h_tot,
        "flange_width_cm": b_f_cm, "flange_thickness_cm": h_f_cm,
        "web_width_cm": b_w_cm, "web_height_cm": h_w_cm,
        "area_cm2": round(A, 2),
        "Ix": round(Ix, 2), "Iy": round(Iy, 2), "Wx": round(Wx, 2),
        "inertia_cm4": {"Ix": round(Ix, 2), "Iy": round(Iy, 2)},
        "kappa_x": round(kappa_web, 4), "kappa_y": 5.0 / 6.0,
        "x_G": b_f_cm / 2.0, "y_G": round(y_G, 2),
    }


# ======================================================================
# CARICAMENTO DA LEGACY
# ======================================================================


def load_sections_from_legacy(path: str | None = None) -> int:
    """Carica sezioni dal file legacy sections.json.

    Args:
        path: percorso al file JSON. Se None, usa il default.

    Returns:
        Numero di sezioni caricate.
    """
    if path is None:
        path = os.path.join(
            os.path.dirname(__file__), "..", "legacy", "sections.json"
        )

    try:
        with open(path, encoding="utf-8") as f:
            sections = json.load(f)
    except FileNotFoundError:
        logger.debug("File sezioni legacy non trovato: '%s'.", path)
        return 0
    except Exception as exc:
        logger.warning("Errore caricamento sezioni legacy: %s", exc)
        return 0

    count = 0
    for sec in sections:
        sid = sec.get("id") or sec.get("name", "")
        if not sid:
            continue

        metadata: dict[str, Any] = {
            "id": sid,
            "section_type": sec.get("section_type", "UNKNOWN"),
            "area_cm2": sec.get("area", 0.0),
            "inertia_cm4": {"Ix": sec.get("Ix", 0.0), "Iy": sec.get("Iy", 0.0)},
            "kappa_x": sec.get("kappa_y", 5.0 / 6.0),
            "kappa_y": sec.get("kappa_z", 5.0 / 6.0),
            "x_G": sec.get("x_G", 0.0),
            "y_G": sec.get("y_G", 0.0),
            "Ix": sec.get("Ix", 0.0),
            "Iy": sec.get("Iy", 0.0),
        }
        if sec.get("width"):
            metadata["width_cm"] = sec["width"]
        if sec.get("height"):
            metadata["height_cm"] = sec["height"]
        if sec.get("diameter"):
            metadata["diameter_cm"] = sec["diameter"]
        if sec.get("flange_width"):
            metadata["flange_width_cm"] = sec["flange_width"]
            metadata["flange_thickness_cm"] = sec.get("flange_thickness", 0.0)
            metadata["web_width_cm"] = sec.get("web_thickness", 0.0)
            metadata["web_height_cm"] = sec.get("web_height", 0.0)

        register_section(sid, metadata)
        count += 1

    logger.info("Caricate %d sezioni da legacy '%s'.", count, path)
    return count


def bootstrap_default_sections() -> None:
    """Registra sezioni standard calcolate."""
    defaults = [
        compute_rectangular(30.0, 50.0),
        compute_rectangular(40.0, 40.0),
        compute_rectangular(25.0, 50.0),
        compute_rectangular(30.0, 60.0),
        compute_circular(30.0),
        compute_circular(40.0),
        compute_t_section(60.0, 10.0, 25.0, 40.0),
        compute_t_section(80.0, 12.0, 30.0, 48.0),
        compute_i_section(20.0, 1.5, 1.0, 27.0),
    ]
    for sec in defaults:
        register_section(sec["id"], sec)
