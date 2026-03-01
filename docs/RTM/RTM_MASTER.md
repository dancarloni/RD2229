# RTM MASTER – RD2229 Repository
## Requirement Traceability Matrix – Pass 1 (Evidence-Only)

> **Metodologia**: ogni campo è compilato solo se verificato nel codice (file:riga, import, docstring).  
> Se un'informazione non è verificabile → `TBD`.  
> Nessuna deduzione normativa che non appaia come stringa nel sorgente.

---

## RECON – Risultati Inventario (FASE 0)

| Elemento | Valore |
|----------|--------|
| Commit analizzato | `git rev-parse HEAD` (branch: `copilot/execute-compliance-pass-1`) |
| Data analisi | 2026-03-01 |
| Moduli `src/` censiti | **27** |
| File `.py` totali in `src/` | ~200+ |
| Test in `tests/` | ~80+ file |
| Test in `tests_legacy/` | ~90+ file (ignorati da pytest.ini) |
| Fonti normative identificate | RD2229, DM92, DM96, NTC2018, ISO 834, EN 1992-1-2, EN 1991-1-4, CNR-DT 207, NTC2018_CIRC |

Strumento audit: `tools/audit_modules.py` (eseguito live durante RECON).

---

## RTM – Tabella Completa

| # | Modulo | Path principale | Entry point | Test associati (path reali) | I/O | Fonti normative (solo se in codice) | Stato | Evidenze chiave |
|---|--------|-----------------|-------------|------------------------------|-----|-------------------------------------|-------|-----------------|
| 1 | **actions** | `src/actions/` | Nessuno | Nessuno | TBD | Nessuna | **STUB** | `src/actions/action_repo.py`: `run()` → `raise NotImplementedError`; commento "STUB S2" |
| 2 | **calc** | `src/calc/` | `compute_shear_area()` in `shear_area_registry.py` | `src/tests/test_shear_area.py` | TBD | Nessuna | **STUB** | `src/calc/section_registry.py`: `SECTION_REGISTRY = {}`; "STUB S2" in entrambi i file |
| 3 | **checks** | `src/checks/` | `get_registry()` in `registry.py` | Nessuno | TBD | RD2229, DM96, NTC2018 (stringhe in `src/checks/registry.py`) | **PARZIALE** | `CheckRegistry` reale; tutti `compute=None`; nessun test integrazione |
| 4 | **cli** | `src/cli/` | `src.cli.main()` (Typer, 5 comandi) | `tests/test_cli_new.py` | Input: JSON project; Output: console/file | RD2229 (docstring `src/cli/entrypoint.py`) | **PARZIALE** | Comandi `new`/`load`/`info` reali; `run`/`export` dipendono da pipeline |
| 5 | **codes** | `src/codes/` | `spectrum_paste_service.build_profile()`; `code_registry.bootstrap_codes()` | `tests/codes/test_vrdc_no_stirrups.py`, `tests/test_ntc2018_hazard_paste_parser.py`, `tests/codes/test_secondary_elements_*.py` (+4) | TBD | NTC2018 (`src/codes/ntc2018/code_module.py:2`, `spectrum_paste_service.py:1`) | **PARZIALE** | `spectrum_paste_service` reale; `code_registry.py` STUB S2; `params/` e `clauses/` vuoti |
| 6 | **config** | `src/config/` | Nessuno (solo dati YAML) | Nessuno | Input: YAML; Output: dict via consumer | Nessuna | **STUB** | Solo `__init__.py` vuoto + 4 file YAML; nessuna logica Python |
| 7 | **core** | `src/core/` | `run_pipeline(project)` in `pipeline.py` | `tests/test_pipeline_smoke.py`, `tests/test_step5_merge.py`, `tests/test_wind_integration_pipeline.py` (+4) | Input: `ProjectModel`; Output: `ResultsModel` | NTC2018 (`src/core/pipeline.py`), RD2229 (`src/core/results.py`) | **PARZIALE** | `pipeline.py` (416 righe) reale; `ntc2018_combinations.py` SKELETON; `ntc2018_adapter.py` SKELETON |
| 8 | **core_calculus** | `src/core_calculus/` | `run_verifications_for_element()` in `verification_service.py`; `compute_section_properties_from_section()` | `tests/test_verification_pipeline.py`, `tests/test_section_calculations.py`, `tests/test_ntc2018_checks.py` (+8) | Input: `CalcInput` dataclass; Output: `VerificationResult` | NTC2018 (`normative_registry.py`), RD2229 (`normative_registry.py`), DM96 (`normative_registry.py`), EC2 (`normative_registry.py`) | **COMPLETO** | `normative_registry.py` (1217 righe): template reali per NTC2018/RD2229/DM96/Fire; `verification_core.py` (655 righe) calcolo asse neutro/tensioni |
| 9 | **domain** | `src/domain/` | `VerificationInput`, `get_concrete_properties()`, `get_section_geometry()` | Nessuno via `src.domain` (test importano da root-level) | TBD | Nessuna | **PARZIALE** | Dataclass e funzioni reali; non importato direttamente dai test (`tests/test_domain_*.py` importano da root `verification_table`) |
| 10 | **elements** | `src/elements/` | `ElementRepository`, `resolve_verification_inputs()` | `src/tests/test_elements_repo.py`, `src/tests/test_resolve_inputs.py` | TBD | Nessuna | **STUB** | `element_repo.py`: tutti metodi TODO; `element_model.py`: metodi STUB S2 |
| 11 | **fire** | `src/fire/` | `iso834_temperature()`, `run_rc_fire_check()`, `evaluate_fire_eligibility()` | `tests/test_fire_selection_eligibility.py` | Input: resistenza R, sezione; Output: `FireCheckResult` | EN 1992-1-2 (`src/fire/rc_fire_check.py:7`), NTC 2018 §3.6.1 (`src/fire/rc_fire_check.py:7`), EN 1991-1-2 (`src/fire/curves.py:8`) | **PARZIALE** | Logica reale; tabella asse-distanza placeholder (TODO caricare da JSON) |
| 12 | **gui** | `src/gui/` | `src.gui.main()` → delega a `src.ui.modern.app.main()` | `tests/legacy_qt/test_norm_selector.py`, `tests/legacy_qt/test_secondary_editor.py` | TBD | RD2229 (`src/gui/entrypoint.py`), NTC2018 (`src/gui/ntc2018_selector.py`) | **INCOMPLETO** | Entrypoint (13 righe) e selector reali; `secondary_elements/` quasi vuoti (8–15 righe ciascuno) |
| 13 | **launcher** | `src/launcher/` | `bootstrap.run_app()` | Nessuno | TBD | RD2229 (`src/launcher/bootstrap.py`) | **INCOMPLETO** | Singolo file; dipende da `apps.sections.app` (fuori `src/`); nessun `__init__.py`; nessun test |
| 14 | **legacy** | `src/legacy/` | `src/legacy/__main__.py`, `src/legacy/ui/__main__.py` | Nessuno via nuova suite | Input/Output: JSON/Tkinter UI | TBD (legacy non scansionato) | **COMPLETO** | 28+ file reali; architettura DO NOT MODIFY; Tkinter UI completa; dati materiali storici |
| 15 | **materials** | `src/materials/` | `MaterialRepository` | `src/tests/test_material_repo.py`, `src/tests/test_resolve_inputs.py` | TBD | Nessuna | **STUB** | `material_repo.py`: tutti metodi TODO/STUB S2 |
| 16 | **methods** | `src/methods/` | `checks_rd2229.*`, `checks_ntc2018.*`, `dispatcher.compute_verification_result()` | `tests/test_rd2229_checks.py`, `tests/test_dm96_checks.py`, `tests/test_ntc2018_checks.py`, `tests/test_fire_checks.py`, `tests/test_ta_method.py`, `tests/test_golden_rd2229.py` | Input: dict parametri strutturali; Output: dict risultati | RD2229 (`src/methods/checks_rd2229.py`), DM92/DM96 (`src/methods/checks_dm96.py:8-9`), NTC2018 (`src/methods/checks_ntc2018.py`), EC2 Parte 1-1 (`src/methods/checks_dm96.py:24`), EC2 Parte 1-2 (`src/methods/checks_fire_dm96.py`) | **COMPLETO** | `checks_rd2229.py` (1443 righe), `checks_dm96.py` (1483 righe), `checks_ntc2018.py` (809 righe): logica reale completa |
| 17 | **plugins** | `src/plugins/` | `PluginRegistry`, `load_plugins_from_folder()`, `load_plugins_from_entry_points()` | `tests/test_plugin_system.py` | Input: folder/entry_points; Output: `PluginSpec` list | RD2229 (`src/plugins/__init__.py`, `base.py`) | **COMPLETO** | `loader.py` (147 righe) real discovery; 3 plugin concreti; registry reale |
| 18 | **project** | `src/project/` | `load_project(path)`, `save_project(model, path)` | `tests/test_project_roundtrip.py`, `tests/test_migration.py`, `tests/test_pipeline_smoke.py` (+7) | Input: `.jsonp`/`.json`; Output: `ProjectModel` (Pydantic) | RD2229 (`src/project/schema.py:norm_code default`), NTC2018 (`src/project/schema.py:SeismicInputs`) | **COMPLETO** | `repository.py` (410 righe): I/O reale + migrazione versioni 1.0.0→1.1.0; `schema.py` (120 righe): Pydantic models completi |
| 19 | **rd2229** | `src/rd2229/` | `src/rd2229/__main__.py`; `mvp.pipeline.run_mvp_demo()`; `seismic.rd2229_39.provider.compute_floor_forces()` | `tests/test_mvp_sqlite_roundtrip.py`, `tests/test_golden_ca_slu_nu_limits.py`, `tests/rd2229_39/test_ondulatory_sussultory_relation.py` (+11) | Input: dict/Pydantic project; Output: HTML/text report; SQLite store | RD2229/RD2229_39 (`src/rd2229/seismic/rd2229_39/`), NTC2018 (`src/rd2229/ui_qt/app.py`), DM92 (commenti TODO in `vba_migration/ca_slu_nu_limits.py:21`) | **PARZIALE** | `mvp/` sub-package funzionale con SQLite + pipeline reale; seismic ondulatory/sussultory reale; UI non testabile headless |
| 20 | **report** | `src/report/` | `HTMLReportRenderer`, `MarkdownReportRenderer` | `src/tests/test_reporting.py` | Input: `ReportData`; Output: HTML/MD string | Nessuna | **STUB** | `renderer_html.py`: `render()` TODO; `renderer_pdf.py`: `raise NotImplementedError`; STUB S2 |
| 21 | **reporting** | `src/reporting/` | `build_report(project, results)`, `export_report_html()`, `export_report_md()` | `tests/test_reporting_smoke.py`, `tests/test_fire_selection_eligibility.py` | Input: `ProjectModel`, `ResultsModel`; Output: `ReportArtifact` (str HTML+MD), file su disco | RD2229 (`src/reporting/report_builder.py`), NTC2018 (`src/reporting/export.py`) | **COMPLETO** | `report_builder.py` (440 righe): logica reale string-template; `export.py` (74 righe): I/O file reale |
| 22 | **repositories** | `src/repositories/` | Nessuno (solo dati) | Nessuno | Input: N/A; Output: JSON/CSV dati materiali | Nessuna | **STUB** | Solo `__init__.py` (docstring) + `data/` con JSON/CSV; nessun codice Python |
| 23 | **tests** (src/) | `src/tests/` | Pytest test collection | N/A | N/A | Nessuna | **PARZIALE** | 7 test smoke per moduli STUB; tutti marcati STUB S2; copertura minimale |
| 24 | **tools** (src/) | `src/tools/` | `verify_cli.py` | Nessuno | TBD | Nessuna | **STUB** | `verify_cli.py`: `run_verifications()` TODO; `load_user_config()` TODO; STUB S2 |
| 25 | **ui** | `src/ui/` | `src.ui.qt.entrypoint.run_gui()`; `src.ui.modern.app.main()` | `tests/test_modern_ui_nongui.py`, `tests/test_ui_background_compute.py`, `tests/legacy_qt/test_ui_qt_registry.py` (+3) | Input: Pydantic ProjectModel; Output: Qt6 GUI | RD2229 (`src/ui/qt/entrypoint.py`, `module_selector.py`) | **PARZIALE** | ViewModels e services reali; Qt widgets strutturali (20–30 righe); app bypassa Qt in test mode |
| 26 | **utils** | `src/utils/` | `BackgroundExecutor` | `tests/test_background_executor.py` | Input: callable; Output: Future | Nessuna | **COMPLETO** | `background.py` (76 righe): ThreadPoolExecutor wrapper completo con callback Tkinter |
| 27 | **wind** | `src/wind/` | `WindActionService.compute()`; `compute_wind_results()` | `tests/test_wind_smoke.py`, `tests/test_wind_integration_pipeline.py` | Input: `WindSite`, `BuildingGeom`, `WindConfig`; Output: `WindActionResults` | NTC2018 §3.3 (`src/wind/ntc2018.py:1-3`), EN 1991-1-4 (`src/wind/ec1991_1_4.py:3`), CNR-DT 207 R1/2018 (`src/wind/cnr_dt207.py:1-3`) | **PARZIALE** | Logica reale per 3 framework normativi; parametri zona placeholder; Cd CNR-DT 207 non implementato |

