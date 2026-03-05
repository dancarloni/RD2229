"""Test per il modulo report (report.py)."""

from __future__ import annotations

import json

import pytest

from src.wind.outputs import (
    FrictionForce,
    PressureZoneResults,
    WindCombination,
    WindProfilePoint,
    WindResults,
    ZoneForce,
)
from src.wind.report import (
    wind_results_to_dict,
    wind_results_to_json,
    generate_summary_table,
    generate_force_summary_table,
)


def _make_results() -> WindResults:
    """Helper: crea un WindResults completo per test."""
    return WindResults(
        method="NTC2018",
        v_b_ms=27.0,
        v_ref_ms=28.5,
        q_b_kN_m2=0.456,
        velocity_profile=[
            WindProfilePoint(z_m=5.0, v_m_s=22.0, q_kN_m2=0.30),
            WindProfilePoint(z_m=10.0, v_m_s=26.0, q_kN_m2=0.42),
            WindProfilePoint(z_m=15.0, v_m_s=28.5, q_kN_m2=0.51),
        ],
        pressure_zones=[
            PressureZoneResults(
                zone_id="wall_D", description="Parete sopravento",
                cpe=0.8, cpi=-0.2, we_kN_m2=0.408, wi_kN_m2=-0.102,
                net_kN_m2=0.510, area_m2=30.0,
            ),
            PressureZoneResults(
                zone_id="wall_E", description="Parete sottovento",
                cpe=-0.5, cpi=0.2, we_kN_m2=-0.255, wi_kN_m2=0.102,
                net_kN_m2=-0.357, area_m2=30.0,
            ),
            PressureZoneResults(
                zone_id="roof_F", description="Copertura zona F",
                cpe=-1.2, net_kN_m2=-0.612, area_m2=8.0,
            ),
        ],
        resultant_forces=[
            ZoneForce(zone_id="wall_D", F_kN=15.3, direction="pressure",
                      tributary_area_m2=30.0, application_point_m=7.5),
            ZoneForce(zone_id="wall_E", F_kN=-10.71, direction="suction",
                      tributary_area_m2=30.0, application_point_m=7.5),
            ZoneForce(zone_id="roof_F", F_kN=-4.896, direction="suction",
                      tributary_area_m2=8.0, application_point_m=15.0),
        ],
        friction_forces=[
            FrictionForce(surface_id="roof", c_fr=0.02, area_m2=100.0,
                          q_p_kN_m2=0.51, F_fr_kN=1.02),
        ],
        combinations=[
            WindCombination(combo_id="SLU_1.5", description="SLU sfavorevole",
                            gamma_w=1.5, psi=1.0),
        ],
        topography_factor=1.0,
        structural_factor=1.0,
        warnings=["Test warning"],
        extra={"sign_eccentricity_m": 0.75},
    )


# ===========================================================================
# wind_results_to_dict
# ===========================================================================

