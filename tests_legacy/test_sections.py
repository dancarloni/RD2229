from core.geometry import CircularSection, RectangularSection
from core.section_properties import compute_section_properties


def test_rectangular_section():
    s = RectangularSection(width=200.0, height=100.0)
    p = compute_section_properties(s)
    assert p.area == 200.0 * 100.0


def test_circular_section():
    s = CircularSection(diameter=100.0)
    p = compute_section_properties(s)
    assert round(p.area, 6) == round(3.141592653589793 * (50.0**2), 6)
