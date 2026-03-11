"""Test per src/grafici/spostamenti.py.

Verifica DiagrammaSpostamenti, SolutoreAnalitico, SolutoreFEM stub,
grafico_spostamenti. Casi noti di trave semplicemente appoggiata.
"""

import math

import numpy as np
import pytest

from src.grafici.spostamenti import (
    DiagrammaSpostamenti,
    ISolutoreSpostamenti,
    SolutoreAnalitico,
    SolutoreFEM,
    grafico_spostamenti,
)

scipy = pytest.importorskip("scipy")


# ---------------------------------------------------------------------------
# DiagrammaSpostamenti
# ---------------------------------------------------------------------------

class TestDiagrammaSpostamenti:
    def test_costruttore(self):
        d = DiagrammaSpostamenti(
            x_cm=[0.0, 50.0, 100.0],
            v_cm=[0.0, -0.5, 0.0],
            u_cm=[0.0, 0.0, 0.0],
            etichetta="Trave test",
            solutore="analitico",
        )
        assert d.v_max_cm == pytest.approx(0.5)
        assert d.u_max_cm == pytest.approx(0.0)

    def test_lunghezze_incompatibili(self):
        with pytest.raises(ValueError, match="stessa lunghezza"):
            DiagrammaSpostamenti(
                x_cm=[0.0, 50.0],
                v_cm=[0.0],
                u_cm=[0.0, 0.0],
            )

    def test_v_max_lista_vuota(self):
        d = DiagrammaSpostamenti(x_cm=[], v_cm=[], u_cm=[])
        assert d.v_max_cm == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# ISolutoreSpostamenti — contratto ABC
# ---------------------------------------------------------------------------

class TestISolutore:
    def test_non_istanziabile_direttamente(self):
        with pytest.raises(TypeError):
            ISolutoreSpostamenti()


# ---------------------------------------------------------------------------
# SolutoreAnalitico — casi noti
# ---------------------------------------------------------------------------

class TestSolutoreAnalitico:
    """Casi noti: trave semplicemente appoggiata."""

    def _trave_sa_carico_concentrato(self, L_cm, P_kg, E_kgcm2, I_cm4, n=100):
        """Carico concentrato al centro: M(x) = P/2·x per x<=L/2, P/2·(L-x) per x>L/2."""
        x = np.linspace(0.0, L_cm, n)
        M = np.where(
            x <= L_cm / 2,
            P_kg / 2.0 * x,
            P_kg / 2.0 * (L_cm - x),
        )
        return x, M, E_kgcm2 * I_cm4

    def _trave_sa_carico_uniforme(self, L_cm, q_kgcm, E_kgcm2, I_cm4, n=200):
        """Carico distribuito uniforme: M(x) = q/2·x·(L-x)."""
        x = np.linspace(0.0, L_cm, n)
        M = q_kgcm / 2.0 * x * (L_cm - x)
        return x, M, E_kgcm2 * I_cm4

    def test_freccia_carico_concentrato_centro(self):
        """f_max = PL³/48EI, errore < 1% con n=100."""
        L = 600.0          # cm
        P = 5000.0         # kg
        E = 210000.0       # kg/cm² (acciaio storico, valore indicativo)
        I = 10000.0        # cm4
        EI = E * I

        f_analitica = P * L**3 / (48.0 * EI)  # cm

        x, M, EI_val = self._trave_sa_carico_concentrato(L, P, E, I, n=200)
        sol = SolutoreAnalitico(bc="semplicemente_appoggiata")
        diag = sol.calcola(list(x), list(M), EI_val, etichetta="Test P centro")

        f_numerica = diag.v_max_cm
        errore_perc = abs(f_numerica - f_analitica) / f_analitica * 100.0
        assert errore_perc < 2.0, (
            f"Freccia numerica {f_numerica:.4f} cm, analitica {f_analitica:.4f} cm, "
            f"errore {errore_perc:.2f}% > 2%"
        )

    def test_freccia_carico_distribuito(self):
        """f_max = 5qL⁴/384EI, errore < 1% con n=200."""
        L = 500.0
        q = 10.0           # kg/cm
        E = 200000.0
        I = 8000.0
        EI = E * I

        f_analitica = 5.0 * q * L**4 / (384.0 * EI)

        x, M, EI_val = self._trave_sa_carico_uniforme(L, q, E, I, n=300)
        sol = SolutoreAnalitico()
        diag = sol.calcola(list(x), list(M), EI_val, etichetta="Test q uniforme")

        f_numerica = diag.v_max_cm
        errore_perc = abs(f_numerica - f_analitica) / f_analitica * 100.0
        assert errore_perc < 2.0, (
            f"Freccia numerica {f_numerica:.4f} cm, analitica {f_analitica:.4f} cm, "
            f"errore {errore_perc:.2f}% > 2%"
        )

    def test_condizioni_contorno_sa_v_agli_estremi(self):
        """v(0)≈0 e v(L)≈0 per bc semplicemente_appoggiata."""
        L = 400.0
        q = 5.0
        E = 150000.0
        I = 5000.0
        x, M, EI = self._trave_sa_carico_uniforme(L, q, E, I, n=100)
        sol = SolutoreAnalitico()
        diag = sol.calcola(list(x), list(M), EI)
        assert abs(diag.v_cm[0]) < 1e-10
        assert abs(diag.v_cm[-1]) < 1e-6  # errore numerico tollerato

    def test_solutore_analitico_etichetta(self):
        L = 300.0
        x = list(np.linspace(0, L, 20))
        M = [0.0] * 20
        sol = SolutoreAnalitico()
        diag = sol.calcola(x, M, 1e8, etichetta="Caso nullo")
        assert diag.etichetta == "Caso nullo"
        assert diag.solutore == "analitico"

    def test_u_sempre_zero(self):
        """SolutoreAnalitico restituisce u(x)=0 (riservato a FEM)."""
        x = list(np.linspace(0, 200, 10))
        M = [100.0] * 10
        sol = SolutoreAnalitico()
        diag = sol.calcola(x, M, 1e6)
        assert all(v == pytest.approx(0.0) for v in diag.u_cm)

    def test_EI_non_positivo_raise(self):
        with pytest.raises(ValueError, match="EI deve essere positivo"):
            SolutoreAnalitico().calcola([0.0, 100.0], [0.0, 0.0], EI_kgcm2=0.0)

    def test_bc_non_valido_raise(self):
        with pytest.raises(ValueError, match="bc '.*' non valido"):
            SolutoreAnalitico(bc="incastro_libero")

    def test_troppo_pochi_punti_raise(self):
        with pytest.raises(ValueError, match="almeno 2"):
            SolutoreAnalitico().calcola([0.0], [0.0], EI_kgcm2=1e6)

    def test_lunghezze_x_M_diverse_raise(self):
        with pytest.raises(ValueError, match="stessa lunghezza"):
            SolutoreAnalitico().calcola([0.0, 100.0, 200.0], [0.0, 100.0], EI_kgcm2=1e6)


