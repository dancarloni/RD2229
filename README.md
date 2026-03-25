## Setup rapido ambiente (venv, dipendenze, verifica Pydantic)

Per creare un ambiente locale riproducibile e verificare che Pydantic sia installato:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
python -c "import pydantic; print(pydantic.__version__)"
```

Se il comando stampa una versione >=2,<3, l’ambiente è pronto.

## ⚠️ Policy obbligatoria: Linting e Formatting pre-commit

**IMPORTANTE:** Prima di ogni commit/push, è **obbligatorio** eseguire questi comandi per evitare fallimenti CI su GitHub:

```bash
# 1. Fix automatico errori linting
python -m ruff check . --fix

# 2. Formatting automatico
python -m ruff format .

# 3. Ordinamento import
python -m isort . --profile black --line-length 100

# 4. Formatting con black
python -m black . --line-length 100

# 5. Verifica finale
python -m ruff check .
python -m flake8 .
```

**Perché questo è necessario:** Gli errori di linting/import che non emergono in locale possono causare fallimenti CI su GitHub a causa di:

- Differenze di ambiente (versioni tool, Python, dipendenze)
- Comandi non eseguiti localmente prima del push
- Cache locali che mascherano errori

**Best practice:**

- Eseguire questi comandi **prima** di ogni `git commit`
- Verificare che `ruff check .` restituisca "All checks passed!"
- I test devono passare: `pytest -q`

Se hai dubbi sulla coerenza locale/CI, usa Docker o GitHub Codespaces per replicare l'ambiente CI.

# RD2229

[![CI](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml/badge.svg)](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml)

Progetto per digitalizzare e rendere calcolabili i metodi storici (Regio Decreto 2229/1939, Santarella, Giangreco) con una GUI che riproduca i passaggi di progetto dell’epoca.

## Obiettivo

Creare un motore di calcolo che:

- gestisca materiali, sezioni, armature e tabelle/abachi storici;
- mostri tutti gli step del calcolo (coefficiente, interpolazione, formula);
- consenta una GUI grafica chiara e “storica”.

## Architettura v0.1.0 (stato attuale)

- Modello progetto validato in `src/project/schema.py` con `ProjectModel` (Pydantic).
- Persistenza JSON/YAML con auto-detect estensione in `src/project/repository.py`.
- Pipeline calcolo in `src/core/pipeline.py` con passi configurabili (`project.pipeline_steps`).
- Reporting MD/HTML in `src/reporting/report_builder.py` + `src/reporting/export.py`.
- Plugin di esempio in `src/plugins/` (`info`, `run`, `export`) con registry/discovery.
- GUI registry moderno in `src/ui/modern/registry.py` e sidebar dinamica in `src/ui/modern/sidebar.py`.

## Entry point CLI/GUI

- CLI Typer: `python -m src.cli.entrypoint --help`
  - comandi: `new`, `load`, `run`, `export`
- GUI: `python -m src.gui.entrypoint`

L’entrypoint installato `rd2229` punta a `src.cli.entrypoint:main`.
L’entrypoint installato `rd2229-gui` punta a `src.gui.entrypoint:main`.

## Avvio rapido GUI moderna (V1)

La GUI operativa principale e tab-based (Progetto, Verifica, Report, Materiali, Sezioni, FEM/Telai, Vento).

```bash
# Avvio GUI moderna
python -m src.ui.modern.app

# Avvio GUI con progetto pre-caricato
python -m src.ui.modern.app --project "./examples/projects/00_Progetto_di_test.jsonp" --output-dir "./"

