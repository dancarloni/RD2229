# REPO_INVENTORY

> Generato automaticamente da `tools/audit_repo.py` — commit `1ed8fef` — 2026-03-03 13:01 UTC
> Questo file è di sola lettura. Non modificare manualmente.

---

## 1. Pacchetti/Moduli in `src/`

Totale pacchetti/moduli rilevati: **27**

- `src\actions` (package, 2 file .py)
- `src\calc` (package, 3 file .py)
- `src\checks` (package, 2 file .py)
- `src\cli` (package, 2 file .py)
- `src\codes` (package, 15 file .py)
- `src\config` (package, 1 file .py)
- `src\core` (package, 8 file .py)
- `src\core_calculus` (package, 21 file .py)
- `src\domain` (package, 5 file .py)
- `src\elements` (package, 4 file .py)
- `src\fire` (package, 4 file .py)
- `src\gui` (package, 8 file .py)
- `src\launcher` (namespace, 1 file .py)
- `src\legacy` (package, 43 file .py)
- `src\materials` (package, 4 file .py)
- `src\methods` (package, 15 file .py)
- `src\plugins` (package, 6 file .py)
- `src\project` (package, 5 file .py)
- `src\rd2229` (namespace, 47 file .py)
- `src\report` (package, 5 file .py)
- `src\reporting` (package, 3 file .py)
- `src\repositories` (package, 1 file .py)
- `src\tests` (package, 7 file .py)
- `src\tools` (package, 3 file .py)
- `src\ui` (package, 21 file .py)
- `src\utils` (package, 2 file .py)
- `src\wind` (package, 7 file .py)

---

## 2. Test

File di test in `tests/`: **102**

