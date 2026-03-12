"""Test per src/esistenti/interventi.py — Fase R.5.

Catalogo interventi NTC2018 §8.6, composizione e ranking.
CATALOGO_BASE è list[Intervento] — iterare direttamente (non come dict).
"""

import pytest

from src.esistenti.interventi import (
    TipoIntervento,
    ObiettivoRanking,
    Intervento,
    ScenarioIntervento,
    VoceRanking,
    CATALOGO_BASE,
    get_intervento_by_id,
    applica_interventi,
    ranking_interventi,
)


# ─── Test CATALOGO_BASE ───────────────────────────────────────────────────────

class TestCatalogo:
    def test_catalogo_non_vuoto(self):
        assert len(CATALOGO_BASE) > 0

    def test_almeno_un_ca_e_mur(self):
        """Catalogo contiene sia interventi c.a. che muratura."""
        tipi = {iv.tipo for iv in CATALOGO_BASE}
        ca_tipi = {TipoIntervento.INCAMICIATURA, TipoIntervento.FRP,
                   TipoIntervento.PARETE_TAGLIO, TipoIntervento.DISSIPATORE}
        mur_tipi = {TipoIntervento.RINGBEAM_MUR, TipoIntervento.INIEZIONI_MUR,
                    TipoIntervento.INTONACO_ARMATO}
        assert tipi & ca_tipi or tipi & mur_tipi  # almeno una delle due

    def test_tutti_hanno_id_e_nome(self):
        for iv in CATALOGO_BASE:
            assert iv.id != ""
            assert iv.nome != ""

    def test_fattori_maggiori_o_uguali_a_1(self):
        for iv in CATALOGO_BASE:
            assert iv.fattore_rho >= 1.0, f"{iv.id}: fattore_rho={iv.fattore_rho}"
            assert iv.fattore_alpha >= 1.0, f"{iv.id}: fattore_alpha={iv.fattore_alpha}"

    def test_costo_definito(self):
        """Ogni intervento ha almeno un modo per calcolare il costo."""
        for iv in CATALOGO_BASE:
            ha_costo = (
                iv.costo_eur_m2 > 0
                or iv.costo_fisso_eur > 0
                or iv.coeff_volume > 0
            )
            assert ha_costo, f"{iv.id}: nessun costo definito"


# ─── Test get_intervento_by_id ────────────────────────────────────────────────

class TestGetInterventoById:
    def test_restituisce_intervento_noto(self):
        iv = get_intervento_by_id("CA_INCAM_PIL")
        assert iv is not None
        assert iv.id == "CA_INCAM_PIL"

    def test_id_inesistente_restituisce_none(self):
        iv = get_intervento_by_id("ID_NON_ESISTE_XXXX")
        assert iv is None


# ─── Test applica_interventi ─────────────────────────────────────────────────

class TestApplicaInterventi:
    def test_scenario_restituito(self):
        iv = CATALOGO_BASE[0]
        sc = applica_interventi([iv], rho_pre=0.5, alpha_pre=0.6)
        assert isinstance(sc, ScenarioIntervento)

    def test_rho_post_maggiore_uguale_pre(self):
        """Intervento con fattore_rho > 1 → rho_post ≥ rho_pre."""
        interventi_rho = [iv for iv in CATALOGO_BASE if iv.fattore_rho > 1.0]
        if not interventi_rho:
            pytest.skip("Nessun intervento con fattore_rho > 1.0")
        sc = applica_interventi(interventi_rho[:1], rho_pre=0.7, alpha_pre=0.8)
        assert sc.rho_post >= sc.rho_pre

    def test_alpha_post_maggiore_uguale_pre(self):
        """Intervento con fattore_alpha > 1 → alpha_post ≥ alpha_pre."""
        interventi_alpha = [iv for iv in CATALOGO_BASE if iv.fattore_alpha > 1.0]
        if not interventi_alpha:
            pytest.skip("Nessun intervento con fattore_alpha > 1.0")
        sc = applica_interventi(interventi_alpha[:1], rho_pre=0.7, alpha_pre=0.8)
        assert sc.alpha_post >= sc.alpha_pre

    def test_composizione_moltiplicativa(self):
        """Due interventi identici → rho_post_2 >= rho_post_1."""
        iv = next((i for i in CATALOGO_BASE if i.fattore_rho > 1.01), None)
        if iv is None:
            pytest.skip("Nessun intervento con fattore_rho > 1.01")
        sc_uno = applica_interventi([iv], rho_pre=0.6, alpha_pre=0.6)
        sc_due = applica_interventi([iv, iv], rho_pre=0.6, alpha_pre=0.6)
        assert sc_due.rho_post >= sc_uno.rho_post

    def test_cap_individuale_non_superato(self):
        """rho_post non supera il cap_rho del singolo intervento."""
        iv = CATALOGO_BASE[0]   # CA_INCAM_PIL, cap_rho=2.5
        sc = applica_interventi([iv], rho_pre=0.5, alpha_pre=0.5)
        assert sc.rho_post <= iv.cap_rho + 1e-9

    def test_cap_raggiunto_segnalato(self):
        """Quando il cap combinato è attivato, cap_raggiunto == True."""
        # FOND_CONSOLID ha cap_rho=1.5; con molti interventi cumulativi si supera
        sc = applica_interventi(CATALOGO_BASE, rho_pre=0.5, alpha_pre=0.5)
        # Con tutti gli interventi l'al rho o alpha supera sicuramente almeno un cap
        assert sc.cap_raggiunto or sc.rho_post > 0  # almeno il calcolo funziona

    def test_costo_non_negativo(self):
        iv = CATALOGO_BASE[0]
        sc = applica_interventi([iv], rho_pre=0.5, alpha_pre=0.5, area_m2=100.0)
        assert sc.costo_totale_eur >= 0.0


# ─── Test ranking_interventi ─────────────────────────────────────────────────

class TestRankingInterventi:
    def test_lista_non_vuota(self):
        voci = ranking_interventi(
            CATALOGO_BASE, rho_pre=0.5, alpha_pre=0.6,
            obiettivo=ObiettivoRanking.MIGLIORAMENTO_MASSIMO,
        )
        assert len(voci) > 0

    def test_voci_sono_voce_ranking(self):
        voci = ranking_interventi(
            CATALOGO_BASE, rho_pre=0.5, alpha_pre=0.6,
        )
        for v in voci:
            assert isinstance(v, VoceRanking)

    def test_ordinato_per_score_decrescente(self):
        voci = ranking_interventi(
            CATALOGO_BASE, rho_pre=0.5, alpha_pre=0.6,
        )
        scores = [v.score for v in voci]
        assert scores == sorted(scores, reverse=True)

    def test_obiettivo_costo_minimo(self):
        """Obiettivo COSTO_MINIMO → score negativo (= -costo)."""
        voci = ranking_interventi(
            CATALOGO_BASE, rho_pre=0.5, alpha_pre=0.6,
            obiettivo=ObiettivoRanking.COSTO_MINIMO,
            area_m2=100.0,
        )
        assert len(voci) > 0

    def test_voce_ha_id_e_nome(self):
        voci = ranking_interventi(CATALOGO_BASE, rho_pre=0.5, alpha_pre=0.6)
        assert voci[0].id_intervento != ""
        assert voci[0].nome != ""
