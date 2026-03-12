"""Test Fase U.3 - src.seismic.gerarchia."""

import pytest

from src.seismic.gerarchia import (
    calcola_v_cd_pilastro,
    calcola_v_cd_trave,
    gamma_rd_per_classe,
    verifica_gerarchia_globale,
    verifica_nodo_gerarchia,
)


def test_gamma_rd_per_classe() -> None:
    assert gamma_rd_per_classe("CD_A") == pytest.approx(1.3)
    assert gamma_rd_per_classe("cd_b") == pytest.approx(1.2)
    assert gamma_rd_per_classe("CD_L") == pytest.approx(1.0)


def test_verifica_nodo_ok() -> None:
    esito = verifica_nodo_gerarchia(
        momenti_pilastri=[250.0, 220.0],
        momenti_travi=[150.0, 150.0],
        gamma_rd_target=1.3,
    )
    assert esito.verificato is True
    assert esito.gamma_rd_eff == pytest.approx((250 + 220) / (150 + 150))


def test_verifica_nodo_non_ok() -> None:
    esito = verifica_nodo_gerarchia(
        momenti_pilastri=[120.0, 110.0],
        momenti_travi=[130.0, 120.0],
        gamma_rd_target=1.3,
    )
    assert esito.verificato is False


def test_v_cd_trave() -> None:
    v_cd = calcola_v_cd_trave(
        m_rb_sinistra=120.0, m_rb_destra=140.0, luce_netta=5.0, v_g_pm_e_su_2=10.0
    )
    assert v_cd == pytest.approx((120 + 140) / 5 + 10)


def test_v_cd_pilastro() -> None:
    v_cd = calcola_v_cd_pilastro(
        m_rc_top=180.0, m_rc_bot=160.0, altezza_netta=3.2, gamma_rd_target=1.3
    )
    assert v_cd == pytest.approx(1.3 * (180 + 160) / 3.2)


def test_verifica_globale() -> None:
    res = verifica_gerarchia_globale(
        nodi=[
            ([250.0, 220.0], [150.0, 150.0]),
            ([120.0, 110.0], [130.0, 120.0]),
            ([260.0, 210.0], [170.0, 150.0]),
        ],
        gamma_rd_target=1.3,
    )
    assert res.nodi_verificati == 2
    assert res.nodi_non_verificati == 1


def test_errori_input() -> None:
    with pytest.raises(ValueError):
        verifica_nodo_gerarchia(momenti_pilastri=[100], momenti_travi=[0], gamma_rd_target=1.3)
    with pytest.raises(ValueError):
        calcola_v_cd_trave(100, 100, 0)
    with pytest.raises(ValueError):
        calcola_v_cd_pilastro(100, 100, 0, 1.3)
