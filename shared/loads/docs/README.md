# Modulo Shared: Gestione Condizioni di Carico

## Scopo

Gestione centralizzata di **N condizioni di carico × M stati limite**.

Consente di:
- Definire multiple condizioni di carico (una per nome: PP, Perm, Acc_Q1, SismaX, ...)
- Associare ogni condizione a uno stato limite (SLU, SLE_rara, SLE_freq, SLE_qp, SLV, SLD)
- Filtrare condizioni per stato limite
- Calcolare inviluppo (massimo/minimo) per ogni stato limite separatamente

## Struttura

```
shared/loads/
├── engine/
│   ├── __init__.py
│   └── models.py              # LoadCondition, LoadConditionManager
├── gui/
│   └── load_table.py          # Widget tabella aggiunta/rimozione condizioni
├── docs/
│   └── README.md              # Questa documentazione
└── tests/
    └── test_load_conditions.py
```

## API Principale

### Classe `LoadCondition`

```python
from shared.loads.engine.models import LoadCondition, LimitState

cond = LoadCondition(
    name="PP+Perm",
    limit_state=LimitState.SLU,
    N=50.0,        # kN
    Mx=120.0,      # kN·m
    My=0.0,
    Tx=35.0,       # kN
    Ty=0.0,
    Mt=0.0,
    is_seismic=False,
    gamma=1.35,    # Coefficiente parziale
)
```

### Classe `LoadConditionManager`

```python
from shared.loads.engine.models import LoadConditionManager

manager = LoadConditionManager()

# Aggiungi condizioni
manager.add_condition(cond1)
manager.add_condition(cond2)
manager.add_condition(cond3)

# Filtra per stato limite
slu_conditions = manager.get_by_limit_state(LimitState.SLU)

# Elenca stati limite presenti
states = manager.limit_states()  # {SLU, SLE_rara, ...}

# Conta condizioni per stato limite
counts = manager.count_by_state()  # {SLU: 2, SLE_rara: 1, ...}

# Serializza/ricrea
data = manager.to_dict()
manager2 = LoadConditionManager.from_dict(data)
```

## Integrazione con Moduli

Ogni modulo di calcolo riceve un `LoadConditionManager` e:

1. **Filtra per stato limite** del modulo
2. **Itera su condizioni** per quello stato limite
3. **Esegue verifica** per ogni condizione
4. **Calcola inviluppo** (massimo utilizzo fra tutte le condizioni)

Esempio:

```python
# Nel modulo VerificheCaEngine
def run(self, input_data: dict, norm_code: str) -> ModuleResult:
    load_manager = input_data['load_manager']

    # Filtra per SLU
    slu_conditions = load_manager.get_by_limit_state(LimitState.SLU)

    slu_checks = []
    for cond in slu_conditions:
        # Esegui verifica per questa condizione
        check = self.check_flessione_retta(cond, section, material)
        slu_checks.append(check)

    # Calcola inviluppo
    worst = max(slu_checks, key=lambda c: c.utilization)

    return ModuleResult(
        ok=all(c.ok for c in slu_checks),
        checks_slu=slu_checks,
        envelope_utilization=worst.utilization,
        envelope_check_name=worst.name,
    )
```

## Schema Dati Serializzato

```json
{
  "conditions": [
    {
      "name": "PP+Perm",
      "limit_state": "SLU",
      "N": 50.0,
      "Mx": 120.0,
      "My": 0.0,
      "Tx": 35.0,
      "Ty": 0.0,
      "Mt": 0.0,
      "is_seismic": false,
      "psi0": null,
      "psi1": null,
      "psi2": null,
      "gamma": 1.35
    },
    {
      "name": "Acc_Q1",
      "limit_state": "SLU",
      "N": 80.0,
      "Mx": 180.0,
      "My": 15.0,
      "Tx": 42.0,
      "Ty": 0.0,
      "Mt": 0.0,
      "is_seismic": false,
      "psi0": 0.7,
      "psi1": 0.5,
      "psi2": 0.3,
      "gamma": 1.5
    }
  ]
}
```

## Note

- **Isolamento stati limite**: Ogni stato limite gestisce le proprie condizioni
- **Flessibilità**: Supporta N condizioni per qualsiasi numero di stati limite
- **Inviluppo per SL**: Il calcolo dell'inviluppo è fatto PER STATO LIMITE
- **Coefficienti psi**: Preparati per future combinazioni automatiche
