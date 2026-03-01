<<<<<<< HEAD
# Modulo: `ui`

## 1. Scopo e ambito

Interfaccia grafica moderna: ViewModels, servizi, entrypoint Qt6 (PyQt6/PySide6), `VerificationTableApp`, features registry.

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: ViewModels (`ProjectViewModel`, `RunViewModel`, `ResultsViewModel`) e servizi (`ProjectIOService`, `CalculationService`) hanno implementazione reale. `module_selector.py` (207 righe) è una finestra Qt reale. Widget individuali (`code_settings.py`, `material_editor.py`, ecc.) sono skeleton (20–30 righe). App bypassa Qt in test mode.

## 3. Evidenze

- `src/ui/modern/viewmodels/__init__.py` — ~200 righe; ViewModels con metodi implementati
- `src/ui/modern/services/__init__.py` — 55 righe; `ProjectIOService`, `CalculationService`
- `src/ui/qt/entrypoint.py` — 84 righe; Qt6 entrypoint con argparse
- `src/ui/qt/module_selector.py` — 207 righe; finestra Qt reale
- `src/ui/modern/app.py:46-47` — `RD2229_UI_TEST` env var per skip Qt event loop
- Test: `tests/test_modern_ui_nongui.py`, `tests/test_ui_background_compute.py`, `tests/legacy_qt/test_ui_qt_registry.py` (+3)

## 4. Input/parametri

- `run_gui(argv: list[str])` — entrypoint Qt
- `ProjectViewModel.load(path: str)` — carica progetto
- `RunViewModel.run()` — esegue pipeline

## 5. Output

- GUI Qt6 (PyQt6/PySide6)
- ViewModels aggiornati (per binding UI)

## 6. Dipendenze

- PyQt6 ≥ 6.4 (opzionale: `rd2229[gui]`)
- `src/project/repository` — `load_project()`
- `src/core/pipeline` — `run_pipeline()`
- `src/reporting` — `build_report()`

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/ui/qt/entrypoint.py`, `module_selector.py` — docstring e selector |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Widget Qt individuali sono skeleton (20–30 righe ciascuno)
- Dipendenza da PyQt6 opzionale — non testabile in CI headless standard
- `VerificationTableApp` ha test ma dipende da Tkinter (legacy)

## 9. Next steps

- [ ] Implementare i widget Qt skeleton (material_editor, code_settings, report_viewer)
- [ ] Aggiungere test headless per ViewModels con `RD2229_UI_TEST=1`
- [ ] Documentare il binding ViewModel→Widget per ogni finestra
=======
# Documentazione Modulo: `ui`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `ui` |
| **Path** | `src/ui` |
| **Tipo** | package |
| **File .py rilevati** | 21 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

> Descrivere in 2-3 righe il *perché* esiste questo modulo e quale problema risolve.

TBD

---

## 3. File / Classi / Funzioni principali

> Elencare i simboli pubblici rilevanti. Non inventare: se non si conosce la firma esatta, annotare TBD.

| File | Classe/Funzione | Descrizione |
|------|-----------------|-------------|
| TBD | TBD | TBD |

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | TBD | TBD |
| Output | TBD | TBD |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/integration/test_gui_verification_flow.py` | TBD | — |
| `tests/legacy_qt/test_ui_pyqt6_smoke.py` | TBD | — |

---

## 6. Fonti normative

> Solo riferimenti a ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`. NESSUN testo copiato.

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| TBD | TBD | — |

---

## 7. Dipendenze interne

> Moduli `src/` da cui questo modulo dipende (import diretti).

- TBD

---

## 8. Note e TODO

- [ ] Compilare sezioni TBD
- [ ] Verificare test correlati
- [ ] Tracciare fonti normative di riferimento
>>>>>>> d5ef881 (feat: audit/docs infrastructure - audit_repo, RTM, governance, normative catalog, module docs)
