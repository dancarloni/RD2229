import pytest

from src.geotecnica import (
    InputCedimenti,
    UnitaTensione,
    calcola_cedimenti,
    cedimento_consolidazione_primaria,
    cedimento_elastico_boussinesq,
    coefficiente_tempo_consolidazione,
    grado_consolidazione_medio,
)


def test_cedimento_elastico_formula_base() -> None:
    dati = InputCedimenti(
        pressione_media=1.0,
        larghezza_fondazione_cm=200.0,
        modulo_elastico_terreno=2000.0,
        coeff_poisson=0.30,
        fattore_influenza_i_rho=1.0,
    )
    rho = cedimento_elastico_boussinesq(dati)
    assert rho == pytest.approx(0.091, rel=1e-2)


def test_cedimento_consolidazione_positivo_se_sigma_aumenta() -> None:
    dati = InputCedimenti(
        pressione_media=0.8,
        larghezza_fondazione_cm=180.0,
        modulo_elastico_terreno=1500.0,
        coeff_poisson=0.30,
        spessore_strato_consolidante_cm=500.0,
        indice_compressione_cc=0.30,
        indice_vuoti_e0=0.80,
        sigma_eff_iniziale=1.0,
        sigma_eff_finale=2.0,
    )
    rho_c = cedimento_consolidazione_primaria(dati)
    assert rho_c > 0.0


def test_cedimento_totale_e_somma_componenti() -> None:
    dati = InputCedimenti(
        pressione_media=0.9,
        larghezza_fondazione_cm=220.0,
        modulo_elastico_terreno=1800.0,
        coeff_poisson=0.28,
        fattore_influenza_i_rho=1.1,
        spessore_strato_consolidante_cm=400.0,
        indice_compressione_cc=0.25,
        indice_vuoti_e0=0.75,
        sigma_eff_iniziale=1.2,
        sigma_eff_finale=2.1,
    )
    risultato = calcola_cedimenti(dati)
    assert risultato.cedimento_totale_cm == pytest.approx(
        risultato.cedimento_immediato_cm + risultato.cedimento_consolidazione_cm
    )


def test_input_kpa_equivalente_a_kg_cm2() -> None:
    dati_kg = InputCedimenti(
        pressione_media=1.0,
        larghezza_fondazione_cm=200.0,
        modulo_elastico_terreno=2000.0,
        coeff_poisson=0.30,
        unita_tensione=UnitaTensione.KG_CM2,
    )
    dati_kpa = InputCedimenti(
        pressione_media=98.0665,
        larghezza_fondazione_cm=200.0,
        modulo_elastico_terreno=196133.0,
        coeff_poisson=0.30,
        unita_tensione=UnitaTensione.KPA,
    )
    rho_kg = cedimento_elastico_boussinesq(dati_kg)
    rho_kpa = cedimento_elastico_boussinesq(dati_kpa)
    assert rho_kg == pytest.approx(rho_kpa, rel=1e-5)


def test_grado_consolidazione_limiti() -> None:
    assert grado_consolidazione_medio(0.0) == 0.0
    assert 0.0 < grado_consolidazione_medio(0.05) < 1.0
    assert 0.0 < grado_consolidazione_medio(1.0) <= 1.0


def test_coefficiente_tempo_consolidazione() -> None:
    t_v = coefficiente_tempo_consolidazione(c_v_cm2_s=0.001, t_secondi=3600.0, h_d_cm=100.0)
    assert t_v == pytest.approx(0.00036)
