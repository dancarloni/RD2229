## Repository overview

**RD2229** is a Python (≥ 3.11) structural-engineering calculation tool that digitises historical Italian methods (Regio Decreto 2229/1939, Santarella, Giangreco, DM96, DM92, NTC2018, Eurocode). It exposes a core calculation engine, a project pipeline, HTML/MD reporting, and both a legacy Tkinter GUI and a modern PySide6 GUI.

## Project layout

```
src/                        # All production code (installed as editable package)
  core_calculus/            # Main verification engine and historical checks
    core/                   # verification_engine.py, geometry_model.py, contracts.py
    normative_registry.py   # All verification templates (TA, SLU, SLE, DM96, …)
  core/                     # Pipeline orchestration (pipeline.py, step5_adapter.py)
  project/                  # ProjectModel, schema versioning, repository.py
  reporting/                # report_builder.py, export.py (HTML + MD, no Jinja2)
  fire/                     # Fire checks (curves.py, eligibility.py, rc_fire_check.py)
  wind/                     # Wind actions (ntc2018.py, ec1991_1_4.py, …)
  materials/                # Material models and repository
  elements/                 # Structural element models
  ui/                       # modern/ (PySide6 MVVM) + main_window.py (legacy Tkinter)
  legacy/                   # Original files – DO NOT MODIFY
calculations/               # Per-element calculation modules (pattern: <element>/<topic>.py)
config/                     # YAML-driven loaders (calculation_codes_loader.py, historical_materials_loader.py)
data/                       # JSON/YAML tables and coefficients loaded at runtime
tests/                      # Pytest suite (~100 test files); conftest.py skips tkinter-dependent files in CI
tests_legacy/               # Archived legacy tests – excluded from all CI runs
verifications/              # Historical verification logic (also in src/core_calculus/core)
core/                       # Shim package that re-exports from src/ for backwards compatibility
```

Key config files: `pyproject.toml` (ruff/black/isort/mypy/pytest/bandit), `pytest.ini`, `.pre-commit-config.yaml`, `.flake8`, `mypy.ini`.

## Environment setup

```bash
python -m venv .venv && source .venv/bin/activate   # Linux/macOS
# .\.venv\Scripts\Activate.ps1                       # Windows PowerShell
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .        # installs src/ as editable package; required for imports to work
```

Always run `pip install -e .` before running tests. Without it, `from src.*` imports may fail.

## Running tests

```bash
# Standard run – skips tkinter-dependent tests automatically when tkinter is absent
PYTHONPATH=. pytest -q

# Run a single test file
PYTHONPATH=. pytest tests/test_ta_method.py -q

# Run only non-GUI tests explicitly
PYTHONPATH=. pytest -q -m "not gui and not slow"
```

`tests/conftest.py` automatically excludes ~25 tkinter-dependent test modules when tkinter is unavailable (headless CI). Do not remove entries from `_TKINTER_DEPENDENT` unless the file no longer imports tkinter transitively.

Important: `pyproject.toml` sets `pythonpath = [".", "src"]` for pytest, but CI also sets `PYTHONPATH=$GITHUB_WORKSPACE` explicitly. When running locally, set `PYTHONPATH=.` to replicate CI behaviour.

## Linting and formatting

```bash
ruff check .                # fast lint (F/E/W/I/N/UP rules, configured in pyproject.toml)
ruff format .               # format with ruff formatter
black --check --line-length 100 .
isort --check-only --diff --profile black --line-length 100 .
flake8 .                    # secondary lint (max-line-length 100, see .flake8)
```

The active CI workflow (`.github/workflows/python-ci.yml`) runs mypy, pytest, and flake8 on Python 3.12. `lint-test.yml` runs ruff, isort, black, and pytest on Python 3.10 and 3.11.

**Known issue in `lint-test.yml`**: `matrix.python-version` uses unquoted `3.10` – YAML parses it as the float `3.1` (trailing zero dropped), selecting a non-existent Python version. Always use quoted strings (`'3.10'`, `'3.11'`) in workflow matrices.

## Type checking

```bash
MYPYPATH=. python tools/run_mypy_ci.py   # uses pyproject.toml strict config
```

mypy is configured strict (`disallow_untyped_defs`, `warn_return_any`, etc.). New functions must include type annotations.

## Pre-commit hooks (local only)

```bash
pip install pre-commit && pre-commit install
pre-commit run --all-files
```

Hooks run: trailing-whitespace, end-of-file-fixer, check-yaml, black, isort, ruff, ruff-format, mypy, bandit, and a custom `replace-sigma` script.

## Key architectural conventions

- **Fixed units**: `cm`, `cm²`, `cm⁴`, `kg/cm²`, `kg/m³`. No implicit conversions. Historical routines use `Kg/cm²`.
- **Calculation codes**: string keys `"TA"`, `"SLU"`, `"SLE"`, `"DM96"`, etc. select engine behaviour/data tables.
- **Verification engine**: use `create_verification_engine(calculation_code)` from `src/core_calculus/core/verification_engine.py`.
- **New calculation modules**: place under `calculations/<element>/<topic>.py`. Return both a final result and intermediate steps (OK/NON OK + steps list).
- **New data tables**: add JSON under `data/` and register in the appropriate `config/*_loader.py`.
- **VerificationInput**: use `Mx=` (bending moment X-axis) and `Ty=` (shear Y-axis; Italian *taglio*) in constructors. Legacy aliases `M=` and `T=` also work. Access stored values via `.M` (→ `Mx`) and `.T` (→ `Ty`) properties.
- **Pipeline API**: `load_project(path)→ProjectModel`, `run_pipeline(ProjectModel)→ResultsModel`, `build_report(ProjectModel, ResultsModel)→ReportArtifact`.
- **GUI**: modern PySide6 GUI uses MVVM + Feature Registry pattern (`src/ui/modern/`). Legacy Tkinter GUI is in `src/ui/main_window.py` – do not modify.
- **Schema versioning**: project JSON schema is v1.1.0; migration chain lives in `src/project/repository.py`.

## Adding a new test

Place the file in `tests/test_<topic>.py`. If it imports tkinter directly or transitively (via `materials_repository`, `sections_app.ui.*`, or `verification_table`), add it to `_TKINTER_DEPENDENT` in `tests/conftest.py`.

## CI workflows summary

| File | Trigger | Python | What it does |
|---|---|---|---|
| `python-ci.yml` | push/PR to main, feature/** | 3.12 | mypy → pytest → flake8 |
| `lint-test.yml` | push/PR to main | 3.10, 3.11 | ruff → isort → black → pytest |
| `ci.yml` | push/PR to main | 3.8 | pytest → pylint → mypy → bandit |
| `nightly.yml` | schedule | – | extended/nightly checks |
