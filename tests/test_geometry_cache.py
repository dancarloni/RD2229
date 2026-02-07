from src.core_calculus.geometry_cache import section_inertia


def test_section_inertia_solid():
    area, ix, iy = section_inertia(0.2, 0.4)
    assert abs(area - 0.08) < 1e-12
    assert ix > 0
    assert iy > 0


def test_section_inertia_hollow():
    area, ix, iy = section_inertia(0.2, 0.4, thickness=0.01)
    assert area < 0.08
    assert ix > 0
    assert iy > 0
