"""Test suite per fondazioni profonde su pali (P.3)."""

from __future__ import annotations

import math

import pytest

from src.geotecnica.models import InputGruppoPali, InputPortanzaPalo, TipologiaPalo
from src.geotecnica.pali import (
    _fattore_adesione_argilla,
    _area_punta_cm2,
    _area_laterale_cm2,
    calcola_efficienza_gruppo,
    calcola_portanza_palo,
    efficienza_gruppo_converse_labarre,
    portanza_laterale_argilla_kg,
    portanza_laterale_cpt_kg,
    portanza_laterale_spt_kg,
    portanza_punta_argilla_kg,
    portanza_punta_cpt_kg,
    portanza_punta_spt_kg,
)


# ---------------------------------------------------------------------------
# Fattore di adesione α
# ---------------------------------------------------------------------------


def test_fattore_adesione_bassa_resistenza():
    # c_u ≤ 0.255 kg/cm2 (~25 kPa): α = 1.0
    assert _fattore_adesione_argilla(0.20) == pytest.approx(1.0)


def test_fattore_adesione_alta_resistenza():
    # c_u ≥ 0.510 kg/cm2 (~50 kPa): α = 0.5
    assert _fattore_adesione_argilla(0.60) == pytest.approx(0.5)


def test_fattore_adesione_intermedio():
    # interpolazione tra 0.255 e 0.510
    alpha = _fattore_adesione_argilla(0.3825)  # punto medio → α = 0.75
    assert 0.5 < alpha < 1.0


def test_fattore_adesione_zero():
    assert _fattore_adesione_argilla(0.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Aree
# ---------------------------------------------------------------------------


def test_area_punta_formula():
    d = 50.0  # cm
    atteso = math.pi * (25.0) ** 2
    assert _area_punta_cm2(d) == pytest.approx(atteso)


def test_area_laterale_formula():
    d, l = 50.0, 1500.0  # cm
    atteso = math.pi * d * l
    assert _area_laterale_cm2(d, l) == pytest.approx(atteso)


# ---------------------------------------------------------------------------
# Portanza in argilla
# ---------------------------------------------------------------------------


def test_portanza_punta_argilla():
    # Palo Φ500, c_u = 0.816 kg/cm2 (~80 kPa)
    d = 50.0
    c_u = 80.0 / 98.0665  # conversione kPa → kg/cm2
    q_p = portanza_punta_argilla_kg(d, c_u)
    a_p = _area_punta_cm2(d)
    assert q_p == pytest.approx(9.0 * c_u * a_p, rel=1e-6)


def test_portanza_laterale_argilla():
    d, l = 50.0, 1500.0
    c_u = 80.0 / 98.0665
    q_s = portanza_laterale_argilla_kg(d, l, c_u)
    assert q_s > 0


def test_portanza_totale_argilla_positiva():
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.ARGILLA,
        diametro_palo_cm=50.0,
        lunghezza_palo_cm=1500.0,
        c_u_kgcm2=80.0 / 98.0665,
        forza_verticale_kg=100_000.0,
    )
    ris = calcola_portanza_palo(inp)
    assert ris.q_lim_kg > 0
    assert ris.q_punta_kg > 0
    assert ris.q_laterale_kg > 0


def test_verifica_palo_argilla_carichi_ridotti():
    # Carico molto basso → verifica OK
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.ARGILLA,
        diametro_palo_cm=50.0,
        lunghezza_palo_cm=1500.0,
        c_u_kgcm2=80.0 / 98.0665,
        forza_verticale_kg=1_000.0,  # basso
    )
    ris = calcola_portanza_palo(inp)
    assert ris.verificato is True
    assert ris.rapporto_utilizzo < 1.0


def test_verifica_palo_argilla_sovraccarico():
    # Carico esagerato → verifica KO
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.ARGILLA,
        diametro_palo_cm=50.0,
        lunghezza_palo_cm=1500.0,
        c_u_kgcm2=80.0 / 98.0665,
        forza_verticale_kg=10_000_000.0,  # molto alto
    )
    ris = calcola_portanza_palo(inp)
    assert ris.verificato is False
    assert ris.rapporto_utilizzo > 1.0


# ---------------------------------------------------------------------------
# Portanza da SPT (sabbia)
# ---------------------------------------------------------------------------


