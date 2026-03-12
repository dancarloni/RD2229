"""Test suite per valutazione del rischio liquefazione (P.5)."""

from __future__ import annotations

import math

import pytest

from src.geotecnica.liquefazione import (
    calcola_crr_7_5,
    calcola_csr,
    calcola_liquefazione,
    calcola_msf,
    classifica_liquefazione,
    correggi_n160,
    fattore_riduzione_r_d,
)
from src.geotecnica.models import ClasseLiquefazione, InputLiquefazione, StratoLiquefazione

# ---------------------------------------------------------------------------
# Fattore di riduzione r_d
# ---------------------------------------------------------------------------


def test_rd_superficiale():
    # z = 0: r_d = 1.0
    assert fattore_riduzione_r_d(0.0) == pytest.approx(1.0)


def test_rd_z5():
    # z = 5 m: r_d = 1 - 0.00765*5 = 0.96175
    assert fattore_riduzione_r_d(5.0) == pytest.approx(1.0 - 0.00765 * 5.0)


def test_rd_z10():
    # z = 10 m (zona 9.15 < z ≤ 23): r_d = 1.174 - 0.0267*10
    assert fattore_riduzione_r_d(10.0) == pytest.approx(1.174 - 0.0267 * 10.0, rel=1e-5)


def test_rd_z25():
    # z = 25 m: r_d = 0.744 - 0.008*25 = 0.544
    assert fattore_riduzione_r_d(25.0) == pytest.approx(0.744 - 0.008 * 25.0, rel=1e-5)


def test_rd_non_negativo():
    # r_d ≥ 0.1 per qualsiasi profondità
    assert fattore_riduzione_r_d(100.0) >= 0.1


# ---------------------------------------------------------------------------
# CSR
# ---------------------------------------------------------------------------


def test_csr_formula():
    # sigma_v = sigma_v_eff → rapporto = 1.0
    csr = calcola_csr(100.0, 100.0, 0.20, 5.0)
    r_d = 1.0 - 0.00765 * 5.0
    atteso = 0.65 * 1.0 * 0.20 * r_d
    assert csr == pytest.approx(atteso, rel=1e-5)


def test_csr_falda_alta():
    # Con falda in superficie: sigma_v ≈ sigma_v_eff → rapporto prossimo a 1
    csr = calcola_csr(100.0, 50.0, 0.30, 3.0)
    assert csr > 0


def test_csr_sigma_eff_zero_errore():
    with pytest.raises(ValueError):
        calcola_csr(100.0, 0.0, 0.20, 5.0)


# ---------------------------------------------------------------------------
# Correzione N_{1,60}
# ---------------------------------------------------------------------------


def test_n160_bassa_tensione():
    # sigma_v_eff bassa → C_N grande → N_{1,60} > N_SPT
    n160 = correggi_n160(10, 50.0)
    c_n = min(math.sqrt(100.0 / 50.0), 1.7)
    assert n160 == pytest.approx(10 * c_n, rel=1e-6)


def test_n160_alta_tensione():
    # sigma_v_eff alta → C_N < 1 → N_{1,60} < N_SPT
    n160 = correggi_n160(20, 200.0)
    c_n = min(math.sqrt(100.0 / 200.0), 1.7)
    assert n160 == pytest.approx(20 * c_n, rel=1e-6)


def test_n160_sigma_eff_zero_errore():
    with pytest.raises(ValueError):
        correggi_n160(10, 0.0)


# ---------------------------------------------------------------------------
# CRR
# ---------------------------------------------------------------------------


def test_crr_n160_zero():
    # N_{1,60}=0: CRR_7.5 minimo
    crr = calcola_crr_7_5(0.0)
    assert crr > 0


def test_crr_n160_alto():
    # N_{1,60} ≥ 30: non liquefacibile
    crr = calcola_crr_7_5(30.0)
    assert crr >= 2.0  # valore elevato


def test_crr_crescente():
    # CRR aumenta all'aumentare di N_{1,60}
    crr5 = calcola_crr_7_5(5.0)
    crr15 = calcola_crr_7_5(15.0)
    crr25 = calcola_crr_7_5(25.0)
    assert crr5 < crr15 < crr25


