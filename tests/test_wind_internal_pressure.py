"""Test per il modulo pressione interna (internal_pressure.py)."""

from __future__ import annotations

import pytest

from src.wind.internal_pressure import (
    compute_cpi_detailed,
    compute_cpi_dominant_opening,
    compute_cpi_simplified,
    get_cpi_values,
)
from src.wind.models import InternalPressureConfig

# ===========================================================================
# compute_cpi_simplified
# ===========================================================================


class TestCpiSimplified:
    def test_returns_tuple(self):
        result = compute_cpi_simplified()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_values_plus_minus_02(self):
        pos, neg = compute_cpi_simplified()
        assert pos == pytest.approx(0.2)
        assert neg == pytest.approx(-0.2)

    def test_symmetric(self):
        pos, neg = compute_cpi_simplified()
        assert pos == pytest.approx(-neg)


# ===========================================================================
# compute_cpi_detailed — EC1 Fig. 7.13
# ===========================================================================


class TestCpiDetailed:
    def test_mu_0_negative(self):
        """mu=0: all openings on leeward → cp_i strongly negative."""
        cpi = compute_cpi_detailed(0.0)
        assert cpi < -0.4

    def test_mu_05_near_zero(self):
        """mu=0.5: balanced openings → cp_i ≈ 0."""
        cpi = compute_cpi_detailed(0.5)
        assert abs(cpi) < 0.05

    def test_mu_1_positive(self):
        """mu=1: all openings on windward → cp_i strongly positive."""
        cpi = compute_cpi_detailed(1.0)
        assert cpi > 0.5

    def test_mu_025(self):
        """mu=0.25 → cp_i ≈ -0.3 (EC1 Fig. 7.13)."""
        cpi = compute_cpi_detailed(0.25)
        assert cpi == pytest.approx(-0.3, abs=0.05)

    def test_mu_075(self):
        """mu=0.75 → cp_i ≈ +0.3 (EC1 Fig. 7.13)."""
        cpi = compute_cpi_detailed(0.75)
        assert cpi == pytest.approx(0.3, abs=0.05)

    def test_monotonic(self):
        """cp_i increases monotonically with mu."""
        mus = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
        cpis = [compute_cpi_detailed(m) for m in mus]
        for i in range(len(cpis) - 1):
            assert cpis[i] < cpis[i + 1]

    def test_clamp_below_0(self):
        """mu < 0 clamped to 0."""
        cpi_neg = compute_cpi_detailed(-0.5)
        cpi_0 = compute_cpi_detailed(0.0)
        assert cpi_neg == pytest.approx(cpi_0)

    def test_clamp_above_1(self):
        """mu > 1 clamped to 1."""
        cpi_high = compute_cpi_detailed(1.5)
        cpi_1 = compute_cpi_detailed(1.0)
        assert cpi_high == pytest.approx(cpi_1)


# ===========================================================================
# compute_cpi_dominant_opening
# ===========================================================================


class TestCpiDominantOpening:
    def test_positive_cpe(self):
        """Dominant opening on windward face (cpe > 0)."""
        cpi = compute_cpi_dominant_opening(0.8)
        assert cpi == pytest.approx(0.75 * 0.8, abs=0.01)

    def test_negative_cpe(self):
        """Dominant opening on leeward face (cpe < 0)."""
        cpi = compute_cpi_dominant_opening(-0.5)
        assert cpi == pytest.approx(0.75 * (-0.5), abs=0.01)

    def test_zero_cpe(self):
        cpi = compute_cpi_dominant_opening(0.0)
        assert cpi == pytest.approx(0.0)


# ===========================================================================
# get_cpi_values — router
# ===========================================================================


class TestGetCpiValues:
    def test_none_config_simplified(self):
        """No config → simplified method."""
        pos, neg = get_cpi_values(None)
        assert pos == pytest.approx(0.2)
        assert neg == pytest.approx(-0.2)

    def test_simplified_config(self):
        config = InternalPressureConfig(method="simplified")
        pos, neg = get_cpi_values(config)
        assert pos == pytest.approx(0.2)
        assert neg == pytest.approx(-0.2)

    def test_detailed_with_mu(self):
        config = InternalPressureConfig(method="detailed", mu=0.5)
        v1, v2 = get_cpi_values(config)
        assert abs(v1) < 0.05
        assert v1 == pytest.approx(v2)

    def test_detailed_dominant_opening(self):
        config = InternalPressureConfig(
            method="detailed",
            dominant_opening=True,
        )
        v1, v2 = get_cpi_values(config, cpe_dominant=0.8)
        expected = 0.75 * 0.8
        assert v1 == pytest.approx(expected, abs=0.01)

    def test_detailed_no_mu_fallback(self):
        """Detailed without mu or dominant → fallback to simplified."""
        config = InternalPressureConfig(method="detailed")
        pos, neg = get_cpi_values(config)
        assert pos == pytest.approx(0.2)
        assert neg == pytest.approx(-0.2)

    def test_unknown_method_fallback(self):
        config = InternalPressureConfig(method="unknown_method")
        pos, neg = get_cpi_values(config)
        assert pos == pytest.approx(0.2)
        assert neg == pytest.approx(-0.2)
