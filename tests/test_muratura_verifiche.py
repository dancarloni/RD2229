"""Test verifiche muratura — compressione, taglio, snellezza, spanciamento.

Verifica con casi noti e limiti normativi NTC2018 §4.5.
"""

import math

import pytest

from src.methods.muratura.verifiche import (
    CriterioTaglio,
    InputCompressione,
    InputSpanciamento,
    InputTaglio,
    NormaMuratura,
    TipoMuratura,
    interpola_phi,
    taglio_diagonale,
    taglio_pressoflessione,
    taglio_scorrimento,
    verifica_compressione,
    verifica_spanciamento,
    verifica_taglio_piano,
)


# ═══════════════════ Coefficiente Φ ═══════════════════

class TestInterpolaPhi:
    def test_phi_lambda_zero_e_zero(self):
        """λ=0, e/t=0 → Φ=1.0."""
        assert interpola_phi(0, 0) == pytest.approx(1.0)

    def test_phi_lambda_zero_e_033(self):
        """λ=0, e/t=0.33 → Φ=0.13."""
        assert interpola_phi(0, 0.33) == pytest.approx(0.13)

    def test_phi_lambda_20_e_zero(self):
        """λ=20, e/t=0 → Φ=0.78."""
        assert interpola_phi(20, 0) == pytest.approx(0.78)

    def test_phi_lambda_27_e_033(self):
        """λ=27, e/t=0.33 → Φ=0.03 (minimo tabella)."""
        assert interpola_phi(27, 0.33) == pytest.approx(0.03)

    def test_phi_interpolazione_bilineare(self):
        """λ=12.5, e/t=0.075 → interpolazione tra λ=10/15 e e/t=0.05/0.10."""
        phi = interpola_phi(12.5, 0.075)
        # Media tra i 4 valori vicini
        assert 0.6 < phi < 0.9

    def test_phi_clamp_alto(self):
        """λ=30 → clamped a 27."""
        phi = interpola_phi(30, 0)
        assert phi == pytest.approx(interpola_phi(27, 0))

    def test_phi_clamp_et_alto(self):
        """e/t=0.5 → clamped a 0.33."""
        phi = interpola_phi(0, 0.5)
        assert phi == pytest.approx(interpola_phi(0, 0.33))

    def test_phi_monotona_lambda(self):
        """Φ deve diminuire con λ crescente (a e/t fissato)."""
        phis = [interpola_phi(lam, 0.1) for lam in range(0, 28, 5)]
        for i in range(len(phis) - 1):
            assert phis[i] >= phis[i + 1]

    def test_phi_monotona_et(self):
        """Φ deve diminuire con e/t crescente (a λ fissato)."""
        ets = [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.33]
        phis = [interpola_phi(15, et) for et in ets]
        for i in range(len(phis) - 1):
            assert phis[i] >= phis[i + 1]

    def test_phi_sempre_positivo(self):
        """Φ deve essere sempre > 0."""
        for lam in range(0, 28):
            for et_10 in range(0, 34):
                et = et_10 / 100.0
                assert interpola_phi(lam, et) >= 0


# ═══════════════════ Compressione ═══════════════════

