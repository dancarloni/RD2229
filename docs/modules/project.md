# Modulo: `project`

## 1. Scopo e ambito

Modello dati centrale del progetto strutturale (`ProjectModel` Pydantic), repository per caricamento/salvataggio su file JSON/JSONP, migrazione versioni schema.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `schema.py` (120 righe) ha modelli Pydantic completi con tutti i sub-model. `repository.py` (410 righe) implementa I/O reale, migrazione versioni (1.0.0→1.1.0), validazione. Test su 10+ file.

## 3. Evidenze

- `src/project/schema.py` — `ProjectModel`, `ProjectInfo`, `GeometryEntry`, `MaterialEntry`, `LoadEntry`, `SeismicInputs`, `CodeSettings`, `WindInputs`, `FireInputs`, `PipelineSteps`
- `src/project/repository.py` — `load_project(path)`, `save_project(model, path)`, `migrate_dict()`
- `src/project/model.py` — `ProjectMeta`, `NormativeProfileRef`, `ModuleConfig`, `ProjectModel` (wrapper MVP)
- `src/project/timeline.py` — `RunRecord`, `OutputManifest`, `sha256_file`, `write_manifest`
- Test: `tests/test_project_roundtrip.py`, `tests/test_project_schema_validation.py`, `tests/test_timeline_manifest_hashing.py`, `tests/test_run_replay_idempotent.py`

## 4. Input/parametri

- `load_project(path: str | Path) -> ProjectModel` — legge JSON/JSONP
- `save_project(model: ProjectModel, path: str | Path)` — scrive JSON
- CLI tools: `tools/validate_project.py`, `tools/run_project.py`, `tools/replay_run.py`

## 5. Output

- `ProjectModel` — modello Pydantic completo
- File JSON su disco
- Run folder: `projects/<project_id>/runs/<run_id>/` con snapshot, manifest, outputs

## 6. Dipendenze

- Pydantic ≥ 2.0 (dipendenza non sempre installata in CI — vedere KNOWN LIMITATIONS)
- jsonschema (per validazione CLI)

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/project/schema.py` — `norm_code` default `"RD2229"` |
| NTC2018 | `src/project/schema.py` — `SeismicInputs`, `CodeSettings` |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Dipendenza da Pydantic ≥ 2.0 può non essere installata (CI blockers pre-esistenti)
- Schema versioning a 1.1.0 — versioni future richiedono nuove migration
- `GeometryEntry` e `LoadEntry` hanno campi TBD in alcuni sotto-schema

## 9. Next steps

- [ ] Documentare ogni campo di `ProjectModel` con tipo, default e significato strutturale
- [ ] Aggiungere migrazione verso versione 1.2.0 quando necessario
- [ ] Risolvere dipendenza Pydantic in CI (issue debito tecnico separata)

---

## I/O, CLI tools, test paths

- Struttura minima e comandi: vedi `docs/SCHEMA_IO.md`
- CLI tools: `tools/validate_project.py`, `tools/run_project.py`, `tools/replay_run.py`
- Test: `tests/test_project_schema_validation.py`, `tests/test_project_roundtrip.py`, `tests/test_timeline_manifest_hashing.py`, `tests/test_run_replay_idempotent.py`

---

## Evidenza file/line

- `src/project/model.py`, `src/project/timeline.py`, `tools/validate_project.py`, `tools/run_project.py`, `tools/replay_run.py`
- `schemas/project.schema.json` (deterministico)
- Vedi anche: `docs/SCHEMA_IO.md` per esempi e struttura file
