"""Test per elementi secondari — normative storiche (DM96, RD2229).

Verifica le funzionalita implementate in G.4:
  - DM96: forza sismica F_h = C * beta * W, drift h/300
  - RD2229: stabilita TA (omega * N / A), SLE NOT_APPLICABLE
  - Dispatcher: routing corretto per norma_attiva
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# DM96 — Modelli
# ---------------------------------------------------------------------------
from src.codes.dm96.secondary_elements.models import (
    COEFFICIENTE_SISMICO_C,
    SecondaryElementSpecDM96,
)


class TestDM96Models:
    """Test per SecondaryElementSpecDM96 e coefficienti."""

    def test_coefficienti_sismici_zone(self):
        assert COEFFICIENTE_SISMICO_C[1] == 0.10
        assert COEFFICIENTE_SISMICO_C[2] == 0.07
        assert COEFFICIENTE_SISMICO_C[3] == 0.04

    def test_beta_piano_terra(self):
        spec = SecondaryElementSpecDM96(piano=1, n_piani=3)
        beta = spec.calcola_beta_piano()
        assert beta == pytest.approx(1.0 + 0.5 * (1 / 3), abs=0.001)

    def test_beta_ultimo_piano(self):
        spec = SecondaryElementSpecDM96(piano=3, n_piani=3)
        beta = spec.calcola_beta_piano()
        assert beta == pytest.approx(1.5, abs=0.001)

    def test_beta_override(self):
        spec = SecondaryElementSpecDM96(piano=1, n_piani=3, beta_piano=2.0)
        assert spec.calcola_beta_piano() == 2.0

    def test_validazione_ok(self):
        spec = SecondaryElementSpecDM96(
            element_type="tramezzo", W_kN=5.0, zona_sismica=2
        )
        assert spec.validate() == []

    def test_validazione_errori(self):
        spec = SecondaryElementSpecDM96(
            element_type="", W_kN=-1.0, zona_sismica=5
        )
        errs = spec.validate()
        assert len(errs) == 3
        assert any("element_type" in e for e in errs)
        assert any("W_kN" in e for e in errs)
        assert any("zona_sismica" in e for e in errs)


# ---------------------------------------------------------------------------
# DM96 — Checks SLU
# ---------------------------------------------------------------------------

from src.codes.dm96.secondary_elements.checks import (
    check_sle_dm96,
    check_slu_dm96,
)


class TestDM96CheckSLU:
    """Test per verifica SLU forza sismica DM96."""

    def test_forza_base_zona2(self):
        """F_h = C(0.07) * beta(1.5) * W(10) = 1.05 kN per ultimo piano 3/3."""
        result = check_slu_dm96({
            "W_a": 10.0,
            "zona_sismica": 2,
            "piano": 3,
            "n_piani": 3,
        })
        assert result["esito"] == "OK"
        assert result["F_h_kN"] == pytest.approx(0.07 * 1.5 * 10.0, abs=0.01)
        assert result["C"] == 0.07

    def test_forza_zona1(self):
        """Zona 1 piu severa."""
        result = check_slu_dm96({
            "W_a": 10.0,
            "zona_sismica": 1,
            "piano": 2,
            "n_piani": 4,
        })
        C = 0.10
        beta = 1.0 + 0.5 * (2 / 4)
        assert result["F_h_kN"] == pytest.approx(C * beta * 10.0, abs=0.01)

    def test_verifica_ok_con_resistenza(self):
        result = check_slu_dm96({
            "W_a": 10.0,
            "zona_sismica": 3,
            "piano": 1,
            "n_piani": 2,
            "F_Rd": 5.0,
        })
        assert result["ok"] is True
        assert result["utilisation"] < 1.0

    def test_verifica_non_ok(self):
        result = check_slu_dm96({
            "W_a": 100.0,
            "zona_sismica": 1,
            "piano": 5,
            "n_piani": 5,
            "F_Rd": 1.0,
        })
        assert result["esito"] == "NON OK"
        assert result["ok"] is False

    def test_senza_resistenza(self):
        result = check_slu_dm96({"W_a": 5.0, "zona_sismica": 2})
        assert result["ok"] is True
        assert "F_h_kN" in result
        assert any("solo calcolo" in d for d in result["decision_log"])

    def test_contract_fields(self):
        result = check_slu_dm96({"W_a": 5.0})
        assert "esito" in result
        assert "decision_log" in result
        assert "norm_references" in result
        assert "trace" in result
        assert "run_id" in result["trace"]


# ---------------------------------------------------------------------------
# DM96 — Checks SLE
# ---------------------------------------------------------------------------

class TestDM96CheckSLE:
    """Test per verifica SLE drift DM96."""

    def test_drift_ok(self):
        result = check_sle_dm96({
            "drift": {"source": "GLOBAL", "value": 0.002, "limit": 0.00333}
        })
        assert result["ok"] is True
        assert result["utilisation"] < 1.0

    def test_drift_non_ok(self):
        result = check_sle_dm96({
            "drift": {"source": "GLOBAL", "value": 0.005, "limit": 0.00333}
        })
        assert result["esito"] == "NON OK"
        assert result["ok"] is False

    def test_drift_default_limit_h300(self):
        """Il limite di default deve essere h/300 = 0.00333."""
        result = check_sle_dm96({
            "drift": {"source": "GLOBAL", "value": 0.003}
        })
        assert result["drift_limit"] == pytest.approx(0.00333, abs=0.001)
        assert result["ok"] is True

    def test_drift_estimated_low_confidence(self):
        result = check_sle_dm96({
            "drift": {"source": "ESTIMATED", "value": 0.001}
        })
        assert result.get("confidence") == "LOW"

    def test_drift_non_fornito(self):
        result = check_sle_dm96({"drift": {}})
        assert result["ok"] is True
        assert any("non fornito" in d for d in result["decision_log"])


# ---------------------------------------------------------------------------
# RD2229 — Checks SLU (Stabilita TA)
# ---------------------------------------------------------------------------

from src.codes.rd2229.secondary_elements.checks import (
    check_sle_rd2229,
    check_slu_rd2229,
    check_stabilita_ta,
)


class TestRD2229CheckSLU:
    """Test per verifica stabilita TA — RD 2229/39."""

    def test_compressione_verificata(self):
        """Elemento con lambda=60, omega~1.05, sigma_c < sigma_c_adm."""
        result = check_stabilita_ta({
            "N_kg": 5000,
            "A_cm2": 200,
            "sigma_c_adm": 60,
            "lambda_snellezza": 60,
        })
        assert result["ok"] is True
        assert result["esito"] == "OK"
        assert result["omega"] > 1.0

    def test_compressione_non_verificata(self):
        """Elemento molto caricato con omega alto."""
        result = check_stabilita_ta({
            "N_kg": 50000,
            "A_cm2": 100,
            "sigma_c_adm": 40,
            "lambda_snellezza": 120,
        })
        assert result["ok"] is False
        assert result["esito"] == "NON OK"

    def test_snellezza_eccessiva(self):
        """Lambda > 140 deve rifiutare."""
        result = check_stabilita_ta({
            "N_kg": 1000,
            "A_cm2": 100,
            "sigma_c_adm": 60,
            "lambda_snellezza": 150,
        })
        assert result["esito"] == "NON OK"
        assert any("snellezza eccessiva" in d for d in result["decision_log"])

    def test_non_compresso(self):
        """N <= 0: non serve verifica stabilita."""
        result = check_stabilita_ta({
            "N_kg": 0,
            "A_cm2": 100,
            "sigma_c_adm": 60,
        })
        assert result["esito"] == "NOT_APPLICABLE"
        assert result["ok"] is True

    def test_lambda_calcolata_da_h_e_imin(self):
        """Lambda calcolata da h/i_min quando non fornita direttamente."""
        result = check_stabilita_ta({
            "N_kg": 3000,
            "A_cm2": 150,
            "sigma_c_adm": 50,
            "h_cm": 300,
            "i_min_cm": 5,  # lambda = 60
        })
        assert result["lambda"] == pytest.approx(60.0, abs=0.1)
        assert result["omega"] > 1.0

    def test_lambda_zero_senza_dati(self):
        """Senza h e i_min, lambda=0, omega=1.0."""
        result = check_stabilita_ta({
            "N_kg": 1000,
            "A_cm2": 100,
            "sigma_c_adm": 60,
        })
        assert result["omega"] == 1.0
        assert result["lambda"] == 0.0

    def test_dati_insufficienti(self):
        result = check_stabilita_ta({
            "N_kg": 1000,
            "A_cm2": 0,
            "sigma_c_adm": 60,
        })
        assert result["esito"] == "ERROR"

    def test_alias_check_slu_rd2229(self):
        """check_slu_rd2229 e un alias di check_stabilita_ta."""
        result = check_slu_rd2229({
            "N_kg": 1000,
            "A_cm2": 100,
            "sigma_c_adm": 60,
            "lambda_snellezza": 50,
        })
        assert result["ok"] is True
        assert result["omega"] == 1.0

    def test_contract_fields(self):
        result = check_stabilita_ta({
            "N_kg": 1000, "A_cm2": 100, "sigma_c_adm": 60,
        })
        assert "esito" in result
        assert "decision_log" in result
        assert "norm_references" in result
        assert "trace" in result
        assert any("RD 2229" in ref for ref in result["norm_references"])


# ---------------------------------------------------------------------------
# RD2229 — Checks SLE (NOT_APPLICABLE)
# ---------------------------------------------------------------------------

class TestRD2229CheckSLE:
    """Test per verifica SLE RD2229 — sempre NOT_APPLICABLE."""

    def test_sle_not_applicable(self):
        result = check_sle_rd2229({})
        assert result["esito"] == "NOT_APPLICABLE"
        assert result["ok"] is True
        assert any("pre-sismica" in d for d in result["decision_log"])


# ---------------------------------------------------------------------------
# Dispatcher — Routing multi-norma
# ---------------------------------------------------------------------------

from verifications.secondary_elements import dispatcher


class DummyProjectModel:
    def __init__(self, norma: str) -> None:
        self.norma_attiva = norma


class TestDispatcherRouting:
    """Test per routing dispatcher verso normative diverse."""

    def test_ntc2018_slu(self):
        inp = {"W_a": 10, "S_a": 0.3, "gamma_a": 1.0, "q_a": 2.0}
        result = dispatcher.run(inp, DummyProjectModel("NTC2018"), "SLU")
        assert result["esito"] == "OK"
        assert "F_a_kN" in result

    def test_dm96_slu(self):
        inp = {"W_a": 10, "zona_sismica": 2, "piano": 1, "n_piani": 2}
        result = dispatcher.run(inp, DummyProjectModel("DM96"), "SLU")
        assert result["esito"] == "OK"
        assert "F_h_kN" in result

    def test_dm92_routes_to_dm96(self):
        """DM92 usa lo stesso modulo di DM96."""
        inp = {"W_a": 10, "zona_sismica": 1, "piano": 1, "n_piani": 1}
        result = dispatcher.run(inp, DummyProjectModel("DM92"), "SLU")
        assert "F_h_kN" in result

    def test_rd2229_slu(self):
        inp = {"N_kg": 1000, "A_cm2": 100, "sigma_c_adm": 60}
        result = dispatcher.run(inp, DummyProjectModel("RD2229"), "SLU")
        assert result["esito"] in ("OK", "NOT_APPLICABLE")

    def test_rd2229_sle_not_applicable(self):
        result = dispatcher.run({}, DummyProjectModel("RD2229"), "SLE")
        assert result["esito"] == "NOT_APPLICABLE"

    def test_dm96_sle(self):
        inp = {"drift": {"source": "GLOBAL", "value": 0.002, "limit": 0.003}}
        result = dispatcher.run(inp, DummyProjectModel("DM96"), "SLE")
        assert result["ok"] is True

    def test_gating_influence_on_global_model(self):
        """Il gating per influence_on_global_model funziona per tutte le norme."""
        for norm in ("NTC2018", "DM96", "RD2229"):
            inp = {"influence_on_global_model": True}
            result = dispatcher.run(inp, DummyProjectModel(norm), "SLU")
            assert result["esito"] == "NOT_APPLICABLE", f"Gating fallito per {norm}"

    def test_contract_trace_for_all_norms(self):
        """Tutti i risultati hanno trace.run_id."""
        for norm in ("NTC2018", "DM96", "RD2229"):
            inp = {"W_a": 5, "N_kg": 500, "A_cm2": 50, "sigma_c_adm": 60,
                   "zona_sismica": 2}
            result = dispatcher.run(inp, DummyProjectModel(norm), "SLU")
            assert "trace" in result
            assert "run_id" in result["trace"]
