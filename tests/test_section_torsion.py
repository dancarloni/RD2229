"""Test proprietà torsionali delle sezioni.

Verifica J_t (costante torsionale St. Venant), C_w (costante di ingobbamento),
e centro di taglio (x_s, y_s) per tutti i tipi di sezione.
"""

from __future__ import annotations

import sys
from math import pi, sqrt
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apps.sections.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    TSection,
    VSection,
)


class TestJtRettangolare:
    """J_t rettangolare: J_t = beta * a^3 * b con beta approssimato."""

    def test_quadrata(self) -> None:
        """Sezione quadrata 10x10: beta(1.0) = 1/3*(1 - 0.63 + 0.052) = 0.1407."""
        s = RectangularSection("Q10", width=10.0, height=10.0)
        s.compute_properties()
        assert s.properties is not None
        assert s.properties.j_t is not None
        # beta = 1/3 * (1 - 0.63*1 + 0.052*1) = 0.14067
        beta = (1.0 / 3.0) * (1.0 - 0.63 + 0.052)
        expected = beta * 10.0**3 * 10.0
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_rettangolo_largo(self) -> None:
        """Sezione 30x10: a=10, b=30."""
        s = RectangularSection("R30x10", width=30.0, height=10.0)
        s.compute_properties()
        a, b = 10.0, 30.0
        ratio = a / b
        beta = (1.0 / 3.0) * (1.0 - 0.63 * ratio + 0.052 * ratio**3)
        expected = beta * a**3 * b
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_centro_taglio_coincide_baricentro(self) -> None:
        s = RectangularSection("R", width=20.0, height=30.0)
        s.compute_properties()
        assert s.properties.x_s == pytest.approx(s.properties.centroid_x)
        assert s.properties.y_s == pytest.approx(s.properties.centroid_y)

    def test_cw_zero(self) -> None:
        s = RectangularSection("R", width=20.0, height=30.0)
        s.compute_properties()
        assert s.properties.c_w == 0.0


class TestJtCircolare:
    """J_t circolare: J_t = pi * r^4 / 2."""

    def test_circolare_piena(self) -> None:
        d = 20.0
        s = CircularSection("C20", diameter=d)
        s.compute_properties()
        r = d / 2
        expected = pi * r**4 / 2
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_circolare_cava(self) -> None:
        D = 30.0
        t = 3.0
        s = CircularHollowSection("CH30x3", outer_diameter=D, thickness=t)
        s.compute_properties()
        r_out = D / 2
        r_in = r_out - t
        expected = (pi / 2) * (r_out**4 - r_in**4)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)


class TestJtRettangolareCava:
    """J_t rettangolare cava: Bredt: J_t = 4*Am^2*t/p."""

    def test_tubo_rettangolare(self) -> None:
        w, h, t = 20.0, 30.0, 2.0
        s = RectangularHollowSection("RH20x30x2", width=w, height=h, thickness=t)
        s.compute_properties()
        b_m = w - t
        h_m = h - t
        A_m = b_m * h_m
        p_m = 2 * (b_m + h_m)
        expected = 4 * A_m**2 * t / p_m
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)


