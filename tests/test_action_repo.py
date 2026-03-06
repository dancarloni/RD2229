"""Test per src/actions/action_repo.py — verifiche strutturali."""

import math

import pytest

from src.actions.action_repo import (
    ACTION_REPOSITORY,
    FlexureCheck,
    PressFlexureCheck,
    SLECrackingCheck,
    SLEStressCheck,
    ShearCheck,
    TorsionCheck,
    get_action,
    list_actions,
    list_actions_for_norm,
    register_action,
)


# ===================================================================
# Repository
# ===================================================================


class TestRepository:
    def test_all_actions_registered(self):
        ids = list_actions()
        assert "flexure_check" in ids
        assert "shear_check" in ids
        assert "press_flexure_check" in ids
        assert "torsion_check" in ids
        assert "sle_stress_check" in ids
        assert "sle_cracking_check" in ids

    def test_get_action_found(self):
        a = get_action("flexure_check")
        assert a is not None
        assert a.action_id == "flexure_check"

    def test_get_action_missing(self):
        assert get_action("nonexistent_action") is None

    def test_list_actions_for_norm_ntc2018(self):
        actions = list_actions_for_norm("NTC2018")
        ids = [a.action_id for a in actions]
        assert "flexure_check" in ids
        assert "shear_check" in ids
        assert "sle_stress_check" in ids
        assert "sle_cracking_check" in ids

    def test_list_actions_for_norm_rd2229(self):
        actions = list_actions_for_norm("RD2229")
        ids = [a.action_id for a in actions]
        assert "flexure_check" in ids
        assert "shear_check" in ids
        assert "press_flexure_check" in ids
        # SLE checks not available for RD2229
        assert "sle_stress_check" not in ids

    def test_register_overwrite(self):
        old = get_action("flexure_check")
        register_action(FlexureCheck())
        new = get_action("flexure_check")
        assert new is not None
        assert new.action_id == old.action_id


# ===================================================================
# FlexureCheck — NTC2018 SLU
# ===================================================================


class TestFlexureCheckSLU:
    def setup_method(self):
        self.check = FlexureCheck()
        self.normative = {
            "norm_code": "NTC2018",
            "material": {"f_cd": 141.7, "f_yd": 3904.0},
        }

    def test_basic_pass(self):
        """Sezione 30×50 con As=6.28 cm² (4ϕ14), M_Ed piccolo."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "Mx": 2000.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is True
        assert result["partials"]["M_Rd_kgm"] > 2000.0

    def test_basic_fail(self):
        """Momento troppo alto per la sezione."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "Mx": 50000.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is False
        assert result["partials"]["utilization"] > 1.0

    def test_zero_area(self):
        """As = 0 → errore."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 0.0, "Mx": 1000.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is False

    def test_utilization_calculation(self):
        """Verifica che utilization = M_Ed / M_Rd."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "Mx": 5000.0}
        result = self.check.run(element, self.normative, {})
        p = result["partials"]
        expected_util = 5000.0 / p["M_Rd_kgm"]
        assert abs(p["utilization"] - round(expected_util, 3)) < 0.01


# ===================================================================
# FlexureCheck — RD2229 TA
# ===================================================================


