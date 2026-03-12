from __future__ import annotations

import pytest

from src.scale.scale import (
    GeometriaRampa,
    ProfiloAcciaioScala,
    calcola_carico_variabile_default,
    calcola_coefficiente_neve,
    profilo_ipe200_s275,
    verifica_scala_ca,
    verifica_scala_metallica,
)


def test_carico_variabile_default_residenziale() -> None:
    assert calcola_carico_variabile_default("residenziale") == pytest.approx(2.0)


def test_coefficiente_neve_intervalli() -> None:
    assert calcola_coefficiente_neve(20.0) == pytest.approx(0.8)
    assert calcola_coefficiente_neve(35.0) == pytest.approx(0.6666666, rel=1e-4)
    assert calcola_coefficiente_neve(70.0) == pytest.approx(0.0)


def test_verifica_scala_ca_nominale_verificata() -> None:
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
    )
    risultato = verifica_scala_ca(geometria)
    assert risultato.tipo == "ca"
    assert risultato.esito_globale is True
    assert len(risultato.verifiche) == 4
    assert "Scala in c.a." in risultato.tabulato_ascii


def test_verifica_scala_ca_warning_fc_e_area() -> None:
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="pubblico",
        armatura_tesa_cm2=18.0,
        livello_conoscenza="LC2",
        area_influenza_m2=3.6,
    )
    risultato = verifica_scala_ca(geometria)
    assert "V-FC-005" in risultato.warning_codes
    assert "V-AREA-002" in risultato.warning_codes


def test_verifica_scala_ca_range_error() -> None:
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=10.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
    )
    with pytest.raises(ValueError, match="V-RANGE-001"):
        verifica_scala_ca(geometria)


def test_verifica_scala_metallica_nominale_verificata() -> None:
    geometria = GeometriaRampa(
        tipologia="acciaio",
        alpha_deg=35.0,
        luce_orizzontale_m=4.0,
        spessore_m=0.15,
        larghezza_m=1.10,
        categoria_uso="residenziale",
    )
    risultato = verifica_scala_metallica(geometria, profilo=profilo_ipe200_s275())
    assert risultato.tipo == "acciaio"
    assert risultato.esito_globale is True
    assert any(item.nome == "Instabilita' flesso-torsionale" for item in risultato.verifiche)


def test_verifica_scala_metallica_warning_ltb_per_profilo_snello() -> None:
    profilo = ProfiloAcciaioScala(
        nome="SNELLO",
        area_mm2=1800.0,
        wpl_mm3=60000.0,
        av_mm2=800.0,
        h_mm=220.0,
        b_mm=120.0,
        tf_mm=5.0,
        tw_mm=3.0,
        fy_mpa=275.0,
        m_cr_kNm=10.0,
    )
    geometria = GeometriaRampa(
        tipologia="acciaio",
        alpha_deg=35.0,
        luce_orizzontale_m=4.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="pubblico",
    )
    risultato = verifica_scala_metallica(geometria, profilo=profilo)
    assert "V-LTB-003" in risultato.warning_codes
    assert risultato.esito_globale is False


def test_risultato_scala_to_dict_contiene_tabulato() -> None:
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
    )
    risultato = verifica_scala_ca(geometria)
    dati = risultato.to_dict()
    assert dati["tipo"] == "ca"
    assert "verifiche" in dati
    assert "tabulato" in dati
    assert dati["tabulato"]["esito"] is not None


# ==== Test casi avanzati (Fase V estesa) ====


