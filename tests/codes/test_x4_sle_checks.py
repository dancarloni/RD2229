import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


def _assert_contract(res: dict) -> None:
    assert "ok" in res
    assert "value" in res
    assert "steps" in res
    assert "trace" in res
    assert "run_id" in res["trace"]
    assert "norm_references" in res


class TestX4Deformabilita:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x4_sle_deformabilita", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_golden_case_ok(self):
        inputs = {
            "q_s_kgf_m2": 300,
            "i_cm": 50,
            "L_cm": 500,
            "E_kgf_cm2": 315000,
            "I_cm4": 33333,
            "phi_viscosita": 2.5,
        }
        res = NTC2018CodeModule.run_check("x4_sle_deformabilita", inputs)
        _assert_contract(res)
        assert res["ok"] is True
        assert res["f_ist_cm"] == pytest.approx(0.116, rel=0.05)
        assert res["f_tot_cm"] == pytest.approx(0.407, rel=0.05)
        assert res["utilisation"] < 1.0

    def test_non_ok_with_warning_def_001(self):
        inputs = {
            "q_s_kgf_m2": 300,
            "i_cm": 50,
            "L_cm": 950,
            "E_kgf_cm2": 315000,
            "I_cm4": 33333,
            "phi_viscosita": 2.5,
        }
        res = NTC2018CodeModule.run_check("x4_sle_deformabilita", inputs)
        assert res["ok"] is False
        assert "X4-DEF-001" in res["warnings"]
        assert res["utilisation"] > 1.0

    def test_multi_schema_changes_result(self):
        base = {
            "q_s_kgf_m2": 300,
            "i_cm": 50,
            "L_cm": 500,
            "E_kgf_cm2": 315000,
            "I_cm4": 33333,
            "include_long_term": False,
        }
        app = NTC2018CodeModule.run_check(
            "x4_sle_deformabilita", {**base, "schema": "appoggio_appoggio"}
        )
        inc = NTC2018CodeModule.run_check(
            "x4_sle_deformabilita", {**base, "schema": "incastro_incastro"}
        )
        assert inc["f_ist_cm"] < app["f_ist_cm"]

    def test_warning_phi_anomalo(self):
        inputs = {
            "q_s_kgf_m2": 250,
            "i_cm": 50,
            "L_cm": 450,
            "E_kgf_cm2": 315000,
            "I_cm4": 32000,
            "phi_viscosita": 3.2,
        }
        res = NTC2018CodeModule.run_check("x4_sle_deformabilita", inputs)
        assert "X4-DEF-003" in res["warnings"]

    def test_warning_e_reduced_without_documentation(self):
        inputs = {
            "q_s_kgf_m2": 250,
            "i_cm": 50,
            "L_cm": 450,
            "E_kgf_cm2": 150000,
            "E_ref_kgf_cm2": 400000,
            "I_cm4": 32000,
        }
        res = NTC2018CodeModule.run_check("x4_sle_deformabilita", inputs)
        assert "X4-DEF-002" in res["warnings"]

    def test_fallback_path(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_deformabilita",
            {
                "L_cm": 500,
                "f_lim_ratio": 250,
                "use_fallback": True,
                "h_cm": 20,
                "k_predim": 80,
            },
        )
        assert "X4-DEF-FALL-001" in res["warnings"]


