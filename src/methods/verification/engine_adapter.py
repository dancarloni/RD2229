from __future__ import annotations

import logging

from app.domain.materials import get_concrete_properties, get_steel_properties
from app.domain.models import VerificationInput, VerificationOutput
from app.domain.sections import get_section_geometry

logger = logging.getLogger(__name__)


def compute_with_engine(
    _input: VerificationInput,
    section_repository: object | None,
    material_repository: object | None,
) -> VerificationOutput | None:
    """Attempt to compute using the optional core engine. Returns None if engine is unavailable."""
    try:
        from src.core_calculus.core.verification_core import (
            LoadCase,
            ReinforcementLayer,
            SectionGeometry,
        )
        from src.core_calculus.core.verification_engine import (
            create_verification_engine,
        )
    except Exception:  # pragma: no cover - optional engine
        return None

    try:
        b_cm, h_cm = get_section_geometry(_input, section_repository, unit="cm")
        fck_mpa, fck_kgcm2, *_ = get_concrete_properties(_input, material_repository)
        fyk_mpa, fyk_kgcm2, *_ = get_steel_properties(_input, material_repository)

        section = SectionGeometry(width=b_cm, height=h_cm)
        d_top = _input.d_sup if _input.d_sup > 0 else 4.0
        d_bottom = _input.d_inf if _input.d_inf > 0 else 4.0
        reinforcement_compressed = ReinforcementLayer(area=_input.As_sup, distance=d_top)
        reinforcement_tensile = ReinforcementLayer(area=_input.As_inf, distance=h_cm - d_bottom)

        loads = LoadCase(
            N=_input.N,
            Mx=_input.Mx,
            My=_input.My,
            Mz=_input.Mz,
            Tx=_input.Tx,
            Ty=_input.Ty,
            At=_input.At,
        )

        code = (_input.verification_method or "TA").upper()
        engine = create_verification_engine(code)
        material = engine.get_material_properties(
            _input.material_concrete or "",
            _input.material_steel or "",
            material_source="RD2229" if code == "TA" else "NTC2018",
        )
        if fck_kgcm2 > 0:
            material.fck = fck_kgcm2
        if fyk_kgcm2 > 0:
            material.fyk = fyk_kgcm2

        result = engine.perform_verification(
            section=section,
            reinforcement_tensile=reinforcement_tensile,
            reinforcement_compressed=reinforcement_compressed,
            material=material,
            loads=loads,
        )

        return VerificationOutput(
            sigma_c_max=result.stress_state.sigma_c_max,
            sigma_c_min=result.stress_state.sigma_c_min,
            sigma_s_max=result.stress_state.sigma_s_tensile,
            asse_neutro=result.neutral_axis.x,
            asse_neutro_x=result.neutral_axis.x,
            asse_neutro_y=result.neutral_axis.y,
            inclinazione_asse_neutro=result.neutral_axis.inclination,
            deformazioni=f"x/h = {result.neutral_axis.depth_ratio(h_cm):.3f}",
            coeff_sicurezza=max(result.utilization_concrete, result.utilization_steel),
            esito="VERIFICATO" if result.is_verified else "NON VERIFICATO",
            messaggi=result.messages,
        )
    except Exception:
        logger.exception("Errore durante il calcolo via core engine")
        return None
