"""Test per src/esistenti/vulnerabilita_mur.py — Fase R.3.

Parete tipo muratura piena: t=50 cm, L=300 cm, h=300 cm.
"""

import pytest

from src.esistenti.vulnerabilita_mur import (
    ConfigVulnerabilitaMur,
    DegradoPreset,
    IndiceVulnerabilitaMur,
    PareteVulnerabile,
    RisultatoParete,
    analisi_lv2_parete,
    analisi_vulnerabilita_mur,
    lv1_letteratura,
    lv1_ntc2018,
    lv1_opcm3274,
    scorrimento_parete,
)
from src.methods.muratura.cinematica import ParametriSismici, RisultatoCinematica

# ─── Fixture ─────────────────────────────────────────────────────────────────


@pytest.fixture
def parete_typ():
    """Parete muratura piena tipica.
    N_sommita = 100 kg/m (carico solaio per metro lineare).
    N_tot = peso_proprio + N_sommita*L/100 (conversione m → cm).
    """
    return PareteVulnerabile(
        id_parete="M1",
        t=50.0,  # cm — spessore
        L=300.0,  # cm — lunghezza in pianta
        h=300.0,  # cm — altezza
        fvd0=2.0,  # kg/cm² — coesione a zero compressione
        fd=20.0,  # kg/cm² — resistenza a compressione muratura
        mu=0.4,  # coefficiente attrito Mohr-Coulomb
        E=20_000.0,  # kg/cm²
        G=8_000.0,  # kg/cm²
        N_sommita=100.0,  # kg/m lineare
    )


@pytest.fixture
def sismica_std():
    """ParametriSismici: campo a_g (non ag)."""
    return ParametriSismici(a_g=0.15, S=1.2, FC=1.35, q=2.0)


@pytest.fixture
def config_std():
    return ConfigVulnerabilitaMur()


@pytest.fixture
def config_degrado_alto():
    return ConfigVulnerabilitaMur(degrado=DegradoPreset.ALTO)


# ─── Test lv1_ntc2018 ────────────────────────────────────────────────────────


class TestLV1NTC2018:
    def test_alpha_positivo(self, parete_typ, sismica_std, config_std):
        alpha, passi = lv1_ntc2018([parete_typ], sismica_std, config_std)
        assert alpha > 0.0

    def test_passi_non_vuoti(self, parete_typ, sismica_std, config_std):
        _, passi = lv1_ntc2018([parete_typ], sismica_std, config_std)
        assert len(passi) > 0

    def test_alpha_decresce_con_ag_alto(self, parete_typ, config_std):
        """Accelerazione più alta → indice alfa LV1 più basso."""
        ag_basso = ParametriSismici(a_g=0.05, S=1.0, FC=1.35, q=2.0)
        ag_alto = ParametriSismici(a_g=0.35, S=1.3, FC=1.35, q=2.0)
        a1, _ = lv1_ntc2018([parete_typ], ag_basso, config_std)
        a2, _ = lv1_ntc2018([parete_typ], ag_alto, config_std)
        assert a1 > a2


# ─── Test lv1_opcm3274 ───────────────────────────────────────────────────────


class TestLV1OPCM3274:
    def test_is_positivo(self, parete_typ, sismica_std, config_std):
        IS, passi = lv1_opcm3274([parete_typ], sismica_std, config_std)
        assert IS > 0.0

    def test_passi_non_vuoti(self, parete_typ, sismica_std, config_std):
        _, passi = lv1_opcm3274([parete_typ], sismica_std, config_std)
        assert len(passi) > 0


# ─── Test lv1_letteratura ────────────────────────────────────────────────────


class TestLV1Letteratura:
    def test_alpha_positivo(self, parete_typ, sismica_std, config_std):
        alpha, passi = lv1_letteratura([parete_typ], sismica_std, config_std)
        assert alpha > 0.0

    def test_formula_turnsek_cacovic(self, parete_typ, sismica_std, config_std):
        """Verifica che la formula Turnšek-Čačovič sia citata nei passaggi."""
        _, passi = lv1_letteratura([parete_typ], sismica_std, config_std)
        assert any("Turnšek" in p or "Cacovic" in p or "letteratura" in p.lower() for p in passi)


# ─── Test scorrimento_parete ─────────────────────────────────────────────────


