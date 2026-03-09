"""Test per por_verifiche.py — Tabella maschi, riepilogo rischio, grafico.

Verifica:
- RigaMaschio e TabellaVerificheMaschi
- genera_tabella_maschi con dati realistici
- calcola_riepilogo_rischio: globale vs locale
- Formato testo ASCII
- Serializzazione to_dict
"""

import pytest

from src.methods.muratura.discretizzazione import Maschio, TipoVincolo
from src.methods.muratura.modello_edificio import MaterialeMuratura
from src.methods.muratura.por_analisi import CurvaPushover, PuntoPushover
from src.methods.muratura.por_verifiche import (
    RigaMaschio,
    TabellaVerificheMaschi,
    calcola_riepilogo_rischio,
    genera_tabella_maschi,
    plot_curva_pushover,
)
from src.methods.muratura.resistenza import ResistenzaMaschio

# ═══════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def materiale_test():
    """Materiale muratura di test (mattoni pieni calce)."""
    return MaterialeMuratura(
        nome="Mattoni pieni calce",
        f=32.0, tau_0=0.76, fvk0=0.20,
        E=15000, G=5000,
        gamma_M=2.0, FC=1.20,
    )


@pytest.fixture
def maschi_test(materiale_test):
    """3 maschi di test per un piano."""
    return [
        Maschio(
            id_maschio=1, id_piano=0, id_parete=1,
            L=150, t=30, h=300,
            x_baricentro=75, y_baricentro=0,
            vincolo=TipoVincolo.INCASTRO,
            materiale=materiale_test,
            N_gravitazionale=15000,
        ),
        Maschio(
            id_maschio=2, id_piano=0, id_parete=1,
            L=100, t=30, h=300,
            x_baricentro=325, y_baricentro=0,
            vincolo=TipoVincolo.INCASTRO,
            materiale=materiale_test,
            N_gravitazionale=10000,
        ),
        Maschio(
            id_maschio=3, id_piano=0, id_parete=2,
            L=200, t=30, h=300,
            x_baricentro=100, y_baricentro=500,
            vincolo=TipoVincolo.INCASTRO,
            materiale=materiale_test,
            N_gravitazionale=20000,
        ),
    ]


@pytest.fixture
def resistenze_test():
    """3 resistenze di test corrispondenti ai maschi."""
    return [
        ResistenzaMaschio(
            id_maschio=1, V_Rd=5000, criterio_dominante="diagonale",
            k_elastico=10000, delta_y=0.5, delta_u=1.5,
        ),
        ResistenzaMaschio(
            id_maschio=2, V_Rd=3000, criterio_dominante="scorrimento",
            k_elastico=8000, delta_y=0.375, delta_u=1.5,
        ),
        ResistenzaMaschio(
            id_maschio=3, V_Rd=8000, criterio_dominante="pressoflessione",
            k_elastico=15000, delta_y=0.533, delta_u=3.0,
        ),
    ]


# ═══════════════════════════════════════════════════════════
#  RigaMaschio
# ═══════════════════════════════════════════════════════════

class TestRigaMaschio:
    """Test dataclass RigaMaschio."""

    def test_default(self):
        r = RigaMaschio()
        assert r.verificato is True
        assert r.DC == 0.0

    def test_to_dict(self):
        r = RigaMaschio(
            id_maschio=1, piano=0, parete=1,
            L=150, t=30, h=300,
            N=15000, V_Ed=4000, V_Rd=5000,
            criterio="diagonale", DC=0.8,
            verificato=True, stato="elastico",
        )
        d = r.to_dict()
        assert d["id"] == 1
        assert d["D/C"] == 0.8
        assert d["verificato"] is True
        assert d["criterio"] == "diagonale"

    def test_non_verificato(self):
        r = RigaMaschio(DC=1.5, verificato=False)
        assert not r.verificato


# ═══════════════════════════════════════════════════════════
#  TabellaVerificheMaschi
# ═══════════════════════════════════════════════════════════

