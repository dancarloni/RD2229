# RECON – Inventario Meccanico Repository RD2229

## Fase 0 – Evidence-Only

**Data**: 2026-03-01  
**Branch**: `copilot/execute-compliance-pass-1`  
**Strumento**: `tools/audit_modules.py` (eseguito live) + analisi manuale

---

## 1. Tree 2 livelli – Cartelle principali

```
src/                    # Codice sorgente principale (installato come package editabile)
  actions/              # STUB S2 – azioni verifica come oggetti
  calc/                 # STUB S2 – registro sezioni e calcolo area taglio
  checks/               # PARZIALE – registro CheckSpec per normative
  cli/                  # PARZIALE – CLI Typer (5 comandi)
  codes/                # PARZIALE – CodeModule NTC2018, spectrum paste, sec.elements
  config/               # STUB – file YAML configurazione
  core/                 # PARZIALE – pipeline principale calcolo
  core_calculus/        # COMPLETO – motore verifiche strutturali
  domain/               # PARZIALE – VerificationInput, proprietà materiali/sezioni
  elements/             # STUB S2 – Element e ElementRepository
  fire/                 # PARZIALE – curva ISO 834, eligibility, rc_fire_check
  gui/                  # INCOMPLETO – entry point GUI thin + stub widgets
  launcher/             # INCOMPLETO – bootstrap applicazione
  legacy/               # COMPLETO – applicazione Tkinter storica (DO NOT MODIFY)
  materials/            # STUB S2 – Material e MaterialRepository
  methods/              # COMPLETO – checks RD2229/DM96/NTC2018/fire
  plugins/              # COMPLETO – sistema plugin con discovery
  project/              # COMPLETO – ProjectModel Pydantic + repository
  rd2229/               # PARZIALE – package principale: MVP, seismic, logging, UI
  report/               # STUB S2 – renderer HTML/MD/PDF (stub)
  reporting/            # COMPLETO – build_report + export HTML/MD
  repositories/         # STUB – solo dati JSON/CSV
  tests/                # PARZIALE – smoke test per moduli STUB (7 file)
  tools/                # STUB S2 – verify_cli e export_results
  ui/                   # PARZIALE – Qt GUI moderna: ViewModels, services, widgets
  utils/                # COMPLETO – BackgroundExecutor
  wind/                 # PARZIALE – calcolo vento NTC2018/EN/CNR

tests/                  # Suite test principale (~80+ file)
tests_legacy/           # Test legacy Tkinter (~90+ file, ignorati da pytest.ini)

docs/                   # Documentazione (ADR, MEGAPLAN, normative, specs, RTM, modules)
  RTM/                  # ← nuovo: RTM_MASTER.md
  modules/              # ← nuovo: doc per modulo
  NORMATIVE_SOURCES/    # ← nuovo: catalog JSON fonti normative
  normative/            # esistente: sources.yaml, coverage_matrix.yaml
  specs/                # esistente: spec architetturali
  MEGAPLAN/             # esistente: piani e roadmap

tools/                  # Strumenti sviluppo (audit, rtm_build, ...)
  audit_modules.py      # esistente: genera inventario moduli
  rtm_build.py          # ← nuovo: rigenera RTM e overview

.github/workflows/      # CI/CD
  ci.yml
  python-ci.yml
  lint-test.yml
  gui-tests.yml
  nightly.yml
```

---

## 2. Lista Moduli Attivi (da src/)

Fonte: output `tools/audit_modules.py` eseguito sul commit corrente.

| # | Modulo | Path | File .py | Stato |
|---|--------|------|----------|-------|
| 1 | actions | src/actions/ | 2 | STUB |
| 2 | calc | src/calc/ | 3 | STUB |
| 3 | checks | src/checks/ | 2 | PARZIALE |
| 4 | cli | src/cli/ | 2 | PARZIALE |
| 5 | codes | src/codes/ | 14 | PARZIALE |
| 6 | config | src/config/ | 1+4yml | STUB |
| 7 | core | src/core/ | 5 | PARZIALE |
| 8 | core_calculus | src/core_calculus/ | 14 | COMPLETO |
| 9 | domain | src/domain/ | 4 | PARZIALE |
| 10 | elements | src/elements/ | 4 | STUB |
| 11 | fire | src/fire/ | 4 | PARZIALE |
| 12 | gui | src/gui/ | 8 | INCOMPLETO |
| 13 | launcher | src/launcher/ | 1 | INCOMPLETO |
| 14 | legacy | src/legacy/ | 28+ | COMPLETO |
| 15 | materials | src/materials/ | 4 | STUB |
| 16 | methods | src/methods/ | 14 | COMPLETO |
| 17 | plugins | src/plugins/ | 6 | COMPLETO |
| 18 | project | src/project/ | 3 | COMPLETO |
| 19 | rd2229 | src/rd2229/ | 20+ | PARZIALE |
| 20 | report | src/report/ | 5 | STUB |
| 21 | reporting | src/reporting/ | 3 | COMPLETO |
| 22 | repositories | src/repositories/ | 1+data | STUB |
| 23 | tests (src/) | src/tests/ | 7 | PARZIALE |
| 24 | tools (src/) | src/tools/ | 3 | STUB |
| 25 | ui | src/ui/ | 14+ | PARZIALE |
| 26 | utils | src/utils/ | 2 | COMPLETO |
| 27 | wind | src/wind/ | 7 | PARZIALE |

