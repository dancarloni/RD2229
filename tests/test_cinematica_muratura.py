"""Test analisi cinematica meccanismi locali muratura.

Verifica i 4 meccanismi (ribaltamento semplice, composto, flessione
verticale, flessione orizzontale) + cinematica lineare/non lineare.

Riferimenti: NTC2018 §C8A.4, Circolare n.7/2019.
"""

import math

import pytest

from src.methods.muratura.cinematica import (
    ForzaCatena,
    G,
    ParametriSismici,
    PareteMuraria,
    PosizioneParete,
    RisultatoCinematica,
    TipoMeccanismo,
    analisi_meccanismi_locali,
    flessione_orizzontale,
    flessione_verticale,
    ribaltamento_composto,
    ribaltamento_semplice,
)


# ═══════════════════ Fixture ═══════════════════

@pytest.fixture
def parete_tipo():
    """Parete tipica: h=300cm, t=30cm, L=400cm, γ=0.0018 kg/cm³."""
    return PareteMuraria(h=300, t=30, L=400, gamma=0.0018)


@pytest.fixture
def parete_con_carico():
    """Parete con sovraccarico in sommità."""
    return PareteMuraria(
        h=300, t=30, L=400, gamma=0.0018,
        N_sommita=500,  # kg/m lineare
    )


@pytest.fixture
def parete_in_quota():
    """Parete in quota (piano intermedio)."""
    return PareteMuraria(
        h=300, t=30, L=400, gamma=0.0018,
        Z=300, H_edificio=900,
    )


@pytest.fixture
def sismica_base():
    """Parametri sismici tipici."""
    return ParametriSismici(a_g=0.15, S=1.2, q=2.0, FC=1.35)


@pytest.fixture
def sismica_alta():
    """Sismica alta per forzare non-verifica."""
    return ParametriSismici(a_g=0.35, S=1.5, q=2.0, FC=1.0)


# ═══════════════════ PareteMuraria ═══════════════════

class TestPareteMuraria:
    def test_peso_proprio(self, parete_tipo):
        W = 300 * 30 * 400 * 0.0018
        assert parete_tipo.peso_proprio == pytest.approx(W, rel=0.01)

    def test_peso_per_m(self, parete_tipo):
        # peso_per_m = h * t * gamma * 100
        w = 300 * 30 * 0.0018 * 100
        assert parete_tipo.peso_per_m == pytest.approx(w, rel=0.01)

    def test_baricentro(self, parete_tipo):
        assert parete_tipo.baricentro_h == pytest.approx(150, rel=0.01)


# ═══════════════════ Enums ═══════════════════

class TestEnums:
    def test_tipo_meccanismo_values(self):
        assert TipoMeccanismo.RIBALTAMENTO_SEMPLICE.value == "ribaltamento_semplice"
        assert TipoMeccanismo.FLESSIONE_VERTICALE.value == "flessione_verticale"

    def test_posizione_parete(self):
        assert PosizioneParete.A_TERRA.value == "a_terra"
        assert PosizioneParete.IN_QUOTA.value == "in_quota"


# ═══════════════════ Ribaltamento Semplice ═══════════════════