class TestScorrimentoParete:
    def test_restituisce_cinematica(self, parete_typ, sismica_std, config_std):
        ris = scorrimento_parete(parete_typ, sismica_std, config_std)
        assert isinstance(ris, RisultatoCinematica)

    def test_alpha0_positivo(self, parete_typ, sismica_std, config_std):
        ris = scorrimento_parete(parete_typ, sismica_std, config_std)
        assert ris.alpha_0 > 0.0

    def test_alpha0_formula_mohr_coulomb(self, parete_typ, sismica_std, config_std):
        """α₀ = (fvd0·A + μ·N_tot) / N_tot deve corrispondere al valore calcolato."""
        ris = scorrimento_parete(parete_typ, sismica_std, config_std)
        A = parete_typ.t * parete_typ.L
        N = parete_typ.N_tot
        alpha0_atteso = (parete_typ.fvd0 * A + parete_typ.mu * N) / N
        assert abs(ris.alpha_0 - alpha0_atteso) < 1e-4

    def test_degradato_riduce_alpha(self, parete_typ, sismica_std):
        """Degrado alto deve ridurre la capacità rispetto a nessun degrado."""
        cfg_no = ConfigVulnerabilitaMur(degrado=DegradoPreset.NESSUNO)
        cfg_si = ConfigVulnerabilitaMur(degrado=DegradoPreset.ALTO)
        ris_no = scorrimento_parete(parete_typ, sismica_std, cfg_no)
        ris_si = scorrimento_parete(parete_typ, sismica_std, cfg_si)
        assert ris_si.alpha_0 <= ris_no.alpha_0


# ─── Test analisi_lv2_parete ─────────────────────────────────────────────────


class TestAnalisiLV2:
    def test_restituisce_risultato(self, parete_typ, sismica_std, config_std):
        ris = analisi_lv2_parete(parete_typ, sismica_std, config_std)
        assert isinstance(ris, RisultatoParete)

    def test_alpha_min_positivo(self, parete_typ, sismica_std, config_std):
        ris = analisi_lv2_parete(parete_typ, sismica_std, config_std)
        assert ris.alpha_min > 0.0

    def test_meccanismo_critico_presente(self, parete_typ, sismica_std, config_std):
        ris = analisi_lv2_parete(parete_typ, sismica_std, config_std)
        assert ris.meccanismo_critico != ""

    def test_alpha_min_le_alpha_medio(self, parete_typ, sismica_std, config_std):
        ris = analisi_lv2_parete(parete_typ, sismica_std, config_std)
        assert ris.alpha_min <= ris.alpha_medio + 1e-9


# ─── Test analisi_vulnerabilita_mur ──────────────────────────────────────────


class TestAnalisiVulnerabilitaMur:
    def test_indice_e_lista(self, parete_typ, sismica_std, config_std):
        indice, risultati = analisi_vulnerabilita_mur([parete_typ], sismica_std, config_std)
        assert isinstance(indice, IndiceVulnerabilitaMur)
        assert len(risultati) == 1

    def test_contatori_coerenti(self, parete_typ, sismica_std, config_std):
        indice, _ = analisi_vulnerabilita_mur([parete_typ], sismica_std, config_std)
        totale = indice.n_verificate + indice.n_critiche + indice.n_vulnerabili
        assert totale == 1

    def test_ranking_ordinato(self, config_std):
        """Ranking ordinato per alpha_min crescente."""
        sismica = ParametriSismici(a_g=0.15, S=1.2, FC=1.35, q=2.0)
        pareti = [
            PareteVulnerabile(
                id_parete="M_A",
                t=50.0,
                L=200.0,
                h=300.0,
                fvd0=1.0,
                fd=12.0,
                mu=0.4,
                E=15_000.0,
                G=6_000.0,
            ),
            PareteVulnerabile(
                id_parete="M_B",
                t=60.0,
                L=400.0,
                h=250.0,
                fvd0=3.0,
                fd=30.0,
                mu=0.5,
                E=25_000.0,
                G=10_000.0,
            ),
        ]
        indice, _ = analisi_vulnerabilita_mur(pareti, sismica, config_std)
        if len(indice.ranking) >= 2:
            assert indice.ranking[0]["alpha_min"] <= indice.ranking[1]["alpha_min"]
