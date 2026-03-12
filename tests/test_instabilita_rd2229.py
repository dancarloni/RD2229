"""Test per la verifica di stabilità TA — RD 2229/39.

Verifica il coefficiente ω, la riduzione σ_c_adm per sezioni snelle,
e il flusso completo di verifica a carico di punta.
"""

import math

import pytest

from src.methods.rd2229.instabilita import (
    EsitoStabilita,
    InputStabilita,
    omega_ca,
    sigma_c_adm_ridotta,
    verifica_stabilita_ta,
)


class TestOmegaCA:
    """Test coefficiente ω per c.a."""

    def test_lambda_basso(self) -> None:
        """λ ≤ 50 → ω = 1.0."""
        assert omega_ca(0) == 1.0
        assert omega_ca(30) == 1.0
        assert omega_ca(50) == 1.0

    def test_lambda_70(self) -> None:
        assert omega_ca(70) == pytest.approx(1.08)

    def test_lambda_85(self) -> None:
        assert omega_ca(85) == pytest.approx(1.32)

    def test_lambda_100(self) -> None:
        assert omega_ca(100) == pytest.approx(1.62)

    def test_lambda_120(self) -> None:
        assert omega_ca(120) == pytest.approx(2.28)

    def test_lambda_140(self) -> None:
        assert omega_ca(140) == pytest.approx(3.0)

    def test_lambda_oltre_140(self) -> None:
        assert omega_ca(150) == 10.0
        assert omega_ca(200) == 10.0

    def test_interpolazione_60(self) -> None:
        """λ=60 → metà tra 50 e 70 → ω = 1.0 + 0.08*0.5 = 1.04."""
        assert omega_ca(60) == pytest.approx(1.04)

    def test_monotona_crescente(self) -> None:
        """ω deve crescere con λ."""
        valori = [omega_ca(lam) for lam in range(0, 141, 5)]
        for i in range(1, len(valori)):
            assert valori[i] >= valori[i - 1]


class TestSigmaCAdmRidotta:
    """Test riduzione σ_c_adm per sezioni snelle."""

    def test_sezione_grande(self) -> None:
        """Dimensione minima ≥ 25 cm → σ_r = 0.7·σ_adm."""
        result = sigma_c_adm_ridotta(60.0, 30.0, 50.0)
        assert result == pytest.approx(0.7 * 60.0)

    def test_sezione_piccola(self) -> None:
        """Dimensione minima = 20 cm → riduzione aggiuntiva."""
        result = sigma_c_adm_ridotta(60.0, 20.0, 40.0)
        expected = 0.7 * 60.0 * (1.0 - 0.03 * (25.0 - 20.0))
        assert result == pytest.approx(expected)

    def test_sezione_molto_piccola(self) -> None:
        """Dimensione minima = 15 cm → riduzione maggiore."""
        result = sigma_c_adm_ridotta(60.0, 15.0, 40.0)
        expected = 0.7 * 60.0 * (1.0 - 0.03 * (25.0 - 15.0))
        assert result == pytest.approx(expected)
        assert result < sigma_c_adm_ridotta(60.0, 20.0, 40.0)

    def test_sezione_25cm(self) -> None:
        """Dimensione esattamente 25 cm → nessuna riduzione extra."""
        result = sigma_c_adm_ridotta(60.0, 25.0, 40.0)
        assert result == pytest.approx(0.7 * 60.0)


