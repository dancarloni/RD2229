"""Test per il modulo CNR-DT 207 R1/2018 (cnr_dt207.py)."""

from __future__ import annotations

import pytest

from src.wind.cnr_dt207 import (
    CscdDetailedResult,
    compute_aerodynamic_admittance,
    compute_background_factor,
    compute_integral_length_scale,
    compute_peak_factor,
    compute_resonance_factor,
    compute_spectral_density,
    compute_structural_factor,
    compute_structural_factor_detailed,
    compute_turbulence_intensity,
    enrich_results_with_cnr_dt207,
)
from src.wind.models import BuildingGeom, StructureGeom, WindSite
from src.wind.outputs import WindResults

# ===========================================================================
# Intensità di turbolenza
# ===========================================================================


class TestTurbulenceIntensity:
    def test_standard_value(self):
        """Iv(10m) con z0=0.05 deve essere circa 0.19."""
        iv = compute_turbulence_intensity(10.0, 0.05, 2.0)
        assert 0.15 < iv < 0.25

    def test_decreases_with_height(self):
        iv10 = compute_turbulence_intensity(10.0, 0.05, 2.0)
        iv50 = compute_turbulence_intensity(50.0, 0.05, 2.0)
        assert iv50 < iv10

    def test_increases_with_roughness(self):
        iv_open = compute_turbulence_intensity(10.0, 0.01, 1.0)
        iv_urban = compute_turbulence_intensity(10.0, 1.00, 10.0)
        assert iv_urban > iv_open

    def test_z_min_clamp(self):
        """Below z_min, should use z_min."""
        iv_low = compute_turbulence_intensity(0.5, 0.05, 2.0)
        iv_min = compute_turbulence_intensity(2.0, 0.05, 2.0)
        assert iv_low == pytest.approx(iv_min)


# ===========================================================================
# Scala integrale di turbolenza
# ===========================================================================


class TestIntegralLengthScale:
    def test_increases_with_height(self):
        L10 = compute_integral_length_scale(10.0)
        L50 = compute_integral_length_scale(50.0)
        assert L50 > L10

    def test_positive(self):
        L = compute_integral_length_scale(10.0)
        assert L > 0

    def test_reference_at_200m(self):
        """At z=200m, L should be close to L_ref=300m."""
        L = compute_integral_length_scale(200.0)
        assert L == pytest.approx(300.0, rel=0.05)


# ===========================================================================
# Fattore di fondo B²
# ===========================================================================


class TestBackgroundFactor:
    def test_small_structure(self):
        """Small structure → B² close to 1."""
        B2 = compute_background_factor(5.0, 5.0, 200.0)
        assert B2 > 0.8

    def test_large_structure(self):
        """Large structure → B² lower."""
        B2_small = compute_background_factor(10.0, 10.0, 200.0)
        B2_large = compute_background_factor(100.0, 50.0, 200.0)
        assert B2_large < B2_small

    def test_range(self):
        B2 = compute_background_factor(30.0, 20.0, 150.0)
        assert 0 < B2 <= 1.0

    def test_zero_L(self):
        assert compute_background_factor(10.0, 10.0, 0.0) == 1.0


# ===========================================================================
# Densità spettrale
# ===========================================================================


class TestSpectralDensity:
    def test_positive(self):
        S = compute_spectral_density(0.5)
        assert S > 0

    def test_zero_frequency(self):
        assert compute_spectral_density(0.0) == 0.0

    def test_peak_around_n05(self):
        """S_L should peak around n ≈ 0.1-0.2."""
        S_low = compute_spectral_density(0.01)
        S_mid = compute_spectral_density(0.15)
        S_high = compute_spectral_density(5.0)
        assert S_mid > S_low
        assert S_mid > S_high


# ===========================================================================
# Ammettenza aerodinamica
# ===========================================================================


class TestAerodynamicAdmittance:
    def test_zero_eta(self):
        assert compute_aerodynamic_admittance(0.0) == 1.0

    def test_small_eta(self):
        R = compute_aerodynamic_admittance(0.1)
        assert 0.9 < R <= 1.0

    def test_large_eta(self):
        R = compute_aerodynamic_admittance(10.0)
        assert R < 0.2

    def test_decreases_monotonically(self):
        etas = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        Rs = [compute_aerodynamic_admittance(e) for e in etas]
        for i in range(len(Rs) - 1):
            assert Rs[i] > Rs[i + 1]


# ===========================================================================
# Fattore di risonanza R²
# ===========================================================================


class TestResonanceFactor:
    def test_positive(self):
        R2 = compute_resonance_factor(1.0, 30.0, 15.0, 25.0, 150.0, 0.05)
        assert R2 > 0

    def test_zero_damping(self):
        R2 = compute_resonance_factor(1.0, 30.0, 15.0, 25.0, 150.0, 0.0)
        assert R2 == 0.0

    def test_higher_damping_reduces_R2(self):
        R2_low = compute_resonance_factor(1.0, 30.0, 15.0, 25.0, 150.0, 0.03)
        R2_high = compute_resonance_factor(1.0, 30.0, 15.0, 25.0, 150.0, 0.10)
        assert R2_high < R2_low

    def test_zero_frequency(self):
        R2 = compute_resonance_factor(0.0, 30.0, 15.0, 25.0, 150.0, 0.05)
        assert R2 == 0.0


