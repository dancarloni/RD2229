"""Test per le proprietà geometriche calcolate (Wx, Wy, principal angle, shear areas).

Verifica contro valori noti per le tipologie principali.
"""

import math
import sys

import pytest

sys.path.insert(0, ".")

from sections_app.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    TSection,
    VSection,
)


class TestRectangularProperties:
    """Rectangular 30x50: known values."""

    def setup_method(self):
        self.sec = RectangularSection("rect_30x50", width=30, height=50)
        self.sec.compute_properties()
        self.p = self.sec.properties

    def test_area(self):
        assert self.p.area == pytest.approx(1500.0)

    def test_centroid(self):
        assert self.p.centroid_x == pytest.approx(15.0)
        assert self.p.centroid_y == pytest.approx(25.0)

    def test_inertia(self):
        assert self.p.ix == pytest.approx(312500.0)
        assert self.p.iy == pytest.approx(112500.0)
        assert self.p.ixy == pytest.approx(0.0, abs=1e-10)

    def test_section_moduli(self):
        # Wx = Ix / y_max = 312500 / 25 = 12500
        assert self.p.wx == pytest.approx(12500.0)
        # Wy = Iy / x_max = 112500 / 15 = 7500
        assert self.p.wy == pytest.approx(7500.0)

    def test_to_dict_includes_wx_wy(self):
        d = self.sec.to_dict()
        assert "Wx" in d
        assert "Wy" in d
        assert d["Wx"] == pytest.approx(12500.0)
        assert d["Wy"] == pytest.approx(7500.0)


class TestCircularProperties:
    """Circular d=20: known values."""

    def setup_method(self):
        self.sec = CircularSection("circ_20", diameter=20)
        self.sec.compute_properties()
        self.p = self.sec.properties

    def test_area(self):
        assert self.p.area == pytest.approx(math.pi * 100)

    def test_inertia_symmetric(self):
        expected = math.pi * 10000 / 4  # pi * r^4 / 4
        assert self.p.ix == pytest.approx(expected)
        assert self.p.iy == pytest.approx(expected)

    def test_wx_equals_wy(self):
        """Circular sections should have equal section moduli."""
        assert self.p.wx is not None
        assert self.p.wy is not None
        assert self.p.wx == pytest.approx(self.p.wy)

    def test_wx_value(self):
        # Wx = Ix / y_max = (pi*r^4/4) / r = pi*r^3/4
        r = 10
        expected = math.pi * r**3 / 4
        assert self.p.wx == pytest.approx(expected)


class TestTSectionProperties:
    """T-section: flange 20x3, web 2x17."""

    def setup_method(self):
        self.sec = TSection(
            "t_20x3_2x17",
            flange_width=20,
            flange_thickness=3,
            web_thickness=2,
            web_height=17,
        )
        self.sec.compute_properties()
        self.p = self.sec.properties

    def test_area(self):
        # A_flange = 20*3 = 60, A_web = 2*17 = 34 => A = 94
        assert self.p.area == pytest.approx(94.0)

    def test_centroid_x_symmetric(self):
        # T-section is symmetric about vertical axis
        assert self.p.centroid_x == pytest.approx(10.0)

    def test_centroid_y(self):
        # y_flange = 17 + 1.5 = 18.5, y_web = 8.5
        # y_G = (60*18.5 + 34*8.5) / 94
        expected = (60 * 18.5 + 34 * 8.5) / 94
        assert self.p.centroid_y == pytest.approx(expected)

    def test_ixy_zero(self):
        # T-section has single axis of symmetry -> Ixy = 0
        assert self.p.ixy == pytest.approx(0.0, abs=1e-10)

    def test_wx_not_none(self):
        assert self.p.wx is not None
        assert self.p.wx > 0

    def test_wy_not_none(self):
        assert self.p.wy is not None
        assert self.p.wy > 0


class TestISectionProperties:
    """I-section: flanges 20x3, web 2x14. Symmetric => centroid at center."""

    def setup_method(self):
        self.sec = ISection(
            "i_20x3_2x14",
            flange_width=20,
            flange_thickness=3,
            web_height=14,
            web_thickness=2,
        )
        self.sec.compute_properties()
        self.p = self.sec.properties

    def test_symmetric_centroid(self):
        total_h = 3 + 14 + 3  # = 20
        assert self.p.centroid_y == pytest.approx(total_h / 2)
        assert self.p.centroid_x == pytest.approx(20 / 2)

    def test_area(self):
        # 2 flanges + web: 2*20*3 + 2*14 = 120 + 28 = 148
        assert self.p.area == pytest.approx(148.0)

    def test_wx_wy_positive(self):
        assert self.p.wx is not None and self.p.wx > 0
        assert self.p.wy is not None and self.p.wy > 0


