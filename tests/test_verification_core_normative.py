from src.core_calculus.core.verification_core import (
    LoadCase,
    MaterialProperties,
    ReinforcementLayer,
    SectionGeometry,
    calculate_neutral_axis_deviated_bending,
    calculate_shear_torsion_stresses,
    calculate_stresses_deviated_bending,
)


def test_neutral_axis_deviated_bending_slu_returns_section_value():
    section = SectionGeometry(width=30.0, height=50.0)
    tens = ReinforcementLayer(area=10.0, distance=45.0)
    comp = ReinforcementLayer(area=8.0, distance=4.0)
    material = MaterialProperties(fck=25.0, fcd=14.17, fyk=450.0, fyd=391.3, Es=200000.0)

    na = calculate_neutral_axis_deviated_bending(
        section=section,
        reinforcement_tensile=tens,
        reinforcement_compressed=comp,
        material=material,
        Mx=80.0,
        My=40.0,
        N=300.0,
        method="SLU",
    )

    assert 0.0 < na.x < section.height
    assert na.inclination > 0.0


def test_stresses_deviated_bending_slu_activate_material_limits():
    section = SectionGeometry(width=30.0, height=50.0)
    tens = ReinforcementLayer(area=10.0, distance=45.0)
    comp = ReinforcementLayer(area=8.0, distance=4.0)
    material = MaterialProperties(fck=25.0, fcd=14.17, fyk=450.0, fyd=391.3, Es=200000.0)
    na = calculate_neutral_axis_deviated_bending(
        section=section,
        reinforcement_tensile=tens,
        reinforcement_compressed=comp,
        material=material,
        Mx=80.0,
        My=40.0,
        N=300.0,
        method="SLU",
    )

    stresses = calculate_stresses_deviated_bending(
        section=section,
        reinforcement_tensile=tens,
        reinforcement_compressed=comp,
        material=material,
        Mx=80.0,
        My=40.0,
        N=300.0,
        neutral_axis=na,
        method="SLU",
    )

    assert stresses.sigma_c_max > 0.0
    assert abs(stresses.sigma_s_tensile) <= material.fyd + 1e-6
    assert abs(stresses.sigma_s_compressed) <= material.fyd + 1e-6


def test_shear_torsion_interaction_increases_equivalent_demand():
    section = SectionGeometry(width=30.0, height=50.0)
    material = MaterialProperties(fck=25.0, fcd=14.17, fyk=450.0, fyd=391.3, Es=200000.0)

    shear_only = calculate_shear_torsion_stresses(
        section=section,
        loads=LoadCase(Tx=80.0, Ty=0.0, Mz=0.0, At=4.0),
        reinforcement_area=4.0,
        material=material,
    )
    combined = calculate_shear_torsion_stresses(
        section=section,
        loads=LoadCase(Tx=80.0, Ty=30.0, Mz=25.0, At=4.0),
        reinforcement_area=4.0,
        material=material,
    )

    assert combined.sigma_c_max > shear_only.sigma_c_max
    assert combined.sigma_s_compressed > 0.0