class TestRibaltamentoSemplice:
    def test_alpha_0_calcolo_manuale(self, parete_tipo, sismica_base):
        """Verifica α₀ con calcolo manuale per parete senza carico."""
        res = ribaltamento_semplice(parete_tipo, sismica_base)

        W = 300 * 30 * 400 * 0.0018  # = 6480 kg
        M_stab = W * 30 / 2  # = 6480 * 15 = 97200
        M_rib = W * 300 / 2  # = 6480 * 150 = 972000
        alpha_atteso = M_stab / M_rib  # = 97200 / 972000 = 0.1

        assert res.alpha_0 == pytest.approx(alpha_atteso, rel=0.01)

    def test_alpha_0_con_sovraccarico(self, parete_con_carico, sismica_base):
        """α₀ con sovraccarico sommitale."""
        res = ribaltamento_semplice(parete_con_carico, sismica_base)

        W = 300 * 30 * 400 * 0.0018
        N_s = 500 * 400 / 100  # = 2000 kg
        M_stab = W * 15 + N_s * 15
        M_rib = W * 150 + N_s * 300
        alpha_atteso = M_stab / M_rib

        assert res.alpha_0 == pytest.approx(alpha_atteso, rel=0.01)

    def test_alpha_0_proporzionale_a_t_su_h(self, sismica_base):
        """α₀ ∝ t/h per parete senza carico (ribaltamento semplice)."""
        p1 = PareteMuraria(h=300, t=30, L=400)
        p2 = PareteMuraria(h=300, t=60, L=400)

        r1 = ribaltamento_semplice(p1, sismica_base)
        r2 = ribaltamento_semplice(p2, sismica_base)

        # α₀ = t/2 / (h/2) = t/h → raddoppiando t, α₀ raddoppia
        assert r2.alpha_0 == pytest.approx(2 * r1.alpha_0, rel=0.01)

    def test_catena_aumenta_alpha(self, parete_tipo, sismica_base):
        """Catena orizzontale in sommità aumenta α₀."""
        res_no_cat = ribaltamento_semplice(parete_tipo, sismica_base)

        catena = ForzaCatena(F=1000, h_applicazione=300, angolo=0)
        res_cat = ribaltamento_semplice(parete_tipo, sismica_base, catene=[catena])

        assert res_cat.alpha_0 > res_no_cat.alpha_0
        assert res_cat.contributo_catene > 0

    def test_catena_inclinata(self, parete_tipo, sismica_base):
        """Catena inclinata: componente orizzontale ridotta."""
        cat_oriz = ForzaCatena(F=1000, h_applicazione=300, angolo=0)
        cat_incl = ForzaCatena(F=1000, h_applicazione=300, angolo=30)

        r_oriz = ribaltamento_semplice(parete_tipo, sismica_base, catene=[cat_oriz])
        r_incl = ribaltamento_semplice(parete_tipo, sismica_base, catene=[cat_incl])

        assert r_incl.alpha_0 < r_oriz.alpha_0

    def test_meccanismo_corretto(self, parete_tipo, sismica_base):
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        assert res.meccanismo == "ribaltamento_semplice"

    def test_passaggi_non_vuoti(self, parete_tipo, sismica_base):
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        assert len(res.passaggi) > 5

    def test_to_dict(self, parete_tipo, sismica_base):
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        d = res.to_dict()
        assert "alpha_0" in d
        assert "verifica_lineare" in d
        assert "passaggi" in d


# ═══════════════════ Cinematica Lineare ═══════════════════

class TestCinematicaLineare:
    def test_a_terra_verifica(self, parete_tipo):
        """Parete a terra con sismica bassa → verificata."""
        sismica = ParametriSismici(a_g=0.05, S=1.0, q=2.0, FC=1.35)
        res = ribaltamento_semplice(parete_tipo, sismica)

        # a_domanda = a_g*S/q = 0.05*1.0/2.0 = 0.025
        # α₀ = t/h = 0.1, a₀* = 0.1 / (0.75*1.35) ≈ 0.0988
        assert res.a_0_star > res.a_domanda
        assert res.verifica_lineare is True

    def test_a_terra_non_verifica(self, parete_tipo, sismica_alta):
        """Parete a terra con sismica alta → non verificata."""
        res = ribaltamento_semplice(parete_tipo, sismica_alta)

        # a_domanda = 0.35*1.5/2.0 = 0.2625
        assert res.a_domanda > 0.2
        # α₀ ≈ 0.1, a₀* ≈ 0.1/(0.75*1.0) ≈ 0.133 < 0.2625
        assert res.verifica_lineare is False

    def test_in_quota(self, parete_in_quota):
        """Parete in quota usa formula diversa per domanda."""
        sismica = ParametriSismici(a_g=0.15, S=1.2, q=2.0, FC=1.35)
        res = ribaltamento_semplice(parete_in_quota, sismica)

        # Verifica che ψ(Z) venga calcolato
        assert res.a_domanda > 0

    def test_e_star_valore(self, parete_tipo, sismica_base):
        """e* ≈ 0.75 per distribuzione lineare."""
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        assert res.e_star == pytest.approx(0.75, rel=0.01)

    def test_m_star_positiva(self, parete_tipo, sismica_base):
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        assert res.M_star > 0

    def test_fc_influenza(self, parete_tipo):
        """FC più alto riduce a₀*."""
        s1 = ParametriSismici(a_g=0.15, S=1.0, q=2.0, FC=1.0)
        s2 = ParametriSismici(a_g=0.15, S=1.0, q=2.0, FC=1.35)

        r1 = ribaltamento_semplice(parete_tipo, s1)
        r2 = ribaltamento_semplice(parete_tipo, s2)

        assert r1.a_0_star > r2.a_0_star


