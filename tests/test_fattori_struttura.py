"""Test Fase U.1/U.1.5 - src.seismic.fattori_struttura."""

import pytest

from src.seismic.fattori_struttura import (
    ClasseDuttilita,
    MetodoAlpha,
    SistemaStrutturale,
    calcola_fattori_struttura,
    calcola_k_w,
    calcola_q0,
    stima_alpha_u_alpha_1,
)


def test_stima_alpha_telaio_un_piano() -> None:
    assert stima_alpha_u_alpha_1(SistemaStrutturale.TELAIO, n_piani=1) == pytest.approx(1.30)


def test_stima_alpha_telaio_tre_piani() -> None:
    assert stima_alpha_u_alpha_1(SistemaStrutturale.TELAIO, n_piani=3) == pytest.approx(1.35)


def test_stima_alpha_parete() -> None:
    assert stima_alpha_u_alpha_1(SistemaStrutturale.PARETE, n_piani=5) == pytest.approx(1.08)


def test_calcola_q0_cd_a() -> None:
    assert calcola_q0(ClasseDuttilita.CD_A, 1.3) == pytest.approx(5.85)


def test_calcola_q0_cd_b() -> None:
    assert calcola_q0(ClasseDuttilita.CD_B, 1.3) == pytest.approx(3.9)


def test_calcola_q0_cd_l() -> None:
    assert calcola_q0(ClasseDuttilita.CD_L, 1.3) == pytest.approx(1.5)


def test_kw_telaio() -> None:
    assert calcola_k_w(SistemaStrutturale.TELAIO, alpha_0=0.0) == pytest.approx(1.0)


def test_kw_parete() -> None:
    # (1 + 0.5) / 3 = 0.5
    assert calcola_k_w(SistemaStrutturale.PARETE, alpha_0=0.5) == pytest.approx(0.5)


def test_calcolo_completo_tabella_cd_a_telaio() -> None:
    ris = calcola_fattori_struttura(
        classe=ClasseDuttilita.CD_A,
        sistema=SistemaStrutturale.TELAIO,
        n_piani=3,
    )
    # q = 4.5 * 1.35 * 1.0 = 6.075
    assert ris.alpha_u_alpha_1 == pytest.approx(1.35)
    assert ris.q_0 == pytest.approx(6.075)
    assert ris.q == pytest.approx(6.075)
    assert ris.warning_q_superiore_6 is True


def test_calcolo_cd_l_forza_q_minimo() -> None:
    ris = calcola_fattori_struttura(
        classe=ClasseDuttilita.CD_L,
        sistema=SistemaStrutturale.PARETE,
        n_piani=2,
        alpha_0=0.2,
    )
    # q preliminare = 1.5 * 0.4 = 0.6 -> forzato a 1.5
    assert ris.q_0 == pytest.approx(1.5)
    assert ris.q == pytest.approx(1.5)


def test_calcolo_con_riduzioni_irregolarita_e_torsione() -> None:
    ris = calcola_fattori_struttura(
        classe=ClasseDuttilita.CD_B,
        sistema=SistemaStrutturale.TELAIO,
        n_piani=3,
        riduci_irregolarita=True,
        riduci_eccentricita_torsionale=True,
    )
    # q base = 3.0 * 1.35 = 4.05 ; riduzione = 0.8 * 0.9 = 0.72
    assert ris.q == pytest.approx(4.05 * 0.72)


def test_calcolo_alpha_da_pushover() -> None:
    ris = calcola_fattori_struttura(
        classe=ClasseDuttilita.CD_B,
        sistema=SistemaStrutturale.TELAIO,
        n_piani=4,
        metodo_alpha=MetodoAlpha.PUSHOVER,
        taglio_collasso=1200.0,
        taglio_prima_plasticizzazione=1000.0,
    )
    assert ris.alpha_u_alpha_1 == pytest.approx(1.2)
    assert ris.q_0 == pytest.approx(3.6)
    assert ris.q == pytest.approx(3.6)


def test_errore_pushover_senza_tagli() -> None:
    with pytest.raises(ValueError):
        calcola_fattori_struttura(
            classe=ClasseDuttilita.CD_A,
            sistema=SistemaStrutturale.TELAIO,
            n_piani=3,
            metodo_alpha=MetodoAlpha.PUSHOVER,
        )


def test_errore_alpha_override_non_positivo() -> None:
    with pytest.raises(ValueError):
        calcola_fattori_struttura(
            classe=ClasseDuttilita.CD_A,
            sistema=SistemaStrutturale.TELAIO,
            n_piani=3,
            alpha_u_alpha_1_override=0.0,
        )
