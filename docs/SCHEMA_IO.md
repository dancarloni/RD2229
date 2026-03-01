# PROJECT I/O + SCHEMA + TIMELINE/REPLAY (MVP)

## project.json struttura minima

```
{
  "meta": {
    "id": "proj1",
    "name": "Test Project",
    "created_at": "2026-03-01T00:00:00Z",
    "updated_at": "2026-03-01T00:00:00Z",
    "commit_hash": "abc123",
    "schema_version": "1.0.0"
  },
  "normative_profile": {
    "source_ids": ["RD2229"],
    "clauses": ["§4.2.1"]
  },
  "modules": [
    {"name": "mod1", "enabled": true, "params": {}}
  ],
  "io_settings": {}
}
```

## Comandi

- Validazione: `python tools/validate_project.py <project.json>`
- Run deterministico: `python tools/run_project.py <project.json>`
- Replay/confronto: `python tools/replay_run.py <run_dir>`

## Esempio di run folder

<<<<<<< HEAD
```
projects/proj1/runs/run_20260301T120000Z/
  project.snapshot.json
  output_mod1.json
  manifest.json
  run_record.json
```
=======
JSON Schema generato: `schemas/project.schema.json` (deterministico, sorted keys).
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))

## Output deterministico
- Nessun timestamp variabile nei file confrontati (solo in path)
- Manifest: elenco file + sha256

<<<<<<< HEAD
## Note
- Placeholder output per moduli senza executor: `{ "status": "TBD", "normative_ids": [...] }`
- Replay segnala drift se sha256 non corrisponde
=======
Dataclass che contiene i risultati della pipeline.

| Classe | Campi principali | Note |
|--------|-----------------|------|
| `ElementResult` | `element_id`, `ok`, `metrics`, `messages` | Risultato per elemento |
| `ResultsModel` | `ok`, `elements[]`, `warnings[]`, `trace[]`, `timestamp`, `schema_version_input` | Risultato globale |

## Pipeline

| Funzione | Modulo | Descrizione |
|----------|--------|-------------|
| `load_project(path)` | `src/project/repository.py` | Carica `ProjectModel` da file JSON |
| `save_project(model, path)` | `src/project/repository.py` | Salva `ProjectModel` su file JSON |
| `run_pipeline(project)` | `src/core/pipeline.py` | Esegue la pipeline → `ResultsModel` |
| `build_report(project, results)` | `src/reporting/report_builder.py` | Genera `ReportArtifact` |
| `export_report_html(artifact, path)` | `src/reporting/export.py` | Esporta report HTML |
| `export_report_md(artifact, path)` | `src/reporting/export.py` | Esporta report Markdown |

## Timeline / Run / Replay (MVP)

Ogni esecuzione (`run`) produce una cartella contenente:

| File | Contenuto |
|------|-----------|
| `project.snapshot.json` | Copia congelata dell'input del progetto |
| `manifest.json` | Metadati run: commit hash, python version, normative IDs, moduli eseguiti, hash SHA-256 di ogni output |
| `output_<step>.json` | Output deterministico per ogni pipeline step |

### Comandi

```bash
# Validare un progetto
python tools/validate_project.py path/to/project.json
# exit 0 = valido, exit 1 = errori (stampati su stderr)

# Eseguire un progetto (crea run folder)
python tools/run_project.py path/to/project.json --output-dir projects
# Crea projects/<run_id>/ con snapshot + manifest + outputs

# Replay e confronto
python tools/replay_run.py projects/<run_id>/
# exit 0 = identico, exit 1 = drift rilevato (diff su stderr + JSON su stdout)
```

### Esempio manifest.json

```json
{
  "commit_hash": "e70ec18",
  "modules_executed": ["validate", "checks"],
  "normative_ids": ["RD2229"],
  "outputs": {
    "output_checks.json": "sha256hex...",
    "output_validate.json": "sha256hex...",
    "project.snapshot.json": "sha256hex..."
  },
  "python_version": "3.12.3",
  "run_id": "run_20260301_194508_e70ec18",
  "schema_version": "1.1.0"
}
```

## Moduli sorgente

| File | Descrizione |
|------|-------------|
| `src/project/schema.py` | Modelli Pydantic (single source of truth) |
| `src/project/model.py` | Re-export + helper runtime (`get_commit_hash`, `project_to_snapshot`) |
| `src/project/repository.py` | Load/save/migrate |
| `src/project/timeline.py` | RunRecord, hashing, manifest, replay, drift detection |

## Limitazioni note

- La colonna "Note" nella matrice moduli è tutta "TBD" — richiede review manuale.
- I pipeline step producono output placeholder deterministici (nessun calcolo strutturale reale in questo MVP).
- `schemas/project.schema.json` deve essere rigenerato se il modello Pydantic cambia.
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
