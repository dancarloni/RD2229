"""Test verifiche acciaio TA (Tensioni Ammissibili).

Verifica flessione, taglio, pressoflessione, instabilità per profili acciaio.
"""

import math
from pathlib import Path

import pytest

from src.steel.sagomario import SagomarioAcciaio
from src.steel.verifiche_ta import (
    BETA_VINCOLI,
    E_ACCIAIO,
    G_ACCIAIO,
    SIGMA_ADM_TA,
    InputVerificaAcciaio,
    TipoAcciaio,
    VincoloEstremita,
    omega_acciaio,
    seleziona_profilo_ottimale,
    verifica_profilo_ta,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "steel"


# ───────────────────────── Fixture ─────────────────────────


@pytest.fixture
def sagomario():
    s = SagomarioAcciaio()
    s.carica_tutti(DATA_DIR)
    return s


@pytest.fixture
def ipe200(sagomario):
    return sagomario.get("IPE 200")


@pytest.fixture
def hea200(sagomario):
    return sagomario.get("HEA 200")


# ───────────────────────── Costanti ─────────────────────────


class TestCostanti:
    def test_sigma_adm_fe430(self):
        assert SIGMA_ADM_TA["Fe430"] == 1900.0

    def test_sigma_adm_fe360(self):
        assert SIGMA_ADM_TA["Fe360"] == 1600.0

    def test_sigma_adm_fe510(self):
        assert SIGMA_ADM_TA["Fe510"] == 2400.0

    def test_equivalenza_s_fe(self):
        assert SIGMA_ADM_TA["S235"] == SIGMA_ADM_TA["Fe360"]
        assert SIGMA_ADM_TA["S275"] == SIGMA_ADM_TA["Fe430"]
        assert SIGMA_ADM_TA["S355"] == SIGMA_ADM_TA["Fe510"]

    def test_modulo_elastico(self):
        assert E_ACCIAIO == 2100000.0

    def test_modulo_taglio(self):
        assert G_ACCIAIO == 810000.0

    def test_beta_vincoli(self):
        assert BETA_VINCOLI["incastro-incastro"] == 0.5
        assert BETA_VINCOLI["cerniera-cerniera"] == 1.0
        assert BETA_VINCOLI["incastro-libero"] == 2.0


# ───────────────────────── Omega acciaio ─────────────────────────


class TestOmegaAcciaio:
    def test_omega_zero(self):
        assert omega_acciaio(0) == 1.0

    def test_omega_negativo(self):
        assert omega_acciaio(-10) == 1.0

    def test_omega_tabella_esatti(self):
        assert omega_acciaio(50) == pytest.approx(1.150)
        assert omega_acciaio(100) == pytest.approx(1.800)
        assert omega_acciaio(200) == pytest.approx(9.080)

    def test_omega_interpolazione(self):
        # λ = 75 → tra 70 (1.310) e 80 (1.430)
        w = omega_acciaio(75)
        assert w == pytest.approx(1.370, abs=0.001)

    def test_omega_oltre_200(self):
        assert omega_acciaio(250) == pytest.approx(9.080)

    def test_omega_crescente(self):
        """ω deve essere monotonamente crescente."""
        prev = 1.0
        for lam in range(0, 201, 5):
            w = omega_acciaio(lam)
            assert w >= prev
            prev = w


# ───────────────────────── Flessione semplice ─────────────────────────


class TestFlessioneSemplice:
    def test_flessione_verificata(self, ipe200):
        """IPE 200 Fe430: Mx = 300000 kg·cm → σ = 300000/194 = 1546 < 1900."""
        inp = InputVerificaAcciaio(profilo=ipe200, Mx=300000.0)
        res = verifica_profilo_ta(inp)
        assert res.sigma_Mx == pytest.approx(300000 / 194.0, rel=0.01)
        assert res.verifica_flessione is True
        assert res.verifica_globale is True

    def test_flessione_non_verificata(self, ipe200):
        """IPE 200 Fe430: Mx = 400000 kg·cm → σ = 400000/194 = 2062 > 1900."""
        inp = InputVerificaAcciaio(profilo=ipe200, Mx=400000.0)
        res = verifica_profilo_ta(inp)
        assert res.sigma_Mx > 1900.0
        assert res.verifica_flessione is False

    def test_flessione_asse_debole(self, ipe200):
        """Flessione asse debole: My = 50000 kg·cm."""
        inp = InputVerificaAcciaio(profilo=ipe200, My=50000.0)
        res = verifica_profilo_ta(inp)
        assert res.sigma_My == pytest.approx(50000 / 28.5, rel=0.01)


# ───────────────────────── Taglio ─────────────────────────


class TestTaglio:
    def test_taglio_semplice(self, ipe200):
        """Taglio Vy su IPE 200."""
        inp = InputVerificaAcciaio(profilo=ipe200, Vy=10000.0)
        res = verifica_profilo_ta(inp)
        A_anima = 20.0 * 0.56  # h * tw
        assert res.tau_Vy == pytest.approx(10000 / A_anima, rel=0.01)
        assert res.verifica_taglio is True

    def test_taglio_elevato(self, ipe200):
        """Taglio molto alto → non verificato."""
        tau_adm = 1900 / math.sqrt(3)
        A_anima = 20.0 * 0.56
        Vy_limite = tau_adm * A_anima
        inp = InputVerificaAcciaio(profilo=ipe200, Vy=Vy_limite * 1.5)
        res = verifica_profilo_ta(inp)
        assert res.verifica_taglio is False


# ───────────────────────── Pressoflessione ─────────────────────────


class TestPressoflessione:
    def test_pressoflessione_verificata(self, ipe200):
        """N + Mx combinati → σ_id = |N/A| + |Mx/Wx|."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            N=-5000.0,  # compressione
            Mx=200000.0,
        )
        res = verifica_profilo_ta(inp)
        sigma_N = 5000 / 28.5
        sigma_Mx = 200000 / 194.0
        assert res.sigma_id == pytest.approx(sigma_N + sigma_Mx, rel=0.01)
        assert res.verifica_pressoflessione is True

    def test_pressoflessione_biassiale(self, ipe200):
        """N + Mx + My combinati."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            N=-3000.0,
            Mx=100000.0,
            My=20000.0,
        )
        res = verifica_profilo_ta(inp)
        sigma_N = 3000 / 28.5
        sigma_Mx = 100000 / 194.0
        sigma_My = 20000 / 28.5
        expected = sigma_N + sigma_Mx + sigma_My
        assert res.sigma_id == pytest.approx(expected, rel=0.01)


