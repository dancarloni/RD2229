"""Test verifiche connessioni acciaio (saldature e bullonature).

Verifica con casi noti e limiti normativi.
"""

import math

import pytest

from src.steel.connessioni import (
    A_GAMBO_BULLONE,
    A_RES_BULLONE,
    BETA_W,
    ClasseBullone,
    F_UB,
    F_YB,
    InputBullone,
    InputSaldatura,
    RisultatoBullone,
    RisultatoSaldatura,
    TipoCollegamentoBullonato,
    TipoSaldatura,
    verifica_bullone_ta,
    verifica_saldatura_ta,
)


# ═══════════════════════ SALDATURE ═══════════════════════

class TestCostantiSaldatura:
    def test_beta_w_fe430(self):
        assert BETA_W["Fe430"] == 0.85

    def test_beta_w_fe510(self):
        assert BETA_W["Fe510"] == 0.90

    def test_beta_w_s355(self):
        assert BETA_W["S355"] == 0.90


class TestSaldaturaFrontale:
    def test_cordone_frontale_verificato(self):
        """Cordone frontale a=0.5 cm, L=10 cm, N=5000 kg → verificato."""
        inp = InputSaldatura(
            tipo=TipoSaldatura.CORDONE_ANGOLO,
            a=0.5, L=10.0, n_cordoni=2,
            N=5000.0,
            tipo_acciaio="Fe430",
            sigma_adm_acciaio=1900.0,
        )
        res = verifica_saldatura_ta(inp)

        A_gola = 0.5 * 10.0 * 2  # = 10 cm²
        assert res.A_gola == pytest.approx(A_gola)

        sigma_adm_w = 0.85 * 1900  # = 1615
        assert res.sigma_adm_w == pytest.approx(sigma_adm_w)

        # σ⊥ = τ⊥ = N/(√2·A_gola) = 5000/(1.414·10) = 353.6
        sigma_perp = 5000 / (math.sqrt(2) * A_gola)
        assert res.sigma_perp == pytest.approx(sigma_perp, rel=0.01)

        assert res.verificato is True

    def test_cordone_frontale_non_verificato(self):
        """Cordone piccolo, carico grande → non verificato."""
        inp = InputSaldatura(
            tipo=TipoSaldatura.CORDONE_ANGOLO,
            a=0.3, L=3.0, n_cordoni=1,
            N=10000.0,
            tipo_acciaio="Fe430",
            sigma_adm_acciaio=1900.0,
        )
        res = verifica_saldatura_ta(inp)
        assert res.verificato is False
        assert res.sfruttamento > 1.0


class TestSaldaturaLaterale:
    def test_cordone_laterale_verificato(self):
        """Cordone laterale: V=3000 kg."""
        inp = InputSaldatura(
            tipo=TipoSaldatura.CORDONE_ANGOLO,
            a=0.5, L=15.0, n_cordoni=2,
            V=3000.0,
            tipo_acciaio="Fe430",
            sigma_adm_acciaio=1900.0,
        )
        res = verifica_saldatura_ta(inp)

        A_gola = 0.5 * 15.0 * 2  # = 15 cm²
        tau_par = 3000 / A_gola
        assert res.tau_par == pytest.approx(tau_par, rel=0.01)
        assert res.verificato is True


class TestSaldaturaCombinata:
    def test_cordone_combinato(self):
        """Cordone con N e V combinati."""
        inp = InputSaldatura(
            tipo=TipoSaldatura.CORDONE_ANGOLO,
            a=0.5, L=10.0, n_cordoni=2,
            N=3000.0, V=2000.0,
            tipo_acciaio="Fe430",
            sigma_adm_acciaio=1900.0,
        )
        res = verifica_saldatura_ta(inp)

        # σ_id = √(σ⊥² + τ⊥² + τ‖²)
        A_gola = 10.0
        sigma_perp = 3000 / (math.sqrt(2) * A_gola)
        tau_perp = sigma_perp  # stessa per cordone frontale
        tau_par = 2000 / A_gola
        sigma_id = math.sqrt(sigma_perp**2 + tau_perp**2 + tau_par**2)
        assert res.sigma_id == pytest.approx(sigma_id, rel=0.01)


class TestSaldaturaTestaTesta:
    def test_completa_penetrazione(self):
        """Saldatura a completa penetrazione: σ_adm = materiale base."""
        inp = InputSaldatura(
            tipo=TipoSaldatura.TESTA_TESTA,
            a=1.0, L=10.0,
            N=10000.0,
            tipo_acciaio="Fe430",
            sigma_adm_acciaio=1900.0,
        )
        res = verifica_saldatura_ta(inp)
        # Nessuna riduzione β_w
        assert res.sigma_adm_w == 1900.0
        assert res.sigma_id == pytest.approx(10000 / 10.0, rel=0.01)


class TestSaldaturaToDict:
    def test_to_dict(self):
        inp = InputSaldatura(
            tipo=TipoSaldatura.CORDONE_ANGOLO,
            a=0.5, L=10.0, N=5000.0,
        )
        res = verifica_saldatura_ta(inp)
        d = res.to_dict()
        assert "sigma_id" in d
        assert "verificato" in d
        assert "passaggi" in d