# Smoke workflow headless (CI/local)
python -m src.ui.modern.app --project "./examples/projects/00_Progetto_di_test.jsonp" --headless
```

Avvio package-level:

```bash
python -m rd2229
```

Dipendenza opzionale per report HTML embedded in-app:

```bash
pip install -e .[gui]
```

Se `PyQt6-WebEngine` non è installato, il Report Viewer usa automaticamente il fallback `QTextBrowser`.

## Struttura del progetto

- [src/rd2229](src/rd2229) — logica di calcolo e modelli
- [data](data) — tabelle e coefficienti digitalizzati
- [docs](docs) — note, roadmap e fonti
  - [Shear form factors and assumptions](docs/SHEAR_FORM_FACTORS.md) — defaults and reference assumptions for κ and A_ref (used for Timoshenko shear areas)
- [tests](tests) — test dei calcoli

## Continuous Integration and Testing

The project uses a headless CI workflow that runs on every push and pull
request against `main`.  The **python-ci.yml** workflow is the sole gating
pipeline; it performs the following steps in order:

1. Install dependencies (including `requirements-dev.txt` and the package
   itself via `pip install -e .`).
2. Run `ruff check src tests`.
3. Run `python tools/run_mypy_ci.py` for static typing.
4. Reinstall editable package (required by some CI runners).
5. Execute the standard test suite with `pytest -q`.
   - `pytest.ini` is configured to **ignore `tests/legacy_tkinter` and
     `tests/legacy_qt` directories** so that GUI tests do not run in the
     headless CI environment.
6. Run `flake8 .` (optional lint pass, mostly redundant with `ruff`).

No step uses `continue-on-error` or other masking; failures block merge.

### GUI and legacy tests

Tests that require a display or third‑party GUI bindings have been moved to
`tests/legacy_qt` or `tests_legacy` (Tkinter). These directories are **not
collected by default**.  The standard CI suite remains lightweight and
non‑GUI.

A separate manual workflow (`.github/workflows/gui-tests.yml`) is provided
for running Qt tests.  It can be triggered via the "Actions" tab and
installs `pytest-qt` plus a real Qt binding (`PySide6`).  This job is
opt‑in and does **not** block merges.

To run GUI tests locally you can use:

```bash
pytest tests/legacy_qt     # Qt-specific tests (requires PySide6/PyQt6)
pytest tests_legacy        # legacy Tkinter tests (requires tkinter)
```

The documentation in `CONTRIBUTING.md` has been updated accordingly.

## Struttura logica dei moduli

### 1. Moduli fondamentali (core)

Elementi comuni a tutte le tipologie di calcolo:

- **Materiali** (`core/materials.py`)
  - Calcestruzzo (resistenze, modulo elastico, coefficienti storici)
  - Acciaio (resistenze, modulo elastico, tipologie storiche)
  - Proprietà fisiche (peso specifico, coefficienti di dilatazione)

- **Geometria delle sezioni** (`core/geometry.py`)
  - Rettangolare
  - Circolare
  - A T
  - Ad L
  - Ad I
  - Altre forme composite
  - A T rovescia
  - A pigreco (Π)
  - Rettangolare cava
  - Circolare cava

- **Armatura** (`core/reinforcement.py`)
  - Ordini di armatura (superiore/inferiore)
  - Area dei ferri per strato
  - Copriferro (superiore/inferiore)
  - Diametro delle barre
  - Staffe (diametro, passo)
  - Ferri piegati
  - Armature aggiuntive

- **Proprietà della sezione** (`core/section_properties.py`)
  - Area
  - Momento statico
  - Momento di inerzia
  - Peso proprio
  - Baricentro

- **Interpolazione** (`core/interpolation.py`)
  - Interpolazione lineare
  - Interpolazione bilineare (per tabelle a due variabili)
  - Lettura e gestione abachi storici

### 2. Moduli di calcolo specifici

Ciascun modulo implementa le procedure storiche per un elemento strutturale.

**Struttura tipo per ogni modulo:**

```
calculations/
├── travi/
│   ├── __init__.py
│   ├── flessione_semplice.py      # Trave inflessa
│   ├── taglio.py                  # Calcolo a taglio
│   ├── torsione.py                # Torsione
│   └── presso_tenso_flessione.py  # Pressoflessione/tensoflessione
├── pilastri/
│   ├── __init__.py
│   ├── compressione_semplice.py
│   ├── pressoflessione_retta.py
│   └── pressoflessione_deviata.py
├── solette/
│   ├── __init__.py
│   ├── piastra_appoggiata.py
│   └── piastra_incastrata.py
├── solai/
│   ├── __init__.py
│   ├── latero_cemento.py
│   └── putrelle_e_voltine.py
├── fondazioni/
│   ├── __init__.py
│   ├── plinti.py
│   ├── travi_rovesce.py
│   └── platee.py
└── scale/
  ├── __init__.py
  └── (moduli per calcoli scale verranno aggiunti qui)
