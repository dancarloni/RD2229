"""Test per il modulo section_fiber — motore geometrico a fibre.

Verifica width_at_depth, height_at_horizontal, compute_concrete_resultant
e get_section_height/width per tutti i 12 tipi di sezione.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from src.methods.section_fiber import (
    compute_concrete_resultant,
    compute_section_area,
    get_section_height,
    get_section_width,
    width_at_depth,
)

# ---------------------------------------------------------------------------
# Helper: creare sezioni mock con SimpleNamespace
# ---------------------------------------------------------------------------

def _rect(w=300.0, h=500.0):
    return SimpleNamespace(section_type="RECTANGULAR", width=w, height=h)


def _circ(d=400.0):
    return SimpleNamespace(section_type="CIRCULAR", diameter=d)


def _circ_hollow(d_out=500.0, t=50.0):
    return SimpleNamespace(section_type="CIRCULAR_HOLLOW", outer_diameter=d_out, thickness=t)


def _rect_hollow(w=400.0, h=600.0, t=20.0):
    return SimpleNamespace(section_type="RECTANGULAR_HOLLOW", width=w, height=h, thickness=t)


def _t_section(bf=600.0, tf=100.0, tw=200.0, hw=400.0):
    return SimpleNamespace(
        section_type="T_SECTION",
        flange_width=bf, flange_thickness=tf,
        web_thickness=tw, web_height=hw,
    )


def _inv_t(bf=600.0, tf=100.0, tw=200.0, hw=400.0):
    return SimpleNamespace(
        section_type="INVERTED_T_SECTION",
        flange_width=bf, flange_thickness=tf,
        web_thickness=tw, web_height=hw,
    )


def _i_section(bf=300.0, tf=20.0, tw=12.0, hw=360.0):
    return SimpleNamespace(
        section_type="I_SECTION",
        flange_width=bf, flange_thickness=tf,
        web_thickness=tw, web_height=hw,
    )


def _pi_section(bf=1000.0, tf=120.0, tw=150.0, hw=500.0):
    return SimpleNamespace(
        section_type="PI_SECTION",
        flange_width=bf, flange_thickness=tf,
        web_thickness=tw, web_height=hw,
    )


def _c_section(w=100.0, h=200.0, tf=10.0, tw=8.0):
    return SimpleNamespace(
        section_type="C_SECTION",
        width=w, height=h,
        flange_thickness=tf, web_thickness=tw,
    )


def _l_section(w=150.0, h=200.0, th=15.0, tv=15.0):
    return SimpleNamespace(
        section_type="L_SECTION",
        width=w, height=h,
        t_horizontal=th, t_vertical=tv,
    )


def _v_section(w=300.0, h=400.0, t=10.0):
    return SimpleNamespace(
        section_type="V_SECTION",
        width=w, height=h, thickness=t,
    )


def _inv_v(w=300.0, h=400.0, t=10.0):
    return SimpleNamespace(
        section_type="INVERTED_V_SECTION",
        width=w, height=h, thickness=t,
    )


# ===========================================================================
# Test get_section_height / get_section_width
# ===========================================================================

class TestSectionDimensions:
    def test_rectangular(self):
        s = _rect(300, 500)
        assert get_section_height(s) == 500.0
        assert get_section_width(s) == 300.0

    def test_circular(self):
        s = _circ(400)
        assert get_section_height(s) == 400.0
        assert get_section_width(s) == 400.0

    def test_circular_hollow(self):
        s = _circ_hollow(500, 50)
        assert get_section_height(s) == 500.0
        assert get_section_width(s) == 500.0

    def test_t_section(self):
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        assert get_section_height(s) == 500.0  # 100 + 400
        assert get_section_width(s) == 600.0

    def test_i_section(self):
        s = _i_section(bf=300, tf=20, tw=12, hw=360)
        assert get_section_height(s) == 400.0  # 2*20 + 360
        assert get_section_width(s) == 300.0

    def test_c_section(self):
        s = _c_section(w=100, h=200, tf=10, tw=8)
        assert get_section_height(s) == 200.0
        assert get_section_width(s) == 100.0

    def test_l_section(self):
        s = _l_section(w=150, h=200, th=15, tv=15)
        assert get_section_height(s) == 200.0
        assert get_section_width(s) == 150.0


# ===========================================================================
# Test width_at_depth per tutti i 12 tipi
# ===========================================================================

class TestWidthAtDepthRectangular:
    def test_inside(self):
        s = _rect(300, 500)
        assert width_at_depth(s, 0) == 300.0
        assert width_at_depth(s, 250) == 300.0
        assert width_at_depth(s, 500) == 300.0

    def test_outside(self):
        s = _rect(300, 500)
        assert width_at_depth(s, -1) == 0.0
        assert width_at_depth(s, 501) == 0.0


class TestWidthAtDepthCircular:
    def test_center(self):
        s = _circ(400)
        # Al centro (y=200), larghezza = diametro
        assert width_at_depth(s, 200) == pytest.approx(400.0, rel=1e-6)

    def test_top_bottom(self):
        s = _circ(400)
        assert width_at_depth(s, 0) == pytest.approx(0.0, abs=0.1)
        assert width_at_depth(s, 400) == pytest.approx(0.0, abs=0.1)

    def test_quarter(self):
        s = _circ(400)
        # y=100 → larghezza = 2*sqrt(200²-100²) = 2*sqrt(30000) ≈ 346.41
        expected = 2 * math.sqrt(200**2 - 100**2)
        assert width_at_depth(s, 100) == pytest.approx(expected, rel=1e-6)


class TestWidthAtDepthCircularHollow:
    def test_center(self):
        s = _circ_hollow(500, 50)
        # Al centro: w_out = 500, w_in = 400 → diff = 100
        assert width_at_depth(s, 250) == pytest.approx(100.0, rel=1e-3)

    def test_outside(self):
        s = _circ_hollow(500, 50)
        assert width_at_depth(s, -1) == 0.0
        assert width_at_depth(s, 501) == 0.0


class TestWidthAtDepthRectangularHollow:
    def test_top_flange(self):
        s = _rect_hollow(400, 600, 20)
        assert width_at_depth(s, 10) == 400.0  # nella flangia superiore

    def test_web(self):
        s = _rect_hollow(400, 600, 20)
        assert width_at_depth(s, 300) == 40.0  # 2 * 20

    def test_bottom_flange(self):
        s = _rect_hollow(400, 600, 20)
        assert width_at_depth(s, 590) == 400.0  # nella flangia inferiore


class TestWidthAtDepthTSection:
    def test_in_flange(self):
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        assert width_at_depth(s, 50) == 600.0

    def test_in_web(self):
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        assert width_at_depth(s, 300) == 200.0

    def test_at_transition(self):
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        # Esattamente alla transizione flangia-anima
        assert width_at_depth(s, 100) == 600.0  # y <= tf → flangia

    def test_just_below_flange(self):
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        assert width_at_depth(s, 101) == 200.0  # y > tf → anima


class TestWidthAtDepthInvertedT:
    def test_in_web(self):
        s = _inv_t(bf=600, tf=100, tw=200, hw=400)
        assert width_at_depth(s, 200) == 200.0  # anima in alto

    def test_in_flange(self):
        s = _inv_t(bf=600, tf=100, tw=200, hw=400)
        assert width_at_depth(s, 450) == 600.0  # flangia in basso


class TestWidthAtDepthISection:
    def test_top_flange(self):
        s = _i_section(bf=300, tf=20, tw=12, hw=360)
        assert width_at_depth(s, 10) == 300.0

    def test_web(self):
        s = _i_section(bf=300, tf=20, tw=12, hw=360)
        assert width_at_depth(s, 200) == 12.0

    def test_bottom_flange(self):
        s = _i_section(bf=300, tf=20, tw=12, hw=360)
        assert width_at_depth(s, 390) == 300.0


class TestWidthAtDepthPiSection:
    def test_in_flange(self):
        s = _pi_section(bf=1000, tf=120, tw=150, hw=500)
        assert width_at_depth(s, 60) == 1000.0

    def test_in_webs(self):
        s = _pi_section(bf=1000, tf=120, tw=150, hw=500)
        assert width_at_depth(s, 300) == 300.0  # 2 * 150


class TestWidthAtDepthCSection:
    def test_top_flange(self):
        s = _c_section(w=100, h=200, tf=10, tw=8)
        assert width_at_depth(s, 5) == 100.0

    def test_web(self):
        s = _c_section(w=100, h=200, tf=10, tw=8)
        assert width_at_depth(s, 100) == 8.0

    def test_bottom_flange(self):
        s = _c_section(w=100, h=200, tf=10, tw=8)
        assert width_at_depth(s, 195) == 100.0


class TestWidthAtDepthLSection:
    def test_horizontal_leg(self):
        s = _l_section(w=150, h=200, th=15, tv=15)
        assert width_at_depth(s, 7) == 150.0  # braccio orizzontale

    def test_vertical_leg(self):
        s = _l_section(w=150, h=200, th=15, tv=15)
        assert width_at_depth(s, 100) == 15.0  # braccio verticale


class TestWidthAtDepthVSection:
    def test_top_wide(self):
        s = _v_section(w=300, h=400, t=10)
        # In alto (y=0): larghezza = 300 (esterna) - 280 (interna) = ~20 (2*t)
        # Ma: w_ext = 300*(1-0) = 300, w_int = 280*(1-0) = 280, diff = 20
        assert width_at_depth(s, 0) == pytest.approx(20.0, rel=0.01)

    def test_bottom_zero(self):
        s = _v_section(w=300, h=400, t=10)
        # In basso (y=h): larghezza = 0
        assert width_at_depth(s, 400) == pytest.approx(0.0, abs=0.1)


class TestWidthAtDepthInvertedV:
    def test_top_zero(self):
        s = _inv_v(w=300, h=400, t=10)
        assert width_at_depth(s, 0) == pytest.approx(0.0, abs=0.1)


# ===========================================================================
# Test integrazione area
# ===========================================================================

class TestAreaIntegration:
    """Verifica che l'integrazione numerica restituisca l'area corretta."""

    def test_rectangular_area(self):
        s = _rect(300, 500)
        area = compute_section_area(s, n_strips=200)
        assert area == pytest.approx(300 * 500, rel=0.01)

    def test_circular_area(self):
        s = _circ(400)
        expected = math.pi * 200**2
        area = compute_section_area(s, n_strips=500)
        assert area == pytest.approx(expected, rel=0.01)

    def test_t_section_area(self):
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        # A = bf*tf + tw*hw = 600*100 + 200*400 = 60000 + 80000 = 140000
        area = compute_section_area(s, n_strips=200)
        assert area == pytest.approx(140000, rel=0.01)

    def test_i_section_area(self):
        s = _i_section(bf=300, tf=20, tw=12, hw=360)
        # A = 2*bf*tf + tw*hw = 2*300*20 + 12*360 = 12000 + 4320 = 16320
        area = compute_section_area(s, n_strips=200)
        assert area == pytest.approx(16320, rel=0.01)

    def test_rect_hollow_area(self):
        s = _rect_hollow(400, 600, 20)
        # A = 400*600 - (400-40)*(600-40) = 240000 - 360*560 = 240000 - 201600 = 38400
        area = compute_section_area(s, n_strips=200)
        assert area == pytest.approx(38400, rel=0.02)

    def test_c_section_area(self):
        s = _c_section(w=100, h=200, tf=10, tw=8)
        # A = 2*w*tf + tw*(h-2*tf) = 2*100*10 + 8*180 = 2000 + 1440 = 3440
        area = compute_section_area(s, n_strips=200)
        assert area == pytest.approx(3440, rel=0.02)

    def test_l_section_area(self):
        s = _l_section(w=150, h=200, th=15, tv=15)
        # A = w*th + tv*(h-th) = 150*15 + 15*185 = 2250 + 2775 = 5025
        area = compute_section_area(s, n_strips=200)
        assert area == pytest.approx(5025, rel=0.02)


# ===========================================================================
# Test compute_concrete_resultant
# ===========================================================================

class TestConcreteResultant:
    """Verifica risultante cls compresso."""

    def test_rect_full_compression(self):
        """Rettangolare, asse neutro tale che stress block copre tutto h."""
        s = _rect(300, 500)
        f_cd = 14.17  # MPa (C25/30)
        # Per coprire tutta h con stress block: lambda*x_na >= h → x_na >= h/lambda = 625
        R_c, M_c = compute_concrete_resultant(s, 625, f_cd, axis="x")
        # x_block = min(0.8 * 625, 500) = 500 → tutta l'altezza
        expected_R = 300 * 500 * f_cd
        assert R_c == pytest.approx(expected_R, rel=0.02)
        # Momento quasi nullo se compressione centrata (simmetrica)
        assert abs(M_c) < expected_R * 5  # piccolo, non esattamente zero per integrazione

    def test_rect_partial_compression(self):
        """Rettangolare, asse neutro parziale."""
        s = _rect(300, 500)
        f_cd = 14.17
        x_na = 200  # mm
        R_c, M_c = compute_concrete_resultant(s, x_na, f_cd, axis="x")
        # x_block = 0.8 * 200 = 160 mm
        expected_R = 300 * 160 * f_cd
        assert R_c == pytest.approx(expected_R, rel=0.02)
        # z_c = h/2 - x_block/2 = 250 - 80 = 170 mm → M_c = R_c * 170
        assert M_c == pytest.approx(R_c * 170, rel=0.05)

    def test_t_section_flange_only(self):
        """T-section: asse neutro nella flangia, solo flangia compressa."""
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        f_cd = 14.17
        # x_na = 50/0.8 = 62.5 → x_block = 50 < tf=100: solo flangia
        x_na = 62.5
        R_c, M_c = compute_concrete_resultant(s, x_na, f_cd, axis="x")
        expected_R = 600 * 50 * f_cd
        assert R_c == pytest.approx(expected_R, rel=0.02)

    def test_t_section_into_web(self):
        """T-section: asse neutro nell'anima, flangia + parte anima compressa."""
        s = _t_section(bf=600, tf=100, tw=200, hw=400)
        f_cd = 14.17
        x_na = 200  # mm → x_block = 160 mm, di cui 100 in flangia + 60 in anima
        R_c, M_c = compute_concrete_resultant(s, x_na, f_cd, axis="x")
        expected_R = (600 * 100 + 200 * 60) * f_cd
        assert R_c == pytest.approx(expected_R, rel=0.03)

    def test_zero_depth(self):
        """Asse neutro a zero: nessuna compressione."""
        s = _rect(300, 500)
        R_c, M_c = compute_concrete_resultant(s, 0, 14.17, axis="x")
        assert R_c == 0.0
        assert M_c == 0.0

    def test_negative_depth(self):
        """Asse neutro negativo: nessuna compressione."""
        s = _rect(300, 500)
        R_c, M_c = compute_concrete_resultant(s, -100, 14.17, axis="x")
        assert R_c == 0.0
        assert M_c == 0.0

    def test_axis_y(self):
        """Risultante per flessione attorno a y (asse neutro verticale)."""
        s = _rect(300, 500)
        f_cd = 14.17
        x_na = 150  # mm → x_block = 0.8*150 = 120 mm
        R_c, M_c = compute_concrete_resultant(s, x_na, f_cd, axis="y")
        # Per asse y: "altezza" = larghezza = 300, width_func = height_at_horizontal
        # height_at_horizontal per rect = height se 0<=x<=width
        # R_c = 500 * 120 * f_cd
        expected_R = 500 * 120 * f_cd
        assert R_c == pytest.approx(expected_R, rel=0.02)
