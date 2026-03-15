import pytest

from src.codes.ntc2018.code_module import NTC2018CodeModule


class TestX5BenchmarkClassificazione:
    @pytest.mark.parametrize(
        "ratio,expected_class,expected_alpha",
        [
            (0.08, "piccola", 0.05),
            (0.20, "media", 0.20),
            (0.40, "grande", 0.40),
            (0.60, "estrema", 0.60),
        ],
    )
    def test_classification_threshold_examples(self, ratio, expected_class, expected_alpha):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {
                "rapporto_apertura": ratio,
                "area_apertura_cm2": ratio * 10_000.0,
                "area_pannello_cm2": 10_000.0,
            },
        )
        assert res["details"]["classe_apertura"] == expected_class
        assert res["details"]["alpha_ap"] == pytest.approx(expected_alpha, rel=1e-12)

    def test_ratio_monotonicity(self):
        low = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {"area_apertura_cm2": 800, "area_pannello_cm2": 10000},
        )
        high = NTC2018CodeModule.run_check(
            "x5_aperture_classificazione",
            {"area_apertura_cm2": 3000, "area_pannello_cm2": 10000},
        )
        assert high["value"] > low["value"]


class TestX5BenchmarkRigidezza:
    def test_ei_eff_nominal_case(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_kgf_cm2": 2_000_000_000,
                "rapporto_apertura": 0.30,
            },
        )
        assert res["details"]["alpha_ap"] == pytest.approx(0.40, rel=1e-12)
        assert res["value"] == pytest.approx(1_200_000_000.0, rel=1e-12)

    def test_monotonicity_more_ratio_lower_ei_eff(self):
        base = {"EI_lordo_kgf_cm2": 1_000_000_000}
        r08 = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza", {**base, "rapporto_apertura": 0.08}
        )
        r20 = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza", {**base, "rapporto_apertura": 0.20}
        )
        r40 = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza", {**base, "rapporto_apertura": 0.40}
        )
        assert r08["value"] > r20["value"] > r40["value"]

    def test_manual_alpha_overrides_ratio_class(self):
        res = NTC2018CodeModule.run_check(
            "x5_aperture_rigidezza",
            {
                "EI_lordo_kgf_cm2": 1_000_000_000,
                "rapporto_apertura": 0.40,
                "alpha_ap": 0.10,
            },
        )
        assert res["details"]["classe_apertura"] == "manuale"
        assert res["value"] == pytest.approx(900_000_000.0, rel=1e-12)


class TestX5BenchmarkCerchiatura:
    def test_q_apertura_example(self):
        res = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "q_area_kgf_m2": 300,
                "area_apertura_m2": 1.44,
                "quota_redistribuita": 0.5,
                "tipo_cerchiatura": "acciaio",
            },
        )
        assert res["details"]["Q_apertura_kgf"] == pytest.approx(432.0, rel=1e-12)
        assert res["details"]["Q_cerchiatura_kgf"] == pytest.approx(216.0, rel=1e-12)

    def test_stiffness_ratio_controls_redistribution(self):
        base = {
            "q_area_kgf_m2": 300,
            "area_apertura_m2": 1.0,
            "k_solaio": 100,
            "tipo_cerchiatura": "acciaio",
        }
        low = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione", {**base, "k_cerchiatura": 50}
        )
        high = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione", {**base, "k_cerchiatura": 300}
        )
        assert high["value"] > low["value"]

    def test_significant_threshold_boundary(self):
        low = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "quota_redistribuita": 0.29,
                "tipo_cerchiatura": "acciaio",
            },
        )
        high = NTC2018CodeModule.run_check(
            "x5_cerchiatura_redistribuzione",
            {
                "quota_redistribuita": 0.31,
                "tipo_cerchiatura": "acciaio",
            },
        )
        assert low["details"]["redistribuzione_significativa"] is False
        assert high["details"]["redistribuzione_significativa"] is True
