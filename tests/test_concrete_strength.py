from tools.concrete_strength import (
    CementType,
    SectionCondition,
    compute_allowable_compressive_stress,
    compute_allowable_shear,
)


def test_sigma_c_normal_simple():
    sigma = compute_allowable_compressive_stress(
        120.0, CementType.NORMAL, SectionCondition.SEMPLICEMENTE_COMPRESA, controlled_quality=False
    )
    assert abs(sigma - 35.0) < 1e-6


def test_sigma_c_high_inflessa():
    sigma = compute_allowable_compressive_stress(
        160.0, CementType.HIGH, SectionCondition.INFLESSA_PRESSOINFLESSA, controlled_quality=False
    )
    assert abs(sigma - 50.0) < 1e-6


def test_sigma_c_controlled_cap():
    sigma = compute_allowable_compressive_stress(
        200.0, CementType.NORMAL, SectionCondition.SEMPLICEMENTE_COMPRESA, controlled_quality=True
    )
    # sigma_c28/3 = 66.666.. -> cap 60
    assert abs(sigma - 60.0) < 1e-6


def test_shear_values():
    service, maximum = compute_allowable_shear(CementType.NORMAL)
    assert service == 4.0 and maximum == 14.0