def test_portanza_punta_spt():
    d = 40.0
    n_spt = 20.0
    q_p = portanza_punta_spt_kg(d, n_spt)
    assert q_p == pytest.approx(4.0 * 20.0 * _area_punta_cm2(d))


def test_portanza_laterale_spt():
    d, l = 40.0, 1000.0
    n_spt = 20.0
    q_s = portanza_laterale_spt_kg(d, l, n_spt)
    assert q_s == pytest.approx(0.2 * 20.0 * _area_laterale_cm2(d, l))


def test_calcola_portanza_palo_sabbia_spt():
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.SABBIA_SPT,
        diametro_palo_cm=40.0,
        lunghezza_palo_cm=1000.0,
        n_spt_medio=20.0,
        forza_verticale_kg=50_000.0,
    )
    ris = calcola_portanza_palo(inp)
    assert ris.q_lim_kg > 0
    assert len(ris.passaggi_calcolo) > 0


# ---------------------------------------------------------------------------
# Portanza da CPT (sabbia)
# ---------------------------------------------------------------------------


def test_portanza_punta_cpt():
    d = 40.0
    q_c = 2.0  # kg/cm2
    q_p = portanza_punta_cpt_kg(d, q_c)
    assert q_p == pytest.approx(0.40 * q_c * _area_punta_cm2(d))


def test_portanza_laterale_cpt():
    d, l = 40.0, 1000.0
    q_c = 2.0
    q_s = portanza_laterale_cpt_kg(d, l, q_c)
    assert q_s == pytest.approx(q_c / 100.0 * _area_laterale_cm2(d, l))


def test_calcola_portanza_palo_cpt():
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.SABBIA_CPT,
        diametro_palo_cm=40.0,
        lunghezza_palo_cm=1000.0,
        q_c_kgcm2=2.0,
        forza_verticale_kg=50_000.0,
    )
    ris = calcola_portanza_palo(inp)
    assert ris.q_lim_kg > 0


# ---------------------------------------------------------------------------
# Passaggi calcolo
# ---------------------------------------------------------------------------


def test_passaggi_calcolo_presenti():
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.ARGILLA,
        diametro_palo_cm=50.0,
        lunghezza_palo_cm=1500.0,
        c_u_kgcm2=0.5,
        forza_verticale_kg=100_000.0,
    )
    ris = calcola_portanza_palo(inp)
    assert len(ris.passaggi_calcolo) >= 5
    assert any("Q_lim" in s for s in ris.passaggi_calcolo)


# ---------------------------------------------------------------------------
# Efficienza gruppo pali (Converse-Labarre)
# ---------------------------------------------------------------------------


def test_efficienza_palo_singolo():
    # Gruppo 1x1: efficienza = 1.0
    eta = efficienza_gruppo_converse_labarre(1, 1, 50.0, 150.0)
    assert eta == pytest.approx(1.0)


def test_efficienza_gruppo_ridotta():
    # Gruppo 2x2 con interasse piccolo: efficienza < 1
    eta = efficienza_gruppo_converse_labarre(2, 2, 50.0, 100.0)
    assert 0.0 < eta < 1.0


def test_efficienza_gruppo_interasse_grande():
    # Interasse molto grande → theta ≈ 0 → efficienza → 1
    eta = efficienza_gruppo_converse_labarre(2, 2, 50.0, 10000.0)
    assert eta > 0.95


def test_calcola_efficienza_gruppo_input():
    inp = InputGruppoPali(
        n_pali_riga=3,
        n_pali_colonna=3,
        diametro_palo_cm=50.0,
        interasse_cm=150.0,
    )
    eta = calcola_efficienza_gruppo(inp)
    assert 0.0 < eta <= 1.0


def test_to_dict_portanza_palo():
    inp = InputPortanzaPalo(
        tipologia=TipologiaPalo.ARGILLA,
        diametro_palo_cm=50.0,
        lunghezza_palo_cm=1500.0,
        c_u_kgcm2=0.5,
        forza_verticale_kg=10_000.0,
    )
    ris = calcola_portanza_palo(inp)
    d = ris.to_dict()
    assert "q_lim_kg" in d
    assert "verificato" in d
    assert "passaggi_calcolo" in d
