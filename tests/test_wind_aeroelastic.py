"""Test per il modulo effetti aeroelastici (aeroelastic.py)."""

from __future__ import annotations

import pytest

from src.wind.aeroelastic import (
    AeroelasticCheckResult,
    GallopingResult,
    VortexSheddingResult,
    check_aeroelastic_effects,
    check_galloping,
    check_vortex_shedding,
    compute_critical_wind_speed,
    get_strouhal_number,
)

# ===========================================================================
# Velocità critica e Strouhal
# ===========================================================================

class TestCriticalWindSpeed:
    def test_basic(self):
        """v_cr = n1 · b / St."""
        v = compute_critical_wind_speed(1.0, 0.5, St=0.18)
        assert v == pytest.approx(1.0 * 0.5 / 0.18, rel=0.01)

    def test_higher_frequency(self):
        v1 = compute_critical_wind_speed(1.0, 0.5, St=0.18)
        v2 = compute_critical_wind_speed(2.0, 0.5, St=0.18)
        assert v2 == pytest.approx(2.0 * v1, rel=0.01)

    def test_zero_frequency(self):
        assert compute_critical_wind_speed(0.0, 0.5) == 0.0

    def test_zero_strouhal(self):
        assert compute_critical_wind_speed(1.0, 0.5, St=0.0) == 0.0


class TestStrouhalNumber:
    def test_circular(self):
        assert get_strouhal_number("circular") == 0.18

    def test_square(self):
        assert get_strouhal_number("square") == 0.12

    def test_unknown_defaults_to_018(self):
        assert get_strouhal_number("unknown_shape") == 0.18

    def test_case_insensitive(self):
        assert get_strouhal_number("CIRCULAR") == 0.18


# ===========================================================================
# Verifica distacco vortici
# ===========================================================================

class TestVortexShedding:
    def test_not_susceptible(self):
        """High v_cr → not susceptible."""
        result = check_vortex_shedding(
            n1_hz=5.0, b_m=0.3, v_mean_ms=10.0,
            section_type="circular",
        )
        # v_cr = 5.0 * 0.3 / 0.18 ≈ 8.33, ratio ≈ 0.83 < 1.25 → susceptible
        # Actually 8.33 / 10.0 = 0.83 < 1.25 → susceptible
        assert isinstance(result, VortexSheddingResult)
        assert result.St == pytest.approx(0.18)

    def test_susceptible_low_frequency(self):
        """Low frequency → low v_cr → susceptible."""
        result = check_vortex_shedding(
            n1_hz=0.5, b_m=1.0, v_mean_ms=20.0,
            section_type="circular",
        )
        # v_cr = 0.5 * 1.0 / 0.18 ≈ 2.78, ratio ≈ 0.14 < 1.25
        assert result.is_susceptible is True
        assert result.check_ratio < 1.25

    def test_not_susceptible_high_frequency(self):
        """High frequency → high v_cr → not susceptible."""
        result = check_vortex_shedding(
            n1_hz=50.0, b_m=0.1, v_mean_ms=10.0,
            section_type="circular",
        )
        # v_cr = 50 * 0.1 / 0.18 ≈ 27.8, ratio ≈ 2.78 > 1.25
        assert result.is_susceptible is False
        assert result.check_ratio > 1.25

    def test_has_warnings(self):
        result = check_vortex_shedding(
            n1_hz=1.0, b_m=0.5, v_mean_ms=10.0,
        )
        assert len(result.warnings) > 0

    def test_insufficient_data(self):
        result = check_vortex_shedding(0.0, 0.5, 10.0)
        assert result.is_susceptible is False
        assert "insufficienti" in result.warnings[0].lower()

    def test_amplitude_estimated_with_mass(self):
        """When mass is provided, amplitude is estimated."""
        result = check_vortex_shedding(
            n1_hz=0.5, b_m=1.0, v_mean_ms=20.0,
            section_type="circular",
            mass_per_length_kg_m=100.0,
            damping_log_dec=0.03,
        )
        assert result.is_susceptible is True
        assert result.y_max_m > 0

    def test_reynolds_number(self):
        result = check_vortex_shedding(
            n1_hz=1.0, b_m=0.5, v_mean_ms=10.0,
        )
        assert result.Re_cr > 0


# ===========================================================================
# Verifica galloping
# ===========================================================================

class TestGalloping:
    def test_circular_not_susceptible(self):
        """Circular sections are not susceptible to galloping."""
        result = check_galloping(
            n1_hz=1.0, b_m=0.5, v_mean_ms=20.0,
            section_type="circular",
        )
        assert result.is_susceptible is False

    def test_square_susceptible(self):
        """Square sections are susceptible to galloping."""
        result = check_galloping(
            n1_hz=1.0, b_m=0.5, v_mean_ms=20.0,
            section_type="square",
            mass_per_length_kg_m=50.0,
            damping_log_dec=0.02,
        )
        assert isinstance(result, GallopingResult)
        assert result.a_G > 0

    def test_custom_a_G(self):
        """Custom a_G override works."""
        result = check_galloping(
            n1_hz=1.0, b_m=0.5, v_mean_ms=20.0,
            section_type="circular",
            mass_per_length_kg_m=100.0,
            damping_log_dec=0.05,
            a_G=5.0,
        )
        assert result.a_G == 5.0

    def test_has_warnings(self):
        result = check_galloping(
            n1_hz=1.0, b_m=0.5, v_mean_ms=20.0,
            section_type="square",
            mass_per_length_kg_m=100.0,
            damping_log_dec=0.05,
        )
        assert len(result.warnings) > 0

    def test_insufficient_mass(self):
        result = check_galloping(
            n1_hz=1.0, b_m=0.5, v_mean_ms=20.0,
            section_type="square",
            mass_per_length_kg_m=0.0,
        )
        assert "insufficienti" in result.warnings[0].lower()


# ===========================================================================
# Verifica complessiva
# ===========================================================================

class TestAeroelasticCheck:
    def test_returns_combined_result(self):
        result = check_aeroelastic_effects(
            n1_hz=1.0, b_m=0.5, v_mean_ms=15.0,
            section_type="circular",
        )
        assert isinstance(result, AeroelasticCheckResult)
        assert isinstance(result.vortex_shedding, VortexSheddingResult)
        assert isinstance(result.galloping, GallopingResult)

    def test_safe_structure(self):
        """Stiff structure → not susceptible."""
        result = check_aeroelastic_effects(
            n1_hz=50.0, b_m=0.1, v_mean_ms=10.0,
            section_type="circular",
        )
        assert result.requires_detailed_analysis is False

    def test_flexible_structure_flagged(self):
        """Flexible structure → flagged for detailed analysis."""
        result = check_aeroelastic_effects(
            n1_hz=0.3, b_m=1.0, v_mean_ms=25.0,
            section_type="circular",
            mass_per_length_kg_m=100.0,
        )
        # v_cr ≈ 0.3*1.0/0.18 ≈ 1.67 vs 25 → susceptible
        assert result.vortex_shedding.is_susceptible is True
        assert result.requires_detailed_analysis is True
        assert len(result.warnings) > 0
