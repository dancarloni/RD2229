from src.core_calculus.core.geometry_model import SectionGeometry, SectionProperties


def test_from_rectangle_metadata_and_bbox():
    geom = SectionGeometry.from_rectangle(10.0, 20.0, rotation_deg=30.0, name="rect")
    assert geom.meta.get("name") == "rect"
    assert geom.meta.get("rotation_deg") == 30.0

    minx, miny, maxx, maxy = geom.bounding_box()
    assert abs(minx + 5.0) < 1e-9
    assert abs(maxx - 5.0) < 1e-9
    assert abs(miny + 10.0) < 1e-9
    assert abs(maxy - 10.0) < 1e-9


def test_bounding_box_includes_holes():
    exterior = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    hole = [(4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0)]
    geom = SectionGeometry(exterior=exterior, holes=[hole])
    assert geom.bounding_box() == (0.0, 0.0, 10.0, 10.0)


def test_section_properties_defaults():
    p = SectionProperties()
    assert p.area == 0.0
    assert p.Ix == 0.0
    assert p.core is None
    assert p.ellipse is None
