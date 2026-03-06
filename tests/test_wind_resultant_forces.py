"""Test per il modulo forze risultanti (resultant_forces.py)."""

from __future__ import annotations

import pytest

from src.wind.outputs import PressureZoneResults, ZoneForce
from src.wind.resultant_forces import (
    compute_zone_force,
    compute_resultant_forces,
    sum_horizontal_forces,
    sum_vertical_forces,
    compute_base_moment,
    forces_to_calc_input,
)


# ===========================================================================
# compute_zone_force
# ===========================================================================

class TestComputeZoneForce:
    def test_basic_positive_pressure(self):
        pz = PressureZoneResults(
            zone_id="wall_D",
            net_kN_m2=1.0,
            area_m2=10.0,
        )
        force = compute_zone_force(pz)
        assert force.F_kN == pytest.approx(10.0)
        assert force.direction == "pressure"

    def test_suction(self):
        pz = PressureZoneResults(
            zone_id="wall_E",
            net_kN_m2=-0.5,
            area_m2=10.0,
        )
        force = compute_zone_force(pz)
        assert force.F_kN == pytest.approx(-5.0)
        assert force.direction == "suction"

    def test_zero_area(self):
        pz = PressureZoneResults(zone_id="z", net_kN_m2=1.0, area_m2=0.0)
        force = compute_zone_force(pz)
        assert force.F_kN == 0.0
        assert force.direction == "none"

    def test_override_tributary_area(self):
        pz = PressureZoneResults(zone_id="z", net_kN_m2=2.0, area_m2=5.0)
        force = compute_zone_force(pz, tributary_area_m2=3.0)
        assert force.F_kN == pytest.approx(6.0)
        assert force.tributary_area_m2 == 3.0

    def test_application_point(self):
        pz = PressureZoneResults(zone_id="z", net_kN_m2=1.0, area_m2=1.0)
        force = compute_zone_force(pz, application_point_m=5.0)
        assert force.application_point_m == 5.0

    def test_eccentricity(self):
        """Eccentricity is stored in ZoneForce (CNR-DT 207 G.7)."""
        pz = PressureZoneResults(zone_id="sign", net_kN_m2=1.0, area_m2=6.0)
        force = compute_zone_force(pz, eccentricity_m=0.75)
        assert force.eccentricity_m == pytest.approx(0.75)
        assert force.F_kN == pytest.approx(6.0)

    def test_eccentricity_default_zero(self):
        pz = PressureZoneResults(zone_id="wall_D", net_kN_m2=1.0, area_m2=5.0)
        force = compute_zone_force(pz)
        assert force.eccentricity_m == 0.0


# ===========================================================================
# compute_resultant_forces
# ===========================================================================

class TestComputeResultantForces:
    def _make_zones(self):
        return [
            PressureZoneResults(zone_id="wall_D", net_kN_m2=0.8, area_m2=20.0),
            PressureZoneResults(zone_id="wall_E", net_kN_m2=-0.5, area_m2=20.0),
            PressureZoneResults(zone_id="roof_F", net_kN_m2=-1.2, area_m2=8.0),
        ]

    def test_returns_list(self):
        forces = compute_resultant_forces(self._make_zones(), height_m=10.0)
        assert isinstance(forces, list)
        assert len(forces) == 3

    def test_wall_application_point_half_height(self):
        forces = compute_resultant_forces(self._make_zones(), height_m=10.0)
        wall_D = [f for f in forces if f.zone_id == "wall_D"][0]
        assert wall_D.application_point_m == pytest.approx(5.0)

    def test_roof_application_point_full_height(self):
        forces = compute_resultant_forces(self._make_zones(), height_m=10.0)
        roof = [f for f in forces if f.zone_id == "roof_F"][0]
        assert roof.application_point_m == pytest.approx(10.0)

    def test_default_area(self):
        zones = [PressureZoneResults(zone_id="z", net_kN_m2=1.0, area_m2=0.0)]
        forces = compute_resultant_forces(zones, default_area_m2=5.0)
        assert len(forces) == 1
        assert forces[0].F_kN == pytest.approx(5.0)

    def test_zero_pressure_excluded(self):
        zones = [PressureZoneResults(zone_id="z", net_kN_m2=0.0, area_m2=10.0)]
        forces = compute_resultant_forces(zones)
        assert len(forces) == 0

    def test_eccentricity_propagated(self):
        """Eccentricity propagated to all ZoneForce entries."""
        zones = [
            PressureZoneResults(zone_id="sign", net_kN_m2=1.5, area_m2=6.0),
        ]
        forces = compute_resultant_forces(zones, eccentricity_m=0.75)
        assert forces[0].eccentricity_m == pytest.approx(0.75)

    def test_force_application_point_override(self):
        zones = [
            PressureZoneResults(zone_id="sign", net_kN_m2=1.0, area_m2=6.0),
        ]
        forces = compute_resultant_forces(
            zones, height_m=10.0, force_application_point_m=4.0,
        )
        assert forces[0].application_point_m == pytest.approx(4.0)


# ===========================================================================
# sum_horizontal_forces
# ===========================================================================

