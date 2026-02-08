from sections_app.geometry_model import SectionGeometry
from sections_app.section_calculations import (
    compute_core_of_inertia,
    _point_in_polygon,
    compute_section_properties_from_geometry,
)


def test_point_in_polygon_basic():
    square = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    assert _point_in_polygon(0, 0, square)
    assert not _point_in_polygon(2, 0, square)


def test_core_scaling_inside_and_not_in_hole():
    outer = SectionGeometry.from_rectangle(10.0, 20.0, name="outer")
    hole = SectionGeometry.from_rectangle(4.0, 6.0, name="hole")
    outer.holes = [hole.exterior]
    props = compute_section_properties_from_geometry(outer)
    core = compute_core_of_inertia(outer, props)
    assert core.polygon is not None
    for x, y in core.polygon:
        assert _point_in_polygon(x, y, outer.exterior)
        # not in hole
        assert not _point_in_polygon(x, y, hole.exterior)
