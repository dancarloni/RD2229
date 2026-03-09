"""Test per ta_models.py e drift_models.py — elementi secondari NTC2018.

Copertura:
  * estimate_ta: RIGID, CANTILEVER_EQ, SDOF_EQ, MANUAL, modello sconosciuto
  * spectral_acceleration_floor: base, sommita', risonanza, limite minimo
  * estimate_drift_metodo_b: calcolo numerico, soft_storey_factor, confidence
  * estimate_drift_user e estimate_drift_global
"""

import math

import pytest

from src.codes.ntc2018.secondary_elements.drift_models import (
    estimate_drift_global,
    estimate_drift_metodo_b,
    estimate_drift_user,
)
from src.codes.ntc2018.secondary_elements.ta_models import (
    estimate_ta,
    spectral_acceleration_floor,
)

# ===========================================================================
# estimate_ta
# ===========================================================================

class TestEstimateTaRigid:
    def test_rigid_returns_zero(self):
        result = estimate_ta({"ta_model": "RIGID"})
        assert result["T_a"] == 0.0
        assert result["ta_model"] == "RIGID"

    def test_rigid_has_decision_log(self):
        result = estimate_ta({"ta_model": "RIGID"})
        assert len(result["decision_log"]) >= 1

    def test_rigid_case_insensitive(self):
        result = estimate_ta({"ta_model": "rigid"})
        assert result["T_a"] == 0.0


class TestEstimateTaCantilever:
    """T_a = 2*pi*sqrt(m*H^3 / (3*E*I))"""

    def test_cantilever_known_value(self):
        # Mensola acciaio: m=100 kg, H=3 m, E=2.1e11 Pa, I=1e-5 m^4
        spec = {
            "ta_model": "CANTILEVER_EQ",
            "massa_kg": 100.0,
            "altezza_m": 3.0,
            "E_Pa": 2.1e11,
            "I_m4": 1.0e-5,
        }
        result = estimate_ta(spec)
        expected = 2.0 * math.pi * math.sqrt(100.0 * 27.0 / (3.0 * 2.1e11 * 1e-5))
        assert result["T_a"] == pytest.approx(expected, rel=1e-6)

    def test_cantilever_concrete(self):
        # Mensola cls: m=500 kg, H=2.5 m, E=3e10 Pa, I=5e-4 m^4
        spec = {
            "ta_model": "CANTILEVER_EQ",
            "massa_kg": 500.0,
            "altezza_m": 2.5,
            "E_Pa": 3.0e10,
            "I_m4": 5.0e-4,
        }
        result = estimate_ta(spec)
        expected = 2.0 * math.pi * math.sqrt(500.0 * 2.5**3 / (3.0 * 3e10 * 5e-4))
        assert result["T_a"] == pytest.approx(expected, rel=1e-6)

    def test_cantilever_missing_param(self):
        spec = {"ta_model": "CANTILEVER_EQ", "massa_kg": 100.0}
        with pytest.raises(ValueError, match="altezza_m"):
            estimate_ta(spec)

    def test_cantilever_negative_param(self):
        spec = {
            "ta_model": "CANTILEVER_EQ",
            "massa_kg": -10.0,
            "altezza_m": 3.0,
            "E_Pa": 2.1e11,
            "I_m4": 1e-5,
        }
        with pytest.raises(ValueError, match="massa_kg"):
            estimate_ta(spec)


class TestEstimateTaSdof:
    """T_a = 2*pi*sqrt(m/k)"""

    def test_sdof_known_value(self):
        # m=200 kg, k=50000 N/m
        spec = {"ta_model": "SDOF_EQ", "massa_kg": 200.0, "rigidezza_N_m": 50000.0}
        result = estimate_ta(spec)
        expected = 2.0 * math.pi * math.sqrt(200.0 / 50000.0)
        assert result["T_a"] == pytest.approx(expected, rel=1e-6)

    def test_sdof_missing_rigidezza(self):
        spec = {"ta_model": "SDOF_EQ", "massa_kg": 200.0}
        with pytest.raises(ValueError, match="rigidezza_N_m"):
            estimate_ta(spec)