```

**Moduli previsti** (da integrare progressivamente):

- `travi/` — Travi (flessione, taglio, torsione)
- `pilastri/` — Pilastri (compressione, pressoflessione)
- `solette/` — Solette e piastre
- `solai/` — Solai (latero-cemento, putrelle e voltine)
- `fondazioni/` — Fondazioni (plinti, travi rovesce, platee)
- `scale/` — Scale
- `muri/` — Muri di sostegno
- Altri moduli specifici da definire

### 3. Moduli di verifica

Verifiche secondo RD 2229/1939 e normative storiche dell'epoca:

```
verifications/
├── __init__.py
├── rd2229/
│   ├── __init__.py
│   ├── tensioni_ammissibili.py    # Verifiche alle tensioni ammissibili
│   ├── deformazioni.py            # Verifiche deformative
│   ├── fessurazione.py            # Controllo fessurazione
│   └── stabilita.py               # Verifiche di stabilità
└── coefficienti/
    ├── __init__.py
    ├── sicurezza.py               # Coefficienti di sicurezza storici
    └── carico.py                  # Coefficienti di carico
```

### 4. Database tabelle storiche

```
data/
├── tables.schema.json             # Schema generale
├── rd2229/
│   ├── coefficienti_rigidezza.json
│   ├── tensioni_ammissibili.json
│   └── coefficienti_sicurezza.json
├── santarella/
│   ├── tabelle_cemento_armato.json
│   └── abachi_flessione.json
└── giangreco/
    ├── tabelle_sezioni.json
    └── diagrammi_interazione.json
```

### Note per integrazioni future

- Ogni nuovo modulo di calcolo deve seguire la struttura `calculations/<elemento>/<sottoargomento>.py`
- Le funzioni di calcolo devono documentare: formule usate, riferimenti normativi, step intermedi
- Le verifiche devono restituire sia il risultato (OK/NON OK) che i passaggi di calcolo
- Tutte le tabelle/coefficienti devono essere centralizzate in `data/` con schema JSON validabile

## Avvio rapido (solo logica)

## Development

We use pre-commit hooks to ensure consistent formatting and basic checks before commits.

Consolidation note: the polygon-based section geometry and the section graphics controller have been unified into canonical modules:

- `src/core_calculus/core/geometry_model.py` (SectionGeometry / SectionProperties)
- `apps/sections/section_graphics.py` (SectionViewTransform / SectionGraphicsController)

See `docs/consolidation.md` and `docs/migration-quickstart.md` for migration details and examples.

Install and enable the hooks locally with:

```bash
pip install pre-commit
pre-commit install
```

Run the checks locally with `pre-commit run --all-files` (useful before PRs).

1. Creare un ambiente Python (consigliato: `.venv`).
   - Windows (PowerShell): `python -m venv .venv ; .\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv ; source .venv/bin/activate`
2. Installare le dipendenze di runtime: `pip install -r requirements.txt`.

   **Opzionale:** per calcoli geometrici più robusti (area/centroid e core basati su buffer), installare `shapely`:

   ```bash
   pip install shapely
   ```

3. Installare le dipendenze di sviluppo e test: `pip install -r requirements-dev.txt` (contiene `pytest`, `flake8`, `mypy`).
4. Abilitare i pre-commit hooks: `pip install pre-commit && pre-commit install`.
5. Eseguire i test: `pytest -q`.
6. Usare i modelli in [src/rd2229](src/rd2229).

## Demo: Verification Table (GUI)

Per aprire la finestra "Verification Table" con alcuni casi di esempio (sezioni e materiali di test) usa lo script demo incluso:

PowerShell:

```powershell
$env:PYTHONPATH='c:\workspaces\RD2229\RD2229\src'; python scripts/run_verification_demo.py
```

Linux/macOS / CMD:

```bash
python scripts/run_verification_demo.py
```

Lo script apre una finestra Tkinter con la tabella per inserimento rapido delle verifiche e precompila alcune righe demo per testare il flusso di inserimento, autocomplete e il calcolatore aree armatura (tasto 'c' su colonne `As` / `As'`).

Esempio rapido (uso delle nuove sezioni):