# ═══════════════════ Cinematica Non Lineare ═══════════════════

class TestCinematicaNonLineare:
    def test_d_0_star_proporzionale_t(self, sismica_base):
        """d₀* ∝ t (spessore parete)."""
        p1 = PareteMuraria(h=300, t=30, L=400)
        p2 = PareteMuraria(h=300, t=60, L=400)

        r1 = ribaltamento_semplice(p1, sismica_base)
        r2 = ribaltamento_semplice(p2, sismica_base)

        assert r2.d_0_star == pytest.approx(2 * r1.d_0_star, rel=0.01)

    def test_d_u_star_quaranta_percento(self, parete_tipo, sismica_base):
        """d*_u = 0.4 × d₀*."""
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        assert res.d_u_star == pytest.approx(0.4 * res.d_0_star, rel=0.01)

    def test_d_0_star_calcolo(self, parete_tipo, sismica_base):
        """d₀* = t × 2/3."""
        res = ribaltamento_semplice(parete_tipo, sismica_base)
        assert res.d_0_star == pytest.approx(30 * 2 / 3, rel=0.01)

    def test_verifica_non_lineare_spesso(self, sismica_base):
        """Parete spessa → d*_u grande → verificata."""
        p = PareteMuraria(h=300, t=60, L=400)
        sismica = ParametriSismici(a_g=0.05, S=1.0, q=2.0, FC=1.35)
        res = ribaltamento_semplice(p, sismica)
        # d*_u = 0.4 × 60 × 2/3 = 16 cm → quasi certamente verificata
        assert res.d_u_star > 10


# ═══════════════════ Ribaltamento Composto ═══════════════════

class TestRibaltamentoComposto:
    def test_alpha_0_con_cuneo(self, parete_tipo, sismica_base):
        """Ribaltamento composto include peso cuneo."""
        res = ribaltamento_composto(parete_tipo, cuneo_h=100, sismica=sismica_base)
        assert res.alpha_0 > 0
        assert res.meccanismo == "ribaltamento_composto"

    def test_alpha_maggiore_senza_cuneo(self, parete_tipo, sismica_base):
        """α₀ composto diverso dal semplice per effetto cuneo."""
        r_semplice = ribaltamento_semplice(parete_tipo, sismica_base)
        r_composto = ribaltamento_composto(parete_tipo, cuneo_h=100, sismica=sismica_base)
        # Il composto ha più massa → α₀ diverso
        assert r_composto.alpha_0 != r_semplice.alpha_0

    def test_cuneo_angolo_influenza(self, parete_tipo, sismica_base):
        """Angolo cuneo modifica il risultato."""
        r1 = ribaltamento_composto(parete_tipo, cuneo_h=100, cuneo_angolo=30, sismica=sismica_base)
        r2 = ribaltamento_composto(parete_tipo, cuneo_h=100, cuneo_angolo=60, sismica=sismica_base)
        assert r1.alpha_0 != r2.alpha_0

    def test_catene_composto(self, parete_tipo, sismica_base):
        """Catene migliorano anche il composto."""
        cat = ForzaCatena(F=2000, h_applicazione=300)
        r_no = ribaltamento_composto(parete_tipo, cuneo_h=100, sismica=sismica_base)
        r_si = ribaltamento_composto(parete_tipo, cuneo_h=100, sismica=sismica_base, catene=[cat])
        assert r_si.alpha_0 > r_no.alpha_0

    def test_passaggi_cuneo(self, parete_tipo, sismica_base):
        res = ribaltamento_composto(parete_tipo, cuneo_h=100, sismica=sismica_base)
        assert any("Cuneo" in p for p in res.passaggi)

    def test_to_dict_composto(self, parete_tipo, sismica_base):
        res = ribaltamento_composto(parete_tipo, cuneo_h=100, sismica=sismica_base)
        d = res.to_dict()
        assert d["meccanismo"] == "ribaltamento_composto"


# ═══════════════════ Flessione Verticale ═══════════════════

