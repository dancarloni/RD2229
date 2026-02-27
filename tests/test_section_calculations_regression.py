import pytest

from src.core_calculus.core.geometry_model import SectionGeometry
from src.core_calculus.section_calculations import (
    _point_in_polygon,
    compute_section_properties_from_geometry,
)


def test_rectangle_inertia_matches_analytic():
    b, h = 10.0, 20.0
    geom = SectionGeometry.from_rectangle(b=b, h=h, name="rect")
    props = compute_section_properties_from_geometry(geom)

    # analytical formulas for rectangle about centroid
    expected_Ix = b * h**3 / 12.0
    expected_Iy = h * b**3 / 12.0

    assert props.area == pytest.approx(b * h, rel=1e-9)
    assert props.Ix == pytest.approx(expected_Ix, rel=1e-6)
    assert props.Iy == pytest.approx(expected_Iy, rel=1e-6)
    assert abs(props.Ixy) < 1e-9


def test_translation_invariance_and_centroid_shift():
    geom = SectionGeometry.from_rectangle(10.0, 20.0)
    props0 = compute_section_properties_from_geometry(geom)

    dx, dy = 37.5, -12.25
    moved = SectionGeometry(exterior=[(x + dx, y + dy) for (x, y) in geom.exterior], meta=geom.meta)
    props1 = compute_section_properties_from_geometry(moved)

    # area and principal moments must be invariant
    assert props0.area == pytest.approx(props1.area)
    assert props0.Ix == pytest.approx(props1.Ix)
    assert props0.Iy == pytest.approx(props1.Iy)
    assert props0.Ixy == pytest.approx(props1.Ixy)

    # centroid should translate by (dx, dy)
    assert props1.x_c == pytest.approx(props0.x_c + dx)
    assert props1.y_c == pytest.approx(props0.y_c + dy)


def test_degenerate_collinear_polygon_returns_zero_properties():
    # three collinear points -> zero area
    geom = SectionGeometry(exterior=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])
    props = compute_section_properties_from_geometry(geom)

    assert props.area == pytest.approx(0.0)
    assert props.Ix == pytest.approx(0.0)
    assert props.Iy == pytest.approx(0.0)
    assert props.Ixy == pytest.approx(0.0)
    assert props.r1 == pytest.approx(0.0)
    assert props.r2 == pytest.approx(0.0)


def test_core_polygon_inside_exterior_and_not_in_hole():
    outer = SectionGeometry.from_rectangle(10.0, 20.0, name="outer")
    hole = SectionGeometry.from_rectangle(4.0, 6.0, name="hole")
    outer.holes = [hole.exterior]

    props = compute_section_properties_from_geometry(outer)
    # ensure a core polygon was produced
    assert props.core is not None and props.core.polygon

    core = props.core.polygon
    # every vertex of core must be inside exterior and not inside any hole
    for x, y in core:
        assert _point_in_polygon(x, y, outer.exterior) is True
        for h in outer.holes:
            assert _point_in_polygon(x, y, h) is False


def test_principal_moments_invariant_sum():
    geom = SectionGeometry.from_rectangle(12.0, 8.0)
    props = compute_section_properties_from_geometry(geom)
    # invariant: I1 + I2 == Ix + Iy
    assert pytest.approx(props.I1 + props.I2, rel=1e-9) == pytest.approx(props.Ix + props.Iy, rel=1e-9)
