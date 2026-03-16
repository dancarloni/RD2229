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


class TestX5BenchmarkPushover:
    def test_pushover_post_has_non_lower_capacity_with_reinforcement(self):
        res = NTC2018CodeModule.run_check(
            "x5_parete_pushover_ante_post",
            {
                "parete_id": "wb_push_1",
                "lunghezza_cm": 450.0,
                "altezza_cm": 300.0,
                "spessore_cm": 30.0,
                "E_kgf_cm2": 240000.0,
                "aperture_esistenti": [
                    {
                        "id": "a1",
                        "tipo": "preesistente",
                        "x_cm": 90.0,
                        "y_cm": 60.0,
                        "h_cm": 80.0,
                        "b_cm": 110.0,
                    }
                ],
                "rinforzi": [
                    {"id": "r1", "tipo": "cerchiatura", "efficacia": 0.12},
                    {"id": "r2", "tipo": "FRP", "efficacia": 0.08},
                ],
                "metodi_pushover": ["bilineare", "trilineare", "numerico"],
                "drift_limit": 0.03,
            },
        )
        assert res["ok"] is True
        cmp_data = res["details"]["compare"]["by_method"]
        assert cmp_data["bilineare"]["ratio_Fu"] >= 1.0
        assert cmp_data["trilineare"]["ratio_K0"] >= 1.0

    def test_pushover_all_methods_present(self):
        res = NTC2018CodeModule.run_check(
            "x5_parete_pushover_ante_post",
            {
                "parete_id": "wb_push_2",
                "lunghezza_cm": 500.0,
                "altezza_cm": 300.0,
                "spessore_cm": 25.0,
                "E_kgf_cm2": 230000.0,
                "metodi_pushover": ["bilineare", "trilineare", "numerico"],
            },
        )
        methods = set(res["details"]["post"]["results"].keys())
        assert methods == {"bilineare", "trilineare", "numerico"}

    def test_seismic_demand_monotonic_with_ag(self):
        base_payload = {
            "parete_id": "wb_push_3",
            "lunghezza_cm": 500.0,
            "altezza_cm": 300.0,
            "spessore_cm": 25.0,
            "E_kgf_cm2": 230000.0,
            "gk_kgf": 100000.0,
            "qk_kgf": 30000.0,
            "q_factor": 1.0,
        }
        low = NTC2018CodeModule.run_check(
            "x5_parete_pushover_ante_post", {**base_payload, "ag_over_g": 0.15}
        )
        high = NTC2018CodeModule.run_check(
            "x5_parete_pushover_ante_post", {**base_payload, "ag_over_g": 0.35}
        )
        d_low = low["details"]["seismic_combinations"]["levels"]["SLV"]["demand_kgf"]
        d_high = high["details"]["seismic_combinations"]["levels"]["SLV"]["demand_kgf"]
        assert d_high > d_low
