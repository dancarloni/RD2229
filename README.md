<<<<<<< HEAD
# RD2229

[![CI](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml/badge.svg)](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml)

Progetto per digitalizzare e rendere calcolabili i metodi storici (Regio Decreto 2229/1939, Santarella, Giangreco) con una GUI che riproduca i passaggi di progetto dell’epoca.

## Obiettivo
Creare un motore di calcolo che:
- gestisca materiali, sezioni, armature e tabelle/abachi storici;
- mostri tutti gli step del calcolo (coefficiente, interpolazione, formula);
- consenta una GUI grafica chiara e “storica”.

## Struttura del progetto
- [src/rd2229](src/rd2229) — logica di calcolo e modelli
- [data](data) — tabelle e coefficienti digitalizzati
- [docs](docs) — note, roadmap e fonti
  - [Shear form factors and assumptions](docs/SHEAR_FORM_FACTORS.md) — defaults and reference assumptions for κ and A_ref (used for Timoshenko shear areas)
- [tests](tests) — test dei calcoli

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
1. Creare un ambiente Python.
2. Installare le dipendenze da [requirements.txt](requirements.txt).
3. Usare i modelli in [src/rd2229](src/rd2229).

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

---

## STEP 3A — Consolidamento Normativo e Tracciabilità

Questo step introduce le fondamenta architetturali per supportare **più normative** (NTC2018/EC8 e legacy come RD2229/39, DM92, DM96) con:
- separazione **Norma / Metodo / Policy**;
- risultati sempre accompagnati da **tracciabilità** (riferimenti, assunzioni, warning, limiti d'uso);
- struttura modulare per le norme legacy, progettata per future riscritture senza impatti sul core.

### Documentazione (STEP 3A)
- `docs/STEP3A_MASTER.md`
- `docs/ARCH_NORMATIVE_KERNEL.md`
- `docs/NORMATIVE_CAPABILITIES.md`
- `docs/LEGACY_CODES/RD2229_39/README.md`

### Nota su RD2229/39
La parte RD2229/39 è documentata come modulo isolato e altamente estendibile:
- masse di piano (impalcato + 1/2 elementi verticali sopra/sotto);
- componente **sussultoria** derivata (125% della ondulatoria), tracciata.

---

## STEP 5, 6, 7 – GUI moderna, reportistica e integrazione motore

### Installazione

```bash
# Installa il pacchetto (core, calcolo, repository)
pip install -e .

# Installa con GUI moderna PySide6 (opzionale)
pip install -e ".[gui]"
```

### Avvio GUI moderna

```bash
# Tramite modulo Python
python -m src.ui.app

# Tramite console script (se installato con pip install -e .[gui])
structcalc
```

> **Nota**: PySide6 è una dipendenza opzionale. Se non installata, il comando mostra
> un messaggio d'errore con istruzioni per l'installazione.

### Esecuzione test

```bash
# Test non-GUI (raccomandati in CI headless)
python -m pytest -m "not gui and not slow" -q

# Test specifici Step5, Step6, viewmodels
python -m pytest tests/test_step5_adapter_smoke.py tests/test_reporting_smoke.py \
    tests/test_modern_ui_nongui.py tests/test_pipeline_smoke.py -v
```

### Architettura GUI moderna (`src/ui/modern/`)

La GUI moderna segue il pattern **MVVM** con **Feature Registry**:

```
src/ui/
├── app.py                  ← entrypoint (python -m src.ui.app)
├── __main__.py             ← python -m src.ui
├── modern/
│   ├── main_window.py      ← QMainWindow + menu + statusbar
│   ├── navigation.py       ← NavigationPanel (sidebar + stacked widget)
│   ├── features/
│   │   ├── registry.py     ← FeatureSpec, register(), get_all()
│   │   └── builtin_features.py  ← schede built-in (ProjectInfo, Run, Results)
│   ├── viewmodels/         ← stato UI (ProjectViewModel, RunViewModel, ResultsViewModel)
│   ├── services/           ← adapter core/repository (ProjectIOService, CalculationService)
│   └── workers/            ← PipelineWorker (QRunnable background)
└── [legacy Tkinter files]  ← mantenuti come deprecated
```

#### Come aggiungere una nuova scheda

```python
from src.ui.modern.features.registry import FeatureSpec, register
from PySide6.QtWidgets import QLabel, QWidget

class MyFeature(FeatureSpec):
    feature_id = "my_feature"
    label = "La Mia Scheda"
    icon = "📐"
    order = 60  # posizione nella sidebar

    def create_widget(self, parent, project_vm, run_vm, results_vm):
        w = QWidget(parent)
        # ... costruisci il widget ...
        return w

# Registra prima di aprire la finestra
register(MyFeature())
```

### Reportistica (`src/reporting/`)

```python
from src.core.pipeline import run_pipeline
from src.reporting.report_builder import build_report
from src.reporting.export import export_report_html, export_report_md

results = run_pipeline(project)
artifact = build_report(project, results, title="Verifica RD2229")

export_report_html(artifact, "report.html")
export_report_md(artifact, "report.md")
```

### Step5 – Integrazione motore di verifica

Il modulo `src/core/step5_adapter.py` collega il `ProjectModel` al motore
`src/core_calculus/verification_service.py`:

```python
from src.core.step5_adapter import can_run_step5, run_step5

ok, reasons = can_run_step5(project)
if ok:
    results, warnings, trace = run_step5(project)
```

La pipeline (`src/core/pipeline.py`) chiama automaticamente step5 e arricchisce
le metriche dei `ElementResult` con i valori numerici dal motore reale.

### TODO futuri

1. Schede GUI complete per Seismic, CodeSettings, Materials, Geometry
2. Template PySide6 con QSS/risorse per styling moderno
3. Export PDF (se si aggiunge WeasyPrint/reportlab come dep opzionale)
4. Fixture di test `tests/fixtures/minimal_project_step5.json`
5. Migrazione schema 1.0.0 → 1.1.0 per campi LC/FC nel ProjectModel
6. Worker asincrono per step5 (usare PipelineWorker anche per step5)
7. Scheda "Log" per visualizzare la traccia completa del calcolo
8. Import/export CSV per geometrie e materiali
9. Integrazione NTC2018 template nella pipeline GUI
10. Documentazione Sphinx auto-generata dai docstring

=======
# RD2229

[![CI](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml/badge.svg)](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml)

Progetto per digitalizzare e rendere calcolabili i metodi storici (Regio Decreto 2229/1939, Santarella, Giangreco) con una GUI che riproduca i passaggi di progetto dell’epoca.

## Obiettivo
Creare un motore di calcolo che:
- gestisca materiali, sezioni, armature e tabelle/abachi storici;
- mostri tutti gli step del calcolo (coefficiente, interpolazione, formula);
- consenta una GUI grafica chiara e “storica”.

## Struttura del progetto
- [src/rd2229](src/rd2229) — logica di calcolo e modelli
- [data](data) — tabelle e coefficienti digitalizzati
- [docs](docs) — note, roadmap e fonti
  - [Shear form factors and assumptions](docs/SHEAR_FORM_FACTORS.md) — defaults and reference assumptions for κ and A_ref (used for Timoshenko shear areas)
- [tests](tests) — test dei calcoli

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
>>>>>>> 7d17959e67335d1598aebfe93ebc3ee7c638c805
