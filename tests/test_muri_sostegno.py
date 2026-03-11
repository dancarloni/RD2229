"""Test suite per muri di sostegno (P.4)."""

from __future__ import annotations

import math

import pytest

from src.geotecnica.models import (
    GeometriaMuro,
    InputMuroSostegno,
    ParametriTerreno,
)
from src.geotecnica.muri_sostegno import (
    ka_coulomb,
    ka_rankine,
    kp_rankine,
    punto_applicazione_spinta_cm,
    spinta_attiva_totale_kg_cm,
    verifica_muro_sostegno,
)

# ---------------------------------------------------------------------------
# Coefficiente di spinta attiva Rankine
# ---------------------------------------------------------------------------


def test_ka_rankine_phi30_orizzontale():
    # K_a = tan²(45 - 15) = tan²(30°) = 1/3
    ka = ka_rankine(30.0)
    assert ka == pytest.approx(math.tan(math.radians(30.0)) ** 2, rel=1e-5)


def test_ka_rankine_phi0():
    # phi=0: K_a = 1
    ka = ka_rankine(0.0)
    assert ka == pytest.approx(1.0, rel=1e-5)


def test_ka_rankine_beta_zero_equals_formula():
    ka_beta0 = ka_rankine(30.0, beta_gradi=0.0)
    ka_formula = math.tan(math.radians(45.0 - 15.0)) ** 2
    assert ka_beta0 == pytest.approx(ka_formula, rel=1e-5)


def test_ka_rankine_phi30_beta10():
    # β=10° < φ=30°: deve restituire un valore positivo < ka orizzontale
    ka_inclinato = ka_rankine(30.0, beta_gradi=10.0)
    ka_oriz = ka_rankine(30.0, beta_gradi=0.0)
    assert 0.0 < ka_inclinato
    # Con β > 0, il Rankine inclinato è generalmente maggiore del Rankine orizzontale
    assert ka_inclinato >= ka_oriz


def test_ka_rankine_beta_maggiore_phi_errore():
    with pytest.raises(ValueError):
        ka_rankine(20.0, beta_gradi=25.0)


# ---------------------------------------------------------------------------
# Coefficiente di spinta passiva Rankine
# ---------------------------------------------------------------------------


def test_kp_rankine_phi30():
    # K_p = tan²(45 + 15) = tan²(60°)
    kp = kp_rankine(30.0)
    assert kp == pytest.approx(math.tan(math.radians(60.0)) ** 2, rel=1e-5)


def test_kp_maggiore_ka():
    for phi in [10.0, 20.0, 30.0, 35.0]:
        assert kp_rankine(phi) > ka_rankine(phi)


# ---------------------------------------------------------------------------
# Coefficiente di spinta attiva Coulomb
# ---------------------------------------------------------------------------


def test_ka_coulomb_muro_verticale_delta0_uguale_rankine():
    # Muro verticale (α=90°), δ=0, β=0: deve coincidere con Rankine
    phi = 30.0
    ka_c = ka_coulomb(phi, delta_gradi=0.0, alpha_gradi=90.0, beta_gradi=0.0)
    ka_r = ka_rankine(phi)
    assert ka_c == pytest.approx(ka_r, rel=1e-3)


def test_ka_coulomb_delta_non_zero():
    # Con δ > 0: K_a Coulomb < K_a Rankine (attrito muro riduce spinta)
    phi = 30.0
    ka_c = ka_coulomb(phi, delta_gradi=10.0, alpha_gradi=90.0, beta_gradi=0.0)
    ka_r = ka_rankine(phi)
    assert ka_c < ka_r


def test_ka_coulomb_positivo():
    ka = ka_coulomb(30.0, 10.0, 80.0, 5.0)
    assert ka > 0


# ---------------------------------------------------------------------------
# Spinta attiva totale
# ---------------------------------------------------------------------------


def test_spinta_attiva_senza_coesione():
    gamma_kg_m3 = 18_000.0
    h_cm = 400.0
    ka = ka_rankine(30.0)
    gamma_kg_cm3 = gamma_kg_m3 / 1_000_000.0
    atteso = 0.5 * ka * gamma_kg_cm3 * h_cm**2
    calc = spinta_attiva_totale_kg_cm(gamma_kg_m3, h_cm, ka, coesione_kg_cm2=0.0)
    assert calc == pytest.approx(atteso, rel=1e-5)


def test_spinta_attiva_con_coesione_ridotta():
    gamma_kg_m3 = 18_000.0
    h_cm = 400.0
    ka = ka_rankine(30.0)
    ea_senza = spinta_attiva_totale_kg_cm(gamma_kg_m3, h_cm, ka, coesione_kg_cm2=0.0)
    ea_con = spinta_attiva_totale_kg_cm(gamma_kg_m3, h_cm, ka, coesione_kg_cm2=0.01)
    assert ea_con <= ea_senza


