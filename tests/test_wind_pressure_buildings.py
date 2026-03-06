"""Test per i coefficienti di pressione edifici e pressione interna."""

from __future__ import annotations

import pytest

from src.wind.pressure_coefficients import (
    get_wall_cpe,
    get_all_wall_cpe,
    get_flat_roof_cpe,
    get_pitched_roof_cpe,
    compute_building_pressure_zones,
)
from src.wind.internal_pressure import (
    compute_cpi_simplified,
    compute_cpi_detailed,
    compute_cpi_dominant_opening,
    get_cpi_values,
)
from src.wind.models import InternalPressureConfig


class TestWallCpe:
    def test_wall_D_positive(self):
        """Parete sopravento: cp_e > 0."""
        cpe = get_wall_cpe(10.0, 10.0, "D")
        assert cpe > 0

    def test_wall_E_negative(self):
        """Parete sottovento: cp_e < 0."""
        cpe = get_wall_cpe(10.0, 10.0, "E")
        assert cpe < 0

    def test_wall_lateral_negative(self):
        """Pareti laterali: cp_e < 0."""
        for zone in ("A", "B", "C"):
            cpe = get_wall_cpe(10.0, 10.0, zone)
            assert cpe < 0, f"Zone {zone} should be negative"

    def test_override(self):
        cpe = get_wall_cpe(10.0, 10.0, "D", override=0.95)
        assert cpe == 0.95

    def test_unknown_zone(self):
        cpe = get_wall_cpe(10.0, 10.0, "Z")
        assert cpe == 0.0

    def test_h_d_ratio_effect(self):
        """Higher h/d → more negative E."""
        cpe_low = get_wall_cpe(5.0, 20.0, "E")  # h/d = 0.25
        cpe_high = get_wall_cpe(50.0, 10.0, "E")  # h/d = 5.0
        assert cpe_high <= cpe_low

    def test_all_wall_cpe(self):
        result = get_all_wall_cpe(10.0, 10.0)
        assert len(result) == 5
        assert "D" in result
        assert "E" in result


class TestFlatRoofCpe:
    def test_zone_F_negative(self):
        cpe = get_flat_roof_cpe("F")
        assert cpe < 0

    def test_zone_H_less_than_F(self):
        """Central zone less extreme than corner."""
        cpe_F = get_flat_roof_cpe("F")
        cpe_H = get_flat_roof_cpe("H")
        assert abs(cpe_F) > abs(cpe_H)

    def test_override(self):
        cpe = get_flat_roof_cpe("F", override=-2.0)
        assert cpe == -2.0

    def test_unknown_zone(self):
        cpe = get_flat_roof_cpe("Z")
        assert cpe == 0.0


class TestPitchedRoofCpe:
    def test_returns_tuple(self):
        result = get_pitched_roof_cpe(30.0, "F")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_high_angle_positive(self):
        """At high angles, windward cp can be positive."""
        cp_min, cp_max = get_pitched_roof_cpe(60.0, "F")
        assert cp_max > 0

    def test_low_angle_negative(self):
        """At low angles, windward cp_min is negative."""
        cp_min, cp_max = get_pitched_roof_cpe(5.0, "F")
        assert cp_min < 0

    def test_leeward(self):
        cp_min, cp_max = get_pitched_roof_cpe(30.0, "I", windward=False)
        assert cp_min < 0


class TestBuildingPressureZones:
    def test_basic_building(self):
        zones = compute_building_pressure_zones(10.0, 10.0, 10.0, 0.5)
        assert len(zones) > 0
        # Each zone should have required keys
        for z in zones:
            assert "zone_id" in z
            assert "net_kN_m2" in z

    def test_flat_roof_building(self):
        zones = compute_building_pressure_zones(10.0, 10.0, 10.0, 0.5, roof_angle_deg=0.0)
        roof_zones = [z for z in zones if "roof" in z["zone_id"]]
        assert len(roof_zones) > 0

    def test_pitched_roof_building(self):
        zones = compute_building_pressure_zones(10.0, 10.0, 10.0, 0.5, roof_angle_deg=30.0)
        roof_zones = [z for z in zones if "roof" in z["zone_id"]]
        assert len(roof_zones) > 0


class TestInternalPressure:
    def test_simplified(self):
        pos, neg = compute_cpi_simplified()
        assert pos == 0.2
        assert neg == -0.2

    def test_detailed_mu_0(self):
        cpi = compute_cpi_detailed(0.0)
        assert cpi < 0  # All openings leeward

    def test_detailed_mu_05(self):
        cpi = compute_cpi_detailed(0.5)
        assert abs(cpi) < 0.05  # Balanced

    def test_detailed_mu_1(self):
        cpi = compute_cpi_detailed(1.0)
        assert cpi > 0  # All openings windward

    def test_detailed_monotonic(self):
        """cp_i should increase monotonically with μ."""
        prev = -1.0
        for mu in [0.0, 0.25, 0.5, 0.75, 1.0]:
            cpi = compute_cpi_detailed(mu)
            assert cpi >= prev
            prev = cpi

    def test_dominant_opening(self):
        cpi = compute_cpi_dominant_opening(0.8)
        assert cpi == pytest.approx(0.6, rel=0.01)

    def test_get_cpi_simplified_default(self):
        pos, neg = get_cpi_values(None)
        assert pos == 0.2
        assert neg == -0.2

    def test_get_cpi_detailed_config(self):
        config = InternalPressureConfig(method="detailed", mu=0.5)
        v1, v2 = get_cpi_values(config)
        assert abs(v1) < 0.05

    def test_get_cpi_dominant_config(self):
        config = InternalPressureConfig(method="detailed", dominant_opening=True)
        v1, v2 = get_cpi_values(config, cpe_dominant=0.8)
        assert v1 > 0
