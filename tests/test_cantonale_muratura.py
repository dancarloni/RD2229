import pytest

from src.methods.muratura.cantonale import (
    InputCantonale,
    InputCatenaCantonale,
    InputSpinta,
    PosizioneSpinta,
    RisultatoCantonale,
    TipoCopertura,
    esegui_verifica_cantonale,
)


def test_inizializzazione_tipo_copertura():
    """Verifica la creazione corretta del modello SpintaPuntone."""
    # Test caso Generico
    spinta_generica = InputSpinta(
        tipo=TipoCopertura.GENERICA, forza_diretta_H_kg=500.0, forza_diretta_V_kg=1500.0
    )
    H, V, passaggi = spinta_generica.calcola_forze()
    assert H == 500.0
    assert V == 1500.0
    assert any("GENERICA" in p for p in passaggi)

    # Test caso Copertura Inclinata (es. Padiglione a 30 gradi)
    # tan(30 gradi) ~ 0.577, q = 10 kg/cm (es. 1000 kg/m), luce = 400 cm
    # V = 10 * 400 / 2 = 2000 kg
    # H = 2000 / 0.577 = 3464.1 kg
    spinta_pad = InputSpinta(
        tipo=TipoCopertura.PADIGLIONE, pendenza_ang_gradi=30.0, luce_cm=400.0, carico_q_kg_cm=10.0
    )
    H_pad, V_pad, pass_pad = spinta_pad.calcola_forze()
    assert V_pad == pytest.approx(2000.0, rel=0.01)
    assert H_pad == pytest.approx(3464.1, rel=0.01)
    assert len(pass_pad) > 1
    assert any("Padiglione" in p for p in pass_pad)


def test_validazione_geometrica_cuneo():
    """Verifica che il modello sollevi errori di validazione per geometrie impossibili."""
    # Valori <= 0
    with pytest.raises(ValueError, match="Dimensioni geometriche fondamentali"):
        InputCantonale(
            h_cm=0, t1_cm=40, t2_cm=40, L1_dist_cm=100, L2_dist_cm=100
        ).valida_geometria()

    with pytest.raises(ValueError, match="Lunghezze di distacco"):
        InputCantonale(
            h_cm=300, t1_cm=40, t2_cm=40, L1_dist_cm=-10, L2_dist_cm=100
        ).valida_geometria()
    # Caso 1: L minore dello spessore
    cuneo_corto = InputCantonale(h_cm=300, t1_cm=50, t2_cm=40, L1_dist_cm=40, L2_dist_cm=100)
    warn_corto = cuneo_corto.valida_geometria()
    assert len(warn_corto) == 1
    assert "minore dello spessore t1" in warn_corto[0]

    # Caso 2: Cuneo esageratamente espanso (es: fessura quasi piatta)
    cuneo_piatto = InputCantonale(h_cm=300, t1_cm=40, t2_cm=40, L1_dist_cm=600, L2_dist_cm=500)
    warn_piatto = cuneo_piatto.valida_geometria()
    assert len(warn_piatto) >= 1
    assert any("maggiore dell'altezza" in w for w in warn_piatto)

    # Caso 3: Snellezza estrema
    cuneo_snello = InputCantonale(h_cm=900, t1_cm=30, t2_cm=40, L1_dist_cm=100, L2_dist_cm=100)
    warn_snello = cuneo_snello.valida_geometria()
    assert len(warn_snello) >= 1
    assert any("Snellezza estrema" in w for w in warn_snello)

    # Caso 4: Geometria standard (nessun warning)
    cuneo_ok = InputCantonale(h_cm=300, t1_cm=40, t2_cm=40, L1_dist_cm=150, L2_dist_cm=150)
    assert len(cuneo_ok.valida_geometria()) == 0


def test_to_dict_risultato():
    """Garantisce la serializzabilità per i tabulati come da linee guida del repo."""
    res = RisultatoCantonale(
        is_verificato=True,
        alpha_0=0.15,
        momento_ribaltante_kg_cm=50000.0,
        momento_stabilizzante_kg_cm=80000.0,
        peso_cuneo_kg=2500.0,
        passaggi_calcolo=["Step 1", "Step 2"],
        warnings=["Warn 1"],
    )
    data = res.to_dict()
    assert data["is_verificato"] is True
    assert data["alpha_0"] == 0.15
    assert data["peso_cuneo_kg"] == 2500.0
    assert len(data["passaggi_calcolo"]) == 2
    assert data["warnings"] == ["Warn 1"]


def test_cinematica_base():
    inp = InputCantonale(h_cm=300, t1_cm=40, t2_cm=40, L1_dist_cm=150, L2_dist_cm=150)
    res = esegui_verifica_cantonale(inp)
    assert res.alpha_0 > 0.0
    assert len(res.passaggi_calcolo) > 0


def test_diagnostica_angolo():
    from src.methods.muratura.cantonale import InputDiagnosticaAngolo, calcola_resistenza_residua_angolo, TipoSogliaApertura
    # Test 1: NTC2018 (should be max(t, 100))
    inp1 = InputDiagnosticaAngolo(distanza_apertura_cm=120.0, spessore_parete_cm=40.0, tipo_soglia=TipoSogliaApertura.NORMATIVA_NTC)
    res1 = calcola_resistenza_residua_angolo(inp1)
    assert res1.is_ok == True
    assert res1.coeff_riduzione_k == 1.0
    assert res1.distanza_minima_richiesta_cm == 100.0
    # Test 2: NTC2018 Failing
    inp2 = InputDiagnosticaAngolo(distanza_apertura_cm=50.0, spessore_parete_cm=40.0, tipo_soglia=TipoSogliaApertura.NORMATIVA_NTC)
    res2 = calcola_resistenza_residua_angolo(inp2)
    assert res2.is_ok == False
    assert res2.coeff_riduzione_k == 0.5
    # Test 3: Basso (asintotico)
    inp3 = InputDiagnosticaAngolo(distanza_apertura_cm=10.0, spessore_parete_cm=40.0)
    res3 = calcola_resistenza_residua_angolo(inp3)
    assert res3.is_ok == False
    assert res3.coeff_riduzione_k == 0.20
    assert res3.status == 'FAIL'

def test_report_estrazione():
    from src.methods.muratura.cantonale import InputDiagnosticaAngolo, calcola_resistenza_residua_angolo, TipoSogliaApertura, InputCantonale, esegui_verifica_cantonale
    from src.report.tabulati_calcolo import sezione_meccanismo_cantonale, sezione_diagnostica_angolo
    
    # Check cinematica report
    inp = InputCantonale(h_cm=300, t1_cm=40, t2_cm=40, L1_dist_cm=150, L2_dist_cm=150)
    res = esegui_verifica_cantonale(inp)
    report_text = sezione_meccanismo_cantonale(res)
    assert 'RIBALTAMENTO CANTONALE 3D' in report_text
    assert 'Moltiplicatore collasso alpha_0' in report_text
    assert 'PASSAGGI DI CALCOLO:' in report_text
    
    # Check diagnostica
    inp_diag = InputDiagnosticaAngolo(distanza_apertura_cm=50.0, spessore_parete_cm=40.0, tipo_soglia=TipoSogliaApertura.NORMATIVA_NTC)
    res_diag = calcola_resistenza_residua_angolo(inp_diag)
    report_diag_text = sezione_diagnostica_angolo(res_diag)
    assert 'DIAGNOSTICA APERTURE' in report_diag_text
    assert 'Stato diagnostica: WARNING' in report_diag_text
    assert 'LOG DECISIONALE:' in report_diag_text
