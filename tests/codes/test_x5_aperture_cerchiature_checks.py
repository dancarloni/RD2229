import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


def _assert_contract(res: dict) -> None:
    assert "ok" in res
    assert "value" in res
    assert "utilisation" in res
    assert "details" in res
    assert "steps" in res
    assert "warnings" in res
    assert "trace" in res
    assert "run_id" in res["trace"]
    assert "norm_references" in res


class TestX5ApertureClassificazione:
    def test_contract_error_when_inputs_missing(self):
        res = NTC2018CodeModule.run_check("x5_aperture_classificazione", {})
        _assert_contract(res)
        assert res["ok"] is False

    def test_small_class_default_alpha(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 800,
                "area_pannello_cm2": 10000,
            },
        )
        _assert_contract(res)
        assert res["ok"] is True
        assert res["details"]["classe_apertura"] == "piccola"
        assert res["details"]["alpha_ap"] == pytest.approx(0.05, rel=1e-9)
        assert res["warnings"] == []

    def test_warning_trigger_fem_ratio_gt_025(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 3000,
                "area_pannello_cm2": 10000,
            },
        )
        assert res["details"]["classe_apertura"] == "grande"
        assert res["details"]["trigger_fem"] is True
        assert "X5-APE-001" in res["warnings"]

    def test_warning_extreme_ratio_gt_050(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 6000,
                "area_pannello_cm2": 10000,
            },
        )
        assert "X5-APE-001" in res["warnings"]
        assert "X5-APE-002" in res["warnings"]

    def test_local_trigger_near_support(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 1200,
                "area_pannello_cm2": 10000,
                "luce_cm": 400,
                "distanza_apertura_appoggio_cm": 20,
            },
        )
        assert res["details"]["trigger_fem"] is True
        assert "apertura_vicina_appoggi" in res["details"]["trigger_reasons"]

    def test_warning_area_manual(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "area_apertura_cm2": 900,
                "area_pannello_cm2": 10000,
                "area_influenza_source": "manuale",
            },
        )
        assert "X5-AREA-001" in res["warnings"]


class TestX5ApertureRigidezza:
    def test_contract_error_when_ei_missing(self):
        res = NTC2018CodeModule.run_check("x5_aperture_rigidezza", {"alpha_ap": 0.2})
        _assert_contract(res)
        assert res["ok"] is False

    def test_ei_eff_from_ratio_default_alpha(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_kgf_cm2": 2_000_000_000,
                "rapporto_apertura": 0.30,
            },
        )
        _assert_contract(res)
        assert res["ok"] is True
        assert res["details"]["classe_apertura"] == "grande"
        assert res["details"]["alpha_ap"] == pytest.approx(0.40, rel=1e-9)
        assert res["value"] == pytest.approx(1_200_000_000.0, rel=1e-12)
        assert res["utilisation"] == pytest.approx(0.6, rel=1e-12)
        assert "X5-APE-001" in res["warnings"]

    def test_ei_input_si_and_manual_alpha(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_Nm2": 980665.0,
                "alpha_ap": 0.2,
            },
        )
        assert res["ok"] is True
        assert res["details"]["EI_lordo_kgf_cm2"] == pytest.approx(1_000_000_000.0, rel=1e-9)
        assert res["details"]["EI_eff_kgf_cm2"] == pytest.approx(800_000_000.0, rel=1e-9)

    def test_extreme_ratio_warnings(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_kgf_cm2": 1_000_000,
                "rapporto_apertura": 0.60,
            },
        )
        assert "X5-APE-001" in res["warnings"]
        assert "X5-APE-002" in res["warnings"]


class TestX5CerchiaturaRedistribuzione:
    def test_contract_with_stiffness_inputs(self):
        res = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "q_area_kgf_m2": 300,
                "area_apertura_m2": 1.44,
                "k_cerchiatura": 80,
                "k_solaio": 120,
                "tipo_cerchiatura": "acciaio",
                "schema_statico_coerente": True,
            },
        )
        _assert_contract(res)
        assert res["ok"] is True
        assert res["value"] == pytest.approx(0.4, rel=1e-12)
        assert res["details"]["Q_apertura_kgf"] == pytest.approx(432.0, rel=1e-12)
        assert res["details"]["trigger_fem"] is True

    def test_warning_cerchiatura_non_ammessa(self):
        res = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "quota_redistribuita": 0.35,
                "tipo_cerchiatura": "muratura",
                "schema_statico_coerente": True,
            },
        )
        assert res["ok"] is False
        assert "X5-CER-001" in res["warnings"]

    def test_warning_schema_non_coerente(self):
        res = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "quota_redistribuita": 0.20,
                "tipo_cerchiatura": "acciaio",
                "schema_statico_coerente": False,
            },
        )
        assert res["ok"] is False
        assert "X5-CER-001" in res["warnings"]

    def test_warning_area_manual(self):
        res = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "quota_redistribuita": 0.2,
                "area_influenza_manuale": True,
                "tipo_cerchiatura": "acciaio",
            },
        )
        assert "X5-AREA-001" in res["warnings"]


class TestX5CodeModuleMetadata:
    def test_available_checks_contains_x5_ids(self):
        checks = NTC2018CodeModule.available_checks()
        ids = {check["id"] for check in checks}
        assert "x5_aperture_classificazione" in ids
        assert "x5_aperture_rigidezza" in ids
        assert "x5_cerchiatura_redistribuzione" in ids

    def test_available_checks_status_implemented(self):
        checks = NTC2018CodeModule.available_checks()
        by_id = {item["id"]: item for item in checks}
        assert by_id["x5_aperture_classificazione"]["status"] == "implemented"
        assert by_id["x5_aperture_rigidezza"]["status"] == "implemented"
        assert by_id["x5_cerchiatura_redistribuzione"]["status"] == "implemented"

    def test_get_check_metadata_for_x5(self):
        meta = NTC2018CodeModule.get_check_metadata("x5_cerchiatura_redistribuzione")
        assert meta is not None
        assert meta["limit_state"] == "SLE"