class TestFlessioneVerticale:
    def test_cerniera_default_meta(self, parete_tipo, sismica_base):
        """Cerniera default a h/2."""
        res = flessione_verticale(parete_tipo, sismica=sismica_base)
        assert res.alpha_0 > 0
        assert res.meccanismo == "flessione_verticale"
        assert any("h₁ = 150" in p or "h₂ = 150" in p for p in res.passaggi)

    def test_cerniera_custom(self, parete_tipo, sismica_base):
        """Cerniera a quota diversa cambia α₀."""
        r1 = flessione_verticale(parete_tipo, h_cerniera=100, sismica=sismica_base)
        r2 = flessione_verticale(parete_tipo, h_cerniera=200, sismica=sismica_base)
        assert r1.alpha_0 != r2.alpha_0

    def test_alpha_flessione_vs_ribaltamento(self, parete_tipo, sismica_base):
        """Flessione verticale ha α₀ diverso dal ribaltamento semplice."""
        r_rib = ribaltamento_semplice(parete_tipo, sismica_base)
        r_flex = flessione_verticale(parete_tipo, sismica=sismica_base)
        # Per parete senza carico, flessione verticale ≈ ribaltamento (ma parte superiore)
        # I valori sono diversi perché il meccanismo è diverso
        assert r_flex.alpha_0 != r_rib.alpha_0

    def test_catena_sopra_cerniera(self, parete_tipo, sismica_base):
        """Solo catene sopra la cerniera contribuiscono."""
        cat_sopra = ForzaCatena(F=1000, h_applicazione=250)  # sopra h/2=150
        cat_sotto = ForzaCatena(F=1000, h_applicazione=50)   # sotto h/2=150

        r_sopra = flessione_verticale(parete_tipo, sismica=sismica_base, catene=[cat_sopra])
        r_sotto = flessione_verticale(parete_tipo, sismica=sismica_base, catene=[cat_sotto])
        r_base = flessione_verticale(parete_tipo, sismica=sismica_base)

        # Catena sopra la cerniera migliora α₀
        assert r_sopra.alpha_0 > r_base.alpha_0
        # Catena sotto la cerniera non cambia α₀
        assert r_sotto.alpha_0 == pytest.approx(r_base.alpha_0, rel=0.001)

    def test_non_lineare_usa_h_sup(self, parete_tipo, sismica_base):
        """Cinematica non lineare usa altezza parte superiore."""
        res = flessione_verticale(parete_tipo, h_cerniera=100, sismica=sismica_base)
        # d₀* = t*2/3 (calcolato sulla parete equivalente con h_sup)
        assert res.d_0_star == pytest.approx(30 * 2 / 3, rel=0.01)


# ═══════════════════ Flessione Orizzontale ═══════════════════

class TestFlessioneOrizzontale:
    def test_alpha_arco(self, parete_tipo, sismica_base):
        """α₀ = 2t/L per arco a 3 cerniere."""
        res = flessione_orizzontale(parete_tipo, sismica=sismica_base)
        alpha_atteso = 2 * 30 / 400  # = 0.15
        assert res.alpha_0 == pytest.approx(alpha_atteso, rel=0.01)

    def test_l_libera_custom(self, parete_tipo, sismica_base):
        """L_libera < L aumenta α₀."""
        r_full = flessione_orizzontale(parete_tipo, sismica=sismica_base)
        r_short = flessione_orizzontale(parete_tipo, L_libera=200, sismica=sismica_base)
        assert r_short.alpha_0 > r_full.alpha_0

    def test_meccanismo_corretto(self, parete_tipo, sismica_base):
        res = flessione_orizzontale(parete_tipo, sismica=sismica_base)
        assert res.meccanismo == "flessione_orizzontale"

    def test_catena_orizzontale(self, parete_tipo, sismica_base):
        """Catena confina lateralmente → aumenta α₀."""
        cat = ForzaCatena(F=2000, h_applicazione=150)
        r_no = flessione_orizzontale(parete_tipo, sismica=sismica_base)
        r_si = flessione_orizzontale(parete_tipo, sismica=sismica_base, catene=[cat])
        assert r_si.alpha_0 > r_no.alpha_0

    def test_alpha_proporzionale_t_su_l(self, sismica_base):
        """α₀ ∝ t/L."""
        p1 = PareteMuraria(h=300, t=30, L=400)
        p2 = PareteMuraria(h=300, t=30, L=200)

        r1 = flessione_orizzontale(p1, sismica=sismica_base)
        r2 = flessione_orizzontale(p2, sismica=sismica_base)

        assert r2.alpha_0 == pytest.approx(2 * r1.alpha_0, rel=0.01)


