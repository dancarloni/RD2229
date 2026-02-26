#!/usr/bin/env python3
"""Tests base per il modulo core.frc (comportamento materiali FRC)."""

from core.frc import frc_stress
from core_models.materials import Material


def test_frc_stress_linear_capped():
    mat = Material(name="CFRP_test", type="frc", frc_enabled=True, frc_fFtu=3000.0, frc_eps_fu=0.02)

    # Strain zero -> stress zero
    assert frc_stress(mat, 0.0) == 0.0

    # Strain halfway to ultimate -> half stress
    s = frc_stress(mat, 0.01)
    assert abs(s - 1500.0) < 1e-9

    # Strain beyond ultimate -> capped at fFtu
    s2 = frc_stress(mat, 0.05)
    assert abs(s2 - 3000.0) < 1e-9


def test_frc_disabled_returns_zero():
    mat = Material(name="NoFRC", type="concrete", frc_enabled=False, frc_fFtu=3000.0, frc_eps_fu=0.02)
    assert frc_stress(mat, 0.01) == 0.0
