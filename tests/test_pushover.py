"""Test Fase U.6 - src.seismic.pushover."""

import numpy as np
import pytest

from src.seismic.pushover import (
    calcola_alpha_u_alpha_1_da_curva,
    converti_adrs,
    pattern_triangolare,
    pattern_uniforme,
    punto_prestazione_intersezione,
    pushover_simplificata,
)


def test_pattern_triangolare() -> None:
    f = pattern_triangolare(np.array([10.0, 10.0, 10.0]), np.array([3.0, 6.0, 9.0]), 90.0)
    assert np.sum(f) == pytest.approx(90.0)
    assert f[2] > f[1] > f[0]


def test_pattern_uniforme() -> None:
    f = pattern_uniforme(3, 90.0)
    assert np.allclose(f, np.array([30.0, 30.0, 30.0]))


def test_pushover_curve_basic() -> None:
    curva = pushover_simplificata(k_iniziale=1000.0, delta_y=0.02, delta_u=0.2, n_step=50)
    assert len(curva.spostamenti) == 50
    assert curva.indice_prima_plasticizzazione > 0
    assert curva.indice_collasso >= curva.indice_prima_plasticizzazione


def test_alpha_from_curve() -> None:
    curva = pushover_simplificata(k_iniziale=1200.0, delta_y=0.02, delta_u=0.25, n_step=70)
    alpha = calcola_alpha_u_alpha_1_da_curva(curva)
    assert alpha >= 1.0


def test_converti_adrs() -> None:
    tagli = np.array([0.0, 100.0, 200.0])
    disp = np.array([0.0, 0.02, 0.04])
    sa, sd = converti_adrs(tagli, disp, m_eff=50.0, gamma_1=1.2)
    assert len(sa) == 3
    assert len(sd) == 3


def test_punto_prestazione() -> None:
    sd_cap = np.array([0.0, 0.05, 0.10, 0.15])
    sa_cap = np.array([0.0, 0.30, 0.25, 0.20])
    sd_dom = np.array([0.0, 0.05, 0.10, 0.15])
    sa_dom = np.array([0.35, 0.28, 0.22, 0.18])
    sd, sa = punto_prestazione_intersezione(sd_cap, sa_cap, sd_dom, sa_dom)
    assert 0.0 <= sd <= 0.15
    assert sa >= 0.0


def test_errori_input() -> None:
    with pytest.raises(ValueError):
        pattern_uniforme(0, 10.0)
    with pytest.raises(ValueError):
        pushover_simplificata(k_iniziale=0.0, delta_y=0.02, delta_u=0.2)
