"""Test FASE N — Carote cls in situ (~66 test).

Gruppi: CoreSample, Formulas, Statistics, DerivedParams, Analysis,
        Integration, Report/Export, Plots, Widget, Package.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_F_CORE = [22.5, 24.1, 23.8, 25.0, 22.0, 24.5, 23.2, 24.8]


def _make_samples():
    from src.codes.carote.core_sample import CoreSample

    return [
        CoreSample(sample_id=f"C{i+1}", f_core_mpa=f)
        for i, f in enumerate(_F_CORE)
    ]


# ===================================================================
# 1. CoreSample (8 test)
# ===================================================================


class TestCoreSample:
    def test_creazione_base(self):
        from src.codes.carote.core_sample import CoreSample

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        assert s.ld_ratio == 1.0  # 100/100

    def test_ld_ratio(self):
        from src.codes.carote.core_sample import CoreSample

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, diameter_mm=100, length_mm=200)
        assert s.ld_ratio == pytest.approx(2.0)

    def test_ld_ratio_custom(self):
        from src.codes.carote.core_sample import CoreSample

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, diameter_mm=75, length_mm=150)
        assert s.ld_ratio == pytest.approx(2.0)

    def test_validazione_fcore_negativo(self):
        from src.codes.carote.core_sample import CoreSample

        with pytest.raises(ValueError, match="f_core_mpa"):
            CoreSample(sample_id="C1", f_core_mpa=-5.0)

    def test_validazione_diametro_zero(self):
        from src.codes.carote.core_sample import CoreSample

        with pytest.raises(ValueError, match="diameter_mm"):
            CoreSample(sample_id="C1", f_core_mpa=25.0, diameter_mm=0)

    def test_validazione_direzione(self):
        from src.codes.carote.core_sample import CoreSample

        with pytest.raises(ValueError, match="direction"):
            CoreSample(sample_id="C1", f_core_mpa=25.0, direction="obliqua")

    def test_validazione_moisture(self):
        from src.codes.carote.core_sample import CoreSample

        with pytest.raises(ValueError, match="moisture"):
            CoreSample(sample_id="C1", f_core_mpa=25.0, moisture="bagnato")

    def test_correction_factors_k_total(self):
        from src.codes.carote.core_sample import CorrectionFactors

        cf = CorrectionFactors(k_ld=0.92, k_dir=1.06)
        assert cf.k_total == pytest.approx(0.92 * 1.06 * 1.0 * 1.0 * 1.0 * 1.0)

    def test_correction_factors_overrides(self):
        from src.codes.carote.core_sample import CorrectionFactors

        cf = CorrectionFactors(k_ld=0.92, overrides={"k_ld": 0.85})
        # override sostituisce k_ld
        assert cf.k_total == pytest.approx(0.85)


# ===================================================================
# 2. Formulas (18 test)
# ===================================================================


class TestFormulasBS1881:
    def test_ld_2(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_bs1881

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=200, diameter_mm=100)
        r = converti_bs1881(s)
        # L/D=2 -> k_ld=1.0, standard sample -> f_is ~ 25 * k_total
        assert r.formulation == "BS1881"
        assert r.f_is_mpa > 0

    def test_ld_1(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_bs1881

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=100, diameter_mm=100)
        r = converti_bs1881(s)
        # L/D=1 -> k_ld=0.80
        assert r.correction_factors.k_ld == pytest.approx(0.80)


class TestFormulasACI214:
    def test_ld_sotto_175(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_aci214

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=100, diameter_mm=100)
        r = converti_aci214(s)
        # L/D=1.0: k = 2/(1.04+0.04*1) = 2/1.08 = 1.8519
        assert r.correction_factors.k_ld == pytest.approx(2.0 / 1.08, rel=1e-3)

    def test_ld_sopra_175(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_aci214

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=200, diameter_mm=100)
        r = converti_aci214(s)
        assert r.correction_factors.k_ld == pytest.approx(1.0)


class TestFormulasTR11:
    def test_basic(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_tr11

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        r = converti_tr11(s)
        assert r.formulation == "TR11"
        assert r.f_is_mpa > 0


class TestFormulasRILEM:
    def test_basic(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_rilem1979

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=200, diameter_mm=100)
        r = converti_rilem1979(s)
        assert r.formulation == "RILEM1979"
        assert r.correction_factors.k_ld == pytest.approx(1.0)


class TestFormulasMasi:
    def test_regressione(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_masi2005

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=100, diameter_mm=100)
        r = converti_masi2005(s)
        # k_ld = 0.667 + 0.167*1 = 0.834
        assert r.correction_factors.k_ld == pytest.approx(0.834, rel=1e-3)


class TestFormulasFiore:
    def test_regressione(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_fiore2008

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=100, diameter_mm=100)
        r = converti_fiore2008(s)
        # k_ld = 0.634 + 0.183*1 = 0.817
        assert r.correction_factors.k_ld == pytest.approx(0.817, rel=1e-3)


class TestFormulasNTC2018:
    def test_tabella(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_ntc2018

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=200, diameter_mm=100)
        r = converti_ntc2018(s)
        assert r.correction_factors.k_ld == pytest.approx(1.0)


class TestFormulasEN13791:
    def test_tabella(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_en13791

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=100, diameter_mm=100)
        r = converti_en13791(s)
        assert r.correction_factors.k_ld == pytest.approx(0.85)


class TestFormulasGiacchetti:
    def test_regressione(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_giacchetti

        s = CoreSample(sample_id="C1", f_core_mpa=25.0, length_mm=100, diameter_mm=100)
        r = converti_giacchetti(s)
        # k_ld = 0.650 + 0.175*1 = 0.825
        assert r.correction_factors.k_ld == pytest.approx(0.825, rel=1e-3)


class TestFormulasCustom:
    def test_moltiplicatore(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_custom

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        r = converti_custom(s, mode="moltiplicatore", multiplier=0.90)
        assert r.correction_factors.k_ld == pytest.approx(0.90)

    def test_parametrica(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_custom

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        r = converti_custom(s, mode="parametrica", template_params={"a": 0.7, "b": 0.15})
        # k_ld = 0.7 + 0.15*1.0 = 0.85
        assert r.correction_factors.k_ld == pytest.approx(0.85)

    def test_espressione(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_custom

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        r = converti_custom(s, mode="espressione", expression="f_core * 0.85")
        assert r.f_is_mpa == pytest.approx(25.0 * 0.85)

    def test_espressione_errore(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_custom

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        with pytest.raises(ValueError, match="Errore nell'espressione"):
            converti_custom(s, mode="espressione", expression="import os")

    def test_mode_invalido(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_custom

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        with pytest.raises(ValueError, match="mode custom non valido"):
            converti_custom(s, mode="xyz")


class TestConvertiTutti:
    def test_tutte_formulazioni(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import STANDARD_FORMULATIONS, converti_tutti

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        results = converti_tutti(s)
        assert len(results) == len(STANDARD_FORMULATIONS)
        for name, r in results.items():
            assert r.formulation == name
            assert r.f_is_mpa > 0

    def test_override_per_formula(self):
        from src.codes.carote.core_sample import CoreSample
        from src.codes.carote.formulas import converti_tutti

        s = CoreSample(sample_id="C1", f_core_mpa=25.0)
        results = converti_tutti(s, overrides_per_formula={"BS1881": {"k_ld": 0.99}})
        # Override k_ld per BS1881
        bs = results["BS1881"]
        assert bs.correction_factors.overrides.get("k_ld") == 0.99


# ===================================================================
# 3. Statistics (15 test)
# ===================================================================


class TestStatisticalSummary:
    def test_summary_base(self):
        from src.codes.carote.statistics import calcola_summary

        s = calcola_summary(_F_CORE)
        assert s.n == 8
        assert s.mean == pytest.approx(23.7375, abs=0.01)
        assert s.std > 0
        assert s.cov > 0

    def test_summary_singolo(self):
        from src.codes.carote.statistics import calcola_summary

        s = calcola_summary([25.0])
        assert s.n == 1
        assert s.std == 0.0

    def test_summary_vuoto(self):
        from src.codes.carote.statistics import calcola_summary

        with pytest.raises(ValueError):
            calcola_summary([])


class TestNTC2018Stats:
    def test_lc2(self):
        from src.codes.carote.statistics import analisi_ntc2018

        r = analisi_ntc2018(_F_CORE, "LC2")
        # f_ck,is = mean * (1 - 1.64*CoV)
        assert r.lc == "LC2"
        assert r.k == 1.64
        assert r.f_ck_is > 0
        assert r.f_ck_is < r.f_m

    def test_lc1(self):
        from src.codes.carote.statistics import analisi_ntc2018

        r1 = analisi_ntc2018(_F_CORE, "LC1")
        r2 = analisi_ntc2018(_F_CORE, "LC2")
        # Stesso k per NTC2018 (cambia solo per FC successivo)
        assert r1.f_ck_is == pytest.approx(r2.f_ck_is)


class TestEN13791:
    def test_metodo_b_n8(self):
        from src.codes.carote.statistics import analisi_en13791_b

        r = analisi_en13791_b(_F_CORE)
        assert r is not None
        assert r.method == "B"
        # k(8) = 1.90
        assert r.k == pytest.approx(1.90)
        assert r.f_ck_is > 0

    def test_metodo_a_insufficiente(self):
        from src.codes.carote.statistics import analisi_en13791_a

        r = analisi_en13791_a(_F_CORE)  # n=8 < 15
        assert r is None

    def test_metodo_a_sufficiente(self):
        from src.codes.carote.statistics import analisi_en13791_a

        # 16 valori
        vals = _F_CORE * 2
        r = analisi_en13791_a(vals)
        assert r is not None
        assert r.method == "A"
        assert r.k == pytest.approx(1.48)

    def test_metodo_b_n_sotto_3(self):
        from src.codes.carote.statistics import analisi_en13791_b

        r = analisi_en13791_b([25.0, 24.0])  # n=2 < 3
        assert r is None


class TestOutliers:
    def test_grubbs_no_outlier(self):
        from src.codes.carote.statistics import test_grubbs

        results = test_grubbs(_F_CORE)
        outliers = [r for r in results if r.is_outlier]
        # Dataset omogeneo, nessun outlier atteso
        assert len(outliers) == 0

    def test_grubbs_con_outlier(self):
        from src.codes.carote.statistics import test_grubbs

        vals = list(_F_CORE) + [50.0]  # valore estremo
        results = test_grubbs(vals)
        outliers = [r for r in results if r.is_outlier]
        assert len(outliers) >= 1
        assert any(o.value == 50.0 for o in outliers)

    def test_chauvenet_no_outlier(self):
        from src.codes.carote.statistics import test_chauvenet

        results = test_chauvenet(_F_CORE)
        outliers = [r for r in results if r.is_outlier]
        assert len(outliers) == 0

    def test_grubbs_pochi_campioni(self):
        from src.codes.carote.statistics import test_grubbs

        assert test_grubbs([25.0, 24.0]) == []


class TestClassificazione:
    def test_c20_25(self):
        from src.codes.carote.statistics import classifica_calcestruzzo

        assert classifica_calcestruzzo(22.0) == "C20/25"

    def test_c25_30(self):
        from src.codes.carote.statistics import classifica_calcestruzzo

        assert classifica_calcestruzzo(25.0) == "C25/30"

    def test_sotto_minimo(self):
        from src.codes.carote.statistics import classifica_calcestruzzo

        result = classifica_calcestruzzo(5.0)
        assert result.startswith("<")


class TestAnalisiCompleta:
    def test_pipeline(self):
        from src.codes.carote.statistics import analisi_statistica_completa

        result = analisi_statistica_completa(_F_CORE)
        assert result.summary.n == 8
        assert "LC2" in result.ntc2018
        assert result.en13791_b is not None
        assert result.classification == "C20/25"


# ===================================================================
# 4. DerivedParams (7 test)
# ===================================================================


class TestDerivedParams:
    def test_fck_25(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        d = calcola_parametri_derivati(25.0)
        assert d.f_cm_is_mpa == pytest.approx(33.0)
        assert d.E_cm_mpa == pytest.approx(31476, rel=0.01)
        assert d.f_ctm_mpa == pytest.approx(2.565, rel=0.01)

    def test_rck(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        d = calcola_parametri_derivati(25.0)
        assert d.Rck_mpa == pytest.approx(25.0 / 0.83, rel=0.01)

    def test_sigma_c_adm_positiva(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        d = calcola_parametri_derivati(25.0)
        assert d.sigma_c_adm_kgcm2 > 0

    def test_frattili_trazione(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        d = calcola_parametri_derivati(25.0)
        assert d.f_ctk_005_mpa == pytest.approx(0.70 * d.f_ctm_mpa)
        assert d.f_ctk_095_mpa == pytest.approx(1.30 * d.f_ctm_mpa)

    def test_passaggi_non_vuoti(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        d = calcola_parametri_derivati(20.0)
        assert len(d.passaggi_calcolo) > 0

    def test_to_dict(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        d = calcola_parametri_derivati(25.0)
        dd = d.to_dict()
        assert "f_ck_is_mpa" in dd
        assert "E_cm_mpa" in dd

    def test_fck_negativo(self):
        from src.codes.carote.derived_params import calcola_parametri_derivati

        with pytest.raises(ValueError):
            calcola_parametri_derivati(-5.0)


# ===================================================================
# 5. Analysis (5 test)
# ===================================================================


class TestAnalysis:
    def test_pipeline_completa(self):
        from src.codes.carote.analysis import analizza_carote

        samples = _make_samples()
        result = analizza_carote(samples)
        assert len(result.conversions) > 0
        assert len(result.statistics) > 0
        assert result.best_estimate is not None
        assert result.timestamp != ""

    def test_subset_formulazioni(self):
        from src.codes.carote.analysis import analizza_carote

        samples = _make_samples()
        result = analizza_carote(samples, formulations=["NTC2018", "BS1881"])
        assert set(result.conversions.keys()) == {"NTC2018", "BS1881"}

    def test_custom_config(self):
        from src.codes.carote.analysis import analizza_carote

        samples = _make_samples()
        result = analizza_carote(
            samples,
            formulations=["NTC2018", "CUSTOM"],
            custom_config={"mode": "moltiplicatore", "multiplier": 0.90},
        )
        assert "CUSTOM" in result.conversions

    def test_to_dict(self):
        from src.codes.carote.analysis import analizza_carote

        samples = _make_samples()
        result = analizza_carote(samples, formulations=["NTC2018"])
        d = result.to_dict()
        assert "formulations" in d
        assert "NTC2018" in d["formulations"]

    def test_empty(self):
        from src.codes.carote.analysis import analizza_carote

        result = analizza_carote([])
        assert result.best_estimate is None
        assert len(result.conversions) == 0


# ===================================================================
# 6. Integration (4 test)
# ===================================================================


class TestIntegration:
    def test_applica_fc(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.integration import applica_fc_a_risultato

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        adj = applica_fc_a_risultato(analysis, lc="LC2")
        assert adj.f_ck_adjusted > 0
        assert adj.f_ck_adjusted <= adj.f_ck_original

    def test_applica_fc_lc1(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.integration import applica_fc_a_risultato

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        adj1 = applica_fc_a_risultato(analysis, lc="LC1")
        adj2 = applica_fc_a_risultato(analysis, lc="LC3")
        # LC1 (FC=1.35) riduce di piu' di LC3 (FC=1.0)
        assert adj1.f_ck_adjusted < adj2.f_ck_adjusted

    def test_registra_materiale(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.integration import registra_materiale_in_situ

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])

        # Mock repo
        class MockRepo:
            def __init__(self):
                self.materials = []
            def add(self, mat):
                self.materials.append(mat)

        repo = MockRepo()
        mat = registra_materiale_in_situ(analysis, repo, lc="LC2")
        assert mat.famiglia == "calcestruzzo"
        assert mat.f_ck > 0
        assert "in situ" in mat.note.lower() or "carote" in mat.note.lower()
        assert len(repo.materials) == 1

    def test_formulazione_mancante(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.integration import applica_fc_a_risultato

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        with pytest.raises(ValueError, match="non presente"):
            applica_fc_a_risultato(analysis, formulation="BS1881")


# ===================================================================
# 7. Report/Export (3 test)
# ===================================================================


class TestReport:
    def test_html_non_vuoto(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.report import genera_report_html_carote

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        html = genera_report_html_carote(analysis)
        assert len(html) > 100
        assert "<html" in html
        assert "NTC2018" in html

    def test_json_export(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.report import esporta_json_carote

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            esporta_json_carote(analysis, path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert "formulations" in data
        finally:
            os.unlink(path)

    def test_csv_export(self):
        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.report import esporta_csv_carote

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            rows = esporta_csv_carote(analysis, path)
            assert rows == 8  # 8 carote, 1 formulazione
        finally:
            os.unlink(path)


# ===================================================================
# 8. Plots (3 test)
# ===================================================================


class TestPlots:
    def test_istogramma(self):
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.figure import Figure

        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.plots import grafico_istogramma_gaussiana

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        fig = grafico_istogramma_gaussiana(analysis, "NTC2018")
        assert isinstance(fig, Figure)

    def test_scatter(self):
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.figure import Figure

        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.plots import grafico_scatter_conversione

        samples = _make_samples()
        analysis = analizza_carote(samples, formulations=["NTC2018"])
        fig = grafico_scatter_conversione(analysis, "NTC2018")
        assert isinstance(fig, Figure)

    def test_boxplot(self):
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.figure import Figure

        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.plots import grafico_boxplot_comparativo

        samples = _make_samples()
        analysis = analizza_carote(samples)
        fig = grafico_boxplot_comparativo(analysis)
        assert isinstance(fig, Figure)

    def test_barre_fck(self):
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.figure import Figure

        from src.codes.carote.analysis import analizza_carote
        from src.codes.carote.plots import grafico_barre_fck

        samples = _make_samples()
        analysis = analizza_carote(samples)
        fig = grafico_barre_fck(analysis)
        assert isinstance(fig, Figure)


# ===================================================================
# 9. Widget (2 test)
# ===================================================================


class TestWidget:
    def test_import_senza_qt(self):
        """Il modulo deve essere importabile anche senza Qt."""
        import src.codes.carote.plots  # noqa: F401

    def test_canvas_import(self):
        """carote_canvas.py deve essere importabile (salta istanza senza Qt)."""
        try:
            import src.gui.widgets.carote_canvas as mod

            assert hasattr(mod, "_QT_AVAILABLE")
        except ImportError:
            pytest.skip("Qt non disponibile")


# ===================================================================
# 10. Package (1 test)
# ===================================================================


class TestPackage:
    def test_init_import(self):
        from src.codes.carote import (
            FORMULATIONS,
            CoreSample,
        )

        assert len(FORMULATIONS) >= 10
        assert CoreSample is not None