class TestJtSezioniAperte:
    """J_t sezioni aperte: J_t = sum(1/3 * b_i * t_i^3)."""

    def test_i_section(self) -> None:
        bf, tf, hw, tw = 20.0, 1.5, 30.0, 1.0
        s = ISection("IPE", flange_width=bf, flange_thickness=tf, web_height=hw, web_thickness=tw)
        s.compute_properties()
        expected = (1.0 / 3.0) * (2 * bf * tf**3 + hw * tw**3)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_i_section_cw(self) -> None:
        """C_w per I simmetrica: C_w = I_f * h_s^2 / 4."""
        bf, tf, hw, tw = 20.0, 1.5, 30.0, 1.0
        s = ISection("IPE", flange_width=bf, flange_thickness=tf, web_height=hw, web_thickness=tw)
        s.compute_properties()
        h = hw + 2 * tf
        I_f = tf * bf**3 / 12
        h_s = h - tf
        expected_cw = I_f * h_s**2 / 4
        assert s.properties.c_w == pytest.approx(expected_cw, rel=0.001)

    def test_i_section_shear_center(self) -> None:
        """Centro di taglio I: coincide col baricentro."""
        s = ISection(
            "IPE", flange_width=20.0, flange_thickness=1.5, web_height=30.0, web_thickness=1.0
        )
        s.compute_properties()
        assert s.properties.x_s == pytest.approx(s.properties.centroid_x)
        assert s.properties.y_s == pytest.approx(s.properties.centroid_y)

    def test_t_section(self) -> None:
        bf, tf, hw, tw = 20.0, 2.0, 25.0, 1.5
        s = TSection("T", flange_width=bf, flange_thickness=tf, web_thickness=tw, web_height=hw)
        s.compute_properties()
        expected = (1.0 / 3.0) * (bf * tf**3 + hw * tw**3)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_c_section(self) -> None:
        w, h, tf, tw = 10.0, 30.0, 1.5, 1.0
        s = CSection("C", width=w, height=h, flange_thickness=tf, web_thickness=tw)
        s.compute_properties()
        hw = h - 2 * tf
        expected = (1.0 / 3.0) * (2 * w * tf**3 + hw * tw**3)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_c_section_shear_center_outside(self) -> None:
        """Centro di taglio C: fuori dall'anima (x_s < 0)."""
        s = CSection("C", width=10.0, height=30.0, flange_thickness=1.5, web_thickness=1.0)
        s.compute_properties()
        # x_s should be negative (outside the web)
        assert s.properties.x_s is not None
        assert s.properties.x_s < 0

    def test_l_section(self) -> None:
        w, h, th, tv = 10.0, 15.0, 1.5, 1.5
        s = LSection("L", width=w, height=h, t_horizontal=th, t_vertical=tv)
        s.compute_properties()
        bv = h - th
        expected = (1.0 / 3.0) * (w * th**3 + bv * tv**3)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_inverted_t_section(self) -> None:
        bf, tf, hw, tw = 20.0, 2.0, 25.0, 1.5
        s = InvertedTSection(
            "IT", flange_width=bf, flange_thickness=tf, web_thickness=tw, web_height=hw
        )
        s.compute_properties()
        expected = (1.0 / 3.0) * (bf * tf**3 + hw * tw**3)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)

    def test_pi_section(self) -> None:
        bf, tf, hw, tw = 30.0, 2.0, 20.0, 1.0
        s = PiSection("Pi", flange_width=bf, flange_thickness=tf, web_height=hw, web_thickness=tw)
        s.compute_properties()
        expected = (1.0 / 3.0) * (bf * tf**3 + 2 * hw * tw**3)
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)


class TestJtVSection:
    """J_t sezione V: approssimazione thin-walled."""

    def test_v_section(self) -> None:
        w, h, t = 20.0, 30.0, 2.0
        s = VSection("V", width=w, height=h, thickness=t)
        s.compute_properties()
        length = sqrt((w / 2) ** 2 + h**2)
        expected = (1.0 / 3.0) * 2 * length * t**3
        assert s.properties.j_t == pytest.approx(expected, rel=0.001)


class TestAllSectionsHaveTorsionProps:
    """Verifica che tutte le sezioni calcolino J_t dopo compute_properties()."""

    def test_all_sections_have_jt(self) -> None:
        sections = [
            RectangularSection("R", width=20, height=30),
            CircularSection("C", diameter=20),
            CircularHollowSection("CH", outer_diameter=30, thickness=3),
            RectangularHollowSection("RH", width=20, height=30, thickness=2),
            ISection("I", flange_width=20, flange_thickness=1.5, web_height=30, web_thickness=1),
            TSection("T", flange_width=20, flange_thickness=2, web_thickness=1.5, web_height=25),
            InvertedTSection(
                "IT", flange_width=20, flange_thickness=2, web_thickness=1.5, web_height=25
            ),
            CSection("C", width=10, height=30, flange_thickness=1.5, web_thickness=1),
            LSection("L", width=10, height=15, t_horizontal=1.5, t_vertical=1.5),
            PiSection("Pi", flange_width=30, flange_thickness=2, web_height=20, web_thickness=1),
            VSection("V", width=20, height=30, thickness=2),
        ]
        for s in sections:
            s.compute_properties()
            assert s.properties is not None, f"{s.section_type}: properties is None"
            assert s.properties.j_t is not None, f"{s.section_type}: J_t is None"
            assert s.properties.j_t > 0, f"{s.section_type}: J_t <= 0"

    def test_jt_in_to_dict(self) -> None:
        """Verifica che J_t appaia nel dizionario serializzato."""
        s = RectangularSection("R", width=20, height=30)
        s.compute_properties()
        d = s.to_dict()
        assert "J_t" in d
        assert d["J_t"] is not None
        assert d["J_t"] > 0


class TestExistingPropertiesUnchanged:
    """Regressione: le proprietà esistenti non devono cambiare."""

    def test_rectangular_area(self) -> None:
        s = RectangularSection("R", width=20, height=30)
        s.compute_properties()
        assert s.properties.area == pytest.approx(600.0)

    def test_circular_area(self) -> None:
        s = CircularSection("C", diameter=20)
        s.compute_properties()
        assert s.properties.area == pytest.approx(pi * 100, rel=0.001)

    def test_i_section_area(self) -> None:
        s = ISection("I", flange_width=20, flange_thickness=1.5, web_height=30, web_thickness=1)
        s.compute_properties()
        expected = 2 * 20 * 1.5 + 30 * 1
        assert s.properties.area == pytest.approx(expected, rel=0.001)
