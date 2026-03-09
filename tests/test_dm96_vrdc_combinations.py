"""Test per DM96 SLE/SLU checks, V_Rd,c, NTC2018 combinazioni, elementi secondari."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from src.core_calculus.contracts import CalcInput, SingleCheckResult, VerificationTemplate


# ======================================================================
# HELPER
# ======================================================================

def _make_template(**kwargs) -> VerificationTemplate:
    defaults = {
        "template_id": "test_template",
        "norm_code": "DM96",
    }
    defaults.update(kwargs)
    return VerificationTemplate(**defaults)


def _make_section(width_mm=300, height_mm=500):
    return SimpleNamespace(width=width_mm, height=height_mm)


def _make_material(f_ck=25.0, f_yk=450.0):
    return SimpleNamespace(f_ck=f_ck, f_yk=f_yk)


def _make_calc_input(**kwargs) -> CalcInput:
    defaults = {
        "section": _make_section(),
        "material": _make_material(),
    }
    defaults.update(kwargs)
    return CalcInput(**defaults)


# ======================================================================
# DM96: FESSURAZIONE SLE
# ======================================================================


class TestFessurazioneSLE:
    def test_missing_w_amm(self):
        from src.methods.dm96.checks import check_fessurazione_sle_dm96
        ci = _make_calc_input(As=10.0, d=45.0, Mx=80.0)
        tpl = _make_template()
        result = check_fessurazione_sle_dm96(ci, tpl)
        assert result.ok is False
        assert "w_amm" in result.messages_it[0].lower() or "non specificata" in result.messages_it[0].lower()

    def test_crack_width_calculation(self):
        from src.methods.dm96.checks import check_fessurazione_sle_dm96
        ci = _make_calc_input(As=10.0, d=45.0, Mx=50.0)
        tpl = _make_template(extra_params={"w_amm_mm": 0.4})
        result = check_fessurazione_sle_dm96(ci, tpl)
        assert isinstance(result, SingleCheckResult)
        assert result.utilisation is not None
        assert "w_k_mm" in result.details
        assert result.details["w_k_mm"] >= 0

    def test_high_moment_fails(self):
        from src.methods.dm96.checks import check_fessurazione_sle_dm96
        ci = _make_calc_input(As=2.0, d=45.0, Mx=200.0)
        tpl = _make_template(extra_params={"w_amm_mm": 0.1})
        result = check_fessurazione_sle_dm96(ci, tpl)
        # High moment + small reinforcement + tight limit → likely fails
        assert result.utilisation is not None
        assert result.utilisation > 0

    def test_no_section_error(self):
        from src.methods.dm96.checks import check_fessurazione_sle_dm96
        ci = CalcInput(section=None, material=_make_material())
        tpl = _make_template(extra_params={"w_amm_mm": 0.3})
        result = check_fessurazione_sle_dm96(ci, tpl)
        assert result.ok is False


# ======================================================================
# DM96: DEFORMAZIONI SLE
# ======================================================================


class TestDeformazioniSLE:
    def test_missing_params(self):
        from src.methods.dm96.checks import check_deformazioni_sle_dm96
        ci = _make_calc_input(Mx=50.0)
        tpl = _make_template()
        result = check_deformazioni_sle_dm96(ci, tpl)
        assert result.ok is False

    def test_deflection_calculation(self):
        from src.methods.dm96.checks import check_deformazioni_sle_dm96
        ci = _make_calc_input(As=10.0, d=45.0, Mx=30.0)
        tpl = _make_template(extra_params={"span_mm": 6000.0, "deflection_limit_ratio": 250})
        result = check_deformazioni_sle_dm96(ci, tpl)
        assert isinstance(result, SingleCheckResult)
        assert result.utilisation is not None
        assert "delta_lt_mm" in result.details
        assert result.details["delta_amm_mm"] == 24.0  # 6000/250

    def test_short_span_passes(self):
        from src.methods.dm96.checks import check_deformazioni_sle_dm96
        ci = _make_calc_input(As=15.0, d=45.0, Mx=10.0)
        tpl = _make_template(extra_params={"span_mm": 3000.0, "deflection_limit_ratio": 250})
        result = check_deformazioni_sle_dm96(ci, tpl)
        assert result.ok is True


# ======================================================================
# DM96: TORSIONE SLU
# ======================================================================


class TestTorsioneSLU:
    def test_zero_torsion(self):
        from src.methods.dm96.checks import check_torsione_slu_dm96
        ci = _make_calc_input(Mz=0.0)
        tpl = _make_template()
        result = check_torsione_slu_dm96(ci, tpl)
        assert result.ok is True
        assert result.utilisation == 0.0

    def test_torsion_with_value(self):
        from src.methods.dm96.checks import check_torsione_slu_dm96
        ci = _make_calc_input(Mz=10.0)
        tpl = _make_template()
        result = check_torsione_slu_dm96(ci, tpl)
        assert isinstance(result, SingleCheckResult)
        assert result.utilisation is not None
        assert "T_Ed_kNm" in result.details
        assert "T_Rd_max_kNm" in result.details
        assert result.details["T_Rd_max_kNm"] > 0


# ======================================================================
# DM96: PUNZONAMENTO SLU
# ======================================================================


class TestPunzonamentoSLU:
    def test_punching_calculation(self):
        from src.methods.dm96.checks import check_punzonamento_slu_dm96
        # Piastra 200mm, pilastro 300x300, N=200kN
        section = _make_section(width_mm=300, height_mm=200)
        ci = _make_calc_input(section=section, N=200.0, As=8.0, d=17.0)
        tpl = _make_template(extra_params={"column_dimensions": [300, 300]})
        result = check_punzonamento_slu_dm96(ci, tpl)
        assert isinstance(result, SingleCheckResult)
        assert result.utilisation is not None
        assert "v_Ed_MPa" in result.details
        assert "v_Rd_c_MPa" in result.details

    def test_no_section(self):
        from src.methods.dm96.checks import check_punzonamento_slu_dm96
        ci = CalcInput(section=None, material=_make_material())
        tpl = _make_template()
        result = check_punzonamento_slu_dm96(ci, tpl)
        assert result.ok is False


# ======================================================================
# DM96: INSTABILITÀ SLU
# ======================================================================


class TestInstabilitaSLU:
    def test_missing_l0(self):
        from src.methods.dm96.checks import check_instabilita_compressione_slu_dm96
        ci = _make_calc_input(N=500.0, Mx=20.0, As=12.0)
        tpl = _make_template()
        result = check_instabilita_compressione_slu_dm96(ci, tpl)
        assert result.ok is False  # l_0 mancante

    def test_short_column(self):
        from src.methods.dm96.checks import check_instabilita_compressione_slu_dm96
        # lambda = l_0 / (min(b,h)/sqrt(12)) = 2000 / (300/3.464) = 23 < 75
        ci = _make_calc_input(N=500.0, Mx=20.0, As=12.0)
        tpl = _make_template(extra_params={"l_0_mm": 2000.0})
        result = check_instabilita_compressione_slu_dm96(ci, tpl)
        assert result.ok is True  # pilastro tozzo
        assert result.details["lambda"] < 75

    def test_slender_column(self):
        from src.methods.dm96.checks import check_instabilita_compressione_slu_dm96
        # Pilastro snello: sezione piccola, l_0 grande
        section = _make_section(width_mm=200, height_mm=200)
        ci = _make_calc_input(section=section, N=300.0, Mx=10.0, As=8.0, d=17.0)
        tpl = _make_template(extra_params={"l_0_mm": 6000.0})
        result = check_instabilita_compressione_slu_dm96(ci, tpl)
        # lambda = 6000 / (200/sqrt(12)) = 6000/57.7 = 104 > 75
        assert result.details["lambda"] > 75
        assert result.utilisation is not None


# ======================================================================
# V_Rd,c WITHOUT STIRRUPS
# ======================================================================


class TestVRdcNoStirrups:
    def test_basic_calculation(self):
        from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups
        result = vrdc_no_stirrups({
            "b_w_mm": 300,
            "d_mm": 450,
            "A_sl_mm2": 1500,
            "f_ck_MPa": 25,
            "gamma_c": 1.5,
        })
        assert result["ok"] is True  # no V_Ed → always ok
        assert result["value"] > 0
        assert result["V_Rd_c_kN"] > 0
        assert len(result["steps"]) >= 5

    def test_with_V_Ed_passing(self):
        from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups
        result = vrdc_no_stirrups({
            "b_w_mm": 300,
            "d_mm": 450,
            "A_sl_mm2": 1500,
            "f_ck_MPa": 25,
            "V_Ed_N": 50000,  # 50 kN
        })
        assert result["ok"] is True
        assert result["V_Rd_c_N"] > 50000

    def test_with_V_Ed_failing(self):
        from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups
        result = vrdc_no_stirrups({
            "b_w_mm": 200,
            "d_mm": 250,
            "A_sl_mm2": 300,
            "f_ck_MPa": 20,
            "V_Ed_N": 500000,  # 500 kN
        })
        assert result["ok"] is False
        assert result["utilisation"] > 1.0

    def test_with_axial_compression(self):
        from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups
        result_no_N = vrdc_no_stirrups({
            "b_w_mm": 300, "d_mm": 450,
            "A_sl_mm2": 1500, "f_ck_MPa": 25,
        })
        result_with_N = vrdc_no_stirrups({
            "b_w_mm": 300, "d_mm": 450,
            "A_sl_mm2": 1500, "f_ck_MPa": 25,
            "N_Ed_N": 200000, "A_c_mm2": 300 * 500,
        })
        # Compression increases V_Rd,c
        assert result_with_N["V_Rd_c_N"] > result_no_N["V_Rd_c_N"]

    def test_invalid_dimensions(self):
        from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups
        result = vrdc_no_stirrups({"b_w_mm": 0, "d_mm": 0})
        assert result["ok"] is False

    def test_k_factor_limit(self):
        from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups
        # d=50mm → k = 1 + sqrt(200/50) = 3.0 → capped at 2.0
        result = vrdc_no_stirrups({
            "b_w_mm": 300, "d_mm": 50,
            "A_sl_mm2": 500, "f_ck_MPa": 25,
        })
        assert result["details"]["k"] == 2.0


# ======================================================================
# NTC2018 COMBINATIONS
# ======================================================================


class TestNTC2018Combinations:
    def test_slu_permanent_only(self):
        from src.core.combinations.ntc2018_combinations import generate_slu_combinations
        combos = generate_slu_combinations({"G1": 10.0})
        assert len(combos) == 1
        assert combos[0]["type"] == "SLU"
        assert combos[0]["total"] == pytest.approx(1.3 * 10.0, abs=0.01)

    def test_slu_with_variable(self):
        from src.core.combinations.ntc2018_combinations import generate_slu_combinations
        combos = generate_slu_combinations({
            "G1": 10.0,
            "G2": 2.0,
            "variable_loads": [
                {"name": "Q1", "value": 5.0, "category": "cat_A"},
            ],
        })
        assert len(combos) == 1
        expected = 1.3 * 10.0 + 1.5 * 2.0 + 1.5 * 5.0
        assert combos[0]["total"] == pytest.approx(expected, abs=0.01)

    def test_slu_multiple_variables(self):
        from src.core.combinations.ntc2018_combinations import generate_slu_combinations
        combos = generate_slu_combinations({
            "G1": 10.0,
            "variable_loads": [
                {"name": "Q1", "value": 5.0, "category": "cat_A"},
                {"name": "vento", "value": 3.0, "category": "vento"},
            ],
        })
        assert len(combos) == 2  # one per dominant action
        assert combos[0]["dominant_action"] == "Q1"
        assert combos[1]["dominant_action"] == "vento"

    def test_sle_quasi_permanente(self):
        from src.core.combinations.ntc2018_combinations import generate_sle_combinations
        combos = generate_sle_combinations({
            "G1": 10.0,
            "variable_loads": [
                {"name": "Q1", "value": 5.0, "category": "cat_A"},
            ],
        })
        qp = [c for c in combos if c["type"] == "SLE_quasi_permanente"]
        assert len(qp) == 1
        # psi_2 for cat_A = 0.3
        expected = 10.0 + 0.3 * 5.0
        assert qp[0]["total"] == pytest.approx(expected, abs=0.01)

    def test_sle_rara_and_frequente(self):
        from src.core.combinations.ntc2018_combinations import generate_sle_combinations
        combos = generate_sle_combinations({
            "G1": 10.0,
            "variable_loads": [
                {"name": "Q1", "value": 5.0, "category": "cat_A"},
            ],
        })
        rara = [c for c in combos if c["type"] == "SLE_rara"]
        freq = [c for c in combos if c["type"] == "SLE_frequente"]
        assert len(rara) == 1
        assert len(freq) == 1
        # Rara: G1 + Q1
        assert rara[0]["total"] == pytest.approx(10.0 + 5.0, abs=0.01)
        # Frequente: G1 + psi_1*Q1 = 10 + 0.5*5 = 12.5
        assert freq[0]["total"] == pytest.approx(10.0 + 0.5 * 5.0, abs=0.01)

    def test_generate_all(self):
        from src.core.combinations.ntc2018_combinations import generate_all_combinations
        combos = generate_all_combinations({
            "G1": 10.0,
            "variable_loads": [
                {"name": "Q1", "value": 5.0, "category": "cat_A"},
            ],
        })
        types = [c["type"] for c in combos]
        assert "SLU" in types
        assert "SLE_quasi_permanente" in types

    def test_serviceability_backward_compat(self):
        from src.core.combinations.ntc2018_combinations import generate_serviceability_combinations
        combos = generate_serviceability_combinations({"G1": 10.0})
        assert len(combos) >= 1


# ======================================================================
# SECONDARY ELEMENTS
# ======================================================================


class TestSecondaryElements:
    def test_check_slu_basic(self):
        from src.codes.ntc2018.secondary_elements.checks import check_slu
        result = check_slu({
            "W_a": 2.0, "S_a": 0.3, "gamma_a": 1.0, "q_a": 2.0,
        })
        assert result["ok"] is True
        assert result["F_a_kN"] == pytest.approx(0.3, abs=0.01)

    def test_check_slu_with_resistance(self):
        from src.codes.ntc2018.secondary_elements.checks import check_slu
        result = check_slu({
            "W_a": 5.0, "S_a": 0.5, "gamma_a": 1.5, "q_a": 2.0,
            "F_Rd": 1.0,  # small resistance → fails
        })
        assert result["ok"] is False
        assert result["utilisation"] > 1.0

    def test_check_sle_drift(self):
        from src.codes.ntc2018.secondary_elements.checks import check_sle
        result = check_sle({
            "drift": {"source": "GLOBAL", "value": 0.003, "limit": 0.005},
        })
        assert result["ok"] is True
        assert result["utilisation"] == pytest.approx(0.6, abs=0.01)

    def test_check_sle_estimated_drift(self):
        from src.codes.ntc2018.secondary_elements.checks import check_sle
        result = check_sle({
            "drift": {"source": "ESTIMATED", "value": 0.004, "limit": 0.005},
        })
        assert result["confidence"] == "LOW"
        assert result["ok"] is True

    def test_check_sle_exceeds_limit(self):
        from src.codes.ntc2018.secondary_elements.checks import check_sle
        result = check_sle({
            "drift": {"source": "GLOBAL", "value": 0.01, "limit": 0.005},
        })
        assert result["ok"] is False

    def test_legacy_aliases(self):
        from src.codes.ntc2018.secondary_elements.checks import check_parapet, check_partition
        assert check_parapet is not None
        assert check_partition is not None

    def test_storage_adapter(self):
        from src.codes.ntc2018.secondary_elements.storage_adapter import (
            save_secondary_element,
            load_secondary_element,
            list_secondary_elements,
            delete_secondary_element,
            clear_storage,
        )
        clear_storage()

        # Save
        rid = save_secondary_element({"type": "parapet", "W_a": 2.0})
        assert rid is not None and rid != "TODO:id"

        # Load
        rec = load_secondary_element(rid)
        assert rec is not None
        assert rec["type"] == "parapet"

        # List
        assert rid in list_secondary_elements()

        # Delete
        assert delete_secondary_element(rid) is True
        assert load_secondary_element(rid) is None
        assert delete_secondary_element(rid) is False

        clear_storage()

    def test_storage_custom_id(self):
        from src.codes.ntc2018.secondary_elements.storage_adapter import (
            save_secondary_element,
            load_secondary_element,
            clear_storage,
        )
        clear_storage()
        rid = save_secondary_element({"id": "my-elem", "type": "partition"})
        assert rid == "my-elem"
        rec = load_secondary_element("my-elem")
        assert rec["type"] == "partition"
        clear_storage()