# ===========================================================================
# Fattore di picco
# ===========================================================================


class TestPeakFactor:
    def test_default(self):
        kp = compute_peak_factor(0.2)
        assert kp == pytest.approx(3.5)

    def test_with_dynamics(self):
        kp = compute_peak_factor(0.2, f1=0.5, B2=0.6, R2=0.3)
        assert kp >= 3.0

    def test_minimum_3(self):
        kp = compute_peak_factor(0.2, f1=0.01, B2=0.99, R2=0.001)
        assert kp >= 3.0


# ===========================================================================
# compute_structural_factor (semplificato e dettagliato)
# ===========================================================================


class TestStructuralFactor:
    def test_rigid_structure(self):
        """h ≤ 15m → cs·cd = 1.0."""
        bg = BuildingGeom(height_m=10.0)
        assert compute_structural_factor(bg) == 1.0

    def test_high_frequency(self):
        """f1 > 1 Hz → cs·cd = 1.0."""
        sg = StructureGeom(height_m=50.0, natural_frequency_hz=2.0)
        assert compute_structural_factor(sg) == 1.0

    def test_tabular_20m(self):
        bg = BuildingGeom(height_m=20.0)
        cscd = compute_structural_factor(bg)
        assert cscd == pytest.approx(0.95, abs=0.01)

    def test_tabular_50m(self):
        bg = BuildingGeom(height_m=50.0)
        cscd = compute_structural_factor(bg)
        assert cscd == pytest.approx(0.90, abs=0.01)

    def test_tabular_100m(self):
        bg = BuildingGeom(height_m=100.0)
        cscd = compute_structural_factor(bg)
        assert cscd == pytest.approx(0.85, abs=0.01)

    def test_override(self):
        bg = BuildingGeom(height_m=50.0)
        assert compute_structural_factor(bg, override=0.92) == 0.92

    def test_detailed_with_f1_and_damping(self):
        """When f1 and damping are provided, uses detailed calculation."""
        sg = StructureGeom(
            height_m=60.0,
            width_m=20.0,
            natural_frequency_hz=0.5,
            damping_log_decrement=0.05,
        )
        cscd = compute_structural_factor(sg)
        assert 0.85 <= cscd <= 1.15

    def test_decreases_with_height(self):
        cscd_20 = compute_structural_factor(BuildingGeom(height_m=20.0))
        cscd_80 = compute_structural_factor(BuildingGeom(height_m=80.0))
        assert cscd_80 < cscd_20


# ===========================================================================
# compute_structural_factor_detailed
# ===========================================================================


class TestStructuralFactorDetailed:
    def test_returns_dataclass(self):
        sg = StructureGeom(
            height_m=60.0,
            width_m=20.0,
            natural_frequency_hz=0.5,
            damping_log_decrement=0.05,
        )
        result = compute_structural_factor_detailed(sg, v_m_ms=25.0)
        assert isinstance(result, CscdDetailedResult)
        assert result.method == "detailed"

    def test_has_all_fields(self):
        sg = StructureGeom(
            height_m=60.0,
            width_m=20.0,
            natural_frequency_hz=0.5,
            damping_log_decrement=0.05,
        )
        result = compute_structural_factor_detailed(sg, v_m_ms=25.0)
        assert result.B2 > 0
        assert result.R2 >= 0
        assert result.kp >= 3.0
        assert result.Iv > 0
        assert result.L_z_m > 0
        assert 0.85 <= result.cscd <= 1.15

    def test_cs_cd_product(self):
        """cs·cd should be approximately cs × cd."""
        sg = StructureGeom(
            height_m=80.0,
            width_m=25.0,
            natural_frequency_hz=0.4,
            damping_log_decrement=0.03,
        )
        result = compute_structural_factor_detailed(sg, v_m_ms=28.0)
        assert result.cscd == pytest.approx(result.cs * result.cd, rel=0.05)


# ===========================================================================
# enrich_results_with_cnr_dt207
# ===========================================================================


class TestEnrichResults:
    def test_adds_cnr_key(self):
        wr = WindResults(method="NTC2018", v_b_ms=25.0, q_b_kN_m2=0.39)
        enriched = enrich_results_with_cnr_dt207(
            wr,
            WindSite(),
            BuildingGeom(height_m=20.0),
        )
        assert "cnr_dt207" in enriched.extra

    def test_has_turbulence_data(self):
        wr = WindResults(method="NTC2018")
        enriched = enrich_results_with_cnr_dt207(
            wr,
            WindSite(),
            BuildingGeom(height_m=20.0),
        )
        cnr = enriched.extra["cnr_dt207"]
        assert "turbulence_intensity_at_h" in cnr
        assert "peak_factor_kp" in cnr
        assert "integral_length_scale_m" in cnr

    def test_preserves_existing_extra(self):
        wr = WindResults(method="NTC2018", extra={"existing_key": 42})
        enriched = enrich_results_with_cnr_dt207(
            wr,
            WindSite(),
            BuildingGeom(height_m=20.0),
        )
        assert enriched.extra["existing_key"] == 42
        assert "cnr_dt207" in enriched.extra
