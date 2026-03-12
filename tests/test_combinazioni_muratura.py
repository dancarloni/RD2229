"""Test per combinazioni_muratura.py — combinazioni personalizzabili."""

import pytest

from src.methods.muratura.combinazioni_muratura import (
    PSI_0,
    PSI_1,
    PSI_2,
    CombinazioneCarico,
    GestoreCombinazioni,
)

# ═══════════════════════════════════════════════════════════
#  Coefficienti ψ
# ═══════════════════════════════════════════════════════════


class TestPsi:
    def test_psi_0_residenziale(self):
        assert PSI_0["A"] == pytest.approx(0.7)

    def test_psi_0_magazzini(self):
        assert PSI_0["E"] == pytest.approx(1.0)

    def test_psi_2_residenziale(self):
        assert PSI_2["A"] == pytest.approx(0.3)

    def test_psi_1_affollamento(self):
        assert PSI_1["C"] == pytest.approx(0.7)


# ═══════════════════════════════════════════════════════════
#  CombinazioneCarico
# ═══════════════════════════════════════════════════════════


class TestCombinazioneCarico:
    def test_calcola_N_SLU(self):
        """SLU fondamentale: 1.3×G1 + 1.5×G2 + 1.5×0.7×Q."""
        c = CombinazioneCarico(gamma_G1=1.3, gamma_G2=1.5, gamma_Q=1.5, psi=0.7)
        N = c.calcola_N(G1=10000, G2=3000, Q=2000)
        # 1.3×10000 + 1.5×3000 + 1.5×0.7×2000 = 13000 + 4500 + 2100 = 19600
        assert N == pytest.approx(19600)

    def test_calcola_N_favorevole(self):
        """SLU favorevole: 1.0×G1 + 0×G2 + 0×Q."""
        c = CombinazioneCarico(gamma_G1=1.0, gamma_G2=0.0, gamma_Q=0.0, psi=0.0)
        N = c.calcola_N(G1=10000, G2=3000, Q=2000)
        assert N == pytest.approx(10000)

    def test_calcola_N_sismica(self):
        """Sismica: 1.0×G1 + 1.0×G2 + 1.0×ψ₂×Q."""
        c = CombinazioneCarico(gamma_G1=1.0, gamma_G2=1.0, gamma_Q=1.0, psi=0.3)
        N = c.calcola_N(G1=10000, G2=3000, Q=2000)
        assert N == pytest.approx(10000 + 3000 + 0.3 * 2000)

    def test_to_dict(self):
        c = CombinazioneCarico(nome="test", tipo="SLU", id_combinazione=42)
        d = c.to_dict()
        assert d["nome"] == "test"
        assert d["id"] == 42


# ═══════════════════════════════════════════════════════════
#  GestoreCombinazioni — default
# ═══════════════════════════════════════════════════════════


class TestGestoreDefault:
    def test_default_genera_6_combinazioni(self):
        g = GestoreCombinazioni(categoria="A")
        assert g.n_combinazioni == 6

    def test_default_tutte_attive(self):
        g = GestoreCombinazioni()
        assert g.n_attive == 6

    def test_default_tutte_predefinite(self):
        g = GestoreCombinazioni()
        for c in g.combinazioni:
            assert c.predefinita is True

    def test_default_include_SLU(self):
        g = GestoreCombinazioni()
        nomi = [c.nome for c in g.combinazioni]
        assert any("SLU" in n for n in nomi)

    def test_default_include_sismica(self):
        g = GestoreCombinazioni()
        tipi = [c.tipo for c in g.combinazioni]
        assert "sismica" in tipi

    def test_categoria_magazzini(self):
        g = GestoreCombinazioni(categoria="E")
        combo_sis = [c for c in g.combinazioni if c.tipo == "sismica"][0]
        assert combo_sis.psi == pytest.approx(0.8)  # ψ₂ per E


# ═══════════════════════════════════════════════════════════
#  CRUD
# ═══════════════════════════════════════════════════════════