```python
from rd2229.core.geometry import (
  InvertedTSection,
  PiSection,
  RectangularHollowSection,
  CircularHollowSection,
)
from rd2229.core.section_properties import compute_section_properties

sec1 = InvertedTSection(flange_width=200.0, flange_thickness=20.0, web_thickness=10.0, web_height=160.0)
sec2 = PiSection(width=200.0, top_thickness=20.0, leg_thickness=10.0, leg_height=160.0)
sec3 = RectangularHollowSection(outer_width=200.0, outer_height=100.0, inner_width=160.0, inner_height=60.0)
sec4 = CircularHollowSection(outer_diameter=100.0, inner_diameter=60.0)

for s in (sec1, sec2, sec3, sec4):
  p = compute_section_properties(s)
  print(f"{s.__class__.__name__}: area={p.area:.2f}, cx={p.centroid_x:.2f}, cy={p.centroid_y:.2f}, Ix={p.ix:.2f}")
```

## Prossimi passi suggeriti

- Digitalizzare le tabelle in [data/tables.schema.json](data/tables.schema.json).
- Implementare le procedure specifiche dei capitoli RD 2229/Santarella/Giangreco.
- Aggiungere GUI (desktop o web) con visualizzazione passo‑passo.

## Calcolo: resistenza del calcestruzzo

È disponibile uno strumento di calcolo per ricavare la tensione ammissibile
del calcestruzzo (`σ_c`) a partire dalla resistenza caratteristica a
28 giorni (`σ_c28`). Lo strumento considera il tipo di cemento,
le condizioni di sezione (semplicemente compresse, inflessa/presso-inflessa)
e la qualità dei controlli (regola `σ_c = σ_c28/3` con cap se previsto).

File:

- [src/rd2229/tools/concrete_strength.py](src/rd2229/tools/concrete_strength.py)

Principali funzioni:

- `compute_allowable_compressive_stress(sigma_c28_kgcm2, cement, condition, controlled_quality)`:
  calcola `σ_c` (Kg/cm²) usando le regole storiche descritte nelle fonti.
- `compute_allowable_shear(cement)`:
  restituisce il carico di sicurezza al taglio e la tensione tangenziale massima (Kg/cm²).

Unità e convenzioni storiche:

- Tutti gli input e gli output del modulo sono espressi in `Kg/cm²` (tensione/pressione),
  coerentemente con le unità storiche usate nel RD 2229 e nei testi dell'epoca.
- Sono comunque disponibili funzioni di conversione verso/da MPa nel modulo,
  se serve interoperare con strumenti moderni.

Note implementative:

- Le regole sono state implementate come traduzione diretta delle tabelle storiche
  (vedi risorse in `docs/` quando disponibili). Questo modulo è standalone
  e non altera il comportamento degli altri moduli del progetto.

### Gestione materiali

I materiali creati dall'utente (es. tipi di calcestruzzo) possono essere
persistiti e riutilizzati in futuri calcoli. Il file di persistenza predefinito
è `data/materials.json` (configurabile in `.rd2229_config.yaml` con la chiave
`materials_file`).

Il package fornisce API CRUD per i materiali in `src/rd2229/tools/materials_manager.py`:

- `add_material(material_dict)` — aggiunge un materiale (calcola `σ_c` se manca);
- `get_material(name)` — ottiene un materiale per nome;
- `update_material(name, updates)` — aggiorna i campi di un materiale;
- `delete_material(name)` — rimuove un materiale;
- `list_materials()` — elenca tutti i materiali.

Esempio rapido (script demo incluso):

```powershell
$env:PYTHONPATH = 'c:\workspaces\RD2229\RD2229\src'; python scripts/run_materials_demo.py
```

Le unità storiche (Kg/cm²) vengono usate per le resistenze e le tensioni.

### GUI per materiali

È disponibile una semplice interfaccia grafica (Tkinter) per gestire i materiali
in modo interattivo (aggiungi/modifica/elimina). La GUI è separata dalle routine
di calcolo e usa `src/rd2229/tools/materials_manager.py` per le operazioni.

Avvio (PowerShell):

```powershell
$env:PYTHONPATH = 'c:\workspaces\RD2229\RD2229\src'
python scripts/run_materials_gui.py
```

La GUI è pensata per prototipazione: se preferisci posso integrarla in una
futura GUI principale del progetto o adattarla a framework diversi (Qt, web).