# ───────────────────────── Instabilità ─────────────────────────


class TestInstabilita:
    def test_instabilita_colonna(self, ipe200):
        """IPE 200, L=400 cm, N=-50000 kg, cerniera-cerniera."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            N=-50000.0,
            L=400.0,
            vincolo="cerniera-cerniera",
        )
        res = verifica_profilo_ta(inp)
        # λ_x = 400/8.26 ≈ 48.4, λ_y = 400/2.24 ≈ 178.6
        assert res.lambda_x == pytest.approx(400 / 8.26, rel=0.01)
        assert res.lambda_y == pytest.approx(400 / 2.24, rel=0.01)
        assert res.omega > 1.0

    def test_instabilita_non_applicata_trazione(self, ipe200):
        """Trazione → instabilità non applicabile."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            N=10000.0,  # trazione
            L=400.0,
        )
        res = verifica_profilo_ta(inp)
        assert res.verifica_instabilita is True  # default, non applicato
        assert res.omega == 1.0

    def test_instabilita_incastro_incastro(self, ipe200):
        """Vincolo incastro-incastro: β=0.5 → snellezza dimezzata."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            N=-50000.0,
            L=400.0,
            vincolo="incastro-incastro",
        )
        res = verifica_profilo_ta(inp)
        assert res.lambda_x == pytest.approx(200 / 8.26, rel=0.01)
        assert res.lambda_y == pytest.approx(200 / 2.24, rel=0.01)

    def test_beta_override(self, ipe200):
        """Override β per singolo asse."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            N=-50000.0,
            L=400.0,
            vincolo="cerniera-cerniera",
            beta_y=0.7,
        )
        res = verifica_profilo_ta(inp)
        assert res.lambda_x == pytest.approx(400 / 8.26, rel=0.01)
        assert res.lambda_y == pytest.approx(0.7 * 400 / 2.24, rel=0.01)


# ───────────────────────── Verifica globale ─────────────────────────


class TestVerificaGlobale:
    def test_profilo_scarico(self, ipe200):
        """Profilo senza sollecitazioni → tutto verificato."""
        inp = InputVerificaAcciaio(profilo=ipe200)
        res = verifica_profilo_ta(inp)
        assert res.verifica_globale is True
        assert res.sfruttamento_sigma == 0.0

    def test_passaggi_non_vuoti(self, ipe200):
        inp = InputVerificaAcciaio(profilo=ipe200, Mx=100000.0)
        res = verifica_profilo_ta(inp)
        assert len(res.passaggi) > 0
        assert any("ESITO" in p for p in res.passaggi)

    def test_to_dict(self, ipe200):
        inp = InputVerificaAcciaio(profilo=ipe200, Mx=100000.0)
        res = verifica_profilo_ta(inp)
        d = res.to_dict()
        assert d["nome_profilo"] == "IPE 200"
        assert "sigma_adm" in d
        assert "passaggi" in d

    def test_sfruttamento(self, ipe200):
        """Sfruttamento coerente con σ_id/σ_adm."""
        inp = InputVerificaAcciaio(profilo=ipe200, Mx=200000.0)
        res = verifica_profilo_ta(inp)
        expected = res.sigma_id / res.sigma_adm
        assert res.sfruttamento_sigma == pytest.approx(expected, rel=0.01)

    def test_sigma_adm_override(self, ipe200):
        """Override tensione ammissibile."""
        inp = InputVerificaAcciaio(
            profilo=ipe200,
            Mx=100000.0,
            sigma_adm_override=1500.0,
        )
        res = verifica_profilo_ta(inp)
        assert res.sigma_adm == 1500.0


# ───────────────────────── Selezione profilo ottimale ─────────────────────────


class TestSelezioneOttimale:
    def test_seleziona_ipe_per_momento(self, sagomario):
        """Seleziona IPE per Mx = 300000 kg·cm, Fe430."""
        p = seleziona_profilo_ottimale("IPE", 300000.0, "Fe430", sagomario)
        assert p is not None
        Wx_min = 300000 / 1900.0  # ≈ 157.9 cm³
        assert p.Wx >= Wx_min

    def test_seleziona_hea(self, sagomario):
        """Seleziona HEA per Mx = 500000 kg·cm."""
        p = seleziona_profilo_ottimale("HEA", 500000.0, "Fe430", sagomario)
        assert p is not None
        assert p.famiglia == "HEA"
        assert p.Wx >= 500000 / 1900.0


# ───────────────────────── Enumerazioni ─────────────────────────


class TestEnum:
    def test_tipo_acciaio_valori(self):
        assert TipoAcciaio.Fe360.value == "Fe360"
        assert TipoAcciaio.S355.value == "S355"

    def test_vincolo_estremita(self):
        assert VincoloEstremita.INCASTRO_INCASTRO.value == "incastro-incastro"
        assert VincoloEstremita.INCASTRO_LIBERO.value == "incastro-libero"
