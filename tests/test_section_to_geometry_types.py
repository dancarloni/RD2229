import math

import pytest

from apps.sections.models.sections import CircularSection, RectangularSection, TSection
from src.core_calculus.section_calculations import compute_section_properties_from_section


def test_compute_properties_from_section_rectangular_and_circular():
    sec = RectangularSection(name="rect_test", width=10.0, height=20.0)
    props = compute_section_properties_from_section(sec)
    assert props.area == pytest.approx(200.0)

    sec2 = CircularSection(name="circ_test", diameter=10.0)
    props2 = compute_section_properties_from_section(sec2)
    # allow small relative tolerance due to polygon approximation
    assert props2.area == pytest.approx(math.pi * 5.0 ** 2, rel=1e-3)


def test_compute_properties_from_section_tsection_approx_area():
    sec = TSection(
        name="t_test",
        flange_width=20.0,
        flange_thickness=3.0,
        web_thickness=2.0,
        web_height=17.0,
    )
    props = compute_section_properties_from_section(sec)
    # expected area = flange + web = 20*3 + 2*17 = 94
    assert props.area == pytest.approx(94.0, rel=1e-9)