class TestSumHorizontalForces:
    def test_sum(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=16.0, direction="pressure"),
            ZoneForce(zone_id="E", F_kN=-10.0, direction="suction"),
        ]
        total = sum_horizontal_forces(forces)
        assert total == pytest.approx(6.0)

    def test_ignores_uplift(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, direction="pressure"),
            ZoneForce(zone_id="roof", F_kN=-5.0, direction="uplift"),
        ]
        total = sum_horizontal_forces(forces)
        assert total == pytest.approx(10.0)

    def test_includes_drag(self):
        forces = [
            ZoneForce(zone_id="fr", F_kN=2.0, direction="drag"),
        ]
        total = sum_horizontal_forces(forces)
        assert total == pytest.approx(2.0)


# ===========================================================================
# sum_vertical_forces
# ===========================================================================

class TestSumVerticalForces:
    def test_uplift(self):
        forces = [
            ZoneForce(zone_id="roof", F_kN=-9.6, direction="uplift"),
        ]
        total = sum_vertical_forces(forces)
        assert total == pytest.approx(-9.6)

    def test_ignores_pressure(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, direction="pressure"),
            ZoneForce(zone_id="roof", F_kN=-5.0, direction="uplift"),
        ]
        total = sum_vertical_forces(forces)
        assert total == pytest.approx(-5.0)


# ===========================================================================
# compute_base_moment
# ===========================================================================

class TestComputeBaseMoment:
    def test_single_force(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, application_point_m=5.0),
        ]
        M = compute_base_moment(forces)
        assert M == pytest.approx(50.0)

    def test_multiple_forces(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, application_point_m=5.0),
            ZoneForce(zone_id="E", F_kN=-6.0, application_point_m=5.0),
        ]
        M = compute_base_moment(forces)
        assert M == pytest.approx(20.0)

    def test_zero_height(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, application_point_m=0.0),
        ]
        M = compute_base_moment(forces)
        assert M == pytest.approx(0.0)


# ===========================================================================
# forces_to_calc_input
# ===========================================================================

class TestForcesToCalcInput:
    def test_basic_mapping(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=16.0, direction="pressure", application_point_m=5.0),
            ZoneForce(zone_id="E", F_kN=-10.0, direction="suction", application_point_m=5.0),
            ZoneForce(zone_id="roof", F_kN=-9.6, direction="uplift", application_point_m=10.0),
        ]
        result = forces_to_calc_input(forces)
        assert "N" in result
        assert "Tx" in result
        assert "Mx" in result

    def test_Tx_horizontal(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=16.0, direction="pressure", application_point_m=5.0),
            ZoneForce(zone_id="E", F_kN=-10.0, direction="suction", application_point_m=5.0),
        ]
        result = forces_to_calc_input(forces)
        assert result["Tx"] == pytest.approx(6.0)

    def test_N_vertical(self):
        forces = [
            ZoneForce(zone_id="roof", F_kN=-9.6, direction="uplift"),
        ]
        result = forces_to_calc_input(forces)
        assert result["N"] == pytest.approx(-9.6)

    def test_includes_friction(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, direction="pressure"),
        ]
        result = forces_to_calc_input(forces, include_friction=2.0)
        assert result["Tx"] == pytest.approx(12.0)

    def test_Mx_moment(self):
        forces = [
            ZoneForce(zone_id="D", F_kN=10.0, direction="pressure", application_point_m=6.0),
        ]
        result = forces_to_calc_input(forces)
        assert result["Mx"] == pytest.approx(60.0)


# ===========================================================================
# Test eccentricità insegne (CNR-DT 207 G.7)
# ===========================================================================

class TestSignEccentricity:
    def test_sign_force_has_eccentricity(self):
        """compute_sign_force restituisce eccentricity_m = b/4."""
        from src.wind.special_structures import compute_sign_force

        result = compute_sign_force(4.0, 2.0, 0.5)
        assert "eccentricity_m" in result
        assert result["eccentricity_m"] == pytest.approx(1.0)  # 4/4 = 1.0

    def test_sign_eccentricity_b_over_4(self):
        """Eccentricità = ±b/4 per qualsiasi larghezza."""
        from src.wind.special_structures import compute_sign_force

        for b in (2.0, 3.0, 6.0, 10.0):
            result = compute_sign_force(b, 2.0, 0.5)
            assert result["eccentricity_m"] == pytest.approx(b / 4.0)

    def test_zone_force_eccentricity_stored(self):
        """ZoneForce dataclass stores eccentricity."""
        zf = ZoneForce(
            zone_id="sign",
            F_kN=5.4,
            direction="pressure",
            eccentricity_m=0.75,
        )
        assert zf.eccentricity_m == pytest.approx(0.75)

    def test_resultant_forces_with_eccentricity(self):
        """compute_resultant_forces propagates eccentricity to ZoneForce."""
        zones = [
            PressureZoneResults(zone_id="sign", net_kN_m2=1.5, area_m2=6.0),
        ]
        forces = compute_resultant_forces(zones, eccentricity_m=1.0)
        assert len(forces) == 1
        assert forces[0].eccentricity_m == pytest.approx(1.0)
        assert forces[0].F_kN == pytest.approx(9.0)
