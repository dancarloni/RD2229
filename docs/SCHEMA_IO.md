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

```
projects/proj1/runs/run_20260301T120000Z/
  project.snapshot.json
  output_mod1.json
  manifest.json
  run_record.json
```

## Output deterministico
- Nessun timestamp variabile nei file confrontati (solo in path)
- Manifest: elenco file + sha256

## Note
- Placeholder output per moduli senza executor: `{ "status": "TBD", "normative_ids": [...] }`
- Replay segnala drift se sha256 non corrisponde
