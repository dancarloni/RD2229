"""Test mirati su coefficienti gamma nel VerificationEngine core."""

from __future__ import annotations

from src.core_calculus.core.verification_engine import (
    MaterialProperties,
    VerificationEngine,
    create_verification_engine,
)


def _mat() -> MaterialProperties:
    return MaterialProperties(fck=30.0, Ec=30000.0, fyk=450.0, Es=200000.0)


def test_factory_creates_engine_with_uppercase_code() -> None:
    engine = create_verification_engine("slu")
    assert isinstance(engine, VerificationEngine)
    assert engine.calculation_code == "SLU"


def test_get_allowable_stresses_ta_defaults() -> None:
    engine = VerificationEngine("TA")
    sigma_c, sigma_s = engine.get_allowable_stresses(_mat())

    assert sigma_c == 15.0  # 0.5 * fck
    assert sigma_s == 225.0  # fyk / 2


def test_get_allowable_stresses_sle_defaults() -> None:
    engine = VerificationEngine("SLE")
    sigma_c, sigma_s = engine.get_allowable_stresses(_mat())

    assert sigma_c == 18.0  # 0.6 * fck
    assert sigma_s == 360.0  # 0.8 * 450


def test_get_allowable_stresses_slu_defaults() -> None:
    engine = VerificationEngine("SLU")
    engine.config = None

    sigma_c, sigma_s = engine.get_allowable_stresses(_mat())

    assert sigma_c == 0.85 * 30.0 / 1.5
    assert sigma_s == 450.0 / 1.15


def test_get_allowable_stresses_slu_config_override() -> None:
    engine = VerificationEngine("SLU")
    engine.config = {
        "safety_coefficients": {
            "gamma_c": {"value": 1.6},
            "gamma_s": {"value": 1.2},
        }
    }

    sigma_c, sigma_s = engine.get_allowable_stresses(_mat())

    assert sigma_c == 0.85 * 30.0 / 1.6
    assert sigma_s == 450.0 / 1.2


def test_get_allowable_stresses_slu_malformed_config_fallback() -> None:
    engine = VerificationEngine("SLU")
    engine.config = {"safety_coefficients": "non_dict"}

    sigma_c, sigma_s = engine.get_allowable_stresses(_mat())

    assert sigma_c == 0.85 * 30.0 / 1.5
    assert sigma_s == 450.0 / 1.15
