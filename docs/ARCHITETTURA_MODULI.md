# Architettura Moduli — RD2229

> Manifesto documentale e indice architetturale del progetto RD2229.
> Questo file descrive tutti i moduli presenti nella codebase, il loro ambito
> normativo, lo stato di implementazione, la copertura dei test e le dipendenze.

---

## 1. Panoramica

Il progetto RD2229 digitalizza metodi storici e correnti di verifica
strutturale (Regio Decreto 2229/1939, DM 09/01/1996, DM 14/02/1992,
NTC 2018, Eurocodici) per elementi in calcestruzzo armato.

L'architettura è organizzata in moduli separati sotto `src/`, ciascuno con
responsabilità distinte.  Il logging centralizzato è fornito dal modulo
`src/rd2229/logging_bridge.py`.

---

## 2. Matrice Moduli

| Modulo | Percorso | Ambito / Norma | Stato | Test |
|--------|----------|----------------|-------|------|
| Core Calculus | `src/core_calculus/` | Motore di verifica — RD2229, DM92, DM96, NTC2018 | COMPLETO | ✔ |
| Core Pipeline | `src/core/` | Orchestrazione pipeline, risultati, combinazioni carichi | COMPLETO | ✔ |
| Project | `src/project/` | Modello dati progetto, persistenza JSON, schema | COMPLETO | ✔ |
| Reporting | `src/reporting/` | Generazione report HTML/Markdown | COMPLETO | ✔ |
| Fire | `src/fire/` | Verifiche al fuoco — ISO 834, NTC2018 §3.6, EN 1992-1-2 | PARZIALE | ✔ |
| Wind | `src/wind/` | Azioni del vento — NTC2018 §3.3, EN 1991-1-4, CNR-DT 207 | PARZIALE | ✔ |
| Materials | `src/materials/` | Repository materiali, proprietà meccaniche | COMPLETO | ✔ |
| Elements | `src/elements/` | Modelli elementi strutturali, risoluzione input | COMPLETO | ✔ |
| Methods | `src/methods/` | Implementazioni verifiche (TA, SLU, SLE) per norma | COMPLETO | ✔ |
| Codes | `src/codes/` | Registri normativi, parametri e clausole | COMPLETO | ✔ |
| Domain | `src/domain/` | Adattatori modello di dominio | COMPLETO | ✔ |
| Checks | `src/checks/` | Registro unificato check con `CheckSpec` / `NormRef` | COMPLETO | ✔ |
| Plugins | `src/plugins/` | Architettura plugin (discovery, registry) | COMPLETO | ✔ |
| RD2229 App | `src/rd2229/` | Entry point, logging, CLI, GUI Qt, sismico Art. 39 | COMPLETO | ✔ |
| CLI Package | `src/cli/` | Entry point CLI Typer-based | COMPLETO | ⚠ |
| UI Modern | `src/ui/` | GUI PyQt6 (MVVM), adattatori legacy Tkinter | PARZIALE | ✔ |

### Legenda stati

| Stato | Significato |
|-------|-------------|
| COMPLETO | Funzionalità principali implementate e testate |
| PARZIALE | Funzionalità base presenti, gap noti documentati come TODO |
| INCOMPLETO | Solo struttura / stub |
| STUB | File placeholder senza logica |

---

## 3. Dettaglio Moduli

### 3.1 Core Calculus (`src/core_calculus/`)

**Scopo:** Motore principale di verifica strutturale.

| File | Descrizione |
|------|-------------|
| `verification_engine.py` | Esecuzione verifiche per elemento |
| `validation_engine.py` | Validazione input |
| `normative_registry.py` | Template di verifica (TA, SLU, SLE, DM96) |
| `section_calculations.py` | Calcoli geometrici di sezione |
| `lc_fc_adjustments.py` | Fattori di carico e combinazioni |
| `contracts.py` | Tipi di dominio (`NormReference`, `ValidationIssue`) |
| `core/geometry_model.py` | Modello geometrico |