---

## Legenda Stato

| Stato | Definizione |
|-------|-------------|
| **COMPLETO** | Entrypoint/call path + test significativi + nessun TODO/stub evidente nelle funzioni core |
| **PARZIALE** | Funziona ma copre solo parte del flusso, oppure ha TODO/gap evidenti, o test limitati |
| **INCOMPLETO** | Struttura esiste ma mancano call path/test o ci sono parti chiave placeholder |
| **STUB** | File/registry presenti ma implementazione minimale / placeholder |
| **NON PRESENTE** | Documentato ma non trovato nel codice |

---

## Riepilogo Stato

| Stato | Conteggio | Moduli |
|-------|-----------|--------|
| COMPLETO | 7 | core_calculus, legacy, methods, plugins, project, reporting, utils |
| PARZIALE | 11 | calc*, checks, cli, codes, core, domain, fire, rd2229, tests(src), ui, wind |
| INCOMPLETO | 2 | gui, launcher |
| STUB | 7 | actions, calc, config, elements, materials, report, repositories, tools |
| NON PRESENTE | 0 | — |

> *`calc` è classificato STUB (non PARZIALE) perché `section_registry.py` è `{}` e `shear_area_registry.py` ha solo fallback minimale.

---

## Riferimenti Normativi – Occorrenze nel Codice