class TestLSectionProperties:
    """L-section 100x80, t=10: asymmetric => Ixy != 0."""

    def setup_method(self):
        self.sec = LSection(
            "l_100x80_10",
            width=100,
            height=80,
            t_horizontal=10,
            t_vertical=10,
        )
        self.sec.compute_properties()
        self.p = self.sec.properties

    def test_area(self):
        # horizontal: 100*10 = 1000, vertical: 10*(80-10) = 700 => total 1700
        assert self.p.area == pytest.approx(1700.0)

    def test_asymmetric_centroid(self):
        # Centroid should not be at center for L-section
        assert self.p.centroid_x != pytest.approx(50.0)
        assert self.p.centroid_y != pytest.approx(40.0)

    def test_ixy_nonzero(self):
        """L-section should have non-zero product of inertia."""
        assert abs(self.p.ixy) > 1e-3

    def test_principal_invariants(self):
        """I1 >= I2 and I1 + I2 = Ix + Iy."""
        assert self.p.principal_ix is not None
        assert self.p.principal_iy is not None
        assert self.p.principal_ix >= self.p.principal_iy
        # Invariant: I1 + I2 = Ix + Iy
        assert (self.p.principal_ix + self.p.principal_iy) == pytest.approx(self.p.ix + self.p.iy, rel=1e-6)

    def test_wx_wy_positive(self):
        assert self.p.wx is not None and self.p.wx > 0
        assert self.p.wy is not None and self.p.wy > 0


class TestPrincipalAngleFix:
    """Verify the principal angle formula is correct (atan2-based)."""

    def test_symmetric_section_zero_angle(self):
        """Symmetric sections should have principal angle = 0."""
        sec = RectangularSection("rect", width=30, height=50)
        sec.compute_properties()
        assert sec.properties.principal_angle_deg == pytest.approx(0.0, abs=1e-6)

    def test_l_section_nonzero_angle(self):
        """L-section should have a non-zero principal angle."""
        sec = LSection("l", width=80, height=60, t_horizontal=8, t_vertical=8)
        sec.compute_properties()
        angle = sec.properties.principal_angle_deg
        assert angle is not None
        assert abs(angle) > 1e-3  # Should be non-zero

    def test_principal_angle_range(self):
        """Principal angle should be in [-90, 90] degrees."""
        sec = LSection("l", width=100, height=80, t_horizontal=10, t_vertical=10)
        sec.compute_properties()
        angle = sec.properties.principal_angle_deg
        assert -90.0 <= angle <= 90.0


class TestAllSectionTypesHaveWxWy:
    """Verify Wx and Wy are computed for all 12 section types."""

    @pytest.mark.parametrize(
        "section",
        [
            RectangularSection("r", 30, 50),
            CircularSection("c", 20),
            TSection("t", 20, 3, 2, 17),
            ISection("i", 20, 3, 14, 2),
            LSection("l", 100, 80, 10, 10),
            PiSection("pi", 30, 3, 20, 2),
            InvertedTSection("it", 20, 3, 2, 17),
            CSection("cs", 20, 40, 3, 2),
            CircularHollowSection("ch", 30, 3),
            RectangularHollowSection("rh", 30, 50, 3),
            VSection("v", 20, 15, 2),
            InvertedVSection("iv", 20, 15, 2),
        ],
        ids=[
            "RECTANGULAR",
            "CIRCULAR",
            "T_SECTION",
            "I_SECTION",
            "L_SECTION",
            "PI_SECTION",
            "INVERTED_T_SECTION",
            "C_SECTION",
            "CIRCULAR_HOLLOW",
            "RECTANGULAR_HOLLOW",
            "V_SECTION",
            "INVERTED_V_SECTION",
        ],
    )
    def test_wx_wy_computed(self, section):
        section.compute_properties()
        p = section.properties
        assert p.wx is not None, f"{section.section_type}: Wx is None"
        assert p.wy is not None, f"{section.section_type}: Wy is None"
        assert p.wx > 0, f"{section.section_type}: Wx <= 0"
        assert p.wy > 0, f"{section.section_type}: Wy <= 0"
