import pytest

from sections_app.models.sections import RectangularSection, TSection
from sections_app.section_calculations import (
    compute_section_properties_from_geometry,
    section_to_geometry,
)


def approx_eq(a, b, rel=1e-4):
    if b == 0:
        return abs(a - b) < rel
    return abs(a - b) / max(abs(b), 1.0) <= rel


def test_rectangular_adapter_and_area():
    sec = RectangularSection(name="r", width=10.0, height=20.0)
    props_old = sec.compute_properties()
    geom = section_to_geometry(sec)
    props_new = compute_section_properties_from_geometry(geom)

    # area consistency
    # map centroid to lower-left-origin coords: x_corner = x_c - minx
    minx, miny, maxx, maxy = geom.bounding_box()
    new_centroid_x = props_new.x_c - minx
    new_centroid_y = props_new.y_c - miny
    assert approx_eq(props_new.area, props_old.area)
    # centroid consistency (both use lower-left origin in legacy model)
    assert approx_eq(new_centroid_x, props_old.centroid_x)
    assert approx_eq(new_centroid_y, props_old.centroid_y)

    # bounding box should match dimensions
    minx, miny, maxx, maxy = geom.bounding_box()
    assert pytest.approx(maxx - minx, rel=1e-4) == 10.0
    assert pytest.approx(maxy - miny, rel=1e-4) == 20.0


def test_T_adapter_bbox_and_area_consistency():
    # T: flange on top, web at bottom
    fw = 12.0
    ft = 2.0
    wt = 1.0
    wh = 6.0
    sec = TSection(name="t", flange_width=fw, flange_thickness=ft, web_thickness=wt, web_height=wh)
    props_old = sec.compute_properties()
    geom = section_to_geometry(sec)

    # Check bbox matches expected extents
    minx, miny, maxx, maxy = geom.bounding_box()
    assert pytest.approx(minx, rel=1e-6) == -fw / 2.0
    assert pytest.approx(maxx, rel=1e-6) == fw / 2.0
    assert pytest.approx(miny, rel=1e-6) == 0.0
    assert pytest.approx(maxy, rel=1e-6) == wh + ft

    # polygon area matches computed area (use shapely if available, else compute shoelace)
    pytest.importorskip("shapely")
    from shapely.geometry import Polygon as ShPolygon

    poly = ShPolygon(geom.exterior, holes=geom.holes)
    assert approx_eq(poly.area, props_old.area)

    # check centroid roughly matches
    props_new = compute_section_properties_from_geometry(geom)
    assert approx_eq(props_new.x_c, props_old.centroid_x)
    assert approx_eq(props_new.y_c, props_old.centroid_y)
