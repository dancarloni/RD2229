"""Test Fase U.2 - src.seismic.duttilita."""

import pytest

from src.seismic.duttilita import (
    calcola_epsilon_cu_confinata,
    calcola_mu_phi_disponibile,
    calcola_mu_phi_richiesta,
    calcola_rho_sx_minimo,
    calcola_theta_u_circolare,
    verifica_duttilita,
)


def test_mu_phi_richiesta_t1_inferiore_tc() -> None:
    mu, warning = calcola_mu_phi_richiesta(q=4.0, t_1=0.4, t_c=0.5)
    assert mu == pytest.approx(1 + 2 * (4 - 1) * (0.5 / 0.4))
    assert warning is False


def test_mu_phi_richiesta_t1_maggiore_tc() -> None:
    mu, warning = calcola_mu_phi_richiesta(q=4.0, t_1=0.8, t_c=0.5)
    assert mu == pytest.approx(2 * 4.0 - 1)
    assert warning is False


def test_mu_phi_warning_zona_tc() -> None:
    mu, warning = calcola_mu_phi_richiesta(q=3.5, t_1=0.52, t_c=0.5)
    assert mu > 0
    assert warning is True


def test_epsilon_cu_confinata() -> None:
    eps = calcola_epsilon_cu_confinata(alpha_confinamento=0.8, rho_sx=0.02, f_yw=450.0, f_c=25.0)
    assert eps == pytest.approx(0.0035 + 0.1 * 0.8 * 0.02 * 450 / 25)


def test_mu_phi_disponibile() -> None:
    mu = calcola_mu_phi_disponibile(epsilon_cu=0.004, epsilon_y=0.002, x_su_d=0.4)
    assert mu == pytest.approx(5.0)


def test_rho_sx_minimo_limite_001() -> None:
    rho = calcola_rho_sx_minimo(
        f_cd=17.0,
        f_yd=391.0,
        nu_d=0.05,
        mu_phi_richiesta=2.0,
        epsilon_sy_d=0.002,
        d_s=16.0,
        b_0=300.0,
    )
    assert rho == pytest.approx(0.01)


def test_theta_u_circolare() -> None:
    theta = calcola_theta_u_circolare(
        f_c=25.0,
        nu_d=0.4,
        rho_tot=0.02,
        rho_b=0.015,
        d_l=16.0,
        l_p=200.0,
    )
    assert isinstance(theta, float)


def test_verifica_duttilita_ok() -> None:
    res = verifica_duttilita(
        q=2.5,
        t_1=0.8,
        t_c=0.5,
        alpha_confinamento=0.8,
        rho_sx=0.03,
        f_yw=450.0,
        f_c=25.0,
        epsilon_y=0.002,
        x_su_d=0.25,
        f_cd=17.0,
        f_yd=391.0,
        nu_d=0.2,
        epsilon_sy_d=0.002,
        d_s=16.0,
        b_0=300.0,
    )
    assert res.verifica_ok is True


def test_verifica_duttilita_non_ok() -> None:
    res = verifica_duttilita(
        q=4.5,
        t_1=0.4,
        t_c=0.5,
        alpha_confinamento=0.6,
        rho_sx=0.005,
        f_yw=450.0,
        f_c=35.0,
        epsilon_y=0.0025,
        x_su_d=0.40,
        f_cd=20.0,
        f_yd=391.0,
        nu_d=0.4,
        epsilon_sy_d=0.002,
        d_s=16.0,
        b_0=300.0,
    )
    assert res.verifica_ok is False


def test_errori_input() -> None:
    with pytest.raises(ValueError):
        calcola_mu_phi_richiesta(q=0, t_1=0.5, t_c=0.5)