**Norme implementate:** RD2229 Art. 7-9, DM92, DM96 §2.3-2.4, NTC2018 §4.1

**Dipendenze:** `src/materials/`, `src/elements/`, `src/domain/`

---

### 3.2 Core Pipeline (`src/core/`)

**Scopo:** Orchestrazione del flusso di calcolo end-to-end.

| File | Descrizione |
|------|-------------|
| `pipeline.py` | `run_pipeline(ProjectModel) → ResultsModel` |
| `results.py` | Aggregazione risultati |
| `step5_adapter.py` | Adattatore NTC2018 Step 5 |
| `combinations/ntc2018_combinations.py` | Generazione combinazioni SLU/SLE |
| `materials/ntc2018_adapter.py` | Adattatore materiali NTC2018 |

**Dipendenze:** `src/project/`, `src/core_calculus/`, `src/reporting/`

---

### 3.3 Project (`src/project/`)

**Scopo:** Modello dati e persistenza del progetto.

| File | Descrizione |
|------|-------------|
| `repository.py` | `load_project()`, `save_project()` |
| `schema.py` | Modello Pydantic (`ProjectModel`) |
| `schema.json` | JSON Schema di validazione |

**Formato I/O:** JSON (`.jsonp`)

---

### 3.4 Reporting (`src/reporting/`)

**Scopo:** Generazione report strutturati.

| File | Descrizione |
|------|-------------|
| `report_builder.py` | `build_report(project, results) → ReportArtifact` |
| `export.py` | `export_report_html()`, `export_report_md()` |

**Formati output:** HTML, Markdown

---

### 3.5 Fire (`src/fire/`)

**Scopo:** Verifiche di resistenza al fuoco per strutture in c.a.

| File | Descrizione |
|------|-------------|
| `rc_fire_check.py` | Check RC al fuoco (tabellare) |
| `curves.py` | Curva ISO 834 standard |
| `eligibility.py` | Valutazione eleggibilità verifica fuoco |

**Norme:** ISO 834-1, NTC2018 §3.6.1, EN 1992-1-2

**Stato:** Metodo tabellare implementato; metodi semplificato e avanzato TODO.

---

### 3.6 Wind (`src/wind/`)

**Scopo:** Calcolo azioni del vento.

| File | Descrizione |
|------|-------------|
| `service.py` | `WindActionService` (dispatcher multi-norma) |
| `ntc2018.py` | Calcolo pressione vento NTC2018 |
| `ec1991_1_4.py` | EN 1991-1-4 |
| `cnr_dt207.py` | CNR-DT 207 |
| `models.py` | `WindSite`, `TerrainCategory`, `BuildingGeometry` |
| `outputs.py` | `PressureZoneResults`, `WindResults` |

**Norme:** NTC2018 §3.3, EN 1991-1-4 §4, CNR-DT 207

**Stato:** NTC2018 base implementata; EN 1991-1-4 e CNR-DT 207 parziali.

---

### 3.7 Checks Registry (`src/checks/`)

**Scopo:** Registro unificato di tutte le verifiche disponibili.

| File | Descrizione |
|------|-------------|
| `registry.py` | `CheckRegistry`, `CheckSpec`, `NormRef`, `get_registry()` |

**Check registrati:**

