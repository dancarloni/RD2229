"""
Test LC/FC adjustments for existing structures.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.core_calculus.lc_fc_adjustments import (
    apply_lc_fc_adjustments,
    get_lc_description_it,
    get_typical_fc_for_lc,
)


@dataclass
class MockMaterial:
    """Mock material for testing."""

    f_ck: float = 25.0  # MPa
    f_yk: float = 450.0  # MPa


def test_apply_lc_fc_lc2():
    """Test LC2 with typical FC = 1.20."""
    material = MockMaterial(f_ck=30.0, f_yk=450.0)
    adjusted = apply_lc_fc_adjustments(material, "LC2", 1.20)

    # Check original values preserved
    assert adjusted.f_ck_original == 30.0
    assert adjusted.f_yk_original == 450.0

    # Check adjusted values (reduced by FC)
    assert adjusted.f_ck_adjusted == pytest.approx(30.0 / 1.20, abs=0.01)
    assert adjusted.f_yk_adjusted == pytest.approx(450.0 / 1.20, abs=0.01)

    # Check metadata
    assert adjusted.lc == "LC2"
    assert adjusted.fc == 1.20


def test_apply_lc_fc_lc1():
    """Test LC1 with typical FC = 1.35 (most conservative)."""
    material = MockMaterial(f_ck=25.0, f_yk=450.0)
    adjusted = apply_lc_fc_adjustments(material, "LC1", 1.35)

    # More reduction for LC1
    assert adjusted.f_ck_adjusted == pytest.approx(25.0 / 1.35, abs=0.01)
    assert adjusted.f_yk_adjusted == pytest.approx(450.0 / 1.35, abs=0.01)


def test_apply_lc_fc_lc3():
    """Test LC3 with FC = 1.00 (full knowledge, no reduction)."""
    material = MockMaterial(f_ck=30.0, f_yk=450.0)
    adjusted = apply_lc_fc_adjustments(material, "LC3", 1.00)

    # No reduction for FC = 1.00
    assert adjusted.f_ck_adjusted == 30.0
    assert adjusted.f_yk_adjusted == 450.0


def test_apply_lc_fc_invalid_lc():
    """Test that invalid LC raises ValueError."""
    material = MockMaterial()
    with pytest.raises(ValueError, match="Invalid LC"):
        apply_lc_fc_adjustments(material, "LC99", 1.20)


def test_apply_lc_fc_invalid_fc_out_of_range():
    """Test that FC out of range [1.0, 1.5] raises ValueError."""
    material = MockMaterial()
    with pytest.raises(ValueError, match="FC out of range"):
        apply_lc_fc_adjustments(material, "LC2", 2.0)

    with pytest.raises(ValueError, match="FC out of range"):
        apply_lc_fc_adjustments(material, "LC2", 0.5)


def test_get_typical_fc_for_lc():
    """Test typical FC values per NTC 2018 Table 8.2."""
    assert get_typical_fc_for_lc("LC1") == 1.35
    assert get_typical_fc_for_lc("LC2") == 1.20
    assert get_typical_fc_for_lc("LC3") == 1.00


def test_get_lc_description_it():
    """Test Italian descriptions for LC levels."""
    assert "limitata" in get_lc_description_it("LC1").lower()
    assert "adeguata" in get_lc_description_it("LC2").lower()
    assert "accurata" in get_lc_description_it("LC3").lower()


def test_design_strengths_computed():
    """Test that design strengths are computed correctly."""
    material = MockMaterial(f_ck=30.0, f_yk=450.0)
    adjusted = apply_lc_fc_adjustments(material, "LC2", 1.20)

    # f_cd = 0.85 * f_ck_adjusted / gamma_c
    expected_fcd = 0.85 * (30.0 / 1.20) / 1.5
    assert adjusted.f_cd == pytest.approx(expected_fcd, abs=0.01)

    # f_yd = f_yk_adjusted / gamma_s
    expected_fyd = (450.0 / 1.20) / 1.15
    assert adjusted.f_yd == pytest.approx(expected_fyd, abs=0.01)
