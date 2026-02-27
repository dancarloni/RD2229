import pathlib
import sys

import pytest

# Ensure repo root is on sys.path for pytest collection environments
ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from apps.sections.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    RectangularHollowSection,
    RectangularSection,
    TSection,
    VSection,
)
from src.core_calculus.section_calculations import (
    compute_section_properties_from_section,
    section_to_geometry,
)

REL_TOL = 1e-4


def rel_close(a, b, tol=REL_TOL):
    if a is None or b is None:
        return False
    if abs(b) < 1e-12:
        return abs(a - b) < tol
    return abs(a - b) / max(abs(b), 1e-12) <= tol


@pytest.mark.parametrize(
    "section, kwargs",
    [
        (RectangularSection, dict(name="r", width=10.0, height=20.0)),
        (CircularSection, dict(name="c", diameter=10.0)),
        (
            TSection,
            dict(name="t", flange_width=10.0, flange_thickness=2.0, web_thickness=1.0, web_height=8.0),
        ),
        (
            InvertedTSection,
            dict(
                name="it",
                flange_width=10.0,
                flange_thickness=2.0,
                web_thickness=1.0,
                web_height=8.0,
            ),
        ),
        (
            ISection,
            dict(
                name="i",
                flange_width=10.0,
                flange_thickness=1.5,
                web_thickness=1.0,
                web_height=12.0,
            ),
        ),
        (
            CSection,
            dict(name="csh", width=10.0, height=8.0, flange_thickness=1.0, web_thickness=1.0),
        ),
        (LSection, dict(name="l", width=8.0, height=8.0, t_horizontal=1.0, t_vertical=1.0)),
        (RectangularHollowSection, dict(name="rh", width=10.0, height=8.0, thickness=1.0)),
        (CircularHollowSection, dict(name="ch", outer_diameter=10.0, thickness=1.0)),
        (VSection, dict(name="v", width=10.0, height=8.0, thickness=1.0)),
        (InvertedVSection, dict(name="iv", width=10.0, height=8.0, thickness=1.0)),
    ],
)
def test_section_properties_match_legacy(section, kwargs):
    # Instantiate legacy section and compute properties
    sec = section(**kwargs)
    old_props = sec.compute_properties()

    # Compute new carbon_fiber_placeholder-based properties
    # pass shear factor None to use defaults internally
    new_props = compute_section_properties_from_section(sec)
    geom = section_to_geometry(sec)

    # map centroid to lower-left-origin coords: x_corner = x_c - minx
    minx, miny, maxx, maxy = geom.bounding_box()
    new_centroid_x = new_props.x_c - minx
    new_centroid_y = new_props.y_c - miny

    assert rel_close(new_props.area, old_props.area)
    assert rel_close(new_centroid_x, old_props.centroid_x)
    assert rel_close(new_centroid_y, old_props.centroid_y)
    assert rel_close(new_props.Ix, old_props.ix)
    assert rel_close(new_props.Iy, old_props.iy)

    # Ixy may be tiny or zero for symmetric shapes
    if old_props.ixy is not None:
        assert rel_close(new_props.Ixy or 0.0, old_props.ixy or 0.0)


def test_adaptor_returns_nontrivial_geometry():
    # For non-rect/circ types, ensure adapter does not fallback to 1x1 degenerate polygon
    sec = TSection(name="t", flange_width=10.0, flange_thickness=2.0, web_thickness=1.0, web_height=8.0)
    geom = section_to_geometry(sec)
    # area should be > 1 and bbox should have expected extents
    minx, miny, maxx, maxy = geom.bounding_box()
    assert maxx - minx > 5.0
    assert maxy - miny > 5.0
