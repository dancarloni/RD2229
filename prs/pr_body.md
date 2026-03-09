## Obiettivo

Migrazione graduale ma definitiva della GUI da Tkinter a PySide6 (Qt), con entrypoint unico `rd2229` e legacy Tkinter confinata in `rd2229.ui_legacy` (opt-in).

## Modifiche principali

### Nuova GUI (skeleton Qt)

- Aggiunto ui_qt con app.py (main/entrypoint) e pagine minime:
  - `pages/home.py`, `pages/settings.py`, `pages/verification.py`
- Aggiunti scaffolding services/viewmodels (MVVM + adapters):
  - `services/project_store.py`, `services/verification_adapter.py`
  - `viewmodels/verification_vm.py`
  - `services/logging_bridge.py`, `services/plugin_registry.py`

### Legacy Tkinter isolata (opt-in)

- Spostata/isolata la UI Tkinter sotto ui_legacy.
- Avvio legacy solo esplicito:
  - `RD2229_LEGACY_UI=1 python -m rd2229.ui_legacy.module_selector`

### Packaging / Avvio

- Aggiornato pyproject.toml:
  - `rd2229 = "rd2229.ui_qt.app:main"`
  - extras `gui = ["PySide6>=6.6"]`
- Supporto `python -m rd2229` via __main__.py.
- Se PySide6 non installato: `rd2229` stampa istruzioni installazione (`pip install -e .[gui]`) ed esce con code 2 (senza stack trace).

### Test

- Aggiunti test guardiani e smoke:
  - anti-tkinter: `test_no_tkinter_imports.py`
  - smoke Qt / entrypoint: `test_app_launch.py`, `test_entrypoint_no_pyside.py`
  - project store, VM/adapter, plugin/logging.
- Fix deterministico per Windows: lettura HTML in UTF-8 nel test (evita UnicodeDecodeError con encoding cp1252).

### Documentazione

- Aggiunto MIGRATION_TKINTER_TO_QT.md.
- README aggiornato con istruzioni di install/avvio e note legacy.

## Come provare in locale

### Install

python -m pip install -e .
python -m pip install -e " .[gui]"   # opzionale (necessario per GUI)

### Run

rd2229
oppure
python -m rd2229

### Test

pytest -q

### Legacy (opt-in)

RD2229_LEGACY_UI=1 python -m rd2229.ui_legacy.module_selector

## Stato qualità

- `python -m pytest -q`: PASS (0 fail)
- Nota: `ruff` / `mypy` non erano disponibili nell'ambiente Agent; demandato alla CI.

## Follow-up (opzionali)

- Wiring UI completa (menu File, navigazione, dock log viewer).
- Writer-side UTF-8 nel report exporter per robustezza (eventuale PR addizionale).
- (Optional) Squash dei due commit di fix duplicati (`ade03ed` + `81725ef`) prima di merge; richiede force-push con `--force-with-lease`.
