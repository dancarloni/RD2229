# Agent State — Verifiche elementi strutturali primari/secondari

## Layout reale
- `src/` — production code (editable package)
- `src/core_calculus/` — core verification engine
- `src/core_calculus/contracts.py` — data contracts
- `src/core_calculus/core/adapters/` — norm adapters (NEW)
- `src/core_calculus/core/classification.py` — element role classification (NEW)
- `src/core_calculus/core/verifier_manager.py` — multi-norm orchestrator (NEW)
- `tests/` — test suite
- `docs/` — documentation

## Decisioni principali

### Adapter pattern
- `NormAdapter` ABC: `applicability()` + `verify()`
- Due adapter reali: `Ntc2018Adapter`, `Rd2229Adapter`
- `VerifierManager`: seleziona adapter, auto-classifica ruolo, produce `CalcOutput`

### Classificazione
- `ElementRole` enum: PRIMARY, SECONDARY, UNDETERMINED
- `classify_element()`: regole configurabili con `ClassificationRule`
- Regole default: beam/column → PRIMARY, wall/partition → SECONDARY

### Profili di verifica
- `PROFILE_PRIMARY_FULL`: verifiche complete per elementi primari
- `PROFILE_SECONDARY_STABILITY`: verifiche stabilità per elementi secondari

## Comandi repo-specific
```bash
# Install
pip install -e ".[gui]"
pip install pytest

# Tests (gating)
PYTHONPATH=".:src" python -m pytest -q --tb=short

# Lint (advisory)
ruff check .
mypy src
```

## Checklist esecuzione
- [x] Discovery repository
- [x] Analisi Issue #42 + sub-issue
- [x] Gap analysis
- [x] Implementazione core (adapter + classification + manager)
- [x] Test unitari + integration
- [x] Documentazione
- [x] CI/checks ALL GREEN
