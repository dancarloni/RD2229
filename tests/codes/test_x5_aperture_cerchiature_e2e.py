import json
from pathlib import Path

import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule
from src.core_calculus.solaio_input import parse_solaio_input


def _load_solaio_fixture() -> dict:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "solaio_input_valid.json"
    return json.loads(fixture.read_text(encoding="utf-8"))


def _compute_ei_lordo_kgf_cm2(ready: dict) -> float:
    e_kgf_cm2 = float(ready["original"]["materiali"]["E"])
    b_cm = float(ready["original"]["geometria"]["interasse_cm"])
    h_cm = float(ready["original"]["geometria"]["spessore_cm"])
    i_cm4 = b_cm * (h_cm**3) / 12.0
    return e_kgf_cm2 * i_cm4


class TestX5E2EFlow:
    def test_e2e_nominal_flow_from_parse_input(self):
        ready = parse_solaio_input(_load_solaio_fixture()).as_ready_dict()

        luce_cm = float(ready["original"]["geometria"]["luce_cm"])
        interasse_cm = float(ready["original"]["geometria"]["interasse_cm"])
        area_pannello_cm2 = luce_cm * interasse_cm
        area_apertura_cm2 = 60.0 * 60.0

        class_res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": area_apertura_cm2,
                "area_pannello_cm2": area_pannello_cm2,
            },
        )
        assert class_res["ok"] is True
        assert class_res["details"]["classe_apertura"] == "media"

        ei_lordo = _compute_ei_lordo_kgf_cm2(ready)
        rig_res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_kgf_cm2": ei_lordo,
                "rapporto_apertura": class_res["value"],
            },
        )
        assert rig_res["ok"] is True
        assert rig_res["details"]["EI_eff_kgf_cm2"] == pytest.approx(ei_lordo * 0.8, rel=1e-12)

        q_tot_kgf_m2 = (
            float(ready["original"]["carichi"]["G1"])
            + float(ready["original"]["carichi"]["G2"])
            + float(ready["original"]["carichi"]["Q"])
        )
        cer_res = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "q_area_kgf_m2": q_tot_kgf_m2,
                "area_apertura_m2": area_apertura_cm2 / 10_000.0,
                "k_cerchiatura": 120,
                "k_solaio": 180,
                "tipo_cerchiatura": "acciaio",
                "rapporto_apertura": class_res["value"],
            },
        )
        assert cer_res["ok"] is True
        assert cer_res["details"]["quota_redistribuita"] == pytest.approx(0.4, rel=1e-12)
        assert cer_res["details"]["trigger_fem"] is True

    def test_e2e_extreme_opening_has_expected_warnings(self):
        ready = parse_solaio_input(_load_solaio_fixture()).as_ready_dict()
        luce_cm = float(ready["original"]["geometria"]["luce_cm"])
        interasse_cm = float(ready["original"]["geometria"]["interasse_cm"])

        class_res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 15_000.0,
                "area_pannello_cm2": luce_cm * interasse_cm,
            },
        )
        assert "X5-APE-001" in class_res["warnings"]
        assert "X5-APE-002" in class_res["warnings"]

        rig_res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_kgf_cm2": _compute_ei_lordo_kgf_cm2(ready),
                "rapporto_apertura": class_res["value"],
            },
        )
        assert "X5-APE-001" in rig_res["warnings"]
        assert "X5-APE-002" in rig_res["warnings"]

    def test_e2e_near_support_triggers_fem_even_when_ratio_low(self):
        ready = parse_solaio_input(_load_solaio_fixture()).as_ready_dict()
        luce_cm = float(ready["original"]["geometria"]["luce_cm"])
        interasse_cm = float(ready["original"]["geometria"]["interasse_cm"])

        class_res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 1000.0,
                "area_pannello_cm2": luce_cm * interasse_cm,
                "luce_cm": luce_cm,
                "distanza_apertura_appoggio_cm": 15.0,
            },
        )
        assert class_res["details"]["rapporto_apertura"] < 0.25
        assert class_res["details"]["trigger_fem"] is True
        assert "apertura_vicina_appoggi" in class_res["details"]["trigger_reasons"]