class TestEstimateTaManual:
    def test_manual_returns_given_value(self):
        result = estimate_ta({"ta_model": "MANUAL", "T_a_manual": 0.35})
        assert result["T_a"] == pytest.approx(0.35)

    def test_manual_zero(self):
        result = estimate_ta({"ta_model": "MANUAL", "T_a_manual": 0.0})
        assert result["T_a"] == 0.0

    def test_manual_missing(self):
        with pytest.raises(ValueError, match="T_a_manual"):
            estimate_ta({"ta_model": "MANUAL"})

    def test_manual_negative(self):
        with pytest.raises(ValueError, match="T_a_manual"):
            estimate_ta({"ta_model": "MANUAL", "T_a_manual": -0.1})


class TestEstimateTaUnknown:
    def test_unknown_model_raises(self):
        with pytest.raises(ValueError, match="non riconosciuto"):
            estimate_ta({"ta_model": "FANTASY"})

    def test_empty_model_raises(self):
        with pytest.raises(ValueError, match="non riconosciuto"):
            estimate_ta({"ta_model": ""})

    def test_none_model_raises(self):
        with pytest.raises(ValueError, match="non riconosciuto"):
            estimate_ta({})


# ===========================================================================
# spectral_acceleration_floor (NTC2018 eq. 7.2.5)
# ===========================================================================

class TestSpectralAccelerationFloor:
    """S_a = alpha_S * max(3*(1+z/H)/(1+(1-T_a/T_1)^2) - 0.5, 1.0)"""

    def test_base_z_zero(self):
        # z=0: amplification = 3*(1+0)/(1+(1-0.5)^2) - 0.5 = 3/1.25 - 0.5 = 1.9
        S_a = spectral_acceleration_floor(z=0, H=10, T_a=0.5, T_1=1.0, alpha_S=0.3)
        ampl = 3.0 * 1.0 / (1.0 + 0.25) - 0.5  # 1.9
        assert S_a == pytest.approx(0.3 * ampl, rel=1e-6)

    def test_summit_z_equals_H(self):
        # z=H: amplification = 3*(1+1)/(1+(1-0.5)^2) - 0.5 = 6/1.25 - 0.5 = 4.3
        S_a = spectral_acceleration_floor(z=10, H=10, T_a=0.5, T_1=1.0, alpha_S=0.3)
        ampl = 3.0 * 2.0 / 1.25 - 0.5  # 4.3
        assert S_a == pytest.approx(0.3 * ampl, rel=1e-6)

    def test_resonance_T_a_equals_T_1(self):
        # T_a = T_1: amplification = 3*(1+z/H)/1 - 0.5
        S_a = spectral_acceleration_floor(z=5, H=10, T_a=1.0, T_1=1.0, alpha_S=0.3)
        ampl = 3.0 * 1.5 / 1.0 - 0.5  # 4.0
        assert S_a == pytest.approx(0.3 * ampl, rel=1e-6)

    def test_minimum_floor(self):
        # Quando amplificazione < 1.0, S_a = alpha_S * 1.0
        # Serve T_a molto diverso da T_1 e z=0
        S_a = spectral_acceleration_floor(z=0, H=10, T_a=0.0, T_1=1.0, alpha_S=0.3)
        ampl = 3.0 * 1.0 / (1.0 + 1.0) - 0.5  # 1.0
        assert S_a == pytest.approx(0.3 * max(ampl, 1.0), rel=1e-6)

    def test_alpha_S_zero(self):
        S_a = spectral_acceleration_floor(z=5, H=10, T_a=0.5, T_1=1.0, alpha_S=0.0)
        assert S_a == 0.0

    def test_invalid_H(self):
        with pytest.raises(ValueError, match="H"):
            spectral_acceleration_floor(z=5, H=0, T_a=0.5, T_1=1.0, alpha_S=0.3)

    def test_invalid_T_1(self):
        with pytest.raises(ValueError, match="T_1"):
            spectral_acceleration_floor(z=5, H=10, T_a=0.5, T_1=0, alpha_S=0.3)


