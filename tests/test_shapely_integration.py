import pytest
from sections_app.geometry_model import SectionGeometry
from sections_app.section_calculations import compute_section_properties_from_geometry


def test_shapely_area_and_core():
    pytest.importorskip("shapely")
    from shapely.geometry import Polygon

    # simple square with a smaller square hole
    exterior = [(0, 0), (10, 0), (10, 10), (0, 10)]
    hole = [(3, 3), (7, 3), (7, 7), (3, 7)]
    geom = SectionGeometry(exterior=exterior, holes=[hole])

    props = compute_section_properties_from_geometry(geom)

    poly = Polygon(exterior, holes=[hole])
    assert abs(props.area - poly.area) < 1e-6
    # if shapely produced a core, it must be inside the polygon
    if props.core and props.core.polygon:
        shp_core = Polygon(props.core.polygon)
        assert shp_core.within(poly) or shp_core.equals(poly)