class TestCRUD:
    def test_aggiungi(self):
        g = GestoreCombinazioni()
        n_prima = g.n_combinazioni
        c = g.aggiungi("Test custom", gamma_G1=1.1, gamma_G2=1.2, gamma_Q=1.0, psi=0.5)
        assert g.n_combinazioni == n_prima + 1
        assert c.predefinita is False
        assert c.attiva is True

    def test_modifica(self):
        g = GestoreCombinazioni()
        c = g.aggiungi("Modif test")
        ok = g.modifica(c.id_combinazione, nome="Modificata", gamma_G1=1.5)
        assert ok
        aggiornata = g.per_id(c.id_combinazione)
        assert aggiornata.nome == "Modificata"
        assert aggiornata.gamma_G1 == pytest.approx(1.5)

    def test_modifica_non_trovato(self):
        g = GestoreCombinazioni()
        assert g.modifica(99999, nome="X") is False

    def test_elimina(self):
        g = GestoreCombinazioni()
        c = g.aggiungi("Da eliminare")
        n_prima = g.n_combinazioni
        ok = g.elimina(c.id_combinazione)
        assert ok
        assert g.n_combinazioni == n_prima - 1
        assert g.per_id(c.id_combinazione) is None

    def test_elimina_non_trovato(self):
        g = GestoreCombinazioni()
        assert g.elimina(99999) is False

    def test_elimina_default(self):
        """L'utente può eliminare anche combinazioni predefinite."""
        g = GestoreCombinazioni()
        primo = g.combinazioni[0]
        assert g.elimina(primo.id_combinazione)


# ═══════════════════════════════════════════════════════════
#  Attiva / Disattiva
# ═══════════════════════════════════════════════════════════


class TestAttivaDisattiva:
    def test_disattiva(self):
        g = GestoreCombinazioni()
        primo = g.combinazioni[0]
        g.disattiva(primo.id_combinazione)
        assert primo.attiva is False
        assert g.n_attive == 5

    def test_attiva(self):
        g = GestoreCombinazioni()
        primo = g.combinazioni[0]
        g.disattiva(primo.id_combinazione)
        g.attiva(primo.id_combinazione)
        assert primo.attiva is True
        assert g.n_attive == 6

    def test_disattiva_non_elimina(self):
        g = GestoreCombinazioni()
        primo = g.combinazioni[0]
        g.disattiva(primo.id_combinazione)
        assert g.n_combinazioni == 6  # ancora 6
        assert g.n_attive == 5

    def test_disattiva_non_trovato(self):
        g = GestoreCombinazioni()
        assert g.disattiva(99999) is False


# ═══════════════════════════════════════════════════════════
#  Ripristino default
# ═══════════════════════════════════════════════════════════


class TestRipristinoDefault:
    def test_ripristina_dopo_eliminazione(self):
        g = GestoreCombinazioni()
        # Elimina una predefinita
        primo = g.combinazioni[0]
        g.elimina(primo.id_combinazione)
        assert g.n_combinazioni == 5
        # Ripristina
        g.ripristina_default()
        assert g.n_combinazioni == 6

    def test_ripristina_mantiene_custom(self):
        g = GestoreCombinazioni()
        g.aggiungi("La mia combo")
        g.ripristina_default()
        # 6 default + 1 custom
        assert g.n_combinazioni == 7
        nomi = [c.nome for c in g.combinazioni]
        assert "La mia combo" in nomi


# ═══════════════════════════════════════════════════════════
#  Calcolo N combinato
# ═══════════════════════════════════════════════════════════


class TestCalcoloNCombinato:
    def test_calcola_N_tutte(self):
        g = GestoreCombinazioni()
        risultati = g.calcola_N_tutte(G1=10000, G2=3000, Q=2000)
        assert len(risultati) == 6

    def test_calcola_N_solo_attive(self):
        g = GestoreCombinazioni()
        g.disattiva(g.combinazioni[0].id_combinazione)
        risultati = g.calcola_N_tutte(G1=10000, G2=3000, Q=2000)
        assert len(risultati) == 5

    def test_N_Ed_max(self):
        g = GestoreCombinazioni()
        N_max = g.N_Ed_max(G1=10000, G2=3000, Q=2000)
        # SLU sfavorevole: 1.3×10000 + 1.5×3000 + 1.5×0.7×2000 = 19600
        assert N_max == pytest.approx(19600)

    def test_N_Ed_max_nessuna_attiva(self):
        g = GestoreCombinazioni()
        for c in g.combinazioni:
            g.disattiva(c.id_combinazione)
        assert g.N_Ed_max(G1=10000, G2=3000, Q=2000) == 0.0

    def test_to_dict(self):
        g = GestoreCombinazioni()
        d = g.to_dict()
        assert d["n_combinazioni"] == 6
        assert d["n_attive"] == 6
        assert len(d["combinazioni"]) == 6
