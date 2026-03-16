import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


class TestX3BenchmarkFlessione:
    def test_benchmark_doc_example_mrd(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 1600,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert res["ok"] is True
        assert res["details"]["x_mm"] == pytest.approx(137.4, rel=0.02)
        assert res["details"]["z_mm"] == pytest.approx(445.0, rel=0.02)
        assert res["M_Rd_kNm"] == pytest.approx(260.0, rel=0.04)

    def test_benchmark_doc_example_uc(self):
        inputs = {
            "b_mm": 300,
            "d_mm": 500,
            "As_mm2": 1600,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
            "M_Ed_kNm": 200,
        }
        res = NTC2018CodeModule.run_check("x3_slu_flessione", inputs)
        assert res["utilisation"] == pytest.approx(0.769, rel=0.06)

    def test_monotonic_as_increase_increases_capacity(self):
        base = {
            "b_mm": 300,
            "d_mm": 500,
            "f_ck_MPa": 25,
            "f_yk_MPa": 420,
        }
        low = NTC2018CodeModule.run_check("x3_slu_flessione", {**base, "As_mm2": 1000})
        high = NTC2018CodeModule.run_check("x3_slu_flessione", {**base, "As_mm2": 1800})
        assert high["M_Rd_kNm"] > low["M_Rd_kNm"]


class TestX3BenchmarkTaglio:
    def test_benchmark_doc_example_vrdc(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 200,
            "f_ck_MPa": 25,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert res["ok"] is True
        # Implementazione corrente: C_Rd,c = 0.18/gamma_c (gamma_c default = 1.5).
        assert res["V_Rd_c_kN"] == pytest.approx(43.89, rel=0.06)
        assert res["details"]["k"] == pytest.approx(1.632, rel=0.03)

    def test_benchmark_doc_example_uc(self):
        inputs = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 200,
            "f_ck_MPa": 25,
            "V_Ed_kN": 40,
        }
        res = NTC2018CodeModule.run_check("x3_slu_taglio", inputs)
        assert res["utilisation"] == pytest.approx(0.911, rel=0.1)
        assert "X3-TAG-002" in res["warnings"]

    def test_monotonic_d_increase_increases_capacity(self):
        base = {
            "bw_mm": 300,
            "Asl_mm2": 250,
            "f_ck_MPa": 25,
        }
        low = NTC2018CodeModule.run_check("x3_slu_taglio", {**base, "d_mm": 250})
        high = NTC2018CodeModule.run_check("x3_slu_taglio", {**base, "d_mm": 500})
        assert high["V_Rd_c_kN"] > low["V_Rd_c_kN"]

    def test_gamma_c_higher_reduces_capacity(self):
        base = {
            "bw_mm": 300,
            "d_mm": 500,
            "Asl_mm2": 250,
            "f_ck_MPa": 25,
        }
        g15 = NTC2018CodeModule.run_check("x3_slu_taglio", {**base, "gamma_c": 1.5})
        g16 = NTC2018CodeModule.run_check("x3_slu_taglio", {**base, "gamma_c": 1.6})
        assert g16["V_Rd_c_kN"] < g15["V_Rd_c_kN"]


class TestX3BenchmarkPunzonamento:
    def test_benchmark_doc_typical_value(self):
        inputs = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_cd_MPa": 16.67,
            "sigma_cp_MPa": 0.0,
        }
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", inputs)
        assert res["ok"] is True
        assert res["V_Rd_c_kN"] == pytest.approx(176.8, rel=0.08)

    def test_sigma_cp_increase_increases_capacity(self):
        base = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.015,
            "f_cd_MPa": 16,
        }
        no_sigma = NTC2018CodeModule.run_check("x3_slu_punzonamento", {**base, "sigma_cp_MPa": 0.0})
        with_sigma = NTC2018CodeModule.run_check(
            "x3_slu_punzonamento", {**base, "sigma_cp_MPa": 1.0}
        )
        assert with_sigma["V_Rd_c_kN"] > no_sigma["V_Rd_c_kN"]

    def test_ved_below_08_no_warning(self):
        base = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_cd_MPa": 16.67,
            "sigma_cp_MPa": 0.0,
        }
        cap = NTC2018CodeModule.run_check("x3_slu_punzonamento", base)["V_Rd_kN"]
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", {**base, "V_Ed_kN": 0.79 * cap})
        assert "X3-PUNZ-001" not in res["warnings"]

    def test_ved_above_08_warning(self):
        base = {
            "b0_mm": 1000,
            "d_mm": 200,
            "rho_l": 0.02,
            "f_cd_MPa": 16.67,
            "sigma_cp_MPa": 0.0,
        }
        cap = NTC2018CodeModule.run_check("x3_slu_punzonamento", base)["V_Rd_kN"]
        res = NTC2018CodeModule.run_check("x3_slu_punzonamento", {**base, "V_Ed_kN": 0.81 * cap})
        assert "X3-PUNZ-001" in res["warnings"]


class TestX3BenchmarkFallback:
    @pytest.mark.parametrize(
        "inputs,expected_case",
        [
            ({"luce_m": 4.5, "interasse_cm": 50, "altezza_cm": 24}, "LC-01"),
            ({"luce_m": 4.5, "interasse_cm": 50, "altezza_cm": 24.1}, "LC-02"),
            ({"luce_m": 5.5, "interasse_cm": 60, "altezza_cm": 28}, "LC-03"),
        ],
    )
    def test_dm96_boundary_classification(self, inputs, expected_case):
        res = NTC2018CodeModule.run_check("x3_dm96_laterocemento", inputs)
        assert res["ok"] is True
        assert res["case_id"] == expected_case

    def test_dm96_outside_table(self):
        res = NTC2018CodeModule.run_check(
            "x3_dm96_laterocemento", {"luce_m": 3.0, "interasse_cm": 40, "altezza_cm": 18}
        )
        assert res["ok"] is False
        assert "X3-DM96-001" in res["warnings"]

    def test_dm16_default_gamma_usage(self):
        res = NTC2018CodeModule.run_check("x3_dm16_legno", {"f_mk_MPa": 30})
        assert res["ok"] is True
        assert res["details"]["gamma_m"] == pytest.approx(1.5)
        assert res["f_md_MPa"] == pytest.approx(20.0, rel=1e-4)

    def test_dm16_warning_missing_fmk(self):
        res = NTC2018CodeModule.run_check("x3_dm16_legno", {"f_mk_MPa": 0})
        assert res["ok"] is False
        assert "X3-DM16-001" in res["warnings"]
