import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


def test_vrdc_no_stirrups_contract():
    res = NTC2018CodeModule.run_check("vrdc_no_stirrups", {})
    assert "trace" in res
    assert "run_id" in res["trace"]
    assert "norm_references" in res


def test_vrdc_no_stirrups_golden_case():
    """Caso noto: trave 25x50 cm, 3φ25, C25, nessuna forza normale.
    V_Rd,c calcolato manualmente secondo NTC2018 §4.1.2.1.3.1 / EC2 §6.2.2.
    """
    inputs = {
        "b_w_mm": 250,
        "d_mm": 450,
        "A_sl_mm2": 1473,  # ~3φ25
        "f_ck_MPa": 25,
        "N_Ed_N": 0,
        "A_c_mm2": 125000,
        "gamma_c": 1.5,
        "V_Ed_N": 50000,  # 50 kN
    }
    res = NTC2018CodeModule.run_check("vrdc_no_stirrups", inputs)
    assert res["ok"] is True
    # V_Rd,c ≈ 71 975 N (tolleranza 1%)
    assert abs(res["value"] - 71974.6) < 720
    assert res["V_Rd_c_kN"] == pytest.approx(71.97, abs=0.5)
    assert res["utilisation"] == pytest.approx(0.6947, abs=0.005)
    assert res["details"]["k"] == pytest.approx(1.6667, abs=0.001)
