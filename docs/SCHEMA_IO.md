# Schema I/O — RD2229

Descrizione delle strutture dati di input e output della pipeline di calcolo.
Tutte le informazioni sono derivate meccanicamente dal codice sorgente.

> **Auditato al commit corrente — generato manualmente. Aggiornare con `tools/audit_modules.py`.**

## Input: `ProjectModel` (`src/project/schema.py`)

Modello Pydantic che definisce il progetto strutturale.
Versione schema corrente: **1.1.0** (costante `CURRENT_SCHEMA_VERSION`).

| Classe | Campi principali | Note |
|--------|-----------------|------|
| `ProjectInfo` | `name`, `description`, `author`, `created_at`, `updated_at` | Metadati progetto |
| `GeometryEntry` | `id`, `type`, `width`, `height`, `fire_selected`, `extra` | Geometria elemento |
| `MaterialEntry` | `id`, `type`, `material_class`, `f_ck`, `f_yk`, `extra` | Materiale |
| `LoadEntry` | `element_id`, `N`, `Mx`, `My`, `Mz`, `Tx`, `Ty` | Carichi su elemento |
| `SeismicInputs` | `class_of_use`, `vita_nominale_years`, `hazard_profile` | Input sismici |
| `CodeSettings` | `norm_code`, `limit_states` | Impostazioni normativa |
| `ProjectModel` | `schema_version`, `project_info`, `geometry[]`, `materials[]`, `loads[]`, `code_settings`, `seismic` | Modello radice |

JSON Schema generato: `src/project/schema.json`.

## Output: `ResultsModel` (`src/core/results.py`)

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

## Limitazioni note

- La colonna "Note" nella matrice moduli è tutta "TBD" — richiede review manuale.
- Non esistono test end-to-end che verifichino il round-trip completo
  `load → pipeline → report → export` con dati reali (il file
  `examples/project_example.json` non è presente nel repository).