# ===========================================================================
# estimate_drift_metodo_b
# ===========================================================================

class TestDriftMetodoB:
    """delta_r = S_d_T1 * (z_m / H_m) * soft_storey_factor / h_interpiano_m"""

    BASE_SPEC = {
        "S_d_T1": 0.05,       # 5 cm spostamento spettrale
        "z_m": 6.0,           # quota 6 m
        "H_m": 12.0,          # edificio 12 m
        "h_interpiano_m": 3.0,
    }

    def test_basic_calculation(self):
        result = estimate_drift_metodo_b(self.BASE_SPEC, soft_storey_factor=1.0)
        # 0.05 * (6/12) * 1.0 / 3.0 = 0.05 * 0.5 / 3.0 = 0.008333...
        expected = 0.05 * 0.5 * 1.0 / 3.0
        assert result["drift_value"] == pytest.approx(expected, rel=1e-6)

    def test_confidence_is_low(self):
        result = estimate_drift_metodo_b(self.BASE_SPEC)
        assert result["confidence"] == "LOW"

    def test_source_is_estimated(self):
        result = estimate_drift_metodo_b(self.BASE_SPEC)
        assert result["source"] == "ESTIMATED"

    def test_method_is_metodo_b(self):
        result = estimate_drift_metodo_b(self.BASE_SPEC)
        assert result["method"] == "METODO_B"

    def test_soft_storey_factor_amplifies(self):
        r1 = estimate_drift_metodo_b(self.BASE_SPEC, soft_storey_factor=1.0)
        r2 = estimate_drift_metodo_b(self.BASE_SPEC, soft_storey_factor=1.5)
        assert r2["drift_value"] == pytest.approx(r1["drift_value"] * 1.5, rel=1e-6)

    def test_soft_storey_factor_clamped_to_1(self):
        # soft_storey_factor < 1.0 viene forzato a 1.0
        r = estimate_drift_metodo_b(self.BASE_SPEC, soft_storey_factor=0.5)
        r1 = estimate_drift_metodo_b(self.BASE_SPEC, soft_storey_factor=1.0)
        assert r["drift_value"] == pytest.approx(r1["drift_value"], rel=1e-6)

    def test_z_zero_gives_zero_drift(self):
        spec = {**self.BASE_SPEC, "z_m": 0.0}
        result = estimate_drift_metodo_b(spec)
        assert result["drift_value"] == 0.0

    def test_has_decision_log(self):
        result = estimate_drift_metodo_b(self.BASE_SPEC)
        assert len(result["decision_log"]) >= 1

    def test_missing_param_raises(self):
        with pytest.raises(ValueError, match="S_d_T1"):
            estimate_drift_metodo_b({"z_m": 6, "H_m": 12, "h_interpiano_m": 3})


# ===========================================================================
# estimate_drift_user / estimate_drift_global
# ===========================================================================

class TestDriftUser:
    def test_returns_given_value(self):
        result = estimate_drift_user(0.003)
        assert result["drift_value"] == pytest.approx(0.003)
        assert result["confidence"] == "HIGH"
        assert result["source"] == "USER"

    def test_zero_value(self):
        result = estimate_drift_user(0.0)
        assert result["drift_value"] == 0.0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            estimate_drift_user(-0.001)


class TestDriftGlobal:
    def test_returns_given_value(self):
        result = estimate_drift_global(0.002)
        assert result["drift_value"] == pytest.approx(0.002)
        assert result["confidence"] == "HIGH"
        assert result["source"] == "GLOBAL"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            estimate_drift_global(-0.001)
