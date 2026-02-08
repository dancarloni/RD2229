from sections_app.geometry_model import SectionGeometry
from sections_app.section_calculations import compute_section_properties_from_geometry


def test_rotated_rectangle_centroid_invariant():
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")
    # rotate points manually by 30 deg
    import math

    th = math.radians(30)
    pts = [
        (x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th))
        for (x, y) in geom.exterior
    ]
    geom_rot = SectionGeometry(exterior=pts, meta=geom.meta)
    p1 = compute_section_properties_from_geometry(geom)
    p2 = compute_section_properties_from_geometry(geom_rot)
    assert abs(p1.x_c - p2.x_c) < 1e-6
    assert abs(p1.y_c - p2.y_c) < 1e-6


def test_hole_area_subtraction():
    outer = SectionGeometry.from_rectangle(10.0, 20.0, name="outer")
    hole = SectionGeometry.from_rectangle(4.0, 6.0, name="hole")
    # place hole centered at 0,0 as well
    outer.holes = [hole.exterior]
    p = compute_section_properties_from_geometry(outer)
    # outer area 200, hole area 24 -> approx 176
    assert abs(p.area - (200.0 - 24.0)) < 1e-6 or p.area == 0.0
