
FIRE_TESTS_PYTEST_AVANZATI – Parametrizzazione, mock L3 FEM e checklist
Status: STABILE
Ruolo: Estensione avanzata dei test pytest per il modulo INCENDIO


1. Scopo del documento
Questo documento estende i test automatici incendio introducendo:

Parametrizzazione dei test con @pytest.mark.parametrize
Mock del solver L3 FEM
Aggancio automatico dei test alla checklist tecnico‑legale
Il risultato è una suite di test:

più compatta
più leggibile
direttamente allineata ai requisiti normativi e legali


2. Parametrizzazione dei test (R30 / R60 / R90 / R120)
2.1 Principio
La stessa logica di test viene riusata per più classi di resistenza al fuoco, variando solo:

classe R
tempo richiesto
esito atteso


2.2 Esempio di test parametrizzato

import pytest

@pytest.mark.parametrize(
    "fire_class, time_req",
    [
        ("R30", 30),
        ("R60", 60),
        ("R90", 90),
        ("R120", 120),
    ]
)
def test_fire_positive_parametrized(code_module_incendio, base_fire_input, fire_class, time_req):
    fire_input = {
        **base_fire_input,
        "fire_class_required": fire_class,
        "fire_time_target": time_req,
    }

    result = code_module_incendio.verify_at_time(time_req, fire_input)

    assert result.stato_limite == "INCENDIO"
    assert result.fire_class_required == fire_class
    assert result.fire_time_achieved >= time_req
    assert result.esito == "OK"




2.3 Parametrizzazione test negativi

@pytest.mark.parametrize(
    "fire_class, time_req",
    [
        ("R60", 60),
        ("R90", 90),
        ("R120", 120),
    ]
)
def test_fire_negative_parametrized(code_module_incendio, base_fire_input, fire_class, time_req):
    fire_input = {
        **base_fire_input,
        "fire_class_required": fire_class,
        "fire_time_target": time_req,
        "force_not_ok": True,
    }

    result = code_module_incendio.verify_at_time(time_req, fire_input)

    assert result.esito == "NOT_OK"
    assert result.fire_time_achieved < time_req




3. Mock del solver L3 FEM
3.1 Mock dedicato
Per testare L3 senza un vero solver FEM:

class MockFireSolverL3:
    def verify_at_time(self, t_req, fire_input):
        # simulazione collasso a 110 min
        t_collapse = fire_input.get("mock_t_collapse", t_req + 10)

        return SimpleNamespace(
            check_id="FIRE_L3_MOCK",
            stato_limite="INCENDIO",
            fire_class_required=fire_input["fire_class_required"],
            fire_time_achieved=t_collapse,
            fire_method="L3",
            norma="EN 1991-1-2 / EN 1992-1-2",
            esito="OK" if t_collapse >= t_req else "NOT_OK",
            warning_note="mock FEM solver",
        )




3.2 Test L3 parametrizzato

@pytest.mark.parametrize(
    "fire_class, time_req, t_collapse, expected",
    [
        ("R90", 90, 95, "OK"),
        ("R120", 120, 110, "NOT_OK"),
    ]
)
def test_fire_l3_fem_mock(fire_class, time_req, t_collapse, expected):
    solver = MockFireSolverL3()
    fire_input = {
        "fire_class_required": fire_class,
        "mock_t_collapse": t_collapse,
    }

    result = solver.verify_at_time(time_req, fire_input)

    assert result.fire_method == "L3"
    assert result.esito == expected




4. Aggancio dei test alla checklist tecnico‑legale
4.1 Principio
Ogni test deve verificare implicitamente che:

metodo sia dichiarato
norma sia presente
stato limite sia corretto
Questi controlli derivano da FIRE_CHECKLIST_TECNICO_LEGALE.md.


4.2 Helper di validazione checklist

def assert_checklist_minima(result):
    assert hasattr(result, "stato_limite")
    assert hasattr(result, "esito")
    assert hasattr(result, "fire_method")
    assert hasattr(result, "norma")




4.3 Uso nei test

def test_fire_r60_checklist(code_module_incendio, base_fire_input):
    fire_input = {
        **base_fire_input,
        "fire_class_required": "R60",
        "fire_time_target": 60,
    }

    result = code_module_incendio.verify_at_time(60, fire_input)

    assert_checklist_minima(result)




5. Benefici dell’approccio

Riduzione drastica del numero di file di test
Copertura sistematica di tutte le classi R
Allineamento automatico con requisiti tecnico‑legali
Facilità di estensione a nuovi elementi (travi, L3 reali)


6. Criteri di accettazione
Questa estensione è completa se:

tutti i test R30–R120 passano
L3 è testabile senza FEM reale
ogni risultato passa la checklist minima


7. Collegamenti

FIRE_TESTS_PYTEST_SKELETON.md
FIRE_ANALISI_AVANZATA_L3_FEM.md
FIRE_CHECKLIST_TECNICO_LEGALE.md
FIRE_NEXT_STEPS_ROADMAP.md