class TestTabellaVerifiche:
    """Test TabellaVerificheMaschi."""

    def test_tabella_vuota(self):
        t = TabellaVerificheMaschi()
        assert t.n_verificati == 0
        assert t.n_non_verificati == 0
        assert t.DC_max == 0.0

    def test_conteggi(self):
        righe = [
            RigaMaschio(verificato=True, DC=0.5),
            RigaMaschio(verificato=True, DC=0.8),
            RigaMaschio(verificato=False, DC=1.2),
        ]
        t = TabellaVerificheMaschi(righe=righe)
        assert t.n_verificati == 2
        assert t.n_non_verificati == 1
        assert t.DC_max == pytest.approx(1.2)

    def test_to_dict(self):
        righe = [RigaMaschio(DC=0.9, verificato=True)]
        t = TabellaVerificheMaschi(righe=righe, direzione="Y")
        d = t.to_dict()
        assert d["direzione"] == "Y"
        assert d["n_maschi"] == 1
        assert d["DC_max"] == pytest.approx(0.9, abs=0.001)
        assert len(d["righe"]) == 1

    def test_formato_testo(self):
        righe = [
            RigaMaschio(
                id_maschio=1, piano=0, parete=1,
                L=150, t=30, h=300,
                N=15000, V_Ed=4000, V_Rd=5000,
                criterio="diagonale", DC=0.8,
                verificato=True, stato="elastico",
            ),
        ]
        t = TabellaVerificheMaschi(righe=righe, direzione="X")
        testo = t.formato_testo()
        assert "TABELLA VERIFICHE MASCHI" in testo
        assert "Direzione X" in testo
        assert "OK" in testo
        assert "1 maschi" in testo


# ═══════════════════════════════════════════════════════════
#  genera_tabella_maschi
# ═══════════════════════════════════════════════════════════

class TestGeneraTabella:
    """Test generazione tabella maschi."""

    def test_genera_tabella_base(self, maschi_test, resistenze_test):
        tagli_ed = {1: 4000, 2: 3500, 3: 6000}
        tabella = genera_tabella_maschi(
            maschi_test, resistenze_test, tagli_ed,
            direzione="X", distribuzione="modo_1",
        )
        assert len(tabella.righe) == 3
        assert tabella.direzione == "X"

    def test_dc_corretto(self, maschi_test, resistenze_test):
        tagli_ed = {1: 4000, 2: 3500, 3: 6000}
        tabella = genera_tabella_maschi(maschi_test, resistenze_test, tagli_ed)
        # M1: V_Ed=4000, V_Rd=5000 → D/C = 0.8
        r1 = tabella.righe[0]
        assert r1.DC == pytest.approx(0.8, abs=0.01)
        assert r1.verificato is True

    def test_dc_superamento(self, maschi_test, resistenze_test):
        tagli_ed = {1: 6000, 2: 4000, 3: 6000}
        tabella = genera_tabella_maschi(maschi_test, resistenze_test, tagli_ed)
        r1 = tabella.righe[0]
        assert r1.DC == pytest.approx(1.2, abs=0.01)
        assert r1.verificato is False

    def test_maschio_mancante_in_resistenze(self, materiale_test):
        """Maschio senza resistenza → V_Rd = 0."""
        maschi = [
            Maschio(
                id_maschio=99, id_piano=0, id_parete=1,
                L=100, t=30, h=300,
                materiale=materiale_test,
                N_gravitazionale=5000,
            ),
        ]
        resistenze = []  # nessuna resistenza
        tagli_ed = {99: 1000}
        tabella = genera_tabella_maschi(maschi, resistenze, tagli_ed)
        assert len(tabella.righe) == 1
        r = tabella.righe[0]
        assert r.V_Rd == 0.0
        # Con V_Ed > 0 e V_Rd = 0 → DC = inf → non verificato
        assert r.DC == float("inf")
        assert r.verificato is False

    def test_taglio_nullo(self, maschi_test, resistenze_test):
        """V_Ed = 0 → D/C = 0, verificato."""
        tagli_ed = {1: 0, 2: 0, 3: 0}
        tabella = genera_tabella_maschi(maschi_test, resistenze_test, tagli_ed)
        for r in tabella.righe:
            assert r.DC == pytest.approx(0.0)
            assert r.verificato is True

    def test_dc_max(self, maschi_test, resistenze_test):
        tagli_ed = {1: 4000, 2: 3500, 3: 6000}
        tabella = genera_tabella_maschi(maschi_test, resistenze_test, tagli_ed)
        dc_values = [r.DC for r in tabella.righe]
        assert tabella.DC_max == pytest.approx(max(dc_values), abs=0.001)


# ═══════════════════════════════════════════════════════════
#  Riepilogo rischio sismico
# ═══════════════════════════════════════════════════════════

