
FIRE_TESTS_PYTEST_SKELETON – Test automatici pytest (R60 / R90 / R120)
Status: STABILE
Ruolo: Scheletro reale di test pytest per il modulo INCENDIO


1. Scopo del documento
Questo documento fornisce uno scheletro reale e pronto all’uso di test pytest, che copre:

Struttura pytest con @pytest.fixture
Mock del solver (CodeModule_INCENDIO)
Test R60 positivo (OK)
Test R60 negativo (NOT_OK)
Test R90 / R120 riusando la stessa struttura
Il file è coerente con:

FIRE_CODEMODULE_INCENDIO.md
FIRE_ESEMPIO_R60_PILASTRO.md
FIRE_ESTENSIONE_R90_R120.md
FIRE_CHECKLIST_TECNICO_LEGALE.md


2. Struttura reale dei test

tests/
└── fire/
    ├── conftest.py
    ├── test_fire_r60_positive.py
    ├── test_fire_r60_negative.py
    ├── test_fire_r90.py
    └── test_fire_r120.py




3. conftest.py – Fixture e mock

import pytest
from types import SimpleNamespace

# =========================
# Mock del CodeModule_INCENDIO
# =========================

class MockFireSolver:
    def verify_at_time(self, t_req, fire_input):
        # comportamento controllato per test
        if fire_input.get("force_not_ok"):
            return SimpleNamespace(
                check_id="FIRE_MOCK",
                stato_limite="INCENDIO",
                fire_class_required=fire_input["fire_class_required"],
                fire_time_achieved=t_req - 10,
                fire_method=fire_input["fire_method"],
                norma="EN 1991-1-2 / EN 1992-1-2",
                esito="NOT_OK",
                warning_note="mocked failure",
            )

        return SimpleNamespace(
            check_id="FIRE_MOCK",
            stato_limite="INCENDIO",
            fire_class_required=fire_input["fire_class_required"],
            fire_time_achieved=t_req,
            fire_method=fire_input["fire_method"],
            norma="EN 1991-1-2 / EN 1992-1-2",
            esito="OK",
            warning_note=None,
        )


@pytest.fixture
def code_module_incendio():
    return MockFireSolver()


@pytest.fixture
def base_fire_input():
    return {
        "fire_required": True,
        "fire_curve": "ISO_834",
        "fire_exposure_sides": 4,
        "fire_method": "L2",
    }




4. Test R60 positivo (OK)

# test_fire_r60_positive.py

def test_fire_r60_ok(code_module_incendio, base_fire_input):
    fire_input = {
        **base_fire_input,
        "fire_class_required": "R60",
        "fire_time_target": 60,
    }

    result = code_module_incendio.verify_at_time(60, fire_input)

    assert result.stato_limite == "INCENDIO"
    assert result.fire_class_required == "R60"
    assert result.fire_method == "L2"
    assert result.esito == "OK"
    assert result.fire_time_achieved >= 60




5. Test R60 negativo (NOT_OK)

# test_fire_r60_negative.py

def test_fire_r60_not_ok(code_module_incendio, base_fire_input):
    fire_input = {
        **base_fire_input,
        "fire_class_required": "R60",
        "fire_time_target": 60,
        "force_not_ok": True,
    }

    result = code_module_incendio.verify_at_time(60, fire_input)

    assert result.stato_limite == "INCENDIO"
    assert result.esito == "NOT_OK"
    assert result.fire_time_achieved < 60




6. Test R90 (riuso struttura)

# test_fire_r90.py

def test_fire_r90_ok(code_module_incendio, base_fire_input):
    fire_input = {
        **base_fire_input,
        "fire_class_required": "R90",
        "fire_time_target": 90,
    }

    result = code_module_incendio.verify_at_time(90, fire_input)

    assert result.fire_class_required == "R90"
    assert result.fire_time_achieved >= 90
    assert result.esito == "OK"




7. Test R120 (riuso struttura)

# test_fire_r120.py

def test_fire_r120_ok(code_module_incendio, base_fire_input):
    fire_input = {
        **base_fire_input,
        "fire_class_required": "R120",
        "fire_time_target": 120,
    }

    result = code_module_incendio.verify_at_time(120, fire_input)

    assert result.fire_class_required == "R120"
    assert result.fire_time_achieved >= 120
    assert result.esito == "OK"




8. Criteri di qualità dei test
I test sono corretti se:

non dipendono da GUI
non usano valori normativi hardcoded
verificano solo comportamento e output
falliscono in caso di regressione


9. Estensioni future

aggiungere test L3 (mock FEM)
parametrizzare R30/R60/R90/R120
integrazione CI (GitHub Actions)


10. Collegamenti

FIRE_ESEMPIO_R60_PILASTRO.md
FIRE_TESTS_AUTOMATICI_R60.md
FIRE_ESTENSIONE_R90_R120.md
FIRE_NEXT_STEPS_ROADMAP.md