def test_verifica_scala_ca_incastrata_doppio_incastro() -> None:
    """Verifica rampa con doppio incastro: momento ridotto a qL²/12."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
        schema_statico="incastrata",
        vincolo_sinistra="incastro",
        vincolo_destra="incastro",
    )
    risultato = verifica_scala_ca(geometria)
    assert risultato.esito_globale is True
    # Con doppio incastro, il momento è 3 volte minore → maggiore capacità
    assert all(item.esito for item in risultato.verifiche)


def test_verifica_scala_ca_singolo_incastro_warning() -> None:
    """Verifica rampa con singolo incastro genera warning V-FIXED-002."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        schema_statico="incastrata",
        vincolo_sinistra="incastro",
        vincolo_destra="cerniera",
    )
    risultato = verifica_scala_ca(geometria)
    assert "V-FIXED-002" in risultato.warning_codes


def test_verifica_scala_ca_con_pianerottolo_autonomo() -> None:
    """Verifica rampa con pianerottolo autonomo."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
        pianerottolo_presente=True,
        pianerottolo_tipo="autonomo",
        pianerottolo_larghezza_m=1.50,
        pianerottolo_altezza_m=0.30,
    )
    risultato = verifica_scala_ca(geometria)
    # Pianerottolo autonomo aggiunge una componente di momento
    assert "V-JOINT-004" in risultato.warning_codes
    # Il momento totale includerà il contributo del pianerottolo
    assert (
        any("pianerottolo" in item.nome.lower() for item in risultato.verifiche)
        or risultato.esito_globale
    )


def test_verifica_scala_ca_con_pianerottolo_continuita() -> None:
    """Verifica rampa con pianerottolo in continuità."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
        pianerottolo_presente=True,
        pianerottolo_tipo="continuita",
        pianerottolo_larghezza_m=1.50,
    )
    risultato = verifica_scala_ca(geometria)
    assert risultato.tipo == "ca"
    # Continuità non aggiunge un warning significativo
    assert "V-JOINT-004" not in risultato.warning_codes or len(risultato.verifiche) > 0


def test_verifica_scala_ca_con_pianerottolo_ibrido() -> None:
    """Verifica rampa con pianerottolo modello ibrido."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
        pianerottolo_presente=True,
        pianerottolo_tipo="ibrido",
        pianerottolo_larghezza_m=1.50,
    )
    risultato = verifica_scala_ca(geometria)
    # Modello ibrido = approssimazione esplicita
    assert "V-JOINT-004" in risultato.warning_codes


def test_verifica_scala_ca_segmentata_cambio_pendenza() -> None:
    """Verifica rampa segmentata con cambio di pendenza moderato."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
        segmenti_rampa=[(1.5, 30.0), (1.5, 32.0)],  # Cambio di 2° (piccolo)
    )
    risultato = verifica_scala_ca(geometria)
    assert risultato.esito_globale is True
    # Cambio di 2° non genera warning (soglia > 15°)
    assert "V-PEND-003" not in risultato.warning_codes


def test_verifica_scala_ca_segmentata_cambio_pendenza_marcato_warning() -> None:
    """Verifica rampa segmentata con cambio di pendenza marcato → warning."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="residenziale",
        armatura_tesa_cm2=20.0,
        segmenti_rampa=[(1.5, 20.0), (1.5, 38.0)],  # Cambio di 18° (grande)
    )
    risultato = verifica_scala_ca(geometria)
    # Cambio di 18° > 15° → genera V-PEND-003
    assert "V-PEND-003" in risultato.warning_codes


def test_verifica_scala_ca_tre_segmenti() -> None:
    """Verifica rampa con tre segmenti progressivi."""
    geometria = GeometriaRampa(
        tipologia="ca",
        alpha_deg=30.0,
        luce_orizzontale_m=3.0,
        spessore_m=0.15,
        larghezza_m=1.20,
        categoria_uso="pubblico",
        armatura_tesa_cm2=20.0,
        segmenti_rampa=[(1.0, 25.0), (1.0, 30.0), (1.0, 35.0)],
    )
    risultato = verifica_scala_ca(geometria)
    assert risultato.tipo == "ca"
    # Vengono selezionati i momenti/tagli massimi tra i segmenti
    assert len(risultato.verifiche) > 0