class TestCompressione:
    def test_compressione_centrata_verificata(self):
        """Parete 100×30, h=300, fd=30 kg/cm², N=50000 kg."""
        inp = InputCompressione(
            L=100, t=30, h=300,
            N=50000, fd=30.0, gamma_M=2.0,
        )
        res = verifica_compressione(inp)
        assert res.A == pytest.approx(3000)
        assert res.sigma == pytest.approx(50000 / 3000, rel=0.01)
        assert res.e == pytest.approx(0)  # compressione centrata
        assert res.verificato is True

    def test_compressione_eccentrica(self):
        """Parete con momento → eccentricità."""
        inp = InputCompressione(
            L=100, t=30, h=300,
            N=50000, M=500000,  # e = M/N = 10 cm, e/t = 10/30 = 0.333
            fd=30.0, gamma_M=2.0,
        )
        res = verifica_compressione(inp)
        assert res.e == pytest.approx(10.0)
        assert res.e_t == pytest.approx(10.0 / 30.0, rel=0.01)
        # Con e/t ≈ 0.33, Φ è molto basso → N_Rd ridotto
        assert res.phi < 0.5

    def test_compressione_snellezza_alta(self):
        """Parete snella: h/t > 20."""
        inp = InputCompressione(
            L=100, t=15, h=500,  # λ = 500/15 = 33.3
            N=10000, fd=30.0, gamma_M=2.0,
        )
        res = verifica_compressione(inp)
        assert res.lam > 27
        assert res.verificato is False  # λ > 27

    def test_compressione_snellezza_bassa(self):
        """Parete tozza: h/t < 5."""
        inp = InputCompressione(
            L=200, t=50, h=200,  # λ = 200/50 = 4
            N=100000, fd=40.0, gamma_M=2.0,
        )
        res = verifica_compressione(inp)
        assert res.lam < 5
        assert res.phi == pytest.approx(1.0, abs=0.01)  # Φ ≈ 1.0 per λ basso

    def test_compressione_to_dict(self):
        inp = InputCompressione(L=100, t=30, h=300, N=50000, fd=30.0)
        res = verifica_compressione(inp)
        d = res.to_dict()
        assert "phi" in d
        assert "lambda" in d
        assert "verificato" in d

    def test_compressione_rho(self):
        """Vincolo ρ=0.75 → h_eff ridotto."""
        inp = InputCompressione(
            L=100, t=30, h=400, rho=0.75,
            N=50000, fd=30.0,
        )
        res = verifica_compressione(inp)
        assert res.h_eff == pytest.approx(300)
        assert res.lam == pytest.approx(10)


# ═══════════════════ Taglio diagonale ═══════════════════

class TestTaglioDiagonale:
    def test_diagonale_verificato(self):
        """Pannello con compressione e taglio moderati."""
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=3000, N=50000,
            tau_0=1.0, gamma_M=2.0,
        )
        res = taglio_diagonale(inp)
        assert res.criterio == "diagonale"
        assert res.V_Rd > 0
        assert res.sigma_0 == pytest.approx(50000 / 6000, rel=0.01)

    def test_diagonale_senza_compressione(self):
        """Senza compressione, V_Rd dipende solo da τ₀."""
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=1000, N=0,
            tau_0=1.0, gamma_M=2.0,
        )
        res = taglio_diagonale(inp)
        # V_t = L×t×(1.5×τ₀d/b)×√1 = L×t×τ₀d×1.5/b
        tau_0d = 0.5  # 1.0/2.0
        b = min(300/200, 1.5)  # h/L = 1.5
        V_expected = 200 * 30 * (1.5 * tau_0d / b) * 1.0
        assert res.V_Rd == pytest.approx(V_expected, rel=0.01)

    def test_diagonale_compressione_aumenta_resistenza(self):
        """La compressione aumenta V_Rd (effetto σ₀)."""
        inp_base = InputTaglio(L=200, t=30, h=300, V=1000, N=0, tau_0=1.0, gamma_M=2.0)
        inp_comp = InputTaglio(L=200, t=30, h=300, V=1000, N=100000, tau_0=1.0, gamma_M=2.0)

        res_base = taglio_diagonale(inp_base)
        res_comp = taglio_diagonale(inp_comp)
        assert res_comp.V_Rd > res_base.V_Rd

    def test_diagonale_passaggi(self):
        inp = InputTaglio(L=200, t=30, h=300, V=3000, N=50000, tau_0=1.0, gamma_M=2.0)
        res = taglio_diagonale(inp)
        assert len(res.passaggi) > 0
        assert any("Turnšek" in p for p in res.passaggi)


# ═══════════════════ Taglio scorrimento ═══════════════════

class TestTaglioScorrimento:
    def test_scorrimento_verificato(self):
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=3000, N=50000,
            fvk0=0.2, mu=0.4, gamma_M=2.0,
        )
        res = taglio_scorrimento(inp)
        assert res.criterio == "scorrimento"

        # fvk = 0.2 + 0.4 × (50000/6000) = 0.2 + 3.33 = 3.53
        sigma_n = 50000 / 6000
        fvk = 0.2 + 0.4 * sigma_n
        fvd = fvk / 2.0
        V_Rd = fvd * 200 * 30
        assert res.V_Rd == pytest.approx(V_Rd, rel=0.01)

    def test_scorrimento_senza_compressione(self):
        """Senza compressione, solo coesione contribuisce."""
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=500, N=0,
            fvk0=0.2, mu=0.4, gamma_M=2.0,
        )
        res = taglio_scorrimento(inp)
        fvd = 0.2 / 2.0
        V_Rd = fvd * 200 * 30
        assert res.V_Rd == pytest.approx(V_Rd, rel=0.01)