| ID Norma | File sorgente (esempi verificati) | Contesto |
|----------|-----------------------------------|----------|
| RD2229 | `src/core_calculus/normative_registry.py`, `src/methods/checks_rd2229.py`, `src/project/schema.py`, `src/checks/registry.py` | Template verifiche TA, check flessione/taglio/pressoflessione |
| DM92 | `src/methods/checks_dm96.py:8-9,73-77`, `src/rd2229/mvp/vba_migration/ca_slu_nu_limits.py` | Tensioni ammissibili, coefficienti parziali |
| DM96 | `src/methods/checks_dm96.py`, `src/core_calculus/normative_registry.py`, `src/checks/registry.py` | Check SLU/SLE/TA DM96 |
| NTC2018 | `src/wind/ntc2018.py:1-3`, `src/core/pipeline.py`, `src/codes/ntc2018/`, `src/core_calculus/normative_registry.py` | Verifiche SLU/SLE, azioni vento §3.3, sisma, incendio §3.6 |
| EN 1992-1-2 | `src/fire/rc_fire_check.py:7` | Verifica incendio strutture in c.a. |
| EN 1991-1-4 | `src/wind/ec1991_1_4.py:3` | Azioni vento Eurocodice |
| CNR-DT 207 | `src/wind/cnr_dt207.py:1-3`, `src/wind/service.py:26` | Turbolenza, risposta dinamica vento |
| ISO 834 | (non trovato come stringa in src/, presente in docs/normative/sources.yaml) | Curva incendio standard |
| EC2 Parte 1-1 | `src/methods/checks_dm96.py:24` | Formule generali riferimento |

---

*Generato da analisi statica/testuale: nessuna esecuzione del codice progetto.*  
*Per rigenerare: `python tools/rtm_build.py` (vedi Fase 5).*