class TestRiepilogoRischio:
    """Test calcola_riepilogo_rischio."""

    def test_globale_governa(self):
        """ζ_E globale < locale → globale governa."""
        ris = calcola_riepilogo_rischio(
            zeta_E_globale=0.60,
            zeta_E_locale=0.85,
        )
        assert ris.governante == "globale"
        assert ris.zeta_E_governante == pytest.approx(0.60)

    def test_locale_governa(self):
        """ζ_E locale < globale → locale governa."""
        ris = calcola_riepilogo_rischio(
            zeta_E_globale=0.90,
            zeta_E_locale=0.50,
        )
        assert ris.governante == "locale"
        assert ris.zeta_E_governante == pytest.approx(0.50)

    def test_edificio_verificato(self):
        """ζ_E ≥ 1.0 → verificato."""
        ris = calcola_riepilogo_rischio(
            zeta_E_globale=1.20,
            zeta_E_locale=1.05,
        )
        assert ris.zeta_E_governante == pytest.approx(1.05)
        assert any("VERIFICATO" in p for p in ris.passaggi)

    def test_edificio_non_verificato(self):
        """ζ_E < 1.0 → NON verificato."""
        ris = calcola_riepilogo_rischio(
            zeta_E_globale=0.70,
            zeta_E_locale=0.80,
        )
        assert ris.zeta_E_governante == pytest.approx(0.70)
        assert any("NON VERIFICATO" in p for p in ris.passaggi)

    def test_solo_globale(self):
        """Solo ζ_E globale disponibile."""
        ris = calcola_riepilogo_rischio(zeta_E_globale=0.75)
        assert ris.governante == "globale"
        assert ris.zeta_E_governante == pytest.approx(0.75)

    def test_solo_locale(self):
        """Solo ζ_E locale disponibile."""
        ris = calcola_riepilogo_rischio(zeta_E_locale=0.60)
        assert ris.governante == "locale"
        assert ris.zeta_E_governante == pytest.approx(0.60)

    def test_nessun_valore(self):
        """Nessun ζ_E → governante vuoto."""
        ris = calcola_riepilogo_rischio()
        assert ris.governante == ""
        assert ris.zeta_E_governante == pytest.approx(0.0)

    def test_to_dict(self):
        ris = calcola_riepilogo_rischio(0.70, 0.80)
        d = ris.to_dict()
        assert "zeta_E_globale" in d
        assert "zeta_E_locale" in d
        assert "zeta_E_governante" in d
        assert "governante" in d

    def test_passaggi_non_vuoti(self):
        ris = calcola_riepilogo_rischio(0.70, 0.80)
        assert len(ris.passaggi) > 0

    def test_parita(self):
        """Se globale == locale, globale governa (<=)."""
        ris = calcola_riepilogo_rischio(0.80, 0.80)
        assert ris.governante == "globale"
        assert ris.zeta_E_governante == pytest.approx(0.80)


# ═══════════════════════════════════════════════════════════
#  Plot pushover (smoke test senza display)
# ═══════════════════════════════════════════════════════════

class TestPlotPushover:
    """Smoke test per plot_curva_pushover."""

    def _curva_test(self):
        """Crea una curva pushover di test."""
        punti = []
        for i in range(11):
            d = i * 0.2
            V = min(5000 * d / 0.5, 5000) if d <= 2.0 else max(5000 * (1 - (d - 2.0) / 2.0), 0)
            punti.append(PuntoPushover(passo=i, delta_controllo=d, V_base=V))
        curva = CurvaPushover(
            punti=punti,
            direzione="X",
            distribuzione="modo_1",
            V_y=4500,
            delta_y=0.45,
            delta_u=2.0,
            k_bilineare=10000,
            mu=4.44,
            T_star=0.25,
        )
        return curva

    def test_plot_ritorna_figura(self):
        """Il plot deve ritornare una figura matplotlib (o None se non disponibile)."""
        curva = self._curva_test()
        fig = plot_curva_pushover(curva, mostra=False)
        # Se matplotlib è installato, deve ritornare una figura
        try:
            import matplotlib  # noqa: F401
            assert fig is not None
        except ImportError:
            assert fig is None

    def test_plot_senza_bilineare(self):
        """Plot senza bilineare (V_y=0) non deve crashare."""
        curva = CurvaPushover(
            punti=[
                PuntoPushover(passo=0, delta_controllo=0, V_base=0),
                PuntoPushover(passo=1, delta_controllo=1, V_base=1000),
            ],
        )
        fig = plot_curva_pushover(curva, mostra=False)
        # Non deve sollevare eccezioni
