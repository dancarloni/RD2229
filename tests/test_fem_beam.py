import math

import numpy as np
import pytest

from src.fem import (
    CaricoConcentrato,
    CaricoDistribuitoGenerico,
    CaricoDistribuitoUniforme,
    CaricoParabolico,
    CaricoRotazioniImposte,
    CaricoTrapezoidale,
    CaricoTriangolare,
    CaricoTriangolareInverso,
    CedimentiNodali,
    ElementoBeam,
)


@pytest.fixture
def beam() -> ElementoBeam:
    return ElementoBeam(
        E=30000.0,
        A=25.0,
        I=1000.0,
        L=500.0,
        angolo=0.0,
        unita_angolo="deg",
        id_nodo_iniziale=1,
        id_nodo_finale=2,
        etichetta="B1",
    )


def test_elemento_beam_valida_input_positivi() -> None:
    with pytest.raises(ValueError):
        ElementoBeam(E=0.0, A=25.0, I=1000.0, L=500.0)


def test_angolo_in_gradi_normalizzato_in_radianti() -> None:
    element = ElementoBeam(E=1.0, A=1.0, I=1.0, L=1.0, angolo=90.0, unita_angolo="deg")
    assert element.angolo_rad == pytest.approx(math.pi / 2.0)
    assert element.coseno == pytest.approx(0.0, abs=1e-12)
    assert element.seno == pytest.approx(1.0)


def test_to_dict_include_metadati_input(beam: ElementoBeam) -> None:
    data = beam.to_dict()
    assert data["id_nodo_iniziale"] == 1
    assert data["id_nodo_finale"] == 2
    assert data["etichetta"] == "B1"
    assert data["unita_angolo"] == "deg"


def test_matrice_rigidezza_locale_elemento_orizzontale(beam: ElementoBeam) -> None:
    expected = np.array(
        [
            [1500.0, 0.0, 0.0, -1500.0, 0.0, 0.0],
            [0.0, 2.88, 720.0, 0.0, -2.88, 720.0],
            [0.0, 720.0, 240000.0, 0.0, -720.0, 120000.0],
            [-1500.0, 0.0, 0.0, 1500.0, 0.0, 0.0],
            [0.0, -2.88, -720.0, 0.0, 2.88, -720.0],
            [0.0, 720.0, 120000.0, 0.0, -720.0, 240000.0],
        ]
    )
    np.testing.assert_allclose(beam.matrice_rigidezza_locale(), expected, rtol=1e-12, atol=1e-12)


def test_matrice_trasformazione_identita_per_angolo_nullo(beam: ElementoBeam) -> None:
    np.testing.assert_allclose(beam.matrice_trasformazione(), np.eye(6), atol=1e-12)


def test_matrice_trasformazione_per_90_gradi() -> None:
    element = ElementoBeam(E=1.0, A=1.0, I=1.0, L=100.0, angolo=90.0, unita_angolo="deg")
    expected = np.array(
        [
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        ]
    )
    np.testing.assert_allclose(element.matrice_trasformazione(), expected, atol=1e-12)


def test_carico_uniforme_trasversale_formula_chiusa(beam: ElementoBeam) -> None:
    carico = CaricoDistribuitoUniforme(intensita=-2.0)
    equivalent = carico.calcola_vettore_equivalente(beam)
    expected = np.array([0.0, -500.0, -41666.666666666664, 0.0, -500.0, 41666.666666666664])
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-12)


def test_carico_triangolare_crescente_formula_chiusa(beam: ElementoBeam) -> None:
    carico = CaricoTriangolare(intensita_massima=-3.0)
    equivalent = carico.calcola_vettore_equivalente(beam)
    expected = np.array([0.0, -225.0, -25000.0, 0.0, -525.0, 37500.0])
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-12)


def test_carico_triangolare_inverso_formula_chiusa(beam: ElementoBeam) -> None:
    carico = CaricoTriangolareInverso(intensita_massima=-3.0)
    equivalent = carico.calcola_vettore_equivalente(beam)
    expected = np.array([0.0, -525.0, -37500.0, 0.0, -225.0, 25000.0])
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-12)


def test_carico_trapezoidale_come_somma_uniforme_piu_triangolare(beam: ElementoBeam) -> None:
    carico = CaricoTrapezoidale(intensita_i=-2.0, intensita_j=-5.0)
    equivalent = carico.calcola_vettore_equivalente(beam)
    expected = (
        CaricoDistribuitoUniforme(intensita=-2.0).calcola_vettore_equivalente(beam).vettore_locale
        + CaricoTriangolare(intensita_massima=-3.0).calcola_vettore_equivalente(beam).vettore_locale
    )
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-12)


def test_carico_concentrato_forza_verticale_con_shape_functions(beam: ElementoBeam) -> None:
    carico = CaricoConcentrato(valore=-10.0, posizione_x=200.0, tipo="forza_y")
    equivalent = carico.calcola_vettore_equivalente(beam)
    expected = np.array([0.0, -6.48, -720.0, 0.0, -3.52, 480.0])
    np.testing.assert_allclose(equivalent.vettore_locale, expected, atol=1e-12)


def test_carico_generico_fallback_numerico(beam: ElementoBeam) -> None:
    carico = CaricoDistribuitoGenerico(
        funzione_intensita=lambda x, l: -4.0 * x / l,
        descrizione="Lineare generico",
    )
    equivalent = carico.calcola_vettore_equivalente(beam)
    expected = (
        CaricoTriangolare(intensita_massima=-4.0).calcola_vettore_equivalente(beam).vettore_locale
    )
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-9, atol=1e-9)


def test_carico_parabolico_genera_vettore_non_nullo(beam: ElementoBeam) -> None:
    carico = CaricoParabolico(intensita_massima=-6.0)
    equivalent = carico.calcola_vettore_equivalente(beam)
    assert equivalent.descrizione == "Carico parabolico"
    assert np.linalg.norm(equivalent.vettore_locale) > 0.0


def test_combinazione_piu_carichi(beam: ElementoBeam) -> None:
    c1 = CaricoDistribuitoUniforme(intensita=-2.0)
    c2 = CaricoConcentrato(valore=-10.0, posizione_x=200.0, tipo="forza_y")
    totale = beam.combina_carichi([c1, c2])
    expected = (
        c1.calcola_vettore_equivalente(beam).vettore_locale
        + c2.calcola_vettore_equivalente(beam).vettore_locale
    )
    np.testing.assert_allclose(totale.vettore_locale, expected, rtol=1e-12)


def test_cedimenti_nodali_equivalenti(beam: ElementoBeam) -> None:
    cedimenti = CedimentiNodali(v_i=-0.5, theta_j=0.01)
    equivalent = cedimenti.calcola_vettore_equivalente(beam)
    expected = beam.matrice_rigidezza_locale() @ np.array([0.0, -0.5, 0.0, 0.0, 0.0, 0.01])
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-12)


def test_rotazioni_imposte_equivalenti(beam: ElementoBeam) -> None:
    rotazioni = CaricoRotazioniImposte(theta_i=0.02, theta_j=-0.01)
    equivalent = rotazioni.calcola_vettore_equivalente(beam)
    expected = beam.matrice_rigidezza_locale() @ np.array([0.0, 0.0, 0.02, 0.0, 0.0, -0.01])
    np.testing.assert_allclose(equivalent.vettore_locale, expected, rtol=1e-12)
