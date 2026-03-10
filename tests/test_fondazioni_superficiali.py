import pytest

from src.geotecnica import (
    CaricoFondazione,
    GeometriaFondazione,
    InputPortanzaFondazione,
    ParametriTerreno,
    UnitaTensione,
    verifica_portanza_slu,
)


def _input_base(**kwargs: object) -> InputPortanzaFondazione:
    terreno = ParametriTerreno(
        gamma_kg_m3=1800.0,
        phi_gradi=30.0,
        coesione=0.20,
        modulo_elastico=2000.0,
        coeff_poisson=0.30,
        unita_tensione=UnitaTensione.KG_CM2,
    )
    geometria = GeometriaFondazione(
        larghezza_b_cm=200.0,
        lunghezza_l_cm=300.0,
        profondita_piano_posa_cm=100.0,
    )
    carico = CaricoFondazione(n_verticale_kg=150000.0, h_orizzontale_kg=0.0)
    data = InputPortanzaFondazione(
        terreno=terreno,
        geometria=geometria,
        carico=carico,
        pressione_agente=0.80,
        unita_pressione_agente=UnitaTensione.KG_CM2,
    )
    for key, value in kwargs.items():
        setattr(data, key, value)
    return data


def test_verifica_portanza_da1_restituisce_due_combinazioni() -> None:
    risultato = verifica_portanza_slu(_input_base())
    assert len(risultato.risultati_slu) == 2


def test_combinazione_governante_e_quella_piu_gravosa() -> None:
    risultato = verifica_portanza_slu(_input_base())
    rapporto_governante = max(r.rapporto_utilizzo for r in risultato.risultati_slu)
    trovato = [r for r in risultato.risultati_slu if r.combinazione == risultato.combinazione_governante][0]
    assert trovato.rapporto_utilizzo == pytest.approx(rapporto_governante)


def test_input_pressione_in_kpa_viene_convertito() -> None:
    input_kg = _input_base(pressione_agente=0.90, unita_pressione_agente=UnitaTensione.KG_CM2)
    input_kpa = _input_base(pressione_agente=88.25985, unita_pressione_agente=UnitaTensione.KPA)

    ris_kg = verifica_portanza_slu(input_kg)
    ris_kpa = verifica_portanza_slu(input_kpa)

    gov_kg = [r for r in ris_kg.risultati_slu if r.combinazione == ris_kg.combinazione_governante][0]
    gov_kpa = [r for r in ris_kpa.risultati_slu if r.combinazione == ris_kpa.combinazione_governante][0]

    assert gov_kg.q_ed_kg_cm2 == pytest.approx(gov_kpa.q_ed_kg_cm2, rel=1e-8)
    assert gov_kg.rapporto_utilizzo == pytest.approx(gov_kpa.rapporto_utilizzo, rel=1e-6)


def test_eccentricita_riduce_portanza() -> None:
    base = verifica_portanza_slu(_input_base())
    ecc = verifica_portanza_slu(
        _input_base(
            geometria=GeometriaFondazione(
                larghezza_b_cm=200.0,
                lunghezza_l_cm=300.0,
                profondita_piano_posa_cm=100.0,
                eccentricita_b_cm=20.0,
            )
        )
    )

    qrd_base = min(r.q_rd_kg_cm2 for r in base.risultati_slu)
    qrd_ecc = min(r.q_rd_kg_cm2 for r in ecc.risultati_slu)
    assert qrd_ecc < qrd_base


def test_carico_orizzontale_riduce_portanza() -> None:
    senza_h = verifica_portanza_slu(_input_base())
    con_h = verifica_portanza_slu(
        _input_base(
            carico=CaricoFondazione(n_verticale_kg=150000.0, h_orizzontale_kg=30000.0)
        )
    )

    qrd_senza_h = min(r.q_rd_kg_cm2 for r in senza_h.risultati_slu)
    qrd_con_h = min(r.q_rd_kg_cm2 for r in con_h.risultati_slu)
    assert qrd_con_h < qrd_senza_h


def test_eccentricita_eccessiva_solleva_errore() -> None:
    with pytest.raises(ValueError):
        verifica_portanza_slu(
            _input_base(
                geometria=GeometriaFondazione(
                    larghezza_b_cm=200.0,
                    lunghezza_l_cm=300.0,
                    profondita_piano_posa_cm=100.0,
                    eccentricita_b_cm=120.0,
                )
            )
        )
