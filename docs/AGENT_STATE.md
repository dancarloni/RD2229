# Agent State — Verifiche elementi strutturali primari/secondari

## Checkpoint Persistente — Fase U (2026-03-12)

### Commit di riferimento

- HEAD: `b98ad7b`
- Branch: `main`

### Implementato in questa sessione

- Nuovo package: `src/seismic/`
- Modulo U.1/U.1.5: `src/seismic/fattori_struttura.py`
	- `ClasseDuttilita` (CD_A, CD_B, CD_L)
	- `SistemaStrutturale` (telaio, parete, misto)
	- Stima tabellata `alpha_u/alpha_1` (NTC2018 semplificata)
	- Calcolo `q_0`, `k_w`, `q`
	- Riduzioni opzionali per irregolarita/eccentricita
	- Vincolo `q >= 1.5` e warning `q > 6.0`
	- Metodo alternativo `PUSHOVER` per alpha da tagli base
- Modulo U.2: `src/seismic/duttilita.py`
	- `mu_phi` richiesta (EC8 a tratti)
	- `mu_phi` disponibile
	- `epsilon_cu` confinata
	- `rho_sx` minimo
	- `theta_u` circolare semplificata
	- Verifica completa richiesta/disponibile (`verifica_duttilita`)
- Export aggiornati:
	- `src/seismic/__init__.py`
	- `src/__init__.py`
	- `src/__all__.py`
- Test aggiunti:
	- `tests/test_fattori_struttura.py`
	- `tests/test_duttilita.py`

### Validazione effettuata

- Comando: `python -m pytest tests/test_fattori_struttura.py tests/test_duttilita.py -q`
- Esito: `24 passed`

### Decisioni tecniche da preservare

- Implementazione incrementale per blocchi verticali: modulo + test + push.
- Mantenere `alpha_u/alpha_1` in `fattori_struttura.py` (non creare modulo separato).
- Gestire da subito la circolarita alpha (`tabella` iniziale + `pushover` raffinamento).
- Preferire API pure/funzionali con dataclass di risultato e `passaggi` tracciabili.

### Prossimi passi vincolanti (ordine operativo)

1. `src/seismic/gerarchia.py` + `tests/test_gerarchia.py` (U.3)
2. `src/seismic/nodi_trave_pilastro.py` + `tests/test_nodi.py` (U.4)
3. `src/seismic/analisi_modale.py` + `tests/test_analisi_modale.py` (U.5)
4. `src/seismic/pushover.py` + `tests/test_pushover.py` (U.6)
5. Esecuzione test aggregati moduli Fase U e push finale

### Criteri di ripresa rapida (se contesto saturo)

- Leggere prima: `docs/AGENT_STATE.md` (questa sezione)
- Leggere poi: `docs/piano_fase_U.md` (decisioni normative e formule)
- Ripartire direttamente dal punto 1 dei prossimi passi

---

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
