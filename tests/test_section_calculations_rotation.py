import math

import pytest

from src.core_calculus.core.geometry_model import SectionGeometry
from src.core_calculus.section_calculations import compute_section_properties_from_geometry


def test_principal_moments_and_radii_invariant_under_rotation():
    geom = SectionGeometry.from_rectangle(12.0, 8.0)
    props0 = compute_section_properties_from_geometry(geom)

    angle_deg = 37.0
    th = math.radians(angle_deg)
    pts = [(x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)) for x, y in geom.exterior]
    geom_rot = SectionGeometry(exterior=pts, meta=geom.meta)
    props1 = compute_section_properties_from_geometry(geom_rot)

    # principal moments and radii of gyration must be invariant
    assert pytest.approx(props0.I1, rel=1e-9) == pytest.approx(props1.I1, rel=1e-9)
    assert pytest.approx(props0.I2, rel=1e-9) == pytest.approx(props1.I2, rel=1e-9)
    assert pytest.approx(props0.r1, rel=1e-9) == pytest.approx(props1.r1, rel=1e-9)
    assert pytest.approx(props0.r2, rel=1e-9) == pytest.approx(props1.r2, rel=1e-9)

    # orientation may be represented differently depending on axis choice; skip strict check here
    # (principal moments and radii are the authoritative invariants tested above).