# ---------------------------------------------------------------------------
# MSF
# ---------------------------------------------------------------------------


def test_msf_m75():
    # M=7.5: MSF = 10^2.24 / 7.5^2.56 ≈ 1.0
    msf = calcola_msf(7.5)
    assert msf == pytest.approx(10.0**2.24 / 7.5**2.56, rel=1e-5)


def test_msf_m65_maggiore_m75():
    # M piccola → MSF > 1 (terreno resistente a più cicli)
    assert calcola_msf(6.5) > calcola_msf(7.5)


def test_msf_m80_minore_m75():
    # M grande → MSF < 1
    assert calcola_msf(8.0) < calcola_msf(7.5)


# ---------------------------------------------------------------------------
# Classificazione
# ---------------------------------------------------------------------------


def test_classifica_bassa():
    assert classifica_liquefazione(0.5) == ClasseLiquefazione.BASSA


def test_classifica_media():
    assert classifica_liquefazione(5.0) == ClasseLiquefazione.MEDIA


def test_classifica_alta():
    assert classifica_liquefazione(20.0) == ClasseLiquefazione.ALTA


# ---------------------------------------------------------------------------
# Calcolo completo
# ---------------------------------------------------------------------------


def _crea_strato(z: float, dz: float = 1.0, n_spt: int = 10) -> StratoLiquefazione:
    gamma_kn_m3 = 18.0  # kN/m3
    sigma_v = gamma_kn_m3 * z  # kPa (approssimato)
    sigma_v_eff = sigma_v * 0.6  # semplificazione: falda a 1/3 della profondità
    return StratoLiquefazione(
        profondita_centro_m=z,
        spessore_m=dz,
        n_spt_grezzo=n_spt,
        sigma_v_kpa=max(sigma_v, 1.0),
        sigma_v_eff_kpa=max(sigma_v_eff, 1.0),
    )


def test_calcola_liquefazione_singolo_strato():
    strato = _crea_strato(5.0, n_spt=5)
    inp = InputLiquefazione(strati=[strato], a_max_g=0.30, magnitudo=6.5)
    ris = calcola_liquefazione(inp)
    assert len(ris.strati) == 1
    assert ris.indice_il >= 0.0


def test_calcola_liquefazione_strato_resistente():
    # N_SPT alto → FS >> 1 → IL vicino a 0
    strato = _crea_strato(5.0, n_spt=35)
    inp = InputLiquefazione(strati=[strato], a_max_g=0.20, magnitudo=7.0)
    ris = calcola_liquefazione(inp)
    assert ris.strati[0].fs > 1.0
    assert ris.classe == ClasseLiquefazione.BASSA


def test_calcola_liquefazione_strato_debole():
    # N_SPT basso + accelerazione alta → FS < 1 possibile
    strato = StratoLiquefazione(
        profondita_centro_m=3.0,
        spessore_m=2.0,
        n_spt_grezzo=5,
        sigma_v_kpa=60.0,
        sigma_v_eff_kpa=30.0,
    )
    inp = InputLiquefazione(strati=[strato], a_max_g=0.40, magnitudo=7.0)
    ris = calcola_liquefazione(inp)
    assert ris.indice_il > 0


def test_calcola_liquefazione_strato_oltre_20m_escluso():
    strati = [
        _crea_strato(5.0),
        _crea_strato(25.0),  # oltre il limite di 20 m
    ]
    inp = InputLiquefazione(strati=strati, a_max_g=0.20)
    ris = calcola_liquefazione(inp)
    assert len(ris.strati) == 1  # solo lo strato a 5 m
    assert any("25" in s and "escluso" in s for s in ris.passaggi_calcolo)


def test_calcola_liquefazione_passaggi_globali():
    strato = _crea_strato(5.0)
    inp = InputLiquefazione(strati=[strato], a_max_g=0.20)
    ris = calcola_liquefazione(inp)
    assert any("IL" in s for s in ris.passaggi_calcolo)


def test_to_dict_liquefazione():
    strato = _crea_strato(5.0)
    inp = InputLiquefazione(strati=[strato], a_max_g=0.20)
    ris = calcola_liquefazione(inp)
    d = ris.to_dict()
    assert "indice_il" in d
    assert "classe" in d
    assert "strati" in d