def test_spinta_attiva_non_negativa():
    # Terreno con elevata coesione: spinta non può essere negativa
    gamma_kg_m3 = 18_000.0
    h_cm = 100.0
    ka = ka_rankine(30.0)
    ea = spinta_attiva_totale_kg_cm(gamma_kg_m3, h_cm, ka, coesione_kg_cm2=1.0)
    assert ea >= 0.0


# ---------------------------------------------------------------------------
# Punto di applicazione
# ---------------------------------------------------------------------------


def test_punto_applicazione_h_terzo():
    h = 400.0
    assert punto_applicazione_spinta_cm(h) == pytest.approx(h / 3.0)


# ---------------------------------------------------------------------------
# Verifica completa muro di sostegno
# ---------------------------------------------------------------------------


def _crea_input_muro(
    phi: float = 30.0,
    gamma: float = 18_000.0,
    h: float = 400.0,
    b: float = 200.0,
    peso: float = 60_000.0,
) -> InputMuroSostegno:
    terreno = ParametriTerreno(
        gamma_kg_m3=gamma,
        phi_gradi=phi,
        coesione=0.0,
    )
    geometria = GeometriaMuro(
        altezza_muro_cm=h,
        larghezza_base_cm=b,
    )
    return InputMuroSostegno(
        terreno_ritenuto=terreno,
        terreno_fondazione=terreno,
        geometria=geometria,
        peso_muro_kg=peso,
    )


def test_verifica_muro_ritorna_risultato():
    inp = _crea_input_muro()
    ris = verifica_muro_sostegno(inp)
    assert ris.spinta_attiva_kg_cm > 0
    assert 0.0 < ris.coefficiente_ka < 1.0
    assert len(ris.verifiche) == 2


def test_verifica_muro_passaggi_calcolo():
    inp = _crea_input_muro()
    ris = verifica_muro_sostegno(inp)
    assert len(ris.passaggi_calcolo) >= 3
    assert any("K_a" in s for s in ris.passaggi_calcolo)


def test_verifica_muro_ribaltamento_presente():
    inp = _crea_input_muro()
    ris = verifica_muro_sostegno(inp)
    nomi = [v.nome_verifica for v in ris.verifiche]
    assert "ribaltamento" in nomi


def test_verifica_muro_scorrimento_presente():
    inp = _crea_input_muro()
    ris = verifica_muro_sostegno(inp)
    nomi = [v.nome_verifica for v in ris.verifiche]
    assert "scorrimento" in nomi


def test_muro_pesante_verifica():
    # Muro pesante con base larga → deve essere verificato
    inp = _crea_input_muro(h=300.0, b=300.0, peso=500_000.0)
    ris = verifica_muro_sostegno(inp)
    # Ribaltamento deve essere OK
    ribalt = next(v for v in ris.verifiche if v.nome_verifica == "ribaltamento")
    assert ribalt.verificato is True


def test_muro_leggero_ribaltamento_ko():
    # Muro molto leggero con base stretta → ribaltamento critico
    inp = _crea_input_muro(h=600.0, b=100.0, peso=500.0)
    ris = verifica_muro_sostegno(inp)
    ribalt = next(v for v in ris.verifiche if v.nome_verifica == "ribaltamento")
    # Con valori estremi (peso minimo), ribaltamento deve essere KO
    assert ribalt.verificato is False


def test_to_dict_muro():
    inp = _crea_input_muro()
    ris = verifica_muro_sostegno(inp)
    d = ris.to_dict()
    assert "spinta_attiva_kg_cm" in d
    assert "coefficiente_ka" in d
    assert "verifiche" in d
    assert "verificato_globale" in d


def test_verifica_coulomb_con_delta():
    # Muro verticale (α=90°) con δ>0: K_a Coulomb < K_a Rankine
    terreno = ParametriTerreno(gamma_kg_m3=18_000.0, phi_gradi=30.0)
    geo = GeometriaMuro(altezza_muro_cm=400.0, larghezza_base_cm=200.0, angolo_paramento_gradi=90.0)
    inp = InputMuroSostegno(
        terreno_ritenuto=terreno,
        terreno_fondazione=terreno,
        geometria=geo,
        peso_muro_kg=80_000.0,
        angolo_attrito_muro_gradi=15.0,
    )
    ris = verifica_muro_sostegno(inp)
    # K_a Coulomb con δ>0 su paramento verticale < K_a Rankine (φ stesso)
    ka_r = ka_rankine(30.0)
    assert ris.coefficiente_ka > 0
    assert ris.coefficiente_ka < ka_r
    assert "Coulomb" in ris.passaggi_calcolo[0]
