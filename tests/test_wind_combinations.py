"""Test per combinazioni, forze risultanti, attrito e schermatura."""

from __future__ import annotations

import pytest

from src.wind.combinations import generate_wind_combinations
from src.wind.friction import (
    compute_building_friction,
    compute_friction_force,
    get_friction_coefficient,
)
from src.wind.outputs import PressureZoneResults, ZoneForce
from src.wind.resultant_forces import (
    compute_base_moment,
    compute_resultant_forces,
    compute_zone_force,
    forces_to_calc_input,
    sum_horizontal_forces,
)
from src.wind.shielding import (
    compute_shielding_factor,
    compute_solar_row_shielding,
    compute_urban_shielding,
)

# ===========================================================================
# Combinazioni
# ===========================================================================

class TestCombinations:
    def _sample_pressures(self):
        return [
            PressureZoneResults(zone_id="D", cpe=0.8, net_kN_m2=0.4),
            PressureZoneResults(zone_id="E", cpe=-0.5, net_kN_m2=-0.25),
        ]

    def test_generates_5_combos(self):
        combos = generate_wind_combinations(self._sample_pressures())
        assert len(combos) == 5

    def test_slu_favorable_zero(self):
        combos = generate_wind_combinations(self._sample_pressures())
        slu_fav = [c for c in combos if c.combo_id == "SLU_0.0"][0]
        assert all(p.net_kN_m2 == 0.0 for p in slu_fav.pressures)

    def test_slu_unfavorable_scaled(self):
        combos = generate_wind_combinations(self._sample_pressures())
        slu = [c for c in combos if c.combo_id == "SLU_1.5"][0]
        assert slu.pressures[0].net_kN_m2 == pytest.approx(0.6, rel=0.01)

    def test_sle_car_scaled(self):
        combos = generate_wind_combinations(self._sample_pressures())
        sle = [c for c in combos if c.combo_id == "SLE_car"][0]
        assert sle.psi == 0.6
        assert sle.pressures[0].net_kN_m2 == pytest.approx(0.24, rel=0.01)

    def test_sle_qp_zero(self):
        combos = generate_wind_combinations(self._sample_pressures())
        qp = [c for c in combos if c.combo_id == "SLE_qp"][0]
        assert qp.psi == 0.0
        assert all(p.net_kN_m2 == 0.0 for p in qp.pressures)

    def test_with_forces(self):
        forces = [ZoneForce(zone_id="D", F_kN=10.0)]
        combos = generate_wind_combinations(self._sample_pressures(), resultant_forces=forces)
        slu = [c for c in combos if c.combo_id == "SLU_1.5"][0]
        assert slu.resultant_forces[0].F_kN == pytest.approx(15.0, rel=0.01)


# ===========================================================================
# Forze risultanti
# ===========================================================================

class TestResultantForces:
    def test_zone_force(self):
        pz = PressureZoneResults(zone_id="D", net_kN_m2=0.5, area_m2=20.0)
        force = compute_zone_force(pz)
        assert force.F_kN == pytest.approx(10.0, rel=0.01)
        assert force.direction == "pressure"

    def test_zone_force_suction(self):
        pz = PressureZoneResults(zone_id="E", net_kN_m2=-0.5, area_m2=20.0)
        force = compute_zone_force(pz)
        assert force.F_kN < 0
        assert force.direction == "suction"

    def test_zone_force_zero_area(self):
        pz = PressureZoneResults(zone_id="X", net_kN_m2=0.5, area_m2=0.0)
        force = compute_zone_force(pz)
        assert force.F_kN == 0.0

    def test_resultant_forces(self):
        zones = [
            PressureZoneResults(zone_id="D", net_kN_m2=0.5, area_m2=20.0),
            PressureZoneResults(zone_id="E", net_kN_m2=-0.3, area_m2=20.0),
        ]
        forces = compute_resultant_forces(zones, height_m=10.0)
        assert len(forces) == 2

    def test_sum_horizontal(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, direction="pressure"),
            ZoneForce(zone_id="E", F_kN=-5.0, direction="suction"),
        ]
        total = sum_horizontal_forces(forces)
        assert total == pytest.approx(5.0, rel=0.01)

    def test_base_moment(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, application_point_m=5.0),
        ]
        M = compute_base_moment(forces)
        assert M == pytest.approx(50.0, rel=0.01)

    def test_to_calc_input(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, direction="pressure", application_point_m=5.0),
        ]
        ci = forces_to_calc_input(forces)
        assert "Tx" in ci
        assert "Mx" in ci
        assert ci["Tx"] == pytest.approx(10.0, rel=0.01)
        assert ci["Mx"] == pytest.approx(50.0, rel=0.01)


# ===========================================================================
# Attrito
# ===========================================================================

class TestFriction:
    def test_smooth_coefficient(self):
        cfr = get_friction_coefficient("SMOOTH")
        assert cfr == pytest.approx(0.01)

    def test_rough_coefficient(self):
        cfr = get_friction_coefficient("ROUGH")
        assert cfr == pytest.approx(0.02)

    def test_very_rough_coefficient(self):
        cfr = get_friction_coefficient("VERY_ROUGH")
        assert cfr == pytest.approx(0.04)

    def test_override(self):
        cfr = get_friction_coefficient("SMOOTH", override=0.05)
        assert cfr == 0.05

    def test_friction_force(self):
        ff = compute_friction_force(0.5, "ROUGH", 100.0)
        assert ff.F_fr_kN == pytest.approx(0.02 * 0.5 * 100.0, rel=0.01)

    def test_building_friction_short(self):
        """Short building (d ≤ min(2h, 4b)) → no friction."""
        forces = compute_building_friction(10.0, 10.0, 10.0, 0.5)
        assert len(forces) == 0

    def test_building_friction_deep(self):
        """Deep building (d > min(2h, 4b)) → friction forces."""
        forces = compute_building_friction(10.0, 10.0, 100.0, 0.5)
        assert len(forces) > 0
        assert all(f.F_fr_kN > 0 for f in forces)


# ===========================================================================
# Schermatura
# ===========================================================================

class TestShielding:
    def test_no_shielding_far(self):
        k = compute_shielding_factor(100.0, 10.0, 10.0)
        assert k == 1.0

    def test_some_shielding_close(self):
        k = compute_shielding_factor(5.0, 10.0, 10.0)
        assert k < 1.0
        assert k >= 0.6

    def test_override(self):
        k = compute_shielding_factor(5.0, 10.0, override=0.8)
        assert k == 0.8

    def test_minimum_bound(self):
        """Shielding factor should never be below 0.6."""
        k = compute_shielding_factor(0.1, 10.0, 10.0)
        assert k >= 0.6

    def test_solar_row_first(self):
        k = compute_solar_row_shielding(0, 5.0, 2.0, 25.0)
        assert k == 1.0

    def test_solar_row_subsequent(self):
        k = compute_solar_row_shielding(2, 5.0, 2.0, 25.0)
        assert k < 1.0

    def test_urban_shielding_tall(self):
        """Tall building above surroundings → no shielding."""
        k = compute_urban_shielding(50.0, 15.0, 20.0)
        assert k == 1.0

    def test_urban_shielding_low(self):
        """Low building among tall surroundings → some shielding."""
        k = compute_urban_shielding(10.0, 20.0, 15.0)
        assert k < 1.0