| Check ID | Norma | Clausola | Implementato |
|----------|-------|----------|:------------:|
| `rd2229.ta_flessione` | RD2229 | Art. 7 | ✔ |
| `rd2229.ta_pressoflessione` | RD2229 | Art. 7-8 | ✔ |
| `rd2229.ta_taglio` | RD2229 | Art. 9 | ✔ |
| `dm96.slu_flessione` | DM96 | §2.3 | ✔ |
| `dm96.slu_pressoflessione` | DM96 | §2.4 | ✔ |
| `ntc2018.slu_flessione` | NTC2018 | §4.1.2 | ✔ |
| `ntc2018.sle_deformazione` | NTC2018 | §4.1.4 | ❌ TODO |
| `ntc2018.sle_fessurazione` | NTC2018 | §4.1.4.2 | ❌ TODO |
| `fire.rc_tabellare` | ISO 834 / NTC2018 | §1 / §3.6.1 | ✔ |
| `wind.ntc2018.pressione_vento` | NTC2018 | §3.3 | ✔ |
| `wind.en1991_1_4.wind_actions` | EN 1991-1-4 | §4 | ❌ TODO |

---

### 3.8 Logging Centralizzato (`src/rd2229/logging_bridge.py`)

**Scopo:** Configurazione centralizzata del logging per l'intero progetto.

**Funzionalità:**
- `setup_logging(level, enable_file, log_dir)` — Configura handler console e file
- `get_logger(name)` — Logger figlio nel namespace `rd2229.*`
- `reset_logging()` — Reset per test
- `log_info(msg)` — Compatibilità all'indietro

**Handler file:** `RotatingFileHandler` con rotazione a 5 MB, 3 backup

**Formato:** `%(asctime)s | %(name)s | %(levelname)s | %(message)s`

---

### 3.9 Plugin System (`src/plugins/`)

**Scopo:** Architettura plugin per estensione modulare.

| File | Descrizione |
|------|-------------|
| `__init__.py` | `PluginSpec`, `ActionSpec`, `ParamSpec`, `PluginRegistry` |
| `loader.py` | Discovery plugin via entry_points o scan cartella |
| `base.py` | `BasePlugin` class |

**Entry point group:** `rd2229.plugins` (configurabile in `config/app.yml`)

---

## 4. Dipendenze tra Moduli

```
project/ ──────► core/pipeline ──────► core_calculus/
                     │                      │
                     ├──► reporting/         ├──► materials/
                     │                      ├──► elements/
                     └──► checks/registry   └──► domain/

fire/ ──► (indipendente, collegabile a pipeline)
wind/ ──► (indipendente, collegabile a pipeline)

rd2229/logging_bridge ──► (usato trasversalmente da tutti i moduli)
plugins/ ──► (infrastruttura, carica moduli a runtime)
```

---

## 5. Glossario Tecnico

| Termine | Significato |
|---------|-------------|
| **TA** | Tensioni Ammissibili (metodo di verifica storico) |
| **SLU** | Stato Limite Ultimo |
| **SLE** | Stato Limite di Esercizio |
| **SLV** | Stato Limite di salvaguardia della Vita |
| **RC / c.a.** | Cemento armato (Reinforced Concrete) |
| **REI** | Resistenza al fuoco (Résistance, Étanchéité, Isolation) |
| **DM92** | Decreto Ministeriale 14/02/1992 |
| **DM96** | Decreto Ministeriale 09/01/1996 |
| **NTC2018** | Norme Tecniche per le Costruzioni 2018 |
| **EC2** | Eurocodice 2 (EN 1992) |
| **ISO 834** | Curva standard di incendio |
| **CNR-DT 207** | Linee guida CNR per azioni del vento |

---

## 6. Gap Noti e TODO

- `ntc2018.sle_deformazione` — Verifica SLE deformazione non implementata
- `ntc2018.sle_fessurazione` — Verifica SLE fessurazione non implementata
- `wind.en1991_1_4` — Calcolo vento EN 1991-1-4 incompleto
- `fire` — Metodi semplificato e avanzato non implementati (solo tabellare)
- `src/cli.py` — File shadowed dal package `src/cli/`; da consolidare
- Internazionalizzazione (i18n) — Non ancora implementata
- Export PDF/DXF/SVG — Non ancora implementato (solo HTML/MD)

---

*Generato il 2026-02-28 — Aggiornare a ogni modifica strutturale.*
