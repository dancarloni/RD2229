"""Test per strutture speciali: tettoie, insegne, pannelli FV, muri isolati."""

from __future__ import annotations

import pytest

from src.wind.special_structures import (
    get_canopy_cp,
    get_canopy_multibay_factor,
    compute_canopy_pressures,
    compute_shelter_pressures,
    get_sign_cf,
    compute_sign_force,
    get_solar_panel_cp,
    compute_solar_pressures,
    get_freestanding_wall_cp,
)


# ===========================================================================
# Tettoie
# ===========================================================================

class TestCanopyCp:
    def test_monopitch_returns_tuple(self):
        cp_max, cp_min = get_canopy_cp("CANOPY_MONO", 10.0, 0.0, "A")
        assert isinstance(cp_max, float)
        assert isinstance(cp_min, float)

    def test_monopitch_max_positive(self):
        cp_max, cp_min = get_canopy_cp("CANOPY_MONO", 15.0, 0.0, "A")
        assert cp_max > 0

    def test_monopitch_min_negative(self):
        cp_max, cp_min = get_canopy_cp("CANOPY_MONO", 15.0, 0.0, "A")
        assert cp_min < 0

    def test_duopitch(self):
        cp_max, cp_min = get_canopy_cp("CANOPY_DUO", 15.0, 0.0, "B")
        assert cp_max > cp_min

    def test_trough(self):
        cp_max, cp_min = get_canopy_cp("CANOPY_TROUGH", 10.0, 0.0, "A")
        assert cp_max > cp_min

    def test_blockage_increases_magnitude(self):
        """Higher blockage → generally higher magnitude coefficients."""
        _, cp_min_open = get_canopy_cp("CANOPY_MONO", 15.0, 0.0, "A")
        _, cp_min_closed = get_canopy_cp("CANOPY_MONO", 15.0, 1.0, "A")
        assert abs(cp_min_closed) >= abs(cp_min_open)

    def test_override(self):
        cp_max, cp_min = get_canopy_cp("CANOPY_MONO", 10.0, 0.0, "A", override_max=3.0, override_min=-3.0)
        assert cp_max == 3.0
        assert cp_min == -3.0

    def test_zone_C_larger_than_A(self):
        """Zone C (downwind) typically has higher max cp than A."""
        cp_max_A, _ = get_canopy_cp("CANOPY_MONO", 15.0, 0.0, "A")
        cp_max_C, _ = get_canopy_cp("CANOPY_MONO", 15.0, 0.0, "C")
        assert cp_max_C > cp_max_A


class TestCanopyMultibay:
    def test_first_bay(self):
        assert get_canopy_multibay_factor(0) == 1.0

    def test_second_bay_reduced(self):
        f = get_canopy_multibay_factor(1)
        assert f < 1.0
        assert f > 0.5

    def test_third_bay_more_reduced(self):
        f2 = get_canopy_multibay_factor(1)
        f3 = get_canopy_multibay_factor(2)
        assert f3 < f2


class TestCanopyPressures:
    def test_compute_canopy_pressures(self):
        results = compute_canopy_pressures("CANOPY_MONO", 15.0, 0.0, 0.5)
        assert len(results) > 0
        for r in results:
            assert "zone_id" in r
            assert "w_max_kN_m2" in r

    def test_multibay_pressures(self):
        results = compute_canopy_pressures("CANOPY_MONO", 15.0, 0.0, 0.5, num_bays=3)
        assert len(results) == 9  # 3 zones × 3 bays


# ===========================================================================
# Pensiline
# ===========================================================================

class TestShelter:
    def test_shelter_reduced(self):
        """Shelter pressures should be less than canopy."""
        canopy = compute_canopy_pressures("CANOPY_MONO", 10.0, 0.0, 0.5)
        shelter = compute_shelter_pressures(10.0, 0.0, 0.5)
        # Shelter cp should be reduced
        for s, c in zip(shelter, canopy):
            assert abs(s["cp_net_max"]) <= abs(c["cp_net_max"])

    def test_shelter_has_reduction_key(self):
        results = compute_shelter_pressures(10.0, 0.0, 0.5)
        assert all("shelter_reduction" in r for r in results)


# ===========================================================================
# Insegne
# ===========================================================================

class TestSignCf:
    def test_solid_plate_default(self):
        cf = get_sign_cf(3.0, 2.0)
        assert cf == pytest.approx(1.8, rel=0.05)

    def test_perforated_sign_reduced(self):
        cf_solid = get_sign_cf(3.0, 2.0, solidity_ratio=1.0)
        cf_perf = get_sign_cf(3.0, 2.0, solidity_ratio=0.5)
        assert cf_perf < cf_solid

    def test_lattice_flat(self):
        cf = get_sign_cf(3.0, 2.0, is_lattice=True, member_type="flat")
        assert cf > 0

    def test_lattice_circular(self):
        cf = get_sign_cf(3.0, 2.0, is_lattice=True, member_type="circular")
        assert cf > 0

    def test_lattice_lower_solidity(self):
        cf_full = get_sign_cf(3.0, 2.0, is_lattice=True, solidity_ratio=1.0)
        cf_low = get_sign_cf(3.0, 2.0, is_lattice=True, solidity_ratio=0.3)
        assert cf_low < cf_full

    def test_override(self):
        cf = get_sign_cf(3.0, 2.0, override=2.5)
        assert cf == 2.5


