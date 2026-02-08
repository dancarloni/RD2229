import pytest
from math import pi

from sections_app.section_calculations import compute_section_properties_from_geometry
from sections_app.geometry_model import SectionGeometry


def test_core_selection_prefers_compact_candidate():
    pytest.importorskip("shapely")
    from shapely.geometry import Polygon

    # square with central hole => expected inner core to be compact
    exterior = [(0, 0), (10, 0), (10, 10), (0, 10)]
    hole = [(3, 3), (7, 3), (7, 7), (3, 7)]
    geom = SectionGeometry(exterior=exterior, holes=[hole])

    props = compute_section_properties_from_geometry(geom)

    assert props.core is not None and props.core.polygon
    core_poly = Polygon(props.core.polygon)
    area = float(core_poly.area)
    perim = float(core_poly.length)

    compactness = (4.0 * pi * area) / (perim * perim + 1e-12)
    hx0, hy0, hx1, hy1 = core_poly.convex_hull.bounds
    dx = hx1 - hx0
    dy = hy1 - hy0
    min_dim = min(dx, dy)
    max_dim = max(dx, dy)
    aspect = float('inf') if min_dim <= 1e-12 else max_dim / (min_dim + 1e-12)

    # core should be reasonably compact and not a skinny sliver
    assert compactness > 0.05
    assert aspect < 4.0
