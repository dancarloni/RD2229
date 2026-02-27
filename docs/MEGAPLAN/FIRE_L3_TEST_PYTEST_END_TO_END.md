
FIRE_L3_TESTS_PYTEST_END_TO_END – Test pytest L3 end‑to‑end
Status: STABILE
Ruolo: Suite di test end‑to‑end per il solver FEM L3 (termico + meccanico + accoppiamento)


1. Scopo
Questa suite verifica end‑to‑end il solver L3 FEM lungo l’intero flusso:

analisi termica (STEP 1)
analisi meccanica (STEP 2)
accoppiamento completo (STEP 3)
I test sono progettati per:

individuare regressioni
validare il criterio di collasso
supportare il Gate di rilascio L3


2. Struttura dei test

tests/
└── fire_l3/
    ├── conftest.py
    ├── test_l3_end_to_end_ok.py
    ├── test_l3_end_to_end_not_ok.py
    ├── test_l3_dt_sensitivity.py
    └── test_l3_alpha_second_order.py




3. Fixture comuni e mock controllati

# conftest.py
import pytest
from types import SimpleNamespace
from fire_l3.thermal import ThermalSolverL3
from fire_l3.mechanical import MechanicalSolverL3
from fire_l3.solver import SolverL3FEM

@pytest.fixture
def l3_components():
    thermal = ThermalSolverL3(fibers=20)
    mechanical = MechanicalSolverL3(fibers=[...], materials={...})
    return thermal, mechanical

@pytest.fixture
def solver_l3(l3_components):
    thermal, mechanical = l3_components
    return SolverL3FEM(thermal, mechanical, dt=5.0, alpha=0.0)




4. Test OK end‑to‑end (R60)

def test_l3_end_to_end_ok(solver_l3):
    res = solver_l3.run(fire_time_target=60, M_Ed_fi=1.0)
    assert res["fire_method"] == "L3"
    assert res["esito"] == "OK"
    assert res["fire_time_achieved"] >= 60




5. Test NOT_OK end‑to‑end (collasso anticipato)

def test_l3_end_to_end_not_ok(solver_l3):
    res = solver_l3.run(fire_time_target=120, M_Ed_fi=5.0)
    assert res["esito"] == "NOT_OK"
    assert res["fire_time_achieved"] < 120




6. Sensibilità al passo temporale (Δt)

import pytest

@pytest.mark.parametrize("dt", [1.0, 2.5, 5.0, 10.0])
def test_l3_dt_sensitivity(l3_components, dt):
    thermal, mechanical = l3_components
    solver = SolverL3FEM(thermal, mechanical, dt=dt, alpha=0.0)
    res = solver.run(fire_time_target=60, M_Ed_fi=1.0)
    assert res["fire_time_achieved"] >= 55




7. Effetti del II ordine (α)

import pytest

@pytest.mark.parametrize("alpha", [0.0, 0.1, 0.2])
def test_l3_second_order_alpha(l3_components, alpha):
    thermal, mechanical = l3_components
    solver = SolverL3FEM(thermal, mechanical, dt=5.0, alpha=alpha)
    res = solver.run(fire_time_target=60, M_Ed_fi=1.0)
    assert res["fire_method"] == "L3"




8. Aggancio al Gate di rilascio
Criteri verificati automaticamente dai test:

esito deterministico
gestione NOT_OK
stabilità numerica
I test sono condizione necessaria per superare:

FIRE_GATE_RILASCIO_L3_FEM.md


9. Criteri di accettazione

tutti i test end‑to‑end passano
nessuna dipendenza da GUI
riproducibilità a parità di input


10. Collegamenti

FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md
FIRE_GATE_RILASCIO_L3_FEM.md
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
