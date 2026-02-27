# RD2229

[![CI](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml/badge.svg)](https://github.com/dancarloni/RD2229/actions/workflows/ci.yml)

Progetto per digitalizzare e rendere calcolabili i metodi storici (Regio Decreto 2229/1939, Santarella, Giangreco) con una GUI che riproduca i passaggi di progetto dell’epoca.

## 🆕 Nuova Architettura Modulare (v0.1.0)

Il progetto è stato **completamente ristrutturato** secondo un'architettura professionale e modulare. Tutti i file originali sono stati preservati in `src/legacy/` senza modifiche, mentre la nuova architettura si trova in moduli dedicati sotto `src/`.

### Struttura Modulare

```
src/
├── legacy/              # File originali preservati (NON MODIFICARE)
├── calc/                # Calcoli (area a taglio, registry sezioni)
├── materials/           # Modelli materiali, validazione, repository
├── elements/            # Modelli elementi strutturali, risoluzione input
├── codes/               # Registry normativo (NTC2018, EC2, ecc.)
│   ├── params/          # Parametri numerici (JSON)
│   └── clauses/         # Clausole normative (YAML)
├── actions/             # Repository azioni di verifica
├── report/              # Renderer report (MD, HTML, PDF)
│   └── templates/       # Template report
├── config/              # Configurazioni YAML (unità, numerici, app, features)
├── tools/               # CLI e utility export
└── tests/               # Test suite completa
```

### Principi Architetturali

- **Separazione totale** tra logica e GUI
- **Unità di misura fisse**: cm, cm², cm⁴, kg/cm², kg/m³ (nessuna conversione implicita)
- **Moduli STUB S2**: tutti i moduli contengono docstring estese, TODO chiari, type hints completi
- **Pipeline completa**: repository → resolver → actions → report
- **Configurazione YAML**: tutte le impostazioni gestite tramite file config
- **Test-driven**: ogni modulo ha test corrispondenti

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

## Note su dipendenze per test GUI
- `pytest` e `matplotlib` sono richiesti per il test suite completo.
- I test GUI richiedono Tk/Tcl installato e disponibile nel runtime Python.

## Demo: Verification Table (GUI)
Per aprire la finestra "Verification Table" con alcuni casi di esempio (sezioni e materiali di test) usa lo script demo incluso:

PowerShell:

```powershell
$env:PYTHONPATH='c:\workspaces\RD2229\RD2229\src'; python scripts/run_verification_demo.py
```

Linux/macOS / CMD:

#### Via CLI
```bash
python -m src.tools.verify_cli --config config/user_conf.yml --format html
```

#### Via Python
```python
from src.materials.material_repo import MaterialRepository
from src.elements.element_repo import ElementRepository
from src.codes.code_registry import bootstrap_codes

# Inizializza repository
materials = MaterialRepository()
elements = ElementRepository()
bootstrap_codes("src/codes")

# Usa i moduli...
```

### Test
```bash
# Test dei nuovi moduli
pytest src/tests/

# Test completi del progetto
pytest
```

### Migrazione Graduale

I nuovi moduli sono **stub S2** pronti per essere ampliati con Copilot Plan:
- Ogni file contiene TODO chiari per implementazioni future
- La struttura è completa e pronta all'uso
- I file legacy rimangono disponibili per retrocompatibilità
- La migrazione può essere incrementale

### Riferimenti

- Vedi [CHANGELOG.md](CHANGELOG.md) per dettagli completi delle modifiche
- Vedi `src/config/` per configurazioni disponibili
- Vedi `src/tests/` per esempi d'uso

---

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