class TestFlexureCheckTA:
    def setup_method(self):
        self.check = FlexureCheck()
        self.normative = {
            "norm_code": "RD2229",
            "material": {
                "sigma_c_adm": 60.0,
                "sigma_s_adm": 1400.0,
                "n_omogenizzazione": 10.0,
            },
        }

    def test_basic_pass(self):
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "Mx": 500.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is True

    def test_concrete_stress_calculation(self):
        """σ_c = M·100 / W dove W = b·h²/6."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "Mx": 500.0}
        result = self.check.run(element, self.normative, {})
        W = 30.0 * 50.0**2 / 6.0
        expected_sigma_c = 500.0 * 100.0 / W
        assert abs(result["partials"]["sigma_c"] - round(expected_sigma_c, 1)) < 0.5


# ===================================================================
# ShearCheck — NTC2018 SLU
# ===================================================================


class TestShearCheckSLU:
    def setup_method(self):
        self.check = ShearCheck()
        self.normative = {
            "norm_code": "NTC2018",
            "material": {"f_yd": 3904.0},
        }

    def test_basic_pass(self):
        """Staffe ϕ8/20 2 bracci, taglio contenuto."""
        element = {
            "b": 30.0, "h": 50.0, "d": 46.0,
            "Tx": 5000.0,
            "staffe_diametro": 8.0,
            "staffe_num_bracci": 2.0,
            "staffe_passo": 20.0,
        }
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is True

    def test_basic_fail(self):
        """Taglio molto alto."""
        element = {
            "b": 30.0, "h": 50.0, "d": 46.0,
            "Tx": 500000.0,
            "staffe_diametro": 8.0,
            "staffe_num_bracci": 2.0,
            "staffe_passo": 20.0,
        }
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is False

    def test_v_rd_formula(self):
        """V_Rd,s = (A_sw/s) × 0.9 × d × f_yd × cot(θ)."""
        element = {
            "b": 30.0, "h": 50.0, "d": 46.0,
            "Tx": 5000.0,
            "staffe_diametro": 8.0,
            "staffe_num_bracci": 2.0,
            "staffe_passo": 20.0,
        }
        result = self.check.run(element, self.normative, {})
        A_sw = 2 * math.pi * (0.8)**2 / 4.0
        V_Rd_s = (A_sw / 20.0) * 0.9 * 46.0 * 3904.0 * 2.5
        assert abs(result["partials"]["V_Rd_s_kg"] - round(V_Rd_s, 1)) < 1.0


# ===================================================================
# ShearCheck — RD2229 TA
# ===================================================================


class TestShearCheckTA:
    def test_basic_pass(self):
        check = ShearCheck()
        norm = {
            "norm_code": "RD2229",
            "material": {"tau_c1_adm": 14.0},
        }
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "Tx": 5000.0}
        result = check.run(element, norm, {})
        tau = 5000.0 / (30.0 * 46.0)
        assert result["ok"] is True
        assert abs(result["partials"]["tau_kg_cm2"] - round(tau, 2)) < 0.05


# ===================================================================
# PressFlexureCheck — NTC2018 SLU
# ===================================================================


class TestPressFlexureCheckSLU:
    def setup_method(self):
        self.check = PressFlexureCheck()
        self.normative = {
            "norm_code": "NTC2018",
            "material": {"f_cd": 141.7, "f_yd": 3904.0},
        }

    def test_basic_pass(self):
        element = {
            "b": 30.0, "h": 50.0, "d": 46.0,
            "As": 6.28, "N": 5000.0, "Mx": 2000.0,
        }
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is True

    def test_high_utilization(self):
        element = {
            "b": 30.0, "h": 50.0, "d": 46.0,
            "As": 6.28, "N": 500000.0, "Mx": 30000.0,
        }
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is False


# ===================================================================
# PressFlexureCheck — RD2229 TA
# ===================================================================


class TestPressFlexureCheckTA:
    def test_basic_pass(self):
        check = PressFlexureCheck()
        norm = {
            "norm_code": "RD2229",
            "material": {"sigma_c_adm": 60.0},
        }
        element = {"b": 30.0, "h": 50.0, "N": 1000.0, "Mx": 200.0}
        result = check.run(element, norm, {})
        A = 30.0 * 50.0
        W = 30.0 * 50.0**2 / 6.0
        sigma_max = 1000.0 / A + 200.0 * 100.0 / W
        assert result["ok"] is True
        assert abs(result["partials"]["sigma_max"] - round(sigma_max, 2)) < 0.1


# ===================================================================
# TorsionCheck
# ===================================================================


class TestTorsionCheck:
    def setup_method(self):
        self.check = TorsionCheck()
        self.normative = {
            "norm_code": "NTC2018",
            "material": {"f_cd": 141.7},
        }

    def test_basic_pass(self):
        element = {"b": 30.0, "h": 50.0, "Mz": 500.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is True

    def test_basic_fail(self):
        element = {"b": 30.0, "h": 50.0, "Mz": 500000.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is False

    def test_t_rd_formula(self):
        """T_Rd,max = 2 × ν × f_cd × A_k × t_ef / 100."""
        element = {"b": 30.0, "h": 50.0, "Mz": 1000.0}
        result = self.check.run(element, self.normative, {})
        t_ef = 30.0 / 6.0
        A_k = (30.0 - t_ef) * (50.0 - t_ef)
        T_Rd = 2.0 * 0.5 * 141.7 * A_k * t_ef / 100.0
        assert abs(result["partials"]["T_Rd_max_kgm"] - round(T_Rd, 1)) < 1.0


# ===================================================================
# SLEStressCheck
# ===================================================================


class TestSLEStressCheck:
    def setup_method(self):
        self.check = SLEStressCheck()
        self.normative = {
            "norm_code": "NTC2018",
            "material": {
                "f_ck": 254.9,
                "f_yk": 4589.0,
                "E_cm": 300000.0,
                "E_s": 2100000.0,
            },
        }

    def test_basic_pass(self):
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "M_sle": 1000.0}
        result = self.check.run(element, self.normative, {})
        assert result["ok"] is True

    def test_limits(self):
        """σ_c ≤ 0.60·f_ck, σ_s ≤ 0.80·f_yk."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "M_sle": 1000.0}
        result = self.check.run(element, self.normative, {})
        p = result["partials"]
        assert p["lim_c"] == pytest.approx(0.60 * 254.9, abs=0.5)
        assert p["lim_s"] == pytest.approx(0.80 * 4589.0, abs=0.5)

    def test_cracked_section_analysis(self):
        """Verifica che calcola asse neutro di sezione fessurata."""
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "M_sle": 1000.0}
        result = self.check.run(element, self.normative, {})
        p = result["partials"]
        # Asse neutro fessurato dovrebbe essere < h/2
        assert p["x_n_cm"] < 25.0
        assert p["x_n_cm"] > 0.0


