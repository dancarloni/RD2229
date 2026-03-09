# ARCH_AUDIT – Mappa architetturale RD2229

Data audit: 2025-02 | Versione schema: 1.0.0

---

## 1. Moduli dati

| Percorso | Contenuto |
|---|---|
| `src/project/schema.py` | `ProjectModel`, `GeometryEntry`, `MaterialEntry`, `LoadEntry`, `CodeSettings`, `SeismicInputs`, `FireSettings` (v1.1.0+) |
| `src/project/repository.py` | CRUD, migrazioni, lettura/scrittura JSON atomica |
| `src/core/results.py` | `ElementResult`, `ResultsModel`, `export_results()` |

## 2. Pipeline e Step5

| Percorso | Ruolo |
|---|---|
| `src/core/pipeline.py` | Orchestratore: validazione → seismica → verifiche per elemento → step5 merge → fire → wind → aggregazione |
| `src/core/step5_adapter.py` | Adattatore: `ProjectModel` → `CalcInput` → `CalcOutput` → `ElementResult`; metriche prefissate con `step5.` |

## 3. Motore di calcolo e registry

| Percorso | Ruolo |
|---|---|
| `src/core_calculus/verification_service.py` | Entry-point calcolo: `run_verifications_for_element()` |
| `src/core_calculus/normative_registry.py` | Registry template per norma (RD2229, NTC2018, DM96) |
| `src/core_calculus/verification_engine.py` | Engine per sezione/materiale |
| `src/checks/registry.py` | `CheckSpec` unificato con `norm_refs`; `CheckRegistry` con copertura per norma |

## 4. Moduli di calcolo specializzati

| Percorso | Ruolo |
|---|---|
| `src/fire/curves.py` | Curva ISO 834: `iso834_temperature(t_min)` |
| `src/fire/eligibility.py` | `evaluate_fire_eligibility(project, element)` |
| `src/fire/rc_fire_check.py` | Check RC semplificato; produce `ElementResultFire` |
| `src/wind/models.py` | `WindSite`, `Terrain`, `Orography`, `BuildingGeom` |
| `src/wind/ntc2018.py` | Calcoli NTC2018 §3.3.* |
| `src/wind/ec1991_1_4.py` | Calcoli EN 1991-1-4 |
| `src/wind/cnr_dt207.py` | Fattori turbolenza/dinamica CNR-DT 207 R1/2018 |
| `src/wind/service.py` | `WindActionService`: orchestrazione multi-norma |
| `src/wind/outputs.py` | `WindResults`, `PressureZoneResults` |

## 5. Normative Knowledge Base (NKB)

| Percorso | Contenuto |
|---|---|
| `docs/normative/sources.yaml` | Fonti normative: titolo, ente, anno, link, note copyright |
| `docs/normative/requirements.yaml` | Requisiti per norma: id, descrizione, clausola, input/output attesi |
| `docs/normative/coverage_matrix.yaml` | Mappa `requirement_id` → `check_id` implementato o TODO |

## 6. Reporting

| Percorso | Ruolo |
|---|---|
| `src/reporting/report_builder.py` | `build_report()` → `ReportArtifact` (MD + HTML); esteso con sezioni Fire/Wind |
| `src/reporting/export.py` | Export atomico file MD/HTML |

## 7. UI

| Percorso | Ruolo |
|---|---|
| `src/ui/app.py` | Entrypoint PySide6: `python -m src.ui.app` |
| `src/ui/modern/` | MVVM moderno; features registry; FieldSpec-driven |
| `src/ui/main_window.py` | Legacy Tkinter (non rimosso per retrocompatibilità) |

## 8. Test

| Percorso | Contenuto |
|---|---|
| `tests/test_pipeline_smoke.py` | Pipeline base |
| `tests/test_step5_adapter_smoke.py` | Step5 adapter |
| `tests/test_fire_selection_eligibility.py` | Fire: selezione + eleggibilità + pipeline |
| `tests/test_wind_smoke.py` | Wind: calcoli minimali |
| `tests/test_wind_integration_pipeline.py` | Wind: integrazione pipeline |
| `tests/test_reporting_smoke.py` | Report: MD/HTML generati correttamente |

## 9. Punti di estensione

### Aggiungere una nuova norma

1. Aggiungere voci in `docs/normative/requirements.yaml` e `coverage_matrix.yaml`.
2. Creare template in `src/core_calculus/normative_registry.py` o file separato.
3. Aggiungere `CheckSpec` in `src/checks/registry.py` con `norm_refs` corretti.

### Aggiungere un nuovo check

1. Implementare funzione `compute(input) -> CheckResult` in modulo appropriato.
2. Registrare in `src/checks/registry.py` con `id`, `title`, `norm_refs`, `input_schema`.
3. Aggiornare `docs/normative/coverage_matrix.yaml`.
4. Aggiungere test in `tests/`.

### Aggiungere una tabella parametri

1. Creare file JSON in `data/` (es. `data/wind/cpe_coefficients.json`).
2. Documentare copyright e fonte in `docs/normative/sources.yaml`.
3. Se non liberamente riproducibile, lasciare TODO nel JSON.

### Aggiungere una feature UI

1. Definire `FieldSpec` nel modulo di dominio.
2. Registrare nel features registry (`src/ui/modern/`).
3. Non hardcodare menu/schede: usare registry-driven rendering.

## 10. Dipendenze critiche

```
ProjectModel ──→ pipeline.run_pipeline() ──→ ResultsModel
                  │
                  ├─ step5_adapter (normative_registry + verification_service)
                  ├─ fire pipeline   (src/fire/)
                  └─ wind pipeline   (src/wind/)
```

## 11. TODO prioritari

1. `LC` e `existing_structure` in `CodeSettings` (Step 1.2) — FATTO in v1.1.0
2. `FireSettings` e `fire_selected` in `ProjectModel`/`GeometryEntry` — FATTO in v1.1.0
3. Implementare tabelle NTC2018 vento §3.3 (dati protetti: TODO in data/wind/)
4. Implementare check RC al fuoco completo (armatura, copriferro da database)
5. Coverage matrix completa per NTC2018 e Eurocodici
6. UI scheda Vento con FieldSpec
7. UI scheda Fuoco con selezione elemento e feedback eleggibilità
8. Export PDF (TODO)
9. Migrazioni schema da v1.0.0 a v1.1.0 in `src/project/repository.py`
10. Parametri CNR-DT 207 R1/2018 (turbolenza) — valori da inserire manualmente
11. CI badge e coverage report
12. Refactoring: rimuovere import `apps/` da `src/` (violazione layer)
