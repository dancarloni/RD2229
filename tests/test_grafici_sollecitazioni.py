"""Test per src/grafici/sollecitazioni.py e src/grafici/inviluppi.py."""

import math

import numpy as np
import pytest

from src.grafici.sollecitazioni import DiagrammaSollecitazioni, grafico_sollecitazioni
from src.grafici.inviluppi import (
    InviluppoSollecitazioni,
    inviluppo_sollecitazioni,
    grafico_inviluppo,
)

matplotlib = pytest.importorskip("matplotlib")


# ---------------------------------------------------------------------------
# DiagrammaSollecitazioni
# ---------------------------------------------------------------------------

class TestDiagrammaSollecitazioni:
    def test_costruttore_diretto(self):
        d = DiagrammaSollecitazioni(
            x_cm=[0.0, 100.0, 200.0],
            M_kgcm=[0.0, 5000.0, 0.0],
            T_kg=[100.0, 0.0, -100.0],
            N_kg=[0.0, 0.0, 0.0],
            etichetta="Test",
            norma="NTC2018",
        )
        assert len(d.x_cm) == 3
        assert d.M_kgcm[1] == pytest.approx(5000.0)

    def test_lunghezze_incompatibili(self):
        with pytest.raises(ValueError, match="stessa lunghezza"):
            DiagrammaSollecitazioni(
                x_cm=[0.0, 100.0],
                M_kgcm=[0.0],
                T_kg=[0.0, 0.0],
                N_kg=[0.0, 0.0],
            )

    def test_da_valori_estremi(self):
        d = DiagrammaSollecitazioni.da_valori_estremi(
            L_cm=500.0,
            M_sx_kgcm=0.0,
            M_dx_kgcm=0.0,
            T_sx_kg=2000.0,
            T_dx_kg=-2000.0,
            N_kg=5000.0,
            n_punti=10,
            etichetta="Trave A",
            norma="RD2229",
        )
        assert len(d.x_cm) == 10
        assert d.x_cm[0] == pytest.approx(0.0)
        assert d.x_cm[-1] == pytest.approx(500.0)
        assert d.N_kg[5] == pytest.approx(5000.0)

    def test_da_valori_estremi_interpolazione_lineare(self):
        d = DiagrammaSollecitazioni.da_valori_estremi(
            L_cm=100.0,
            M_sx_kgcm=1000.0,
            M_dx_kgcm=3000.0,
            T_sx_kg=0.0,
            T_dx_kg=0.0,
            n_punti=3,
        )
        # Metà → 2000 kg·cm
        assert d.M_kgcm[1] == pytest.approx(2000.0)

    def test_da_risultato_checks_chiavi_standard(self):
        risultato = {
            "M_Ed_kgcm": 12000.0,
            "T_Ed_kg": 800.0,
            "N_Ed_kg": 3000.0,
            "norma": "NTC2018",
            "etichetta": "Comb. 1",
        }
        d = DiagrammaSollecitazioni.da_risultato_checks(risultato, L_cm=300.0, n_punti=5)
        assert d.M_kgcm[0] == pytest.approx(12000.0)
        assert d.T_kg[2] == pytest.approx(800.0)
        assert d.norma == "NTC2018"
        assert d.etichetta == "Comb. 1"

    def test_da_risultato_checks_chiavi_alternative(self):
        risultato = {"Med_kgcm": 5000.0, "Ted_kg": 400.0, "Ned_kg": 0.0}
        d = DiagrammaSollecitazioni.da_risultato_checks(risultato, L_cm=200.0)
        assert d.M_kgcm[0] == pytest.approx(5000.0)

    def test_da_risultato_checks_valori_mancanti(self):
        """Senza chiavi M/T/N, restituisce diagramma nullo."""
        d = DiagrammaSollecitazioni.da_risultato_checks({}, L_cm=100.0, n_punti=4)
        assert all(v == pytest.approx(0.0) for v in d.M_kgcm)


