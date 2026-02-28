# Schema I/O — Convenzioni Input / Output / Configurazioni

> Documentazione delle convenzioni di dati, formati e validazione
> per tutti i moduli del progetto RD2229.

---

## 1. Formato Progetto

### Modello Dati (`ProjectModel`)

Il progetto è definito dal modello Pydantic in `src/project/schema.py` con
JSON Schema generato in `src/project/schema.json`.

| Sezione | Tipo | Descrizione |
|---------|------|-------------|
| `project_info` | `ProjectInfo` | Nome, descrizione, autore, date |
| `code_settings` | `CodeSettings` | Norma attiva, stati limite, unità |
| `geometry` | `list[GeometryEntry]` | Geometria elementi (id, tipo, dimensioni) |
| `loads` | `list[LoadEntry]` | Sollecitazioni per elemento (N, Mx, My, Tx, Ty) |
| `fire_settings` | `FireSettings` | Abilitazione fuoco, scenario, durata |
| `seismic_inputs` | `dict` | Parametri sismici opzionali |
| `schema_version` | `str` | Versione schema (attualmente `1.1.0`) |

### Persistenza

| Operazione | Funzione | Formato |
|------------|----------|---------|
| Caricamento | `load_project(path)` | JSON (`.jsonp`, `.json`) o YAML |
| Salvataggio | `save_project(project, path)` | JSON o YAML (da estensione file) |

- Scrittura atomica con file temporaneo `.tmp` + `os.replace()`.
- Migrazione automatica di formati legacy (`sections` → `geometry`).

---

## 2. Formati di Output

### Report

| Formato | Funzione | Estensione |
|---------|----------|------------|
| HTML | `export_report_html(artifact, path)` | `.html` |
| Markdown | `export_report_md(artifact, path)` | `.md` |

Il report è costruito da `build_report(project, results)` che produce
un `ReportArtifact` con sezioni strutturate.

### Risultati Pipeline

`run_pipeline(ProjectModel)` restituisce un `ResultsModel`:

```python
@dataclass
class ResultsModel:
    ok: bool                    # True se tutte le verifiche sono soddisfatte
    elements: list[dict]        # Risultati per elemento
    warnings: list[str]         # Avvertimenti
    trace: dict                 # Traccia di esecuzione
```

---

## 3. Dati Normativi

### Vento (`data/wind/`)

| File | Contenuto | Norma |
|------|-----------|-------|
| `ntc2018_wind_zones.json` | Zone di vento con parametri (vb0, a0, ka) | NTC2018 Tab. 3.3.I |

### Fuoco (`data/fire/`)

| File | Contenuto | Norma |
|------|-----------|-------|
| `axis_distance_table.json` | Tabella distanze asse per durata fuoco | EN 1992-1-2 |

### Sismico (`data/rd2229/seismic/`)

| File | Contenuto | Norma |
|------|-----------|-------|
| `p_coeff_table.json` | Coefficienti sismici `p` | RD2229 Art. 39 |

### Coefficienti (`src/repositories/data/`)

| File | Contenuto |
|------|-----------|
| `tables.schema.json` | Schema JSON per tabelle coefficienti RD2229 |

---

## 4. Configurazione

### Impostazioni Progetto (`CodeSettings`)

| Campo | Tipo | Default | Descrizione |
|-------|------|---------|-------------|
| `norm_code` | `str` | `"NTC2018"` | Normativa di riferimento |
| `limit_states` | `list[str]` | `["SLU"]` | Stati limite da verificare |
| `existing_structure` | `bool` | `False` | Struttura esistente |
| `units` | `dict` | kN, cm | Sistema unità |

### Impostazioni Fuoco (`FireSettings`)

| Campo | Tipo | Default | Descrizione |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Abilitazione verifiche fuoco |
| `scenario` | `str` | `"ISO_834"` | Curva di incendio |
| `required_rating_minutes` | `int` | `60` | Durata resistenza richiesta |

---

## 5. Validazione

- Il modello `ProjectModel` utilizza **Pydantic** per la validazione
  strutturale e di tipo dei dati in ingresso.
- Il JSON Schema (`schema.json`) è generato automaticamente dal modello
  Pydantic e può essere usato per validazione esterna.
- La `ValidationEngine` in `src/core_calculus/validation_engine.py`
  esegue validazioni di dominio (range, coerenza, completezza).

---

## 6. Logging

Tutti i moduli utilizzano il logging centralizzato tramite
`src/rd2229/logging_bridge.py`:

```python
from src.rd2229.logging_bridge import get_logger
logger = get_logger("nome_modulo")
logger.info("Operazione completata")
```

Formato standard:
```
2026-02-28 08:51:23 | rd2229.pipeline | INFO | Pipeline started
```

Opzione file rotante: `logs/rd2229.log` (5 MB, 3 backup)

---

*Generato il 2026-02-28 — Aggiornare a ogni modifica dei formati I/O.*
