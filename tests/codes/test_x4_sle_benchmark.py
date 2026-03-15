import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


class TestX4BenchmarkDeformabilita:
    def test_b01_freccia_doc_example(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_deformabilita",
            {
                "q_s_kgf_m2": 300,
                "i_cm": 50,
                "L_cm": 500,
                "E_kgf_cm2": 315000,
                "I_cm4": 33333,
                "include_long_term": False,
            },
        )
        assert res["f_ist_cm"] == pytest.approx(0.116, rel=0.05)

    def test_b02_freccia_lungo_termine(self):
        base = {
            "q_s_kgf_m2": 300,
            "i_cm": 50,
            "L_cm": 500,
            "E_kgf_cm2": 315000,
            "I_cm4": 33333,
            "phi_viscosita": 2.5,
        }
        res = NTC2018CodeModule.run_check("x4_sle_deformabilita", base)
        assert res["f_tot_cm"] == pytest.approx(res["f_ist_cm"] * 3.5, rel=0.02)

    def test_b03_freccia_incastro_incastro(self):
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
        assert inc["f_ist_cm"] == pytest.approx(app["f_ist_cm"] / 5.0, rel=0.06)

    def test_b04_monotonia_piu_carico_piu_freccia(self):
        base = {
            "i_cm": 50,
            "L_cm": 500,
            "E_kgf_cm2": 315000,
            "I_cm4": 33333,
        }
        low = NTC2018CodeModule.run_check("x4_sle_deformabilita", {**base, "q_s_kgf_m2": 250})
        high = NTC2018CodeModule.run_check("x4_sle_deformabilita", {**base, "q_s_kgf_m2": 400})
        assert high["f_tot_cm"] > low["f_tot_cm"]

    def test_b05_monotonia_piu_luce_piu_freccia(self):
        base = {
            "q_s_kgf_m2": 300,
            "i_cm": 50,
            "E_kgf_cm2": 315000,
            "I_cm4": 33333,
        }
        l500 = NTC2018CodeModule.run_check("x4_sle_deformabilita", {**base, "L_cm": 500})
        l600 = NTC2018CodeModule.run_check("x4_sle_deformabilita", {**base, "L_cm": 600})
        assert l600["f_tot_cm"] > l500["f_tot_cm"]


class TestX4BenchmarkTensioniEFessurazione:
    def test_b06_sigma_c_rara_example(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_tensioni",
            {
                "M_rara_kgf_cm": 800000,
                "M_qp_kgf_cm": 500000,
                "b_cm": 100,
                "d_cm": 20,
                "As_cm2": 20,
                "f_ck_kgf_cm2": 300,
                "f_yk_kgf_cm2": 4500,
                "E_c_kgf_cm2": 310000,
            },
        )
        assert res["details"]["sigma_c_rara_kgf_cm2"] == pytest.approx(145, rel=0.08)

    def test_b07_sigma_c_qp_example(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_tensioni",
            {
                "M_rara_kgf_cm": 800000,
                "M_qp_kgf_cm": 500000,
                "b_cm": 100,
                "d_cm": 20,
                "As_cm2": 20,
                "f_ck_kgf_cm2": 300,
                "f_yk_kgf_cm2": 4500,
                "E_c_kgf_cm2": 310000,
            },
        )
        assert res["details"]["sigma_c_qp_kgf_cm2"] == pytest.approx(90, rel=0.1)

    def test_b08_wk_example(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_tensioni",
            {
                "M_rara_kgf_cm": 800000,
                "M_qp_kgf_cm": 500000,
                "b_cm": 100,
                "d_cm": 20,
                "As_cm2": 20,
                "f_ck_kgf_cm2": 300,
                "f_yk_kgf_cm2": 4500,
                "E_c_kgf_cm2": 310000,
            },
        )
        assert res["details"]["w_k_mm"] == pytest.approx(0.23, rel=0.2)

    def test_b09_monotonia_piu_momento_piu_tensione(self):
        base = {
            "M_qp_kgf_cm": 500000,
            "b_cm": 100,
            "d_cm": 20,
            "As_cm2": 20,
            "f_ck_kgf_cm2": 300,
            "f_yk_kgf_cm2": 4500,
            "E_c_kgf_cm2": 310000,
        }
        m1 = NTC2018CodeModule.run_check("x4_sle_tensioni", {**base, "M_rara_kgf_cm": 700000})
        m2 = NTC2018CodeModule.run_check("x4_sle_tensioni", {**base, "M_rara_kgf_cm": 900000})
        assert m2["details"]["sigma_c_rara_kgf_cm2"] > m1["details"]["sigma_c_rara_kgf_cm2"]


class TestX4BenchmarkVibrazioni:
    def test_b10_f1_example(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni",
            {
                "L_m": 6,
                "EI_Nm2": 2.0e9,
                "m_kg_m": 10000,
                "xi": 0.05,
            },
        )
        assert res["details"]["f1_Hz"] == pytest.approx(19.5, rel=0.1)

    def test_b11_f1_multi_schema(self):
        base = {
            "L_m": 8,
            "EI_Nm2": 1.5e9,
            "m_kg_m": 9000,
            "xi": 0.05,
        }
        app = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni", {**base, "schema": "appoggio_appoggio"}
        )
        inc = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni", {**base, "schema": "incastro_incastro"}
        )
        assert inc["details"]["f1_Hz"] > app["details"]["f1_Hz"]

    def test_b12_monotonia_piu_luce_meno_f1(self):
        base = {
            "EI_Nm2": 1.5e9,
            "m_kg_m": 9000,
            "xi": 0.05,
        }
        short = NTC2018CodeModule.run_check("x4_sle_vibrazioni", {**base, "L_m": 6})
        long = NTC2018CodeModule.run_check("x4_sle_vibrazioni", {**base, "L_m": 10})
        assert long["details"]["f1_Hz"] < short["details"]["f1_Hz"]

    def test_b13_a_rms_example(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni",
            {
                "L_m": 6,
                "EI_Nm2": 2.0e9,
                "m_kg_m": 10000,
                "xi": 0.05,
                "F_ped_N": 700,
            },
        )
        assert res["details"]["a_RMS_m_s2"] == pytest.approx(0.165, rel=0.1)


class TestX4BenchmarkBoundaries:
    def test_b14_boundary_l_zero_error(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_vibrazioni", {"L_m": 0.0, "EI_Nm2": 2.0e9, "m_kg_m": 10000}
        )
        assert res["ok"] is False

    def test_b15_boundary_i_zero_error(self):
        res = NTC2018CodeModule.run_check(
            "x4_sle_deformabilita",
            {
                "q_s_kgf_m2": 300,
                "i_cm": 50,
                "L_cm": 500,
                "E_kgf_cm2": 315000,
                "I_cm4": 0.0,
            },
        )
        assert res["ok"] is False