class TestSignForce:
    def test_basic_force(self):
        result = compute_sign_force(3.0, 2.0, 0.5)
        assert result["F_kN"] > 0
        assert result["cf"] > 0

    def test_force_proportional_to_pressure(self):
        r1 = compute_sign_force(3.0, 2.0, 0.5)
        r2 = compute_sign_force(3.0, 2.0, 1.0)
        assert r2["F_kN"] == pytest.approx(r1["F_kN"] * 2.0, rel=0.01)


# ===========================================================================
# Pannelli fotovoltaici
# ===========================================================================

class TestSolarPanelCp:
    def test_ground_mounted(self):
        cp_max, cp_min = get_solar_panel_cp("SOLAR_GROUND", 25.0, "edge")
        assert cp_max > 0
        assert cp_min < 0

    def test_ground_interior_less_than_edge(self):
        _, cp_min_edge = get_solar_panel_cp("SOLAR_GROUND", 25.0, "edge")
        _, cp_min_int = get_solar_panel_cp("SOLAR_GROUND", 25.0, "interior")
        assert abs(cp_min_int) < abs(cp_min_edge)

    def test_ground_shielding(self):
        """Later rows should have lower cp due to shielding."""
        _, cp_min_0 = get_solar_panel_cp("SOLAR_GROUND", 25.0, "edge", row_index=0)
        _, cp_min_2 = get_solar_panel_cp("SOLAR_GROUND", 25.0, "edge", row_index=2)
        assert abs(cp_min_2) < abs(cp_min_0)

    def test_flat_roof(self):
        cp_max, cp_min = get_solar_panel_cp("SOLAR_FLAT_ROOF", 15.0, "interior")
        assert cp_min < 0

    def test_flat_roof_corner_worse(self):
        _, cp_min_corner = get_solar_panel_cp("SOLAR_FLAT_ROOF", 15.0, "corner")
        _, cp_min_int = get_solar_panel_cp("SOLAR_FLAT_ROOF", 15.0, "interior")
        assert abs(cp_min_corner) > abs(cp_min_int)

    def test_pitched_roof_flush(self):
        cp_max, cp_min = get_solar_panel_cp("SOLAR_PITCHED_ROOF", 20.0, roof_angle_deg=20.0)
        assert isinstance(cp_max, float)

    def test_pitched_roof_tilted(self):
        """Tilted panels should have higher cp than flush."""
        _, cp_flush = get_solar_panel_cp("SOLAR_PITCHED_ROOF", 20.0, roof_angle_deg=20.0)
        _, cp_tilted = get_solar_panel_cp("SOLAR_PITCHED_ROOF", 30.0, roof_angle_deg=20.0)
        assert abs(cp_tilted) >= abs(cp_flush)

    def test_tracker(self):
        cp_max, cp_min = get_solar_panel_cp("SOLAR_TRACKER", 0.0, "interior", tracking_angle_deg=30.0)
        assert cp_max > 0 or cp_min < 0

    def test_tracker_stow(self):
        """At 0° tracking, loads should be low."""
        cp_max, cp_min = get_solar_panel_cp("SOLAR_TRACKER", 0.0, "interior", tracking_angle_deg=0.0)
        assert abs(cp_max) < 0.5
        assert abs(cp_min) < 0.5


class TestSolarPressures:
    def test_compute_multi_row(self):
        results = compute_solar_pressures("SOLAR_GROUND", 25.0, 0.5, num_rows=3)
        assert len(results) == 3

    def test_first_row_edge(self):
        results = compute_solar_pressures("SOLAR_GROUND", 25.0, 0.5, num_rows=2)
        assert results[0]["position"] == "edge"
        assert results[1]["position"] == "interior"


# ===========================================================================
# Muri isolati / recinzioni
# ===========================================================================

class TestFreestandingWall:
    def test_basic_wall(self):
        cp = get_freestanding_wall_cp(10.0, 3.0)
        assert cp > 0

    def test_corner_higher(self):
        cp_center = get_freestanding_wall_cp(10.0, 3.0, return_corner=False)
        cp_corner = get_freestanding_wall_cp(10.0, 3.0, return_corner=True)
        assert cp_corner > cp_center

    def test_fence_reduced(self):
        cp_solid = get_freestanding_wall_cp(10.0, 2.0, solidity_ratio=1.0)
        cp_fence = get_freestanding_wall_cp(10.0, 2.0, solidity_ratio=0.5)
        assert cp_fence < cp_solid

    def test_override(self):
        cp = get_freestanding_wall_cp(10.0, 3.0, override=3.0)
        assert cp == 3.0
