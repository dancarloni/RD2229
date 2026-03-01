# PROJECT IO + SCHEMA + TIMELINE/REPLAY — Recon (Mega #42)

## Stato attuale (marzo 2026)

### Esistente
- `src/project/schema.py`: Modelli Pydantic completi (`ProjectInfo`, `GeometryEntry`, `MaterialEntry`, `LoadEntry`, `SeismicInputs`, ecc.), versionamento schema (`CURRENT_SCHEMA_VERSION`), single source of truth.
- `src/project/repository.py`: Funzioni `load_project`, `save_project`, `migrate_dict` con catena di migrazioni (None→1.0.0, 1.0.0→1.1.0), logging, testata.
- `src/project/schema.json`: JSON Schema generato, dettagliato, con $defs e proprietà coerenti ai modelli Pydantic.
- `docs/modules/project.md`: Documentazione aggiornata, evidenze di test, TODO e gap noti, riferimenti a test e versionamento.
- `pyproject.toml`: Pydantic v2 già in dependencies, toolchain moderna, script CLI già presenti.
- Test: `tests/test_project_roundtrip.py`, `tests/test_migration.py`, `tests/test_pipeline_smoke.py` coprono roundtrip, migrazione, pipeline.

### Pattern CLI/tool
- tools/ contiene solo tool legacy/diagnostici, nessun validate/run/replay per project.json.
- Nessun runner/timeline/manifest/hashing deterministico, nessun tool validate/run/replay, nessun output folder strutturato per run.

## Riutilizzo
- Modelli Pydantic e validazione da `src/project/schema.py`.
- Funzioni di I/O e migrazione da `src/project/repository.py`.
- Struttura e naming dei test esistenti.
- JSON Schema già generato (da mantenere deterministico).

## Da aggiungere (MVP)
- `src/project/model.py`: wrapper/alias per ProjectModel e submodel (se serve separazione logica).
- `src/project/timeline.py`: RunRecord, OutputManifest, hashing util, write_manifest.
- `tools/validate_project.py`, `tools/run_project.py`, `tools/replay_run.py`: CLI tool per validazione, run deterministica, replay/confronto manifest.
- `schemas/project.schema.json`: mantenimento schema deterministico (se non già garantito).
- Nuovi test: validazione schema, roundtrip, manifest, replay idempotente.
- Doc: `docs/SCHEMA_IO.md` (struttura project.json, comandi, esempi), update a `docs/modules/project.md`.

## Prossimi passi
- Fase 1: ProjectModel + Repository (estensione/minimo refactor se serve)
- Fase 2: Schema JSON deterministico
- Fase 3: Timeline/Manifest/Hashing
- Fase 4: Tools validate/run/replay
- Fase 5: Tests
- Fase 6: Docs
- Fase 7: CI/Verifica

*(Generato da Copilot agent — run-to-completion, branch copilot/project-io-timeline-mvp)*