class TestVerificaStabilitaTA:
    """Test del flusso completo di verifica a carico di punta."""

    def _input_pilastro(
        self, Nr: float = -50000.0, Mr: float = 0.0, L: float = 300.0
    ) -> InputStabilita:
        """Pilastro 30×30 cm, L=300 cm."""
        B, H = 30.0, 30.0
        A_sez = B * H
        I = B * H**3 / 12.0
        A_s = 12.0  # cm² armatura
        n = 15.0
        A_ci = A_sez + n * A_s
        r = math.sqrt(I / A_sez)
        return InputStabilita(
            Nr=Nr,
            Mr=Mr,
            B=B,
            H=H,
            A_sez=A_sez,
            I_yp=I,
            I_zp=I,
            A_ci=A_ci,
            r_yp=r,
            r_zp=r,
            A_ft=A_s,
            sigma_c_adm=60.0,
            sigma_s_adm=1200.0,
            E_c=300000.0,
            n=n,
            L=L,
            beta_y=1.0,
            beta_z=1.0,
        )

    def test_asta_tesa(self) -> None:
        """Nr ≥ 0 → non compressa, verifica non necessaria."""
        inp = self._input_pilastro(Nr=1000.0)
        ris = verifica_stabilita_ta(inp)
        assert ris.esito == EsitoStabilita.NON_COMPRESSA
        assert ris.verifica_soddisfatta is True

    def test_compressione_semplice_bassa(self) -> None:
        """Pilastro corto con bassa compressione → verifica OK."""
        inp = self._input_pilastro(Nr=-10000.0, L=200.0)
        ris = verifica_stabilita_ta(inp)
        assert ris.lambda_max > 0
        assert ris.omega >= 1.0
        assert ris.Pcr > 0
        assert ris.esito == EsitoStabilita.VERIFICATA

    def test_compressione_semplice_alta(self) -> None:
        """Pilastro snello con compressione molto alta → verifica NON OK."""
        inp = self._input_pilastro(Nr=-500000.0, L=800.0)
        ris = verifica_stabilita_ta(inp)
        assert (
            ris.esito == EsitoStabilita.NON_VERIFICATA
            or ris.esito == EsitoStabilita.SNELLEZZA_ECCESSIVA
        )

    def test_snellezza_calcolo(self) -> None:
        """Verifica calcolo snellezza."""
        inp = self._input_pilastro(Nr=-10000.0, L=300.0)
        ris = verifica_stabilita_ta(inp)
        r = inp.r_yp
        expected_lambda = 300.0 / r
        assert ris.lambda_y == pytest.approx(expected_lambda, rel=0.01)

    def test_carico_critico(self) -> None:
        """Verifica carico critico Euleriano."""
        inp = self._input_pilastro(Nr=-10000.0, L=300.0)
        ris = verifica_stabilita_ta(inp)
        E_rid = 0.4 * inp.E_c
        expected_Pcr = math.pi**2 * E_rid * inp.I_yp / (300.0**2)
        assert ris.Pcr == pytest.approx(expected_Pcr, rel=0.01)

    def test_pressoflessione_tre_verifiche(self) -> None:
        """Con Mr ≠ 0, devono esserci le 3 verifiche."""
        inp = self._input_pilastro(Nr=-30000.0, Mr=200000.0, L=300.0)
        ris = verifica_stabilita_ta(inp)
        assert ris.alpha_M > 1.0
        # Le 3 verifiche devono avere tensioni calcolate
        assert ris.sigma_c_1 > 0
        assert ris.sigma_c_2 > 0
        assert ris.sigma_c_3 > 0

    def test_beta_influence(self) -> None:
        """beta > 1 (mensola) aumenta la snellezza."""
        inp1 = self._input_pilastro(Nr=-30000.0, L=300.0)
        inp1.beta_y = 1.0
        ris1 = verifica_stabilita_ta(inp1)

        inp2 = self._input_pilastro(Nr=-30000.0, L=300.0)
        inp2.beta_y = 2.0
        ris2 = verifica_stabilita_ta(inp2)

        assert ris2.lambda_y > ris1.lambda_y

    def test_omega_tabella_noti(self) -> None:
        """Verifica che i valori noti della tabella ω siano corretti."""
        punti = [(50, 1.0), (70, 1.08), (85, 1.32), (100, 1.62), (120, 2.28), (140, 3.0)]
        for lam, omega_atteso in punti:
            assert omega_ca(lam) == pytest.approx(omega_atteso), f"ω({lam}) errato"

    def test_to_dict(self) -> None:
        inp = self._input_pilastro(Nr=-30000.0, Mr=100000.0)
        ris = verifica_stabilita_ta(inp)
        d = ris.to_dict()
        assert "esito" in d
        assert "omega" in d
        assert "lambda_max" in d
        assert "passaggi" in d
        assert len(d["passaggi"]) > 0

    def test_passaggi_non_vuoti(self) -> None:
        inp = self._input_pilastro(Nr=-30000.0)
        ris = verifica_stabilita_ta(inp)
        assert len(ris.passaggi) >= 5
