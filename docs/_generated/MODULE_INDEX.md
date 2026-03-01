# MODULE_INDEX

> Generato automaticamente da `tools/audit_repo.py` — commit `3f4d5ac` — 2026-03-01 00:49 UTC
> Questo file è di sola lettura. Non modificare manualmente.

| Modulo | Path | Tipo | File .py | Test rilevati | Stato | Note |
|--------|------|------|----------|---------------|-------|------|
| `actions` | `src/actions` | package | 2 | — | INCOMPLETO | TBD |
| `calc` | `src/calc` | package | 3 | `tests/test_area_calculations.py`, `tests/test_rebar_calculator.py` (+4) | PARZIALE | TBD |
| `checks` | `src/checks` | package | 2 | `tests/test_dm96_checks.py`, `tests/test_fire_checks.py` (+2) | PARZIALE | TBD |
| `cli` | `src/cli` | package | 2 | `tests/test_cli_new.py` | PARZIALE | TBD |
| `codes` | `src/codes` | package | 15 | — | INCOMPLETO | TBD |
| `config` | `src/config` | package | 1 | `tests/rd2229_39/test_configurable_factor.py` | PARZIALE | TBD |
| `core` | `src/core` | package | 6 | `tests/test_core_improved.py`, `tests/test_core_selection_scoring.py` | PARZIALE | TBD |
| `core_calculus` | `src/core_calculus` | package | 21 | — | INCOMPLETO | TBD |
| `domain` | `src/domain` | package | 5 | `tests/test_domain_materials.py`, `tests/test_domain_sections.py` (+1) | PARZIALE | TBD |
| `elements` | `src/elements` | package | 4 | `tests/codes/test_secondary_elements_cantilever.py`, `tests/codes/test_secondary_elements_chimney.py` (+3) | PARZIALE | TBD |
| `fire` | `src/fire` | package | 4 | `tests/test_fire_checks.py`, `tests/test_fire_selection_eligibility.py` | PARZIALE | TBD |
| `gui` | `src/gui` | package | 8 | `tests/integration/test_gui_verification_flow.py`, `tests/test_modern_ui_nongui.py` | PARZIALE | TBD |
| `launcher` | `src/launcher` | namespace | 1 | — | STUB | TBD |
| `legacy` | `src/legacy` | package | 43 | — | INCOMPLETO | TBD |
| `materials` | `src/materials` | package | 4 | `tests/test_domain_materials.py`, `tests/test_materials_cache.py` | PARZIALE | TBD |
| `methods` | `src/methods` | package | 15 | — | INCOMPLETO | TBD |
| `plugins` | `src/plugins` | package | 6 | `tests/test_logging_and_plugins.py` | PARZIALE | TBD |
| `project` | `src/project` | package | 3 | `tests/test_project_roundtrip.py`, `tests/test_project_store.py` | PARZIALE | TBD |
| `rd2229` | `src/rd2229` | namespace | 47 | `tests/test_golden_rd2229.py`, `tests/test_rd2229_checks.py` | STUB | TBD |
| `report` | `src/report` | package | 5 | `tests/test_mvp_report_builder.py`, `tests/test_reporting_smoke.py` | PARZIALE | TBD |
| `reporting` | `src/reporting` | package | 3 | `tests/test_reporting_smoke.py` | PARZIALE | TBD |
| `repositories` | `src/repositories` | package | 1 | — | INCOMPLETO | TBD |
| `tests` | `src/tests` | package | 7 | — | INCOMPLETO | TBD |
| `tools` | `src/tools` | package | 3 | — | INCOMPLETO | TBD |
| `ui` | `src/ui` | package | 21 | `tests/integration/test_gui_verification_flow.py`, `tests/legacy_qt/test_ui_pyqt6_smoke.py` (+7) | PARZIALE | TBD |
| `utils` | `src/utils` | package | 2 | — | INCOMPLETO | TBD |
| `wind` | `src/wind` | package | 7 | `tests/test_wind_integration_pipeline.py`, `tests/test_wind_smoke.py` | PARZIALE | TBD |

---

## Legenda stati

| Stato | Significato |
|-------|-------------|
| COMPLETO | Modulo con implementazione verificabile, test presenti e documentazione. |
| PARZIALE | Modulo implementato ma test o documentazione mancanti/incompleti. |
| INCOMPLETO | Modulo presente ma implementazione parziale o non verificabile. |
| STUB | Directory o file presente ma senza `__init__.py` o contenuto significativo. |
| NON PRESENTE | Nessun file Python rilevato. |

> **Nota**: gli stati sono derivati meccanicamente da euristiche su file system.
> La verifica manuale è necessaria per una classificazione definitiva.