# ---------------------------------------------------------------------------
# grafico_sollecitazioni (headless)
# ---------------------------------------------------------------------------

class TestGraficoSollecitazioni:
    def test_crea_figura(self):
        d = DiagrammaSollecitazioni.da_valori_estremi(
            L_cm=400.0,
            M_sx_kgcm=-8000.0,
            M_dx_kgcm=-8000.0,
            T_sx_kg=1500.0,
            T_dx_kg=-1500.0,
            n_punti=15,
        )
        fig, (ax_M, ax_T, ax_N) = grafico_sollecitazioni(d)
        assert fig is not None
        assert ax_M is not None
        assert ax_T is not None
        assert ax_N is not None
        import matplotlib
        matplotlib.pyplot.close(fig)

    def test_assi_preesistenti(self):
        import matplotlib.pyplot as plt
        d = DiagrammaSollecitazioni.da_valori_estremi(
            L_cm=200.0, M_sx_kgcm=0.0, M_dx_kgcm=0.0,
            T_sx_kg=500.0, T_dx_kg=500.0, n_punti=5
        )
        fig, (ax_M, ax_T, ax_N) = plt.subplots(3, 1)
        fig_out, axes_out = grafico_sollecitazioni(d, ax_M=ax_M, ax_T=ax_T, ax_N=ax_N, fig=fig)
        assert fig_out is fig
        plt.close(fig)


# ---------------------------------------------------------------------------
# InviluppoSollecitazioni
# ---------------------------------------------------------------------------

class TestInviluppoSollecitazioni:
    def _diagrammi(self):
        d1 = DiagrammaSollecitazioni(
            x_cm=[0.0, 50.0, 100.0],
            M_kgcm=[0.0, 2000.0, 0.0],
            T_kg=[500.0, 0.0, -500.0],
            N_kg=[1000.0, 1000.0, 1000.0],
            etichetta="Comb. 1",
        )
        d2 = DiagrammaSollecitazioni(
            x_cm=[0.0, 50.0, 100.0],
            M_kgcm=[0.0, 3000.0, 0.0],
            T_kg=[700.0, 0.0, -700.0],
            N_kg=[-500.0, -500.0, -500.0],
            etichetta="Comb. 2",
        )
        return d1, d2

    def test_inviluppo_max(self):
        d1, d2 = self._diagrammi()
        inv = inviluppo_sollecitazioni([d1, d2])
        assert inv.M_max_kgcm[1] == pytest.approx(3000.0)
        assert inv.M_min_kgcm[1] == pytest.approx(2000.0)
        assert inv.T_max_kg[0] == pytest.approx(700.0)
        assert inv.T_min_kg[0] == pytest.approx(500.0)
        assert inv.N_max_kg[0] == pytest.approx(1000.0)
        assert inv.N_min_kg[0] == pytest.approx(-500.0)

    def test_n_combinazioni(self):
        d1, d2 = self._diagrammi()
        inv = inviluppo_sollecitazioni([d1, d2])
        assert inv.n_combinazioni == 2
        assert inv.etichette == ["Comb. 1", "Comb. 2"]

    def test_ascissa_incongruente(self):
        d1, d2 = self._diagrammi()
        d_cattivo = DiagrammaSollecitazioni(
            x_cm=[0.0, 100.0],
            M_kgcm=[0.0, 0.0],
            T_kg=[0.0, 0.0],
            N_kg=[0.0, 0.0],
        )
        with pytest.raises(ValueError, match="stessa ascissa"):
            inviluppo_sollecitazioni([d1, d_cattivo])

    def test_lista_vuota(self):
        with pytest.raises(ValueError, match="almeno un"):
            inviluppo_sollecitazioni([])

    def test_grafico_inviluppo(self):
        d1, d2 = self._diagrammi()
        inv = inviluppo_sollecitazioni([d1, d2])
        fig, (ax_M, ax_T, ax_N) = grafico_inviluppo(inv, diagrammi=[d1, d2])
        assert fig is not None
        import matplotlib
        matplotlib.pyplot.close(fig)
