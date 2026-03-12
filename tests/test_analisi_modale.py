"""Test Fase U.5 - src.seismic.analisi_modale."""

import numpy as np
import pytest

from src.seismic.analisi_modale import (
    combina_cqc,
    combina_srss,
    fattore_partecipazione,
    massa_modale_effettiva,
    risolvi_autovalori_modali,
    taglio_base_modale,
    verifica_partecipazione_minima,
)


def test_autovalori_periodi() -> None:
    k = np.array([[20.0, 0.0], [0.0, 80.0]])
    m = np.array([[2.0, 0.0], [0.0, 2.0]])
    res = risolvi_autovalori_modali(k, m)
    assert len(res.omega) == 2
    assert np.all(res.periodi > 0)


def test_fattore_partecipazione() -> None:
    masse = np.array([10.0, 20.0])
    modo = np.array([1.0, 1.0])
    gamma = fattore_partecipazione(masse, modo)
    assert gamma == pytest.approx((10 + 20) / (10 + 20))


def test_massa_modale_effettiva() -> None:
    masse = np.array([10.0, 20.0])
    modo = np.array([1.0, 1.0])
    m_eff = massa_modale_effettiva(masse, modo)
    assert m_eff > 0


def test_verifica_partecipazione_minima() -> None:
    ok = verifica_partecipazione_minima(np.array([70.0, 20.0]), np.array([100.0]))
    assert ok is True


def test_srss() -> None:
    e = combina_srss(np.array([3.0, 4.0]))
    assert e == pytest.approx(5.0)


def test_cqc() -> None:
    e = combina_cqc(np.array([3.0, 4.0]), np.array([10.0, 20.0]), xi=0.05)
    assert e > 0


def test_taglio_base_modale() -> None:
    assert taglio_base_modale(100.0, 0.25) == pytest.approx(25.0)