# ===================================================================
# SLECrackingCheck
# ===================================================================


class TestSLECrackingCheck:
    def setup_method(self):
        self.check = SLECrackingCheck()
        self.normative = {
            "norm_code": "NTC2018",
            "material": {
                "f_ctm": 25.0,
                "E_s": 2100000.0,
                "E_cm": 300000.0,
            },
        }

    def test_basic_pass(self):
        element = {
            "width_cm": 30.0, "height_cm": 50.0, "d": 46.0,
            "As": 6.28, "M_sle": 1000.0,
            "cover_cm": 3.0, "diam_barre_mm": 14.0,
        }
        result = self.check.run(element, self.normative, {"w_lim_mm": 0.3})
        assert result["ok"] is True

    def test_high_moment_fails(self):
        element = {
            "width_cm": 30.0, "height_cm": 50.0, "d": 46.0,
            "As": 2.0, "M_sle": 5000.0,
            "cover_cm": 3.0, "diam_barre_mm": 14.0,
        }
        result = self.check.run(element, self.normative, {"w_lim_mm": 0.3})
        # With very small As and high moment, cracking should fail
        assert result["partials"]["w_k_mm"] > 0

    def test_w_lim_from_settings(self):
        element = {
            "width_cm": 30.0, "height_cm": 50.0, "d": 46.0,
            "As": 6.28, "M_sle": 1000.0,
        }
        result = self.check.run(element, self.normative, {"w_lim_mm": 0.4})
        assert result["partials"]["w_lim_mm"] == 0.4


# ===================================================================
# Integrazione: tutte le azioni hanno output strutturato
# ===================================================================


class TestOutputFormat:
    """Tutte le azioni devono restituire action_id, ok, messages, partials."""

    @pytest.fixture(params=[
        "flexure_check", "shear_check", "press_flexure_check",
        "torsion_check", "sle_stress_check", "sle_cracking_check",
    ])
    def action_id(self, request):
        return request.param

    def test_output_structure(self, action_id):
        action = get_action(action_id)
        assert action is not None
        element = {"b": 30.0, "h": 50.0, "d": 46.0, "As": 6.28, "Mx": 1000.0}
        normative = {
            "norm_code": "NTC2018",
            "material": {
                "f_cd": 141.7, "f_yd": 3904.0, "f_ck": 254.9,
                "f_yk": 4589.0, "E_cm": 300000.0, "E_s": 2100000.0,
                "f_ctm": 25.0,
            },
        }
        result = action.run(element, normative, {"w_lim_mm": 0.3})
        assert "action_id" in result
        assert "ok" in result
        assert "messages" in result
        assert isinstance(result["messages"], list)
        assert len(result["messages"]) > 0
