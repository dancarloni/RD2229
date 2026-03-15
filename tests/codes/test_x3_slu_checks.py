import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


def _assert_contract(res: dict) -> None:
    assert "ok" in res
    assert "value" in res
    assert "steps" in res
    assert "trace" in res
    assert "run_id" in res["trace"]
    assert "norm_references" in res


class TestX3Flessione:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x3_slu_flessione", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_golden_case_ok(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 1600,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
            "M_Ed_kNm": 200,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        _assert_contract(res)
        assert res["ok"] is True
        assert res["M_Rd_kNm"] == pytest.approx(260.0, rel=0.04)
        assert res["utilisation"] == pytest.approx(0.77, rel=0.07)

    def test_warning_x_over_xlim(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 3500,
            "f_ck_MPa": 25,
            "f_yk_MPa": 450,
            "M_Ed_kNm": 200,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert "X3-FLEX-001" in res["warnings"]

    def test_warning_out_of_domain(self):
        inputs = {
            "b_mm": 200,
            "d_mm": 250,
            "As_mm2": 6000,
            "f_ck_MPa": 20,
            "f_yk_MPa": 450,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert "X3-FLEX-002" in res["warnings"]
        assert res["ok"] is False

    def test_non_ok_when_m_ed_exceeds_m_rd(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 1200,
            "f_ck_MPa": 20,
            "f_yk_MPa": 400,
            "M_Ed_kNm": 260,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert res["ok"] is False
        assert res["utilisation"] > 1.0

    def test_without_m_ed_returns_capacity_only(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 1600,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert res["utilisation"] is None
        assert res["M_Rd_kNm"] > 0

    def test_custom_x_lim_ratio(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 2600,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
            "x_lim_over_d": 0.35,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert "X3-FLEX-001" in res["warnings"]

    def test_normative_references_present(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 1600,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert any("NTC2018" in ref for ref in res["norm_references"])
        assert any("EN 1992-1-1" in ref for ref in res["norm_references"])


class TestX3Taglio:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x3_slu_taglio", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_golden_case_ok(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 2000,
            "f_ck_MPa": 25,
            "V_Ed_kN": 40,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        _assert_contract(res)
        assert res["ok"] is True
        assert res["V_Rd_c_kN"] > 0

    def test_warning_rho_out_of_range(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 9000,
            "f_ck_MPa": 25,
            "V_Ed_kN": 50,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert "X3-TAG-001" in res["warnings"]

    def test_warning_ratio_above_06(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 1500,
            "f_ck_MPa": 25,
            "V_Ed_kN": 70,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert "X3-TAG-002" in res["warnings"]

    def test_non_ok_when_v_ed_exceeds_v_rd(self):
        inputs = {
            "bw_mm": 250,
            "d_mm": 350,
            "Asl_mm2": 900,
            "f_ck_MPa": 20,
            "V_Ed_kN": 200,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert res["ok"] is False
        assert res["utilisation"] > 1.0

    def test_k_upper_bound(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 80,
            "Asl_mm2": 700,
            "f_ck_MPa": 25,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert res["details"]["k"] <= 2.0

    def test_capacity_only_without_v_ed(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 1200,
            "f_ck_MPa": 25,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert res["utilisation"] is None
        assert res["V_Rd_c_kN"] > 0

    def test_normative_references_present(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 1200,
            "f_ck_MPa": 25,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert any("NTC2018" in ref for ref in res["norm_references"])
        assert any("EN 1992-1-1" in ref for ref in res["norm_references"])


class TestX3Punzonamento:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_golden_case_with_f_cd(self):
        inputs = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_cd_MPa": 16.67,
            "sigma_cp_MPa": 0.0,
            "V_Ed_kN": 160,
        }
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", inputs)
        _assert_contract(res)
        assert res["V_Rd_c_kN"] > 0

    def test_compute_f_cd_from_f_ck(self):
        inputs = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_ck_MPa": 25,
            "gamma_c": 1.5,
            "V_Ed_kN": 150,
        }
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", inputs)
        assert res["details"]["f_cd_MPa"] == pytest.approx(16.6667, rel=1e-3)

    def test_warning_above_08(self):
        base = {
            "b0_mm": 900,
            "d_mm": 180,
            "rho_l": 0.018,
            "f_cd_MPa": 15,
            "sigma_cp_MPa": 0.0,
        }
        cap = NTC2018CodeModule.run_check("x3_slu_punzonamento", base)["V_Rd_c_kN"]
        base["V_Ed_kN"] = 0.85 * cap
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", base)
        assert "X3-PUNZ-001" in res["warnings"]

    def test_non_ok_when_v_ed_exceeds_capacity(self):
        inputs = {
            "b0_mm": 900,
            "d_mm": 180,
            "rho_l": 0.012,
            "f_cd_MPa": 12,
            "sigma_cp_MPa": 0.0,
            "V_Ed_kN": 800,
        }
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", inputs)
        assert res["ok"] is False
        assert res["utilisation"] > 1.0

    def test_capacity_only_without_v_ed(self):
        inputs = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_cd_MPa": 16.67,
            "sigma_cp_MPa": 0.0,
        }
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", inputs)
        assert res["utilisation"] is None
        assert res["V_Rd_c_kN"] > 0

    def test_normative_references_present(self):
        inputs = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_cd_MPa": 16.67,
        }
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", inputs)
        assert any("NTC2018" in ref for ref in res["norm_references"])
        assert any("EN 1992-1-1" in ref for ref in res["norm_references"])


class TestX3DM96Fallback:
    def test_in_range_case_lc01(self):
        inputs = {"luce_m": 4.0, "interasse_cm": 50, "altezza_cm": 22}
        res = NTC2018CodeModule.run_check("x3_dm96_laterocemento", inputs)
        _assert_contract(res)
        assert res["ok"] is True
        assert res["case_id"] == "LC-01"
        assert 0.15 <= res["k_dm96"] <= 0.17

    def test_in_range_case_lc02(self):
        inputs = {"luce_m": 5.1, "interasse_cm": 50, "altezza_cm": 25}
        res = NTC2018CodeModule.run_check("x3_dm96_laterocemento", inputs)
        assert res["ok"] is True
        assert res["case_id"] == "LC-02"

    def test_in_range_case_lc03(self):
        inputs = {"luce_m": 6.0, "interasse_cm": 60, "altezza_cm": 30}
        res = NTC2018CodeModule.run_check("x3_dm96_laterocemento", inputs)
        assert res["ok"] is True
        assert res["case_id"] == "LC-03"

    def test_out_of_range_warning(self):
        inputs = {"luce_m": 8.0, "interasse_cm": 70, "altezza_cm": 22}
        res = NTC2018CodeModule.run_check("x3_dm96_laterocemento", inputs)
        assert res["ok"] is False
        assert "X3-DM96-001" in res["warnings"]

    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x3_dm96_laterocemento", {})
        assert res["ok"] is False


class TestX3DM16Fallback:
    def test_missing_fmk_warning(self):
        inputs = {"classe_legno": "massiccio", "classe_servizio": "1"}
        res = NTC2018CodeModule.run_check("x3_dm16_legno", inputs)
        _assert_contract(res)
        assert res["ok"] is False
        assert "X3-DM16-001" in res["warnings"]

    def test_valid_case_with_default_gamma(self):
        inputs = {
            "classe_legno": "lamellare",
            "classe_servizio": "1",
            "f_mk_MPa": 24,
        }
        res = NTC2018CodeModule.run_check("x3_dm16_legno", inputs)
        assert res["ok"] is True
        assert res["f_md_MPa"] == pytest.approx(16.0, rel=1e-4)

    def test_gamma_not_lower_than_15(self):
        inputs = {
            "classe_legno": "massiccio",
            "classe_servizio": "1",
            "f_mk_MPa": 21,
            "gamma_m": 1.2,
        }
        res = NTC2018CodeModule.run_check("x3_dm16_legno", inputs)
        assert res["ok"] is True
        assert res["details"]["gamma_m"] == pytest.approx(1.5)

    def test_valid_case_with_custom_gamma(self):
        inputs = {
            "classe_legno": "esistente",
            "classe_servizio": "da indagine",
            "f_mk_MPa": 18,
            "gamma_m": 1.8,
        }
        res = NTC2018CodeModule.run_check("x3_dm16_legno", inputs)
        assert res["ok"] is True
        assert res["f_md_MPa"] == pytest.approx(10.0, rel=1e-4)

    def test_normative_reference_present(self):
        inputs = {
            "classe_legno": "lamellare",
            "classe_servizio": "1",
            "f_mk_MPa": 24,
        }
        res = NTC2018CodeModule.run_check("x3_dm16_legno", inputs)
        assert any("DM 16/1/1996" in ref for ref in res["norm_references"])


class TestX3CodeModuleMetadata:
    def test_available_checks_contains_x3_ids(self):
        checks = NTC2018CodeModule.available_checks()
        ids = {check["id"] for check in checks}
        assert "x3_slu_flessione" in ids
        assert "x3_slu_taglio" in ids
        assert "x3_slu_punzonamento" in ids
        assert "x3_dm96_laterocemento" in ids
        assert "x3_dm16_legno" in ids

    def test_get_check_metadata_for_x3(self):
        meta = NTC2018CodeModule.get_check_metadata("x3_slu_taglio")
        assert meta is not None
        assert meta["limit_state"] == "SLU"