# ═══════════════════ Taglio pressoflessione ═══════════════════

class TestTaglioPressoflessione:
    def test_pressoflessione(self):
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=5000, N=100000,
            fd=40.0, psi=1.0, gamma_M=2.0,
        )
        res = taglio_pressoflessione(inp)
        assert res.criterio == "pressoflessione"

        # V_pf = (L²×t×σ₀)/(2h₀)×(1 - σ₀/(0.85fd))
        sigma_0 = 100000 / 6000
        h0 = 1.0 * 300
        V_expected = (200**2 * 30 * sigma_0) / (2 * h0) * (1 - sigma_0 / (0.85 * 40))
        assert res.V_Rd == pytest.approx(V_expected, rel=0.01)

    def test_pressoflessione_sigma_alta(self):
        """Se σ₀ ≈ 0.85fd → V_pf ≈ 0."""
        inp = InputTaglio(
            L=100, t=30, h=300,
            V=1000, N=100000,
            fd=39.2,  # σ₀ = 100000/3000 = 33.3, 0.85×39.2 = 33.3
            psi=1.0,
        )
        res = taglio_pressoflessione(inp)
        assert res.V_Rd < 10  # quasi zero


# ═══════════════════ Verifica taglio combinata ═══════════════════

class TestVerificaTaglioPiano:
    def test_tutti_criteri(self):
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=5000, N=50000,
            tau_0=1.0, fvk0=0.2, mu=0.4, fd=40.0,
            gamma_M=2.0, psi=1.0,
        )
        risultati = verifica_taglio_piano(inp)
        assert len(risultati) == 3
        # Ordinati per V_Rd crescente
        for i in range(len(risultati) - 1):
            assert risultati[i].V_Rd <= risultati[i + 1].V_Rd

    def test_solo_diagonale(self):
        """Se mancano fvk0 e fd, solo criterio diagonale."""
        inp = InputTaglio(
            L=200, t=30, h=300,
            V=3000, N=50000,
            tau_0=1.0, gamma_M=2.0,
        )
        risultati = verifica_taglio_piano(inp)
        assert len(risultati) == 1
        assert risultati[0].criterio == "diagonale"


# ═══════════════════ Spanciamento ═══════════════════

class TestSpanciamento:
    def test_parete_ok(self):
        """Parete con λ < 20."""
        inp = InputSpanciamento(h=300, t=30, lambda_max=20)
        res = verifica_spanciamento(inp)
        assert res.lam == pytest.approx(10)
        assert res.verificato is True

    def test_parete_non_ok(self):
        """Parete snella con λ > 20."""
        inp = InputSpanciamento(h=600, t=15, lambda_max=20)
        res = verifica_spanciamento(inp)
        assert res.lam == pytest.approx(40)
        assert res.verificato is False

    def test_rho_riduce_snellezza(self):
        """ρ < 1 riduce h_eff e quindi λ."""
        inp = InputSpanciamento(h=400, t=20, rho=0.75, lambda_max=20)
        res = verifica_spanciamento(inp)
        assert res.h_eff == pytest.approx(300)
        assert res.lam == pytest.approx(15)
        assert res.verificato is True

    def test_limite_sismico(self):
        """Zona sismica: λ_max = 12."""
        inp = InputSpanciamento(h=300, t=20, lambda_max=12)
        res = verifica_spanciamento(inp)
        assert res.lam == pytest.approx(15)
        assert res.verificato is False

    def test_to_dict(self):
        inp = InputSpanciamento(h=300, t=30)
        res = verifica_spanciamento(inp)
        d = res.to_dict()
        assert "lambda" in d
        assert "verificato" in d

    def test_passaggi(self):
        inp = InputSpanciamento(h=300, t=30)
        res = verifica_spanciamento(inp)
        assert len(res.passaggi) > 0
        assert any("spanciamento" in p.lower() for p in res.passaggi)


# ═══════════════════ Enum ═══════════════════

class TestEnum:
    def test_tipo_muratura(self):
        assert TipoMuratura.MATTONI_PIENI.value == "mattoni_pieni"
        assert TipoMuratura.TUFO.value == "tufo"

    def test_norma_muratura(self):
        assert NormaMuratura.NTC2018.value == "NTC2018"
        assert NormaMuratura.DM87.value == "DM87"
