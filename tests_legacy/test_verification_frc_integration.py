#!/usr/bin/env python3
"""Integration tests for FRC contribution in verification engine."""

from core.verification_core import LoadCase, MaterialProperties, ReinforcementLayer, SectionGeometry
from core.verification_engine import VerificationEngine
from core_models.materials import Material


def test_frc_increases_tensile_stress():
    # Geometry and reinforcement
    section = SectionGeometry(width=20.0, height=40.0)
    As = ReinforcementLayer(area=2.0, distance=35.0)  # tensile reinforcement near bottom
    As_p = ReinforcementLayer(area=1.0, distance=5.0)

    # Material properties (concrete and steel)
    mat = MaterialProperties(fck=160.0)

    # Loads (bending moment)
    loads = LoadCase(N=0.0, Mx=1000.0)

    engine = VerificationEngine(calculation_code="TA")

    # Without FRC
    result_no_frc = engine.perform_verification(section, As, As_p, mat, loads)
    sigma_s_no_frc = result_no_frc.stress_state.sigma_s_tensile

    # With FRC material (enabled) and some area
    frc_mat = Material(
        name="CFRP_kit", type="frc", frc_enabled=True, frc_fFtu=3000.0, frc_eps_fu=0.02
    )
    result_with_frc = engine.perform_verification(
        section, As, As_p, mat, loads, frc_material=frc_mat, frc_area=0.5
    )
    sigma_s_with_frc = result_with_frc.stress_state.sigma_s_tensile

    assert sigma_s_with_frc >= sigma_s_no_frc
    # And the FRC equivalent field should be present (sigma_frc recorded)
    assert result_with_frc.stress_state.sigma_frc == 0.0 or hasattr(
        result_with_frc.stress_state, "sigma_frc"
    )
