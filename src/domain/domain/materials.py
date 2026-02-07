from __future__ import annotations

import logging
from typing import Iterable, Optional

from app.domain.models import VerificationInput  # type: ignore[import]

logger = logging.getLogger(__name__)


def _get_material_by_name(material_repository: Optional[object], name: str):
    if not material_repository or not name:
        return None
    try:
        if hasattr(material_repository, "find_by_name"):
            return material_repository.find_by_name(name)
        if hasattr(material_repository, "get_by_name"):
            return material_repository.get_by_name(name)
    except Exception:
        logger.exception("Errore ricerca materiale '%s'", name)
    return None


def _extract_material_property(material, keys: Iterable[str]) -> Optional[float]:
    for key in keys:
        if hasattr(material, key):
            val = getattr(material, key)
            if isinstance(val, (int, float)):
                return float(val)
    props = getattr(material, "properties", {}) or {}
    for key in keys:
        if key in props and isinstance(props[key], (int, float)):
            return float(props[key])
    return None


def get_concrete_properties(
    _input: VerificationInput,
    material_repository: Optional[object],
) -> tuple[float, float, float]:
    """Returns (fck_MPa, fck_kgcm2, sigma_ca_kgcm2)."""
    fallback_fck = 25.0
    fck_mpa = None
    if material_repository is not None and _input.material_concrete:
        mat = _get_material_by_name(material_repository, _input.material_concrete)
        if mat is not None:
            fck_mpa = _extract_material_property(mat, ["fck_MPa", "fck_mpa", "fck"])
    if fck_mpa is None:
        logger.warning("Materiale cls '%s' non trovato; uso fck=%s MPa", _input.material_concrete, fallback_fck)
        fck_mpa = fallback_fck
    fck_kgcm2 = fck_mpa * 10.197
    sigma_ca = 0.5 * fck_kgcm2
    return fck_mpa, fck_kgcm2, sigma_ca


def get_steel_properties(
    _input: VerificationInput,
    material_repository: Optional[object],
) -> tuple[float, float, float]:
    """Returns (fyk_MPa, fyk_kgcm2, sigma_fa_kgcm2)."""
    fallback_fyk = 450.0
    fyk_mpa = None
    if material_repository is not None and _input.material_steel:
        mat = _get_material_by_name(material_repository, _input.material_steel)
        if mat is not None:
            fyk_mpa = _extract_material_property(mat, ["fyk_MPa", "fyk_mpa", "fyk"])
    if fyk_mpa is None:
        logger.warning(
            "Materiale acciaio '%s' non trovato; uso fyk=%s MPa",
            _input.material_steel,
            fallback_fyk,
        )
        fyk_mpa = fallback_fyk
    fyk_kgcm2 = fyk_mpa * 10.197
    gamma_s_ta = 1.5
    sigma_fa = fyk_kgcm2 / gamma_s_ta
    return fyk_mpa, fyk_kgcm2, sigma_fa
