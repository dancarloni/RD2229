"""Test Fase U.4 - src.seismic.nodi_trave_pilastro."""

import pytest

from src.seismic.nodi_trave_pilastro import (
    calcola_eta,
    calcola_v_jhd,
    calcola_v_rd_diagonale,
    stima_a_sh_min,
    verifica_nodo_trave_pilastro,
)


def test_v_jhd() -> None:
    v = calcola_v_jhd(a_s1=8.0, f_yd=400.0, n_g=200.0, v_c=300.0)
    assert v == pytest.approx(8 * 400 * (1 + 200 / (8 * 400)) - 300)


def test_eta_standard() -> None:
    eta, warning = calcola_eta(f_ck=30.0)
    assert eta > 0
    assert warning is False


def test_eta_fallback_fck_alto() -> None:
    eta, warning = calcola_eta(f_ck=350.0)
    assert eta == pytest.approx(0.05)
    assert warning is True


def test_v_rd_diagonale() -> None:
    v_rd = calcola_v_rd_diagonale(eta=0.5, f_cd=17.0, b_j=40.0, h_jc=40.0, nu_d=0.2)
    assert v_rd > 0


def test_v_rd_radicando_negativo() -> None:
    v_rd = calcola_v_rd_diagonale(eta=0.1, f_cd=17.0, b_j=40.0, h_jc=40.0, nu_d=0.5)
    assert v_rd == pytest.approx(0.0)


def test_a_sh_min() -> None:
    a_sh = stima_a_sh_min(v_jhd=200.0, f_yd=400.0, braccio=1.0)
    assert a_sh == pytest.approx(0.5)


def test_verifica_nodo_ok() -> None:
    res = verifica_nodo_trave_pilastro(
        a_s1=2.0,
        f_yd=100.0,
        n_g=10.0,
        v_c=150.0,
        f_ck=30.0,
        f_cd=17.0,
        b_j=40.0,
        h_jc=40.0,
        nu_d=0.1,
    )
    assert res.verificato is True


def test_verifica_nodo_non_ok() -> None:
    res = verifica_nodo_trave_pilastro(
        a_s1=20.0,
        f_yd=400.0,
        n_g=500.0,
        v_c=0.0,
        f_ck=30.0,
        f_cd=5.0,
        b_j=20.0,
        h_jc=20.0,
        nu_d=0.7,
    )
    assert res.verificato is False


def test_warning_nu_d_alto() -> None:
    res = verifica_nodo_trave_pilastro(
        a_s1=5.0,
        f_yd=300.0,
        n_g=100.0,
        v_c=50.0,
        f_ck=300.0,
        f_cd=12.0,
        b_j=30.0,
        h_jc=30.0,
        nu_d=0.9,
    )
    assert res.warning_nu_d_alto is True
    assert res.warning_fck_alto is True
