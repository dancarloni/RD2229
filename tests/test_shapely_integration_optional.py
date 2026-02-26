import pytest

pytest.importorskip("shapely")

from src.core_calculus.core.geometry_model import SectionGeometry
from src.core_calculus.section_calculations import compute_section_properties_from_geometry


def test_shapely_buffer_based_core_available_and_within_polygon():
    outer = SectionGeometry.from_rectangle(10.0, 20.0)
    props = compute_section_properties_from_geometry(outer)
    # when shapely is available we still expect a core polygon to be produced
    assert props.core is not None
    assert props.core.polygon is not None
    # every vertex inside exterior
    from src.core_calculus.section_calculations import _point_in_polygon

    for x, y in props.core.polygon:
        assert _point_in_polygon(x, y, outer.exterior)