# ---------------------------------------------------------------------------
# SolutoreFEM — implementazione Hermite (Fase M completata)
# ---------------------------------------------------------------------------

class TestSolutoreFEM:
    def test_restituisce_diagramma_spostamenti(self):
        """SolutoreFEM.calcola() deve restituire un DiagrammaSpostamenti valido."""
        x = list(np.linspace(0.0, 500.0, 21))
        # Momento parabolico da carico uniforme (approssimazione)
        M = [2.0 * xi * (500.0 - xi) / 2.0 for xi in x]
        sol = SolutoreFEM()
        diag = sol.calcola(x, M, EI_kgcm2=3e7)
        assert isinstance(diag, DiagrammaSpostamenti)
        assert diag.solutore == "FEM-Hermite"
        assert len(diag.v_cm) == len(x)
        assert len(diag.u_cm) == len(x)

    def test_appoggi_nulli_semplicemente_appoggiata(self):
        """v(0) e v(L) devono essere nulli con bc='semplicemente_appoggiata'."""
        x = list(np.linspace(0.0, 400.0, 41))
        M = [2.0 * xi * (400.0 - xi) / 2.0 for xi in x]
        diag = SolutoreFEM("semplicemente_appoggiata").calcola(x, M, EI_kgcm2=2e7)
        assert abs(diag.v_cm[0]) < 1e-10
        assert abs(diag.v_cm[-1]) < 1e-10

    def test_incastro_appoggio_origine_nulla(self):
        """Con bc='incastro_appoggio', v(0) = 0."""
        x = list(np.linspace(0.0, 300.0, 31))
        M = [50.0 * xi for xi in x]
        diag = SolutoreFEM("incastro_appoggio").calcola(x, M, EI_kgcm2=1e7)
        assert abs(diag.v_cm[0]) < 1e-10

    def test_bc_invalido_errore(self):
        """bc non valido deve sollevare ValueError."""
        with pytest.raises(ValueError, match="bc"):
            SolutoreFEM(bc="semplicemente_appogiata")   # typo realístico

    def test_ei_negativo_errore(self):
        """EI non positivo deve sollevare ValueError."""
        sol = SolutoreFEM()
        with pytest.raises(ValueError, match="EI"):
            sol.calcola([0.0, 100.0], [0.0, 0.0], EI_kgcm2=-1.0)

    def test_doppio_incastro_estremi_nulli(self):
        """Con bc='doppio_incastro': v(0)=0, v(L)=0 (e slope≈0 agli estremi)."""
        x = list(np.linspace(0.0, 400.0, 41))
        M = [1.0 * xi * (400.0 - xi) / 2.0 for xi in x]
        diag = SolutoreFEM("doppio_incastro").calcola(x, M, EI_kgcm2=1e7)
        assert abs(diag.v_cm[0]) < 1e-10
        assert abs(diag.v_cm[-1]) < 1e-10

    def test_u_cm_sempre_zero(self):
        """u(x) deve essere zero per elementi singoli."""
        x = [0.0, 100.0, 200.0]
        M = [0.0, 50.0, 0.0]
        diag = SolutoreFEM().calcola(x, M, EI_kgcm2=1e6)
        assert all(abs(u) < 1e-15 for u in diag.u_cm)


# ---------------------------------------------------------------------------
# grafico_spostamenti (headless)
# ---------------------------------------------------------------------------

class TestGraficoSpostamenti:
    matplotlib = pytest.importorskip("matplotlib")

    def test_crea_figura(self):
        import matplotlib.pyplot as plt

        d = DiagrammaSpostamenti(
            x_cm=list(np.linspace(0, 400, 20)),
            v_cm=list(np.sin(np.linspace(0, math.pi, 20)) * -0.8),
            u_cm=[0.0] * 20,
            etichetta="Test",
            solutore="analitico",
        )
        fig, (ax_v, ax_u) = grafico_spostamenti(d)
        assert fig is not None
        plt.close(fig)

    def test_scala_non_modifica_dati(self):
        """Il fattore di scala è solo visivo, non altera DiagrammaSpostamenti."""
        import matplotlib.pyplot as plt

        d = DiagrammaSpostamenti(
            x_cm=[0.0, 100.0, 200.0],
            v_cm=[0.0, -1.0, 0.0],
            u_cm=[0.0, 0.0, 0.0],
        )
        grafico_spostamenti(d, scala=100.0)
        # v_cm originali invariati
        assert d.v_cm[1] == pytest.approx(-1.0)
        plt.close("all")