class TestSaldaturaAreaNulla:
    def test_gola_nulla(self):
        """a=0 → area nulla, non deve crashare."""
        inp = InputSaldatura(
            tipo=TipoSaldatura.CORDONE_ANGOLO,
            a=0.0, L=10.0, N=1000.0,
        )
        res = verifica_saldatura_ta(inp)
        assert res.A_gola == 0


# ═══════════════════════ BULLONATURE ═══════════════════════

class TestCostantiBulloni:
    def test_f_ub_8_8(self):
        assert F_UB["8.8"] == pytest.approx(8160, rel=0.01)

    def test_f_yb_8_8(self):
        assert F_YB["8.8"] == pytest.approx(6528, rel=0.01)

    def test_a_res_m20(self):
        assert A_RES_BULLONE[20] == pytest.approx(2.45, rel=0.01)

    def test_a_gambo_m20(self):
        assert A_GAMBO_BULLONE[20] == pytest.approx(3.142, rel=0.01)


class TestBulloneTaglio:
    def test_taglio_verificato(self):
        """M20 cl 8.8: taglio 3000 kg → verificato."""
        inp = InputBullone(
            diametro=20, classe="8.8",
            n_bulloni=4, n_piani_taglio=1,
            V=3000.0,
        )
        res = verifica_bullone_ta(inp)
        assert res.verifica_taglio is True
        assert res.F_v_Rd > 0

    def test_taglio_non_verificato(self):
        """Un bullone piccolo con carico alto → non verificato."""
        inp = InputBullone(
            diametro=12, classe="4.6",
            n_bulloni=1, n_piani_taglio=1,
            V=5000.0,
        )
        res = verifica_bullone_ta(inp)
        assert res.verifica_taglio is False


class TestBulloneTrazione:
    def test_trazione_verificata(self):
        """M20 cl 8.8: trazione 5000 kg → verificato."""
        inp = InputBullone(
            diametro=20, classe="8.8",
            n_bulloni=2,
            N=5000.0,
        )
        res = verifica_bullone_ta(inp)
        assert res.verifica_trazione is True
        assert res.F_t_Rd > 0


class TestBulloneInterazione:
    def test_interazione_verificata(self):
        """M20 cl 8.8 con taglio e trazione moderati."""
        inp = InputBullone(
            diametro=20, classe="8.8",
            n_bulloni=4, n_piani_taglio=1,
            V=2000.0, N=3000.0,
        )
        res = verifica_bullone_ta(inp)
        assert res.verifica_interazione is True
        assert res.sfruttamento_interazione < 1.0
        assert res.sfruttamento_interazione > 0

    def test_interazione_formula(self):
        """Verifica formula (V/V_Rd)² + (N/N_Rd)² ≤ 1."""
        inp = InputBullone(
            diametro=20, classe="8.8",
            n_bulloni=1, n_piani_taglio=1,
            V=2000.0, N=2000.0,
        )
        res = verifica_bullone_ta(inp)

        # Ricalcolo manuale
        tau_adm = F_UB["8.8"] / 3.0
        sigma_adm_b = 0.8 * F_YB["8.8"] / 1.5
        A_g = A_GAMBO_BULLONE[20]
        A_r = A_RES_BULLONE[20]

        F_v_1 = tau_adm * A_g
        F_t_1 = sigma_adm_b * A_r

        interazione = (2000 / F_v_1) ** 2 + (2000 / F_t_1) ** 2
        assert res.sfruttamento_interazione == pytest.approx(interazione, rel=0.01)


class TestBulloneRifollamento:
    def test_rifollamento(self):
        """Verifica rifollamento con dati lamiera."""
        inp = InputBullone(
            diametro=20, classe="8.8",
            n_bulloni=2, n_piani_taglio=1,
            V=5000.0,
            t=1.0,          # spessore lamiera
            e1=4.0,         # distanza dal bordo
            p1=6.0,         # interasse
            fu_lamiera=4400.0,  # f_u lamiera Fe430
        )
        res = verifica_bullone_ta(inp)
        assert res.F_b_Rd > 0
        assert res.sfruttamento_rifollamento >= 0


class TestBulloneToDict:
    def test_to_dict(self):
        inp = InputBullone(diametro=20, classe="8.8", V=3000.0)
        res = verifica_bullone_ta(inp)
        d = res.to_dict()
        assert "diametro" in d
        assert "classe" in d
        assert "verifica_globale" in d


class TestBulloneVerificaGlobale:
    def test_tutto_verificato(self):
        """Bullone ben dimensionato → verifica globale OK."""
        inp = InputBullone(
            diametro=24, classe="10.9",
            n_bulloni=4, n_piani_taglio=2,
            V=2000.0, N=1000.0,
        )
        res = verifica_bullone_ta(inp)
        assert res.verifica_globale is True

    def test_passaggi_non_vuoti(self):
        inp = InputBullone(diametro=20, classe="8.8", V=3000.0)
        res = verifica_bullone_ta(inp)
        assert len(res.passaggi) > 0
        assert any("ESITO" in p for p in res.passaggi)


class TestClasseBulloneEnum:
    def test_classi(self):
        assert ClasseBullone.CL_8_8.value == "8.8"
        assert ClasseBullone.CL_10_9.value == "10.9"
