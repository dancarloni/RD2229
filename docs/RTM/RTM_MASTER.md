# RTM_MASTER — Requirement Traceability Matrix

> **Versione**: 1.0 — 2026-03-01
> **Generato da**: `tools/audit_repo.py` (struttura) + revisione manuale (contenuto)
> **Regola**: tutte le celle con dati non verificabili meccanicamente sono marcate `TBD`.
> **Aggiornamento**: aggiornare questa matrice ad ogni nuova feature; rigenerare le righe modulo con `tools/audit_repo.py`.

---

## Istruzioni d'uso

- **Modulo**: nome del package/modulo in `src/` (link al file doc in `docs/modules/`).
- **File/Classi/Funzioni**: riferimenti reali verificabili nel codice sorgente. Se non verificato → TBD.
- **Test**: path reali in `tests/`. Se assenti → `—`.
- **I/O**: formato input/output se rilevabile. TBD altrimenti.
- **Fonti normative**: ID da `docs/NORMATIVE_SOURCES/sources.catalog.json` + clausola. TBD se non tracciato.
- **Stato**: derivato oggettivamente (vedi Legenda in `docs/MANIFESTO_GOVERNANCE.md`).

---

## Matrice

| Modulo | File/Classi/Funzioni | Test (path reali) | I/O | Fonti normative (ID + clausola) | Stato |
|--------|---------------------|-------------------|-----|----------------------------------|-------|
| [`actions`](../modules/actions.md) | `src/actions/action_repo.py` | — | TBD | TBD | INCOMPLETO |
| [`calc`](../modules/calc.md) | `src/calc/section_registry.py`, `src/calc/shear_area_registry.py` | `tests/test_area_calculations.py`, `tests/test_rebar_calculator.py` | TBD | TBD | PARZIALE |
| [`checks`](../modules/checks.md) | `src/checks/registry.py` | `tests/test_dm96_checks.py`, `tests/test_fire_checks.py` | TBD | DM96 (TBD), NTC2018 (TBD) | PARZIALE |
| [`cli`](../modules/cli.md) | `src/cli/__init__.py`, `src/cli/entrypoint.py` | `tests/test_cli_new.py` | CLI args → stdout | TBD | PARZIALE |
| [`codes`](../modules/codes.md) | `src/codes/code_registry.py`, `src/codes/ntc2018/` | — | TBD | NTC2018 (TBD) | INCOMPLETO |
| [`config`](../modules/config.md) | `src/config/` | `tests/rd2229_39/test_configurable_factor.py` | YAML/JSON → dict | TBD | PARZIALE |
| [`core`](../modules/core.md) | `src/core/pipeline.py`, `src/core/results.py`, `src/core/step5_adapter.py` | `tests/test_core_improved.py`, `tests/test_pipeline_smoke.py` | ProjectModel → ResultsModel | TBD | PARZIALE |
| [`core_calculus`](../modules/core_calculus.md) | `src/core_calculus/verification_engine.py`, `src/core_calculus/normative_registry.py`, `src/core_calculus/contracts.py` | — | TBD | RD2229 (TBD), DM96 (TBD), NTC2018 (TBD) | INCOMPLETO |
| [`domain`](../modules/domain.md) | `src/domain/domain/models.py`, `src/domain/domain/sections.py`, `src/domain/domain/materials.py` | `tests/test_domain_materials.py`, `tests/test_domain_sections.py` | TBD | TBD | PARZIALE |
| [`elements`](../modules/elements.md) | `src/elements/element_model.py`, `src/elements/element_repo.py` | `tests/codes/test_secondary_elements_*.py` | TBD | NTC2018 (TBD) | PARZIALE |
| [`fire`](../modules/fire.md) | `src/fire/curves.py`, `src/fire/eligibility.py`, `src/fire/rc_fire_check.py` | `tests/test_fire_checks.py`, `tests/test_fire_selection_eligibility.py` | TBD | NTC2018 (§3.6), EN1992_1_2 (TBD), ISO834 (TBD) | PARZIALE |
| [`gui`](../modules/gui.md) | `src/gui/entrypoint.py`, `src/gui/ntc2018_selector.py` | `tests/integration/test_gui_verification_flow.py` | GUI events | TBD | PARZIALE |
| [`launcher`](../modules/launcher.md) | `src/launcher/bootstrap.py` | — | TBD | TBD | STUB |
| [`legacy`](../modules/legacy.md) | `src/legacy/` (43 file) | — | TBD | TBD | INCOMPLETO |
| [`materials`](../modules/materials.md) | `src/materials/` | `tests/test_domain_materials.py`, `tests/test_materials_cache.py` | JSON/dict → MaterialModel | TBD | PARZIALE |
| [`methods`](../modules/methods.md) | `src/methods/` (15 file) | — | TBD | RD2229 (TBD), DM92 (TBD), DM96 (TBD), NTC2018 (TBD) | INCOMPLETO |
| [`plugins`](../modules/plugins.md) | `src/plugins/loader.py`, `src/plugins/__init__.py` | `tests/test_logging_and_plugins.py` | TBD | TBD | PARZIALE |
| [`project`](../modules/project.md) | `src/project/schema.py`, `src/project/repository.py` | `tests/test_project_roundtrip.py`, `tests/test_project_store.py` | JSON/SQLite → ProjectModel | TBD | PARZIALE |
| [`rd2229`](../modules/rd2229.md) | `src/rd2229/` (47 file — namespace, no `__init__.py`) | `tests/test_golden_rd2229.py`, `tests/test_rd2229_checks.py` | TBD | RD2229 (TBD) | STUB |
| [`report`](../modules/report.md) | `src/report/renderer_html.py`, `src/report/renderer_md.py` | `tests/test_mvp_report_builder.py`, `tests/test_reporting_smoke.py` | ResultsModel → HTML/MD | TBD | PARZIALE |
| [`reporting`](../modules/reporting.md) | `src/reporting/report_builder.py`, `src/reporting/export.py` | `tests/test_reporting_smoke.py` | ResultsModel → HTML/MD | TBD | PARZIALE |
| [`repositories`](../modules/repositories.md) | `src/repositories/` | — | TBD | TBD | INCOMPLETO |
| [`tests` (src)](../modules/tests_src.md) | `src/tests/` (7 file — test interni al package) | — | TBD | TBD | INCOMPLETO |
| [`tools` (src)](../modules/tools_src.md) | `src/tools/export_results.py`, `src/tools/verify_cli.py` | — | TBD | TBD | INCOMPLETO |
| [`ui`](../modules/ui.md) | `src/ui/modern/app.py`, `src/ui/qt/entrypoint.py` | `tests/test_modern_ui_nongui.py`, `tests/test_ui_qt_verification_service.py` | GUI events | TBD | PARZIALE |
| [`utils`](../modules/utils.md) | `src/utils/background.py` | — | TBD | TBD | INCOMPLETO |
| [`wind`](../modules/wind.md) | `src/wind/ntc2018.py`, `src/wind/ec1991_1_4.py`, `src/wind/cnr_dt207.py` | `tests/test_wind_integration_pipeline.py`, `tests/test_wind_smoke.py` | dict → WindResult | NTC2018 (§3.3), EN1991_1_4 (TBD), CNR_DT207 (TBD) | PARZIALE |

---

## Legenda

| Stato | Significato |
|-------|-------------|
| COMPLETO | Implementazione + test + doc + fonti normative tracciate. |
| PARZIALE | Implementato ma almeno un elemento (test/doc/fonti) mancante. |
| INCOMPLETO | Implementazione avviata ma con parti mancanti. |
| STUB | File presente ma senza contenuto funzionale. |
| NON PRESENTE | Funzionalità attesa ma non trovata. |
| TBD | Non ancora determinato. |

---

## Storia revisioni

| Data | Autore | Note |
|------|--------|------|
| 2026-03-01 | audit_repo.py + manuale | Prima stesura: struttura generata automaticamente, contenuto TBD. |