- `tests\codes\test_secondary_elements_cantilever.py`
- `tests\codes\test_secondary_elements_chimney.py`
- `tests\codes\test_secondary_elements_partition.py`
- `tests\codes\test_secondary_elements_signage.py`
- `tests\codes\test_vrdc_no_stirrups.py`
- `tests\integration\test_gui_verification_flow.py`
- `tests\legacy_qt\test_app_launch.py`
- `tests\legacy_qt\test_norm_selector.py`
- `tests\legacy_qt\test_secondary_editor.py`
- `tests\legacy_qt\test_ui_pyqt6_smoke.py`
- `tests\legacy_qt\test_ui_qt_registry.py`
- `tests\legacy_qt\test_ui_qt_smoke.py`
- `tests\rd2229_39\test_configurable_factor.py`
- `tests\rd2229_39\test_ondulatory_sussultory_relation.py`
- `tests\rd2229_39\test_p_from_table.py`
- `tests\rd2229_39\test_trace_presence.py`
- `tests\test_adapter_and_properties.py`
- `tests\test_area_calculations.py`
- `tests\test_background_executor.py`
- `tests\test_cli_new.py`
- `tests\test_comprehensive.py`
- `tests\test_core_improved.py`
- `tests\test_core_selection_scoring.py`
- `tests\test_crud_operations.py`
- `tests\test_csv_io.py`
- `tests\test_dm96_checks.py`
- `tests\test_domain_materials.py`
- `tests\test_domain_sections.py`
- `tests\test_entrypoint_no_pyside.py`
- `tests\test_fire_checks.py`
- `tests\test_fire_selection_eligibility.py`
- `tests\test_geometry_cache.py`
- `tests\test_geometry_model_extra.py`
- `tests\test_golden_ca_slu_nu_limits.py`
- `tests\test_golden_rd2229.py`
- `tests\test_hello.py`
- `tests\test_lc_fc_adjustments.py`
- `tests\test_logging_and_plugins.py`
- `tests\test_materials_cache.py`
- `tests\test_migration.py`
- `tests\test_modern_ui_nongui.py`
- `tests\test_module_registry.py`
- `tests\test_module_registry_refresh.py`
- `tests\test_module_selector_controller.py`
- `tests\test_module_selector_integration.py`
- `tests\test_mvp_domain_invariants.py`
- `tests\test_mvp_end_to_end.py`
- `tests\test_mvp_jsoncode_loader.py`
- `tests\test_mvp_real_min_check.py`
- `tests\test_mvp_report_builder.py`
- `tests\test_mvp_result_trace_contract.py`
- `tests\test_mvp_schema_migration.py`
- `tests\test_mvp_sqlite_roundtrip.py`
- `tests\test_new_architecture.py`
- `tests\test_no_tkinter_imports.py`
- `tests\test_ntc2018_checks.py`
- `tests\test_ntc2018_hazard_paste_parser.py`
- `tests\test_ntc2018_hazard_profile_persistence.py`
- `tests\test_pipeline_smoke.py`
- `tests\test_plot_section.py`
- `tests\test_plugin_system.py`
- `tests\test_project_io_timeline.py`
- `tests\test_project_roundtrip.py`
- `tests\test_project_schema_validation.py`
- `tests\test_project_store.py`
- `tests\test_rd2229_checks.py`
- `tests\test_rebar_calculator.py`
- `tests\test_reporting_smoke.py`
- `tests\test_rotation_invariants.py`
- `tests\test_run_replay_idempotent.py`
- `tests\test_secondary_elements_gating.py`
- `tests\test_section_adapter_and_properties.py`
- `tests\test_section_calculations.py`
- `tests\test_section_calculations_extra.py`
- `tests\test_section_calculations_regression.py`
- `tests\test_section_calculations_rotation.py`
- `tests\test_section_graphics_extra.py`
- `tests\test_section_graphics_fake_canvas.py`
- `tests\test_section_graphics_transform.py`
- `tests\test_section_graphics_transform_extra.py`
- `tests\test_section_properties_wx_wy.py`
- `tests\test_section_shapes.py`
- `tests\test_section_to_geometry_types.py`
- `tests\test_shapely_integration.py`
- `tests\test_shapely_integration_optional.py`
- `tests\test_shear_areas_complete.py`
- `tests\test_shear_meta.py`
- `tests\test_shim_import.py`
- `tests\test_step5_adapter_smoke.py`
- `tests\test_step5_merge.py`
- `tests\test_storage.py`
- `tests\test_ta_method.py`
- `tests\test_table_navigation.py`
- `tests\test_timeline_manifest_hashing.py`
- `tests\test_ui_background_compute.py`
- `tests\test_ui_qt_settings_service.py`
- `tests\test_ui_qt_verification_service.py`
- `tests\test_verification_dispatcher.py`
- `tests\test_verification_pipeline.py`
- `tests\test_verification_vm.py`
- `tests\test_wind_integration_pipeline.py`
- `tests\test_wind_smoke.py`

---

## 3. CI Workflows

Workflow in `.github/workflows/`: **4**

- `.github\workflows\gui-tests.yml` (30 righe)
- `.github\workflows\lint-test.yml` (46 righe)
- `.github\workflows\nightly.yml` (29 righe)
- `.github\workflows\python-ci.yml` (45 righe)

---

## 4. Tools / Scripts

Script in `tools/`: **19**

- `tools\__init__.py`
- `tools\audit_modules.py`
- `tools\audit_repo.py`
- `tools\concrete_strength.py`
- `tools\debug_run_suggest.py`
- `tools\diagnose_gui.py`
- `tools\generate_module_docs.py`
- `tools\materials_manager.py`
- `tools\profile_calculus.py`
- `tools\rd2229_calc.py`
- `tools\replay_run.py`
- `tools\rewrite_sections_app_imports.py`
- `tools\rtm_build.py`
- `tools\run_mypy_ci.py`
- `tools\run_project.py`
- `tools\split_sections_app.py`
- `tools\sync_verifications.py`
- `tools\validate_project.py`
- `tools\verify_softw_components.py`

---

## 5. Entry points (da pyproject.toml)

> Rilevamento meccanico limitato. Consultare `pyproject.toml` per la lista completa.

  - `rd2229 = "rd2229.ui_qt.app:main"`
  - `rd2229-gui = "rd2229.ui_qt.app:main"`
  - `rd2229-cli = "src.cli.entrypoint:main"`