**Totale: 27 moduli**

---

## 3. Conteggio File Test per Modulo

| Modulo | Test in tests/ | Test in src/tests/ | Test in tests_legacy/ |
|--------|----------------|--------------------|-----------------------|
| calc | test_area_calculations.py, test_rebar_calculator.py, test_section_calculations.py | test_shear_area.py | — |
| checks | — | — | — |
| cli | test_cli_new.py | — | — |
| codes | codes/test_vrdc_no_stirrups.py, test_ntc2018_hazard_paste_parser.py, codes/test_secondary_elements_*.py (+4) | test_code_routing.py | — |
| core | test_pipeline_smoke.py, test_step5_merge.py, test_wind_integration_pipeline.py (+4) | — | — |
| core_calculus | test_verification_pipeline.py, test_section_calculations.py, test_ntc2018_checks.py (+8) | — | — |
| elements | — | test_elements_repo.py, test_resolve_inputs.py | — |
| fire | test_fire_selection_eligibility.py | — | — |
| gui | legacy_qt/test_norm_selector.py, legacy_qt/test_secondary_editor.py | — | — |
| materials | — | test_material_repo.py | — |
| methods | test_rd2229_checks.py, test_dm96_checks.py, test_ntc2018_checks.py, test_fire_checks.py, test_ta_method.py, test_golden_rd2229.py | — | — |
| plugins | test_plugin_system.py | — | — |
| project | test_project_roundtrip.py, test_migration.py (+8) | — | — |
| rd2229 | test_mvp_sqlite_roundtrip.py, test_golden_ca_slu_nu_limits.py, rd2229_39/*.py (+11) | — | — |
| report | — | test_reporting.py | — |
| reporting | test_reporting_smoke.py | — | — |
| ui | test_modern_ui_nongui.py, test_ui_background_compute.py, legacy_qt/test_ui_qt_registry.py (+3) | — | — |
| utils | test_background_executor.py | — | — |
| wind | test_wind_smoke.py, test_wind_integration_pipeline.py | — | — |

---

## 4. Occorrenze Normative nel Codice (grep su src/)

| Stringa cercata | File con occorrenze (campione) |
|-----------------|-------------------------------|
| NTC2018 | src/wind/ntc2018.py, src/core/pipeline.py, src/codes/ntc2018/*, src/core_calculus/normative_registry.py, src/methods/checks_ntc2018.py, src/fire/rc_fire_check.py, src/project/schema.py |
| DM96 | src/methods/checks_dm96.py, src/core_calculus/normative_registry.py, src/checks/registry.py |
| DM92 | src/methods/checks_dm96.py:8-9,73-77, src/rd2229/mvp/vba_migration/ca_slu_nu_limits.py |
| RD2229 | src/methods/checks_rd2229.py, src/core_calculus/normative_registry.py, src/project/schema.py, src/cli/entrypoint.py |
| EC2 | src/methods/checks_dm96.py:24 (Parte 1-1), src/methods/checks_fire_dm96.py (Parte 1-2) |
| EN1991 | src/wind/ec1991_1_4.py:3 |
| CNR-DT 207 | src/wind/cnr_dt207.py:1-3, src/wind/service.py:26 |
| incendio | src/fire/rc_fire_check.py, src/core/pipeline.py, src/fire/eligibility.py |
| vento | src/wind/*.py, src/core/pipeline.py |
| sisma | src/project/schema.py (SeismicInputs), src/rd2229/seismic/ |

---

*Fine RECON. Numero moduli target fissato a **27**.*
