
FIRE_TESTS_AUTOMATICI_R60 – Derivazione test automatici dal caso R60
Status: STABILE
Ruolo: Specifica e template di test automatici (pytest / unittest)


1. Scopo del documento
Questo documento deriva test automatici eseguibili dal caso studio FIRE_ESEMPIO_R60_PILASTRO.md, con l’obiettivo di:

validare in modo automatico il CodeModule_INCENDIO
garantire non‑regressione delle verifiche incendio
fornire test riproducibili per CI/CD
I test sono progettati per:

pytest (consigliato)
unittest (alternativa standard library)


2. Principi vincolanti dei test

Nessun valore normativo hardcoded
I test usano gli stessi input concettuali del caso R60
L’esito atteso è definito solo in termini di:esito
stato_limite
fire_class_required
fire_time_achieved
I test non verificano formule interne, ma il comportamento del solver.


3. Struttura consigliata del repository

/tests
  /fire
    test_fire_r60_pilastro.py
    test_fire_r60_input_validation.py
    test_fire_r60_output_schema.py




4. Fixture comune – Input incendio R60
4.1 Fixture concettuale
La fixture rappresenta l’input minimo conforme a PLAN_INPUT_COMUNE:

# fixture concettuale (da adattare al codice reale)
fire_input_r60 = {
    "fire_required": True,
    "fire_class_required": "R60",
    "fire_time_target": 60,
    "fire_curve": "ISO_834",
    "fire_exposure_sides": 4,
    "fire_method": "L2",
    "fire_protection_type": None,
}




5. Test principali con pytest (raccomandato)
5.1 Test di successo – R60 soddisfatta

import pytest

def test_fire_r60_pilastro_ok(code_module_incendio, fire_input_r60):
    result = code_module_incendio.verify_at_time(60, fire_input_r60)

    assert result.stato_limite == "INCENDIO"
    assert result.fire_class_required == "R60"
    assert result.fire_method == "L2"
    assert result.esito == "OK"
    assert result.fire_time_achieved >= 60




5.2 Test di non‑regressione – output schema

def test_fire_r60_output_schema(code_module_incendio, fire_input_r60):
    result = code_module_incendio.verify_at_time(60, fire_input_r60)

    required_fields = [
        "check_id",
        "stato_limite",
        "esito",
        "fire_class_required",
        "fire_time_achieved",
        "fire_method",
        "norma",
    ]

    for field in required_fields:
        assert hasattr(result, field)




5.3 Test di input incompleto

def test_fire_r60_missing_input(code_module_incendio):
    bad_input = {
        "fire_required": True,
        "fire_class_required": "R60",
    }

    with pytest.raises(ValueError):
        code_module_incendio.verify_at_time(60, bad_input)




6. Test equivalenti con unittest

import unittest

class TestFireR60Pilastro(unittest.TestCase):

    def test_r60_ok(self):
        result = code_module_incendio.verify_at_time(60, fire_input_r60)
        self.assertEqual(result.esito, "OK")
        self.assertGreaterEqual(result.fire_time_achieved, 60)

    def test_schema(self):
        result = code_module_incendio.verify_at_time(60, fire_input_r60)
        self.assertTrue(hasattr(result, "stato_limite"))

if __name__ == '__main__':
    unittest.main()




7. Test di casi limite (estensioni consigliate)
7.1 R60 non soddisfatta

input con sezione ridotta
atteso: esito = NOT_OK
7.2 Caso fuori campo normativo

metodo L2 non ammesso
atteso: NOT_APPLICABLE


8. Integrazione con checklist tecnico‑legale
Ogni test deve implicitamente verificare:

metodo dichiarato
norma presente
assenza di hardcoding
Questi controlli derivano da: FIRE_CHECKLIST_TECNICO_LEGALE.md


9. Uso in CI/CD

esecuzione automatica a ogni commit
blocco merge se un test incendio fallisce
test incendio separati dai test SLU/SLE


10. Criteri di accettazione dei test
I test sono considerati validi se:

riproducono il caso R60
falliscono su input errato
intercettano regressioni
non dipendono da GUI o report


11. Collegamenti

FIRE_ESEMPIO_R60_PILASTRO.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_CHECKLIST_TECNICO_LEGALE.md
FIRE_NEXT_STEPS_ROADMAP.md
