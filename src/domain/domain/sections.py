from __future__ import annotations

import logging

from app.domain.models import VerificationInput

logger = logging.getLogger(__name__)


def _get_section_by_id_or_name(section_id: str, section_repository: object | None):
    if not section_repository or not section_id:
        return None
    try:
        if hasattr(section_repository, "find_by_id"):
            found = section_repository.find_by_id(section_id)
            if found is not None:
                return found
    except Exception:
        logger.exception("Errore ricerca sezione per id=%s", section_id)
    try:
        get_all = getattr(section_repository, "get_all_sections", None)
        if callable(get_all):
            for sec in get_all():
                if sec.id == section_id or sec.name == section_id:
                    return sec
    except Exception:
        logger.exception("Errore ricerca sezione per nome=%s", section_id)
    return None


def _extract_section_dimensions_cm(section) -> tuple[float, float] | None:
    if section is None:
        return None
    width = None
    height = None
    if hasattr(section, "width"):
        width = getattr(section, "width")
    if hasattr(section, "height"):
        height = getattr(section, "height")
    if (width is None or height is None) and hasattr(section, "dimensions"):
        dims = getattr(section, "dimensions") or {}
        width = width or dims.get("width") or dims.get("diameter")
        height = height or dims.get("height") or dims.get("diameter")
    if width and height:
        return float(width), float(height)
    return None


def get_section_geometry(
    _input: VerificationInput,
    section_repository: object | None,
    *,
    unit: str = "cm",
) -> tuple[float, float]:
    default_b, default_h = 30.0, 50.0
    if section_repository is None or not _input.section_id:
        logger.warning(
            "SectionRepository mancante o section_id vuoto; uso fallback %sx%s cm",
            default_b,
            default_h,
        )
        return (
            default_b * 10 if unit == "mm" else default_b,
            default_h * 10 if unit == "mm" else default_h,
        )

    section = _get_section_by_id_or_name(_input.section_id, section_repository)
    if section is None:
        logger.warning(
            "Sezione '%s' non trovata; uso fallback %sx%s cm",
            _input.section_id,
            default_b,
            default_h,
        )
        return (
            default_b * 10 if unit == "mm" else default_b,
            default_h * 10 if unit == "mm" else default_h,
        )

    dims = _extract_section_dimensions_cm(section)
    if dims is None:
        logger.warning(
            "Sezione '%s' senza dimensioni; uso fallback %sx%s cm",
            _input.section_id,
            default_b,
            default_h,
        )
        return (
            default_b * 10 if unit == "mm" else default_b,
            default_h * 10 if unit == "mm" else default_h,
        )

    b_cm, h_cm = dims
    if unit == "mm":
        return b_cm * 10.0, h_cm * 10.0
    return b_cm, h_cm
