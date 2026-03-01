# Modulo: `core`

## 1. Scopo e ambito

Pipeline principale di calcolo strutturale: orchestrazione dei passi (vento, incendio, elementi, normativa) da `ProjectModel` a `ResultsModel`. Include anche l'adapter per Step 5 (gerarchia capacità/esistenti NTC2018) e modelli risultati.

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: `src/core/pipeline.py` (416 righe) ha logica reale multi-step. `step5_adapter.py` (318 righe) è reale. `results.py` (76 righe) è reale. Però `combinations/ntc2018_combinations.py` e `materials/ntc2018_adapter.py` sono esplicitamente SKELETON con return pass-through.

## 3. Evidenze

- `src/core/pipeline.py` — `run_pipeline(project: ProjectModel) -> ResultsModel`; logica multi-step
- `src/core/step5_adapter.py` — `run_step5()`, `can_run_step5()` reali
- `src/core/results.py` — `ElementResult`, `ResultsModel`, `export_results`
- `src/core/combinations/ntc2018_combinations.py` — SKELETON dichiarato
- `src/core/materials/ntc2018_adapter.py` — SKELETON dichiarato
- Test: `tests/test_pipeline_smoke.py`, `tests/test_step5_merge.py`, `tests/test_wind_integration_pipeline.py` (+4)

## 4. Input/parametri

- `run_pipeline(project: ProjectModel) -> ResultsModel` — input centralizzato Pydantic

## 5. Output

- `ResultsModel` — contiene `List[ElementResult]`, warnings, metadata

## 6. Dipendenze

- `src/project/repository` — `ProjectModel`
- `src/fire` — `iso834_temperature()`, `run_rc_fire_check()`
- `src/wind` — `WindActionService`
- `src/core_calculus` — engine verifiche
- `src/reporting` — (usato da CLI, non pipeline diretta)

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| NTC2018 | `src/core/pipeline.py` — sezione step NTC2018 |
| RD2229 | `src/core/results.py` — `norm_code` default |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- `ntc2018_combinations.py`: combinazioni di carico non implementate (SKELETON)
- `ntc2018_adapter.py`: adattatore materiali NTC2018 non implementato
- Step 5 copre solo strutture esistenti (NTC2018 §7); strutture nuove: TBD

## 9. Next steps

- [ ] Implementare `ntc2018_combinations.py` con combinazioni SLU/SLE
- [ ] Implementare `ntc2018_adapter.py` per conversione parametri materiali
- [ ] Aggiungere test integrazione con ProjectModel completo