class TestWindResultsToDict:
    def test_has_meta(self):
        report = wind_results_to_dict(_make_results())
        assert "meta" in report
        assert report["meta"]["method"] == "NTC2018"
        assert "date" in report["meta"]

    def test_has_base_parameters(self):
        report = wind_results_to_dict(_make_results())
        bp = report["base_parameters"]
        assert bp["v_b_ms"] == 27.0
        assert bp["q_b_kN_m2"] == 0.456

    def test_has_velocity_profile(self):
        report = wind_results_to_dict(_make_results())
        assert "velocity_profile" in report
        assert len(report["velocity_profile"]) == 3

    def test_exclude_profile(self):
        report = wind_results_to_dict(_make_results(), include_profile=False)
        assert "velocity_profile" not in report

    def test_has_pressure_zones(self):
        report = wind_results_to_dict(_make_results())
        assert "pressure_zones" in report
        assert len(report["pressure_zones"]) == 3

    def test_has_resultant_forces(self):
        report = wind_results_to_dict(_make_results())
        assert "resultant_forces" in report
        assert len(report["resultant_forces"]) == 3

    def test_has_force_summary(self):
        report = wind_results_to_dict(_make_results())
        assert "force_summary" in report
        summary = report["force_summary"]
        assert "N" in summary
        assert "Tx" in summary
        assert "Mx" in summary

    def test_has_friction(self):
        report = wind_results_to_dict(_make_results())
        assert "friction_forces" in report
        assert report["friction_total_kN"] == pytest.approx(1.02)

    def test_has_combinations(self):
        report = wind_results_to_dict(_make_results())
        assert "combinations" in report

    def test_exclude_combinations(self):
        report = wind_results_to_dict(_make_results(), include_combinations=False)
        assert "combinations" not in report

    def test_has_warnings(self):
        report = wind_results_to_dict(_make_results())
        assert "warnings" in report
        assert "Test warning" in report["warnings"]

    def test_extra_excluded_by_default(self):
        report = wind_results_to_dict(_make_results())
        assert "extra" not in report

    def test_extra_included(self):
        report = wind_results_to_dict(_make_results(), include_extra=True)
        assert "extra" in report
        assert report["extra"]["sign_eccentricity_m"] == 0.75

    def test_project_name(self):
        report = wind_results_to_dict(
            _make_results(), project_name="Progetto Test",
        )
        assert report["meta"]["project"] == "Progetto Test"

    def test_peak_pressure(self):
        report = wind_results_to_dict(_make_results())
        assert "peak_pressure" in report
        assert report["peak_pressure"]["z_ref_m"] == 15.0

    def test_pressure_zone_with_cpi(self):
        """Zones with cpi include full pressure breakdown."""
        report = wind_results_to_dict(_make_results())
        wall_D = report["pressure_zones"][0]
        assert "cpi" in wall_D
        assert "we_kN_m2" in wall_D
        assert "wi_kN_m2" in wall_D

    def test_pressure_zone_without_cpi(self):
        """Zones without cpi omit pressure breakdown."""
        report = wind_results_to_dict(_make_results())
        roof_F = report["pressure_zones"][2]
        assert "cpi" not in roof_F

    def test_eccentricity_in_forces(self):
        """Forces with eccentricity include the field."""
        r = _make_results()
        r.resultant_forces[0].eccentricity_m = 0.75
        report = wind_results_to_dict(r)
        assert report["resultant_forces"][0]["eccentricity_m"] == 0.75

    def test_empty_results(self):
        """Empty results still produce valid report."""
        report = wind_results_to_dict(WindResults())
        assert "meta" in report
        assert "base_parameters" in report


# ===========================================================================
# wind_results_to_json
# ===========================================================================

class TestWindResultsToJson:
    def test_valid_json(self):
        j = wind_results_to_json(_make_results())
        parsed = json.loads(j)
        assert isinstance(parsed, dict)
        assert "meta" in parsed

    def test_indent(self):
        j = wind_results_to_json(_make_results(), indent=4)
        assert "    " in j

    def test_no_ascii_escape(self):
        """Italian characters should not be escaped."""
        j = wind_results_to_json(_make_results())
        # "Parete sopravento" should appear unescaped
        assert "Parete sopravento" in j

    def test_roundtrip(self):
        """JSON → parse → dict matches original."""
        report1 = wind_results_to_dict(_make_results())
        j = json.dumps(report1, indent=2, ensure_ascii=False)
        report2 = json.loads(j)
        assert report1 == report2


# ===========================================================================
# generate_summary_table
# ===========================================================================

class TestSummaryTable:
    def test_returns_list(self):
        rows = generate_summary_table(_make_results())
        assert isinstance(rows, list)
        assert len(rows) == 3

    def test_row_keys(self):
        rows = generate_summary_table(_make_results())
        for r in rows:
            assert "zone_id" in r
            assert "cpe" in r
            assert "net_kN_m2" in r
            assert "area_m2" in r
            assert "F_kN" in r

    def test_force_computed(self):
        rows = generate_summary_table(_make_results())
        wall_D = rows[0]
        assert wall_D["F_kN"] == pytest.approx(0.510 * 30.0, rel=0.01)

    def test_empty_results(self):
        rows = generate_summary_table(WindResults())
        assert rows == []


# ===========================================================================
# generate_force_summary_table
# ===========================================================================

class TestForceSummaryTable:
    def test_returns_list(self):
        rows = generate_force_summary_table(_make_results())
        assert isinstance(rows, list)
        assert len(rows) == 3

    def test_moment_computed(self):
        rows = generate_force_summary_table(_make_results())
        wall_D = rows[0]
        assert wall_D["M_kNm"] == pytest.approx(15.3 * 7.5, rel=0.01)

    def test_eccentricity_included(self):
        r = _make_results()
        r.resultant_forces[0].eccentricity_m = 1.0
        rows = generate_force_summary_table(r)
        assert "eccentricity_m" in rows[0]
        assert rows[0]["eccentricity_m"] == 1.0

    def test_eccentricity_omitted_when_zero(self):
        rows = generate_force_summary_table(_make_results())
        assert "eccentricity_m" not in rows[0]

    def test_empty_results(self):
        rows = generate_force_summary_table(WindResults())
        assert rows == []
