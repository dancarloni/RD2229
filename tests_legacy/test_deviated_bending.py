from core.verification_core import (
    SectionGeometry,
    ReinforcementLayer,
    MaterialProperties,
    calculate_neutral_axis_deviated_bending,
)
import math


def test_neutral_axis_deviated_bending_angle():
    sec = SectionGeometry(width=30.0, height=50.0)
    # Tensile at bottom (distance from top), compressed top near 4 cm
    top = ReinforcementLayer(area=1.0, distance=4.0)
    bot = ReinforcementLayer(area=2.0, distance=46.0)
    mat = MaterialProperties(fck=25.0, Ec=31000.0, fyk=450.0)

    Mx = 50.0
    My = 30.0
    na = calculate_neutral_axis_deviated_bending(
        section=sec,
        reinforcement_tensile=bot,
        reinforcement_compressed=top,
        material=mat,
        Mx=Mx,
        My=My,
        N=0.0,
        method="SLU",
    )

    expected_angle = math.degrees(math.atan2(My, Mx))
    # Check inclination close to expected
    assert abs(na.inclination - expected_angle) < 1e-6
    # Neutral axis should be within section height
    assert 0.0 < na.x < sec.height


def test_neutral_axis_with_axial_loads():
    sec = SectionGeometry(width=30.0, height=50.0)
    top = ReinforcementLayer(area=1.0, distance=4.0)
    bot = ReinforcementLayer(area=2.0, distance=46.0)
    mat = MaterialProperties(fck=25.0, Ec=31000.0, fyk=450.0)

    # Apply compressive axial load -> neutral axis should move deeper
    na_noN = calculate_neutral_axis_deviated_bending(sec, bot, top, mat, 40.0, 10.0, N=0.0)
    na_comp = calculate_neutral_axis_deviated_bending(sec, bot, top, mat, 40.0, 10.0, N=-5000.0)
    assert na_comp.x >= na_noN.x