class TestX4Tensioni:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x4_sle_tensioni", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_golden_case_ok(self):
        inputs = {
            "M_rara_kgf_cm": 800000,
            "M_qp_kgf_cm": 500000,
            "b_cm": 100,
            "d_cm": 20,
            "As_cm2": 20,
            "f_ck_kgf_cm2": 300,
            "f_yk_kgf_cm2": 4500,
            "E_c_kgf_cm2": 310000,
            "E_s_kgf_cm2": 2100000,
            "classe_esposizione": "ordinaria",
        }
        res = NTC2018CodeModule.run_check("x4_sle_tensioni", inputs)
        _assert_contract(res)
        assert res["ok"] is True
        assert res["details"]["sigma_c_rara_kgf_cm2"] == pytest.approx(145, rel=0.08)
        assert res["details"]["w_k_mm"] == pytest.approx(0.23, rel=0.15)
        assert res["utilisation"] < 1.0

    def test_non_ok_with_multiple_warnings(self):
        inputs = {
            "M_rara_kgf_cm": 2_000_000,
            "M_qp_kgf_cm": 1_500_000,
            "b_cm": 100,
            "d_cm": 20,
            "As_cm2": 20,
            "f_ck_kgf_cm2": 300,
            "f_yk_kgf_cm2": 4500,
            "E_c_kgf_cm2": 310000,
            "E_s_kgf_cm2": 2100000,
            "classe_esposizione": "ordinaria",
        }
        res = NTC2018CodeModule.run_check("x4_sle_tensioni", inputs)
        assert res["ok"] is False
        assert "X4-SLE-001" in res["warnings"]
        assert "X4-SLE-002" in res["warnings"]
        assert "X4-SLE-003" in res["warnings"]
        assert "X4-SLE-004" in res["warnings"]

    def test_exposure_class_changes_crack_limit(self):
        base = {
            "M_rara_kgf_cm": 900000,
            "M_qp_kgf_cm": 600000,
            "b_cm": 100,
            "d_cm": 20,
            "As_cm2": 20,
            "f_ck_kgf_cm2": 300,
            "f_yk_kgf_cm2": 4500,
            "E_c_kgf_cm2": 310000,
            "E_s_kgf_cm2": 2100000,
        }
        ord_res = NTC2018CodeModule.run_check(
            "x4_sle_tensioni", {**base, "classe_esposizione": "ordinaria"}
        )
        agg_res = NTC2018CodeModule.run_check(
            "x4_sle_tensioni", {**base, "classe_esposizione": "molto_aggressiva"}
        )
        assert agg_res["details"]["w_lim_mm"] < ord_res["details"]["w_lim_mm"]

    def test_fallback_path(self):
        inputs = {
            "M_rara_kgf_cm": 600000,
            "M_qp_kgf_cm": 300000,
            "f_ck_kgf_cm2": 300,
            "W_cm3": 3000,
            "use_fallback": True,
        }
        res = NTC2018CodeModule.run_check("x4_sle_tensioni", inputs)
        assert "X4-SLE-FALL-001" in res["warnings"]
        assert res["ok"] is False

    def test_normative_references_present(self):
        inputs = {
            "M_rara_kgf_cm": 800000,
            "M_qp_kgf_cm": 500000,
            "b_cm": 100,
            "d_cm": 20,
            "As_cm2": 20,
            "f_ck_kgf_cm2": 300,
            "f_yk_kgf_cm2": 4500,
            "E_c_kgf_cm2": 310000,
        }
        res = NTC2018CodeModule.run_check("x4_sle_tensioni", inputs)
        assert any("NTC2018" in ref for ref in res["norm_references"])
        assert any("EN 1992-1-1" in ref for ref in res["norm_references"])


class TestX4Vibrazioni:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x4_sle_vibrazioni", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_golden_case_ok(self):
        inputs = {
            "L_m": 6,
            "EI_Nm2": 2.0e9,
            "m_kg_m": 10000,
            "xi": 0.05,
            "destinazione": "residenziale",
        }
        res = NTC2018CodeModule.run_check("x4_sle_vibrazioni", inputs)
        _assert_contract(res)
        assert res["ok"] is True
        assert res["details"]["f1_Hz"] > 4.0
        assert res["details"]["a_RMS_m_s2"] < 0.5

    def test_frequency_non_ok(self):
        inputs = {
            "L_m": 12,
            "EI_Nm2": 2.0e7,
            "m_kg_m": 1500,
            "xi": 0.05,
            "destinazione": "residenziale",
        }
        res = NTC2018CodeModule.run_check("x4_sle_vibrazioni", inputs)
        assert "X4-VIB-001" in res["warnings"]

    def test_acceleration_non_ok(self):
        inputs = {
            "L_m": 5,
            "EI_Nm2": 5.0e9,
            "m_kg_m": 3000,
            "xi": 0.01,
            "destinazione": "residenziale",
        }
        res = NTC2018CodeModule.run_check("x4_sle_vibrazioni", inputs)
        assert "X4-VIB-002" in res["warnings"]

    def test_thresholds_depend_on_use_category(self):
        base = {
            "L_m": 10,
            "EI_Nm2": 8.0e8,
            "m_kg_m": 7000,
            "xi": 0.05,
        }
        palestra = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni", {**base, "destinazione": "palestre"}
        )
        passerella = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni", {**base, "destinazione": "passerelle"}
        )
        assert palestra["details"]["f1_lim_Hz"] == pytest.approx(5.0)
        assert passerella["details"]["f1_lim_Hz"] == pytest.approx(8.0)
        assert passerella["ok"] is False

    def test_warning_low_mass(self):
        inputs = {
            "L_m": 5,
            "EI_Nm2": 1.0e8,
            "m_kg_m": 30,
            "xi": 0.1,
        }
        res = NTC2018CodeModule.run_check("x4_sle_vibrazioni", inputs)
        assert "X4-VIB-003" in res["warnings"]

    def test_fallback_path(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni", {"use_fallback": True, "delta_cm": 1.0}
        )
        assert "X4-VIB-FALL-001" in res["warnings"]
        assert res["value"] == pytest.approx(18.0)


class TestX4CodeModuleMetadata:
    def test_available_checks_contains_x4_ids(self):
        checks = NTC2018CodeModule.available_checks()
        ids = {check["id"] for check in checks}
        assert "x4_sle_deformabilita" in ids
        assert "x4_sle_tensioni" in ids
        assert "x4_sle_vibrazioni" in ids

    def test_get_check_metadata_for_x4(self):
        meta = NTC2018CodeModule.get_check_metadata("x4_sle_vibrazioni")
        assert meta is not None
        assert meta["limit_state"] == "SLE"
