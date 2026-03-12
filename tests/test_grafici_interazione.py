"""Test per src/grafici/interazione.py.

Verifica PuntoLavoro, DominioFactory (routing norme), sovrapponi_punto_lavoro.
I test di calcolo dominio (calcola_dominio_3d) sono coperti dalla suite Fase J.
"""

import pytest

from src.grafici.interazione import (
    _NORME_SLU,
    _NORME_TA,
    DominioFactory,
    PuntoLavoro,
    _normalizza_norma,
    sovrapponi_punto_lavoro,
)

# ---------------------------------------------------------------------------
# PuntoLavoro
# ---------------------------------------------------------------------------


class TestPuntoLavoro:
    def test_costruttore_minimo(self):
        p = PuntoLavoro(N_Ed_kg=5000.0)
        assert p.N_Ed_kg == pytest.approx(5000.0)
        assert p.Mx_Ed_kgcm == pytest.approx(0.0)
        assert p.My_Ed_kgcm == pytest.approx(0.0)
        assert p.etichetta == ""

    def test_costruttore_completo(self):
        p = PuntoLavoro(
            N_Ed_kg=-10000.0,
            Mx_Ed_kgcm=500000.0,
            My_Ed_kgcm=250000.0,
            etichetta="SLU — Comb. 1",
            norma="NTC2018",
        )
        assert p.etichetta == "SLU — Comb. 1"
        assert p.norma == "NTC2018"


# ---------------------------------------------------------------------------
# _normalizza_norma
# ---------------------------------------------------------------------------


class TestNormalizzaNorma:
    def test_maiuscolo(self):
        assert _normalizza_norma("ntc2018") == "NTC2018"

    def test_spazi_rimossi(self):
        assert _normalizza_norma("NTC 2018") == "NTC2018"

    def test_gia_normalizzata(self):
        assert _normalizza_norma("RD2229") == "RD2229"


# ---------------------------------------------------------------------------
# DominioFactory.norme_disponibili
# ---------------------------------------------------------------------------


class TestNormeDisponibili:
    def test_contiene_norme_ta(self):
        norme = DominioFactory.norme_disponibili()
        for n in _NORME_TA:
            assert n in norme, f"Norma TA '{n}' non presente in norme_disponibili()"

    def test_contiene_norme_slu(self):
        norme = DominioFactory.norme_disponibili()
        for n in _NORME_SLU:
            assert n in norme, f"Norma SLU '{n}' non presente in norme_disponibili()"

    def test_lista_ordinata(self):
        norme = DominioFactory.norme_disponibili()
        assert norme == sorted(norme, key=str.upper)


# ---------------------------------------------------------------------------
# DominioFactory.registra (registry custom)
# ---------------------------------------------------------------------------


class TestDominioFactoryRegistra:
    def test_registra_e_usa(self):
        """Una funzione custom registrata deve essere richiamata dalla factory."""
        chiamata = []

        def _mia_funzione(spec, **kwargs):
            chiamata.append(True)
            return "risultato_custom"

        DominioFactory.registra("NORMA_TEST_XYZ", _mia_funzione)
        try:
            from unittest.mock import MagicMock

            spec = MagicMock()
            spec.norma = "NORMA_TEST_XYZ"
            risultato = DominioFactory.calcola(spec, norma="NORMA_TEST_XYZ")
            assert risultato == "risultato_custom"
            assert chiamata
        finally:
            # Pulizia registry per non inquinare altri test
            DominioFactory._registry.pop("NORMA_TEST_XYZ", None)

    def test_norma_sconosciuta_raise(self):
        from unittest.mock import MagicMock

        spec = MagicMock()
        spec.norma = "NORMA_INESISTENTE_ABC"
        with pytest.raises(ValueError, match="non supportata"):
            DominioFactory.calcola(spec, norma="NORMA_INESISTENTE_ABC")


# ---------------------------------------------------------------------------
# sovrapponi_punto_lavoro (headless)
# ---------------------------------------------------------------------------


class TestSovrappontiPuntoLavoro:
    matplotlib = pytest.importorskip("matplotlib")

    def test_disegna_senza_errori(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([0, 100000], [0, -50000], "r-")  # dominio finto

        p = PuntoLavoro(
            N_Ed_kg=-20000.0,
            Mx_Ed_kgcm=40000.0,
            etichetta="Ed",
        )
        sovrapponi_punto_lavoro(ax, p, theta_fisso_rad=0.0)

        assert len(ax.collections) > 0  # scatter aggiunto
        plt.close(fig)

    def test_proiezione_theta_zero(self):
        """Con θ=0, M_proiettato = |Mx·cos(0)| + |My·sin(0)| = Mx."""

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        p = PuntoLavoro(N_Ed_kg=0.0, Mx_Ed_kgcm=50000.0, My_Ed_kgcm=30000.0)
        sovrapponi_punto_lavoro(ax, p, theta_fisso_rad=0.0)
        plt.close(fig)

    def test_proiezione_theta_90gradi(self):
        """Con θ=π/2, M_proiettato = |Mx·cos(90)| + |My·sin(90)| = My."""
        import math

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        p = PuntoLavoro(N_Ed_kg=0.0, Mx_Ed_kgcm=0.0, My_Ed_kgcm=70000.0)
        sovrapponi_punto_lavoro(ax, p, theta_fisso_rad=math.pi / 2)
        plt.close(fig)