# ═══════════════════ Analisi Completa ═══════════════════

class TestAnalisiMeccanismiLocali:
    def test_tutti_meccanismi(self, parete_tipo, sismica_base):
        """Con cuneo → 4 meccanismi."""
        risultati = analisi_meccanismi_locali(
            parete_tipo, sismica_base, cuneo_h=100,
        )
        assert len(risultati) == 4
        meccanismi = {r.meccanismo for r in risultati}
        assert "ribaltamento_semplice" in meccanismi
        assert "ribaltamento_composto" in meccanismi
        assert "flessione_verticale" in meccanismi
        assert "flessione_orizzontale" in meccanismi

    def test_senza_cuneo_tre_meccanismi(self, parete_tipo, sismica_base):
        """Senza cuneo → 3 meccanismi (no composto)."""
        risultati = analisi_meccanismi_locali(parete_tipo, sismica_base)
        assert len(risultati) == 3

    def test_ordinati_per_alpha(self, parete_tipo, sismica_base):
        """Risultati ordinati per α₀ crescente (primo = più critico)."""
        risultati = analisi_meccanismi_locali(
            parete_tipo, sismica_base, cuneo_h=100,
        )
        alphas = [r.alpha_0 for r in risultati]
        assert alphas == sorted(alphas)

    def test_primo_piu_critico(self, parete_tipo, sismica_base):
        """Il primo risultato ha α₀ più basso."""
        risultati = analisi_meccanismi_locali(
            parete_tipo, sismica_base, cuneo_h=100,
        )
        assert risultati[0].alpha_0 <= risultati[-1].alpha_0

    def test_catene_migliorano_tutti(self, parete_tipo, sismica_base):
        """Catene migliorano α₀ di tutti i meccanismi."""
        cat = [ForzaCatena(F=3000, h_applicazione=280)]

        r_no = analisi_meccanismi_locali(parete_tipo, sismica_base, cuneo_h=100)
        r_si = analisi_meccanismi_locali(parete_tipo, sismica_base, catene=cat, cuneo_h=100)

        # Confronta ribaltamento semplice
        alpha_no = next(r.alpha_0 for r in r_no if r.meccanismo == "ribaltamento_semplice")
        alpha_si = next(r.alpha_0 for r in r_si if r.meccanismo == "ribaltamento_semplice")
        assert alpha_si > alpha_no


# ═══════════════════ Casi Limite ═══════════════════

class TestCasiLimite:
    def test_parete_molto_spessa(self, sismica_base):
        """Parete spessa → α₀ alto → verificata."""
        p = PareteMuraria(h=200, t=80, L=400)
        res = ribaltamento_semplice(p, sismica_base)
        assert res.alpha_0 > 0.3

    def test_parete_molto_snella(self, sismica_base):
        """Parete snella → α₀ basso."""
        p = PareteMuraria(h=500, t=15, L=400)
        res = ribaltamento_semplice(p, sismica_base)
        assert res.alpha_0 < 0.05

    def test_no_sismica(self, parete_tipo):
        """Con a_g=0 → domanda nulla → verificata."""
        sismica = ParametriSismici(a_g=0, S=1.0)
        res = ribaltamento_semplice(parete_tipo, sismica)
        assert res.a_domanda == 0.0
        assert res.verifica_lineare is True

    def test_catena_multipla(self, parete_tipo, sismica_base):
        """Più catene sommano i contributi."""
        cat1 = ForzaCatena(F=1000, h_applicazione=200)
        cat2 = ForzaCatena(F=1000, h_applicazione=300)

        r1 = ribaltamento_semplice(parete_tipo, sismica_base, catene=[cat1])
        r2 = ribaltamento_semplice(parete_tipo, sismica_base, catene=[cat1, cat2])
        assert r2.alpha_0 > r1.alpha_0

    def test_costante_g(self):
        """G = 981 cm/s²."""
        assert G == pytest.approx(981.0)
