# Architettura Moduli — RD2229

Matrice generata meccanicamente da `tools/audit_modules.py`.
Ogni riga corrisponde a un package reale in `src/`.
Colonne normative e stati di completamento sono intenzionalmente assenti
o marcati "TBD" dove non verificabili automaticamente.

> **Auditato al commit `9b6b9c2` — 2026-02-28 17:22 UTC**

| Modulo | Path | File .py | Test correlati | Note |
|--------|------|----------|----------------|------|
| `actions` | `src/actions/` | 2 | — | TBD |
| `calc` | `src/calc/` | 3 | `tests/test_area_calculations.py`, `tests/test_rebar_calculator.py`, `tests/test_section_calculations.py` (+3) | TBD |
| `checks` | `src/checks/` | 2 | `tests/test_dm96_checks.py`, `tests/test_fire_checks.py`, `tests/test_ntc2018_checks.py` (+1) | TBD |
| `cli` | `src/cli/` | 2 | `tests/test_cli_new.py`, `tests/test_regression_gui_cli.py`, `tests/test_suggestion_click_realistic.py` (+2) | TBD |
| `codes` | `src/codes/` | 15 | — | TBD |
| `config` | `src/config/` | 1 | `tests/rd2229_39/test_configurable_factor.py` | TBD |
| `core` | `src/core/` | 6 | `tests/test_core_and_graphics.py`, `tests/test_core_improved.py`, `tests/test_core_selection_scoring.py` | TBD |
| `core_calculus` | `src/core_calculus/` | 21 | — | TBD |
| `domain` | `src/domain/` | 5 | `tests/test_domain_materials.py`, `tests/test_domain_sections.py`, `tests/test_mvp_domain_invariants.py` | TBD |
| `elements` | `src/elements/` | 4 | `tests/codes/test_secondary_elements_cantilever.py`, `tests/codes/test_secondary_elements_chimney.py`, `tests/codes/test_secondary_elements_partition.py` (+2) | TBD |
| `fire` | `src/fire/` | 4 | `tests/test_fire_checks.py`, `tests/test_fire_selection_eligibility.py` | TBD |
| `gui` | `src/gui/` | 8 | `tests/integration/test_gui_verification_flow.py`, `tests/test_main_window_gui.py`, `tests/test_modern_ui_nongui.py` (+1) | TBD |
| `launcher` | `src/launcher/` | 1 | — | TBD |
| `legacy` | `src/legacy/` | 42 | — | TBD |
| `materials` | `src/materials/` | 4 | `tests/test_domain_materials.py`, `tests/test_materials_cache.py` | TBD |
| `methods` | `src/methods/` | 15 | — | TBD |
| `plugins` | `src/plugins/` | 6 | `tests/test_logging_and_plugins.py` | TBD |
| `project` | `src/project/` | 3 | `tests/test_project_roundtrip.py`, `tests/test_project_store.py` | TBD |
| `rd2229` | `src/rd2229/` | 47 | `tests/test_golden_rd2229.py`, `tests/test_rd2229_checks.py` | TBD |
| `report` | `src/report/` | 5 | `tests/test_mvp_report_builder.py`, `tests/test_reporting_smoke.py` | TBD |
| `reporting` | `src/reporting/` | 3 | `tests/test_reporting_smoke.py` | TBD |
| `repositories` | `src/repositories/` | 1 | — | TBD |
| `tests` | `src/tests/` | 7 | — | TBD |
| `tools` | `src/tools/` | 3 | — | TBD |
| `ui` | `src/ui/` | 21 | `tests/integration/test_gui_verification_flow.py`, `tests/test_main_window_gui.py`, `tests/test_modern_ui_nongui.py` (+9) | TBD |
| `utils` | `src/utils/` | 2 | — | TBD |
| `wind` | `src/wind/` | 7 | `tests/test_main_window_gui.py`, `tests/test_wind_integration_pipeline.py`, `tests/test_wind_smoke.py` | TBD |
| `__all__.py` | `src/__all__.py` | 1 | — | top-level file |
| `__init__.py` | `src/__init__.py` | 1 | — | top-level file |
