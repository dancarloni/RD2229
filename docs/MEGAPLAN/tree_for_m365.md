# Project tree (filtered) — formato compatibile M365 Copilot

**Filtro applicato:** esclusi i nomi di cartelle che iniziano con `.` e quelli contenenti `cache`.

**Nota:** la rappresentazione completa è fornita nel blocco JSON sottostante e nel file `tree_no_dot_cache.json`.

## Sommario (Markdown, espanso fino a profondità 3)

- **RD2229/**
  - `.flake8`
  - `.gitignore`
  - `.pre-commit-config.yaml`
  - `.rd2229_config.yaml`
  - `AGGIIORNAMENTO_FOCUS.md`
  - `BLOCCO 01.txt`
  - `BLOCCO 02.txt`
  - `BLOCCO 03.txt`
  - `BLOCCO 04.txt`
  - `BLOCCO 05.txt`
  - `BLOCCO 06.txt`
  - `BLOCCO 07.txt`
  - `BLOCCO 08.txt`
  - `BLOCCO 09.txt`
  - `BLOCCO 10.txt`
  - `BLOCCO 11.txt`
  - `BLOCCO 12.txt`
  - `CHANGELOG.md`
  - `CONTRIBUTING.md`
  - `COPILOT_SEARCH_2229.md`
  - `IMPLEMENTATION_SUMMARY.md`
  - `MIGRATION.md`
  - `Makefile`
  - `PLANCODE.md`
  - `Piano di progetto.md`
  - `Plan_master.md`
  - `Plan_master2.md`
  - `R.D. 16.11.1939 n.2229.pdf`
  - `RD2229.code-workspace`
  - `README.md`
  - `Report_claude_DM92_DM96_Fuoco.md`
  - `Session_2_Result_Summary.md`
  - `Session_5_Prompt_RD2229.md`
  - `Session_5_Result_Summary_RD2229.md`
  - `Session_6_Result_Summary_RD2229_Refinement.md`
  - **Support/**
    - `comparativa_norme_esistente.csv`
    - `comparativa_norme_esistente.json`
    - `comparativa_norme_esistente.md`
    - `riferimenti_eurocodici_ntc.txt`
  - `__init__.py.disabled`
  - `__main__.py`
  - `analyze_sections_json.py`
  - **app/**
    - `__init__.py`
    - **domain/**
      - `__init__.py`
      - `materials.py`
      - `models.py`
      - `sections.py`
    - **entrypoints/**
      - `run_demo.py`
    - **ui/**
      - `__init__.py`
      - `csv_io.py`
      - `project_actions.py`
      - `rebar_calculator.py`
      - `suggestion_box.py`
      - `verification_table_app.py`
    - **verification/**
      - `__init__.py`
      - `engine_adapter.py`
      - `methods_sle.py`
      - `methods_slu.py`
      - `methods_ta.py`
  - `app.log`
  - **apps/**
    - **sections/**
      - `__init__.py`
      - `app.py`
      - **config/**
        - _0 dirs, 2 files — see JSON for full tree_
      - **domain/**
        - _0 dirs, 3 files — see JSON for full tree_
      - **io/**
        - _0 dirs, 2 files — see JSON for full tree_
      - **models/**
        - _0 dirs, 2 files — see JSON for full tree_
      - **modules/**
        - _0 dirs, 1 files — see JSON for full tree_
      - `saved_sections.csv`
      - `section_calculations.py.bak`
      - `section_graphics.py`
      - **services/**
        - _0 dirs, 10 files — see JSON for full tree_
      - `shear_factors.py`
      - `storage.py`
      - **ui/**
        - _1 dirs, 15 files — see JSON for full tree_
  - **archive/**
    - `historical_materials.json`
    - `sec_repository_backup.jsons`
    - `sections_backup.json`
  - **calculations/**
    - `__init__.py`
    - **pilastri/**
      - `__init__.py`
      - `carico_punta.py`
      - `compressione_semplice.py`
    - **scale/**
      - `__init__.py`
    - **solette/**
      - `__init__.py`
    - **travi/**
      - `__init__.py`
      - `flessione_semplice.py`
  - **config/**
    - `README.md`
    - `__init__.py`
    - **calculation_codes/**
      - `SLE.jsoncode`
      - `SLU.jsoncode`
      - `TA.jsoncode`
    - `calculation_codes_loader.py`
    - **historical_materials/**
      - `DM92.jsoncode`
      - `NTC2008.jsoncode`
      - `NTC2018.jsoncode`
      - `RD2229.jsoncode`
    - `historical_materials_loader.py`
  - **core/**
    - `__init__.py`
    - `verification_core.py`
    - `verification_engine.py`
  - **core_models/**
    - `__init__.py`
    - `loads.py`
    - `materials.py`
  - **data/**
    - `material_sources.json`
    - `notification_settings.json`
  - `demo_config_system.py`
  - `demo_sections.json`
  - `demo_verification_engine.py`
  - **docs/**
    - `AUTO_AGGIORNAMENTO_VERIFICATION_TABLE.md`
    - `CARICAMENTO_AUTOMATICO_STARTUP.md`
    - `CLAUDE.md`
    - `CONFIG_JSONCODE_SYSTEM.md`
    - `FIXES_WINDOW_AND_SEARCH.md`
    - `FRC_IMPLEMENTATION.md`
    - `GESTIONE_CAMPI_DINAMICI.md`
    - `IMPLEMENTAZIONE_PERSISTENZA.md`
    - **MEGAPLAN/**
      - `FIRE_ANALISI_AVANZATA_L3_FEM.md`
      - `FIRE_BENCHMARK_2D_R120_AUTOMATICO.md`
      - `FIRE_BENCHMARK_2D_R90_AUTOMATICO.md`
      - `FIRE_CASE_STUDIO_2D_PARETE_R120.md`
      - `FIRE_CASE_STUDIO_2D_PARETE_R90.md`
      - `FIRE_CASE_STUDIO_L2_VS_L3_PILASTRO_R90.md`
      - `FIRE_CHECKLIST_TECNICO_LEGALE.md`
      - `FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md`
      - `FIRE_CODEMODULE_INCENDIO.md`
      - `FIRE_ESEMPIO_R60_PILASTRO.md`
      - `FIRE_ESTENSIONE_R90_R120.md`
      - `FIRE_GATE_RILASCIO_L3_FEM.md`
      - `FIRE_INTEGRAZIONE_L3_IN_CODEMODULE.md`
      - `FIRE_INTEGRAZIONE_SOFTWARE.md`
      - `FIRE_L3_ANALISI_COMPLETE_E_CONFRONTO_L2_L3.md`
      - `FIRE_L3_COSTITUTIVE_NONLINEARI.md`
      - `FIRE_L3_STEP1_ANALISI_TERMICA.md`
      - `FIRE_L3_STEP2_ANALISI_MECCANICA.md`
      - `FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md`
      - `FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md`
      - `FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO.md`
      - `FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO.md`
      - `FIRE_L3_STEP4_MODELLI_2D_PARETI.md`
      - `FIRE_L3_TEST_PYTEST_END_TO_END.md`
      - `FIRE_MASTER.md`
      - `FIRE_NEXT_STEPS_ROADMAP.md`
      - `FIRE_NORMATIVA_EC.md`
      - `FIRE_NORMATIVA_NTC.md`
      - `FIRE_PROGRAMMA_FUTURO_L3_FEM.md`
      - `FIRE_PROMPT_MASTER.md`
      - `FIRE_PROTOTIPO_LE_MINIMALE.md`
      - `FIRE_RELAZIONE_CALCOLO_TIPO_L3_2D_PARETI.md`
      - `FIRE_SOLVER_L3_FEM_CODICE.md`
      - `FIRE_TEORIA_CALCOLO.md`
      - `FIRE_TEST-PYTEST_SKELETON.md`
      - `FIRE_TESTS_AUTOMATICI_R60.md`
      - `FIRE_TESTS_PYTEST_AVANZATI.md`
      - `FIRE_VERIFICA_TRAVI_A_CALDO.md`
      - `MEGAPLAN_NTC2018_EC_con_risposte.md`
      - `MEGAPLAN_NTC2018_MasterPlan.md`
      - `PLAN_CALCOLO.md`
      - `PLAN_GUI.md`
      - `PLAN_INCENDIO_MASTER_REVISIONE_2026_Q1.md`
      - `PLAN_INPUT_COMUNE.md`
      - `PLAN_MASTER.md`
      - `PLAN_OUTPUT_COMUNE.md`
      - `PLAN__NTC2018_EC_Integrazoini.md`
      - `tree_no_dot_cache.txt`
    - `MODIFICHE_5_OBIETTIVI.md`
    - `OFFLINE_INSTRUCTIONS.md`
    - `PERSISTENZA_COMPLETATA.md`
    - `PERSISTENZA_MATERIAL_COMPLETATA.md`
    - `PERSISTENZA_MATERIAL_REPOSITORY.md`
    - `PERSISTENZA_REPOSITORY.md`
    - `PERSISTENZA_SUMMARY.md`
    - `RIEPILOGO_FASE_3_CARICAMENTO_STARTUP.md`
    - `RIEPILOGO_NUOVE_SEZIONI_E_ROTAZIONE.md`
    - `ROADMAP.md`
    - `SECTION_MANAGER_IMPROVEMENTS.md`
    - `SHEAR_FORM_FACTORS.md`
    - `SINTESI_FINALE_7_OBIETTIVI.md`
    - `TEST_REPOSITORY_CANONICI.md`
    - `VERIFICATION_TABLE_KEYBOARD.md`
    - `VERIFICA_7_OBIETTIVI.md`
    - `VERIFICA_FINALE_COMPLETE_9_OBIETTIVI.md`
    - `WINDOW_MANAGEMENT_FIX.md`
    - **adr/**
      - `0001-axis-conventions.md`
      - `0002-strategy-pattern.md`
      - `0003-repository-schema.md`
    - `audit_report.md`
    - `consolidation-plan.md`
    - `consolidation.md`
    - `formulas.md`
    - `geometry.md`
    - `graphics.md`
    - `index.md`
    - `migration-quickstart.md`
    - `module_structure.md`
    - `perf.md`
    - `section-calculations.md`
    - **visual_basic/**
      - `Impostazioni_INDEX.md`
      - `PrincipCA_TA_INDEX.md`
  - `esempio_pressoflessione_deviata.py`
  - **examples/**
    - `demo_backup_system.py`
    - `demo_export_backup.py`
    - `demo_export_gui.py`
    - `demo_material_persistence.py`
    - `demo_persistenza.py`
    - `demo_recovery_system.py`
    - `demo_verification_table_auto_update.py`
  - **gui/**
    - `__init__.py`
    - `materials_gui.py`
    - `section_gui.py`
  - `historical_materials.json`
  - `historical_materials.py`
  - **historical_ta/**
    - `__init__.py`
    - `checks.py`
    - `geometry.py`
    - `materials.py`
    - `stress.py`
  - **libs/**
    - **app_module/**
      - `app.py`
      - **models/**
        - _0 dirs, 1 files — see JSON for full tree_
      - **modules/**
        - _0 dirs, 2 files — see JSON for full tree_
      - `saved_sections.csv`
      - **services/**
        - _0 dirs, 9 files — see JSON for full tree_
      - **ui/**
        - _0 dirs, 9 files — see JSON for full tree_
  - **logs/**
    - `README.md`
  - **mat_repository/**
    - `Mat_repository.jsonm`
  - `material_sources.py`
  - `materials.json`
  - `materials_backup.json`
  - `materials_repository.py`
  - `mkdocs.yml`
  - **modules/**
    - `carbon_fiber_placeholder.py`
    - `debug_viewer.py`
    - `frc_placeholder.py`
    - `geometry.py`
    - `historical_placeholder.py`
    - `material_editor.py`
    - `modules_config.json`
    - `registry.py`
  - `mypy.ini`
  - `nul`
  - `output_esempio.txt`
  - **patches/**
    - `0001-Deprecate-sections.json-auto-migrate-to-sec_reposito.patch`
  - **path/**
    - **to/**
      - **src/**
        - _0 dirs, 1 files — see JSON for full tree_
  - `progetto.zip`
  - `project_tree.txt`
  - `pyproject.toml`
  - `pytest.ini`
  - `quantities_registry.csv`
  - `quantities_registry.py`
  - `reorganize_sections_app.py`
  - `requirements-dev.in`
  - `requirements-dev.txt`
  - `requirements.in`
  - `requirements.txt`
  - **scripts/**
    - `apply_patch_and_test.ps1`
    - `auto_fix_bandit.py`
    - `auto_fix_bandit_extra.py`
    - `auto_fix_random_random.py`
    - `check_dynamic_fields.py`
    - `clean_trailing_whitespace.py`
    - `cleanup_precommit_cache.py`
    - `debug_combobox.py`
    - `debug_combobox2.py`
    - `debug_suggestions.py`
    - `debug_verification_input.py`
    - `demo_campi_dinamici.py`
    - `force_clear_precommit_cache.py`
    - `inspect_inverted_t.py`
    - `inspect_l.py`
    - `inspect_l2.py`
    - `inspect_materials.py`
    - `inspect_shapes.py`
    - `inspect_v_props.py`
    - `inspect_v_rects.py`
    - `manual_demo.py`
    - `materials_cli.py`
    - `remove_corrupt_repo_cache.py`
    - `replace_sigma.py`
    - `run-local.ps1`
    - `run-local.sh`
    - `run_concrete_tests.py`
    - `run_lint_from_venv.py`
    - `run_materials_demo.py`
    - `run_materials_gui.py`
    - `run_materials_runner.py`
    - `run_precommit_elevated.ps1`
    - `run_section_graphics_demo.py`
    - `run_verification_demo.py`
    - `smoke_imports.py`
    - `update_imports.py`
  - **sec_repository/**
    - `sec_repository.jsons`
    - `sec_repository_backup.jsons`
  - `sections.json`
  - `sections.json.bak`
  - **sections_app/**
  - `sections_tree.txt`
  - **softw_components/**
    - **geometry_model_module/**
      - `saved_sections.csv`
    - **section_calculations_module/**
      - **models/**
        - _0 dirs, 1 files — see JSON for full tree_
      - `saved_sections.csv`
      - **services/**
        - _0 dirs, 3 files — see JSON for full tree_
    - **section_graphics_module/**
      - `saved_sections.csv`
    - **sections_app_module/**
      - `__init__.py`
      - `saved_sections.csv`
    - **shear_factors_module/**
      - `saved_sections.csv`
      - `shear_factors.py`
    - **storage_module/**
      - `saved_sections.csv`
  - **src/**
    - `__init__.py`
    - **_io_disabled/**
      - `__init__.py`
    - **core_calculus/**
      - `__init__.py`
      - `contracts.py`
      - **core/**
        - _0 dirs, 12 files — see JSON for full tree_
      - `geometry_cache.py`
      - `lc_fc_adjustments.py`
      - `normative_registry.py`
      - `section_calculations.py`
      - `validation_engine.py`
      - `verification_engine.py`
      - `verification_service.py`
    - **domain/**
      - `__init__.py`
      - **domain/**
        - _0 dirs, 4 files — see JSON for full tree_
    - **launcher/**
      - `bootstrap.py`
    - **methods/**
      - `__init__.py`
      - `checks_dm96.py`
      - `checks_fire_dm96.py`
      - `checks_ntc2018.py`
      - `checks_rd2229.py`
      - `prestress_models.py`
      - `protocols.py`
      - `ta.py`
      - **verification/**
        - _0 dirs, 7 files — see JSON for full tree_
    - **rd2229/**
      - **core/**
        - _0 dirs, 0 files — see JSON for full tree_
      - **gui/**
        - _0 dirs, 0 files — see JSON for full tree_
      - **sections_app/**
        - _3 dirs, 0 files — see JSON for full tree_
      - **tools/**
        - _0 dirs, 0 files — see JSON for full tree_
    - **repositories/**
      - `__init__.py`
      - **data/**
        - _0 dirs, 5 files — see JSON for full tree_
    - **ui/**
      - `__init__.py`
      - `code_settings_window.py`
      - `debug_viewer.py`
      - `frc_manager.py`
      - `frc_verification_window.py`
      - `historical_main_window.py`
      - `historical_material_window.py`
      - `main_window.py`
      - `module_selector.py`
      - `notification_center.py`
      - `notification_settings_window.py`
      - `section_manager.py`
      - **ui/**
        - _0 dirs, 7 files — see JSON for full tree_
      - `verification_comparator.py`
    - **utils/**
      - `__init__.py`
      - `background.py`
  - `tatus --porcelain`
  - `test_veloce_deviata.py`
  - **tests/**
    - `golden_rd2229.json`
    - `test_adapter_and_properties.py`
    - `test_area_calculations.py`
    - `test_background_executor.py`
    - `test_comprehensive.py`
    - `test_core_and_graphics.py`
    - `test_core_improved.py`
    - `test_core_selection_scoring.py`
    - `test_crud_operations.py`
    - `test_csv_io.py`
    - `test_dm96_checks.py`
    - `test_domain_materials.py`
    - `test_domain_sections.py`
    - `test_fire_checks.py`
    - `test_geometry_cache.py`
    - `test_geometry_model_extra.py`
    - `test_golden_rd2229.py`
    - `test_graphics_flags.py`
    - `test_lc_fc_adjustments.py`
    - `test_main_window_gui.py`
    - `test_materials_cache.py`
    - `test_module_registry.py`
    - `test_module_registry_refresh.py`
    - `test_module_selector_controller.py`
    - `test_module_selector_integration.py`
    - `test_module_selector_ui.py`
    - `test_new_architecture.py`
    - `test_ntc2018_checks.py`
    - `test_persistence_edit_cycle.py`
    - `test_rd2229_checks.py`
    - `test_rebar_calculator.py`
    - `test_rotation_invariants.py`
    - `test_section_adapter_and_properties.py`
    - `test_section_calculations.py`
    - `test_section_calculations_extra.py`
    - `test_section_calculations_regression.py`
    - `test_section_calculations_rotation.py`
    - `test_section_graphics_extra.py`
    - `test_section_graphics_fake_canvas.py`
    - `test_section_graphics_transform.py`
    - `test_section_graphics_transform_extra.py`
    - `test_section_properties_wx_wy.py`
    - `test_section_shapes.py`
    - `test_section_to_geometry_types.py`
    - `test_shapely_integration.py`
    - `test_shapely_integration_optional.py`
    - `test_shear_areas_complete.py`
    - `test_shear_meta.py`
    - `test_shim_import.py`
    - `test_storage.py`
    - `test_ta_method.py`
    - `test_table_navigation.py`
    - `test_ui_background_compute.py`
    - `test_verification_dispatcher.py`
    - `test_verification_pipeline.py`
  - **tests_legacy/**
    - `README.md`
    - `conftest.py`
    - `test_all_sections.py`
    - `test_auto_load_startup.py`
    - `test_backup_system.py`
    - `test_bas_adapter.py`
    - `test_canonical_repository_paths.py`
    - `test_concrete_strength.py`
    - `test_config_loaders.py`
    - `test_deviated_bending.py`
    - `test_drawing_geometry.py`
    - `test_export_backup.py`
    - `test_export_gui.py`
    - `test_frc_basic.py`
    - `test_frc_verification_window.py`
    - `test_gui_compatibility.py`
    - `test_historical_import_csv.py`
    - `test_historical_material_window.py`
    - `test_historical_materials.py`
    - `test_historical_ta.py`
    - `test_integration_persistence.py`
    - `test_json_wrappers.py`
    - `test_main_window_material_button.py`
    - `test_main_window_save.py`
    - `test_manual_demo.py`
    - `test_material_persistence.py`
    - `test_materials_frc.py`
    - `test_materials_repository.py`
    - `test_migration_sections_json.py`
    - `test_module_selector_frc_buttons.py`
    - `test_module_selector_material_button.py`
    - `test_module_selector_section_button.py`
    - `test_new_sections.py`
    - `test_notification_center.py`
    - `test_notification_service.py`
    - `test_notification_settings.py`
    - `test_notification_settings_ui.py`
    - `test_numerical_ta.py`
    - `test_persistence.py`
    - `test_recovery_system.py`
    - `test_repository_save.py`
    - `test_search_helpers_with_repo.py`
    - `test_section_manager_autorefresh.py`
    - `test_section_manager_columns.py`
    - `test_section_manager_new_button.py`
    - `test_section_manager_new_stays_open.py`
    - `test_section_manager_ui.py`
    - `test_section_parser_compat.py`
    - `test_sections.py`
    - `test_sections_properties.py`
    - `test_sections_random_demo.py`
    - `test_shear_areas.py`
    - `test_shear_help_button.py`
    - `test_startup_integration.py`
    - `test_torsion.py`
    - `test_verification_comparator_visuals.py`
    - `test_verification_frc_integration.py`
    - `test_verification_table.py`
    - `test_verification_table_api.py`
    - `test_verification_table_auto_update.py`
    - `test_verification_table_autocomplete_and_events.py`
    - `test_verification_table_combobox.py`
    - `test_verification_table_csv.py`
    - `test_verification_table_csv_roundtrip.py`
    - `test_verification_table_dialogs.py`
    - `test_verification_table_edgecases.py`
    - `test_verification_table_import_mapping_and_logging.py`
    - `test_verification_table_integration.py`
    - `test_verification_table_jsonp.py`
    - `test_verification_table_more.py`
    - `test_verification_table_navigation.py`
    - `test_verification_table_suggestions_on_empty.py`
  - **tools/**
    - `__init__.py`
    - `concrete_strength.py`
    - `materials_manager.py`
    - `profile_calculus.py`
    - `rd2229_calc.py`
    - `rewrite_sections_app_imports.py`
    - `run_mypy_ci.py`
    - `split_sections_app.py`
    - `sync_verifications.py`
    - `verify_softw_components.py`
  - `tree_output.txt`
  - **ui/**
    - `module_selector.py`
  - `verification_items.py`
  - `verification_items_repository.py`
  - `verification_project.py`
  - `verification_table.py`
  - **verifications/**
    - `__init__.py`
    - **pilastri/**
      - `__init__.py`
    - **rd2229/**
      - `__init__.py`
      - `tensioni_ammissibili.py`
    - **scale/**
      - `__init__.py`
    - **solette/**
      - `__init__.py`
    - **travi/**
      - `__init__.py`
  - **visual_basic/**
    - `ApplyBasToWorkbook.ps1`
    - `CA_SLE.bas`
    - `CA_SLE.txt`
    - `CA_SLU.bas`
    - `CA_SLU.txt`
    - `ISTRUZIONI_IMPORTAZIONE_VBA.txt`
    - `Impostazioni.bas`
    - `Impostazioni.txt`
    - `PrincipCA_TA.bas`
    - `PrincipCA_TA.txt`
    - `frmAltriDati.frm`
    - `frmAltriDati.frx`
    - `frmDatiGene.frm`
    - `frmDatiGene.frx`
    - `frmDatiGene2.frm`
    - `frmDatiGene2.frx`
    - `frmGeomCalastr.frm`
    - `frmGeomCalastr.frx`
    - `frmGeomCalastrConfin.frm`
    - `frmGeomCalastrConfin.frx`
    - `frmGeomFRP.frm`
    - `frmGeomFRP.frx`
    - `frmGeomFRPconfin.frm`
    - `frmGeomFRPconfin.frx`
    - `frmGeomSezCircCA.frm`
    - `frmGeomSezCircCA.frx`
    - `frmGeomSezDoppioT.frm`
    - `frmGeomSezDoppioT.frx`
    - `frmGeomSezGenerica.frm`
    - `frmGeomSezGenerica.frx`
    - `frmGeomSezRettCA.frm`
    - `frmGeomSezRettCA.frx`
    - `frmGeomSezScat.frm`
    - `frmGeomSezScat.frx`
    - `frmGeomSezT.frm`
    - `frmGeomSezT.frx`
    - `frmGeomSezTrovescia.frm`
    - `frmGeomSezTrovescia.frx`
    - `frmInformaz.frm`
    - `frmInformaz.frx`
    - `frmMaterAcc.frm`
    - `frmMaterAcc.frx`
    - `frmMaterCA.frm`
    - `frmMaterCA.frx`
    - `frmMaterCAesist.frm`
    - `frmMaterCAesist.frx`
    - `frmMaterFRC.frm`
    - `frmMaterFRC.frx`
    - `frmMaterFRP.frm`
    - `frmMaterFRP.frx`
    - `frmPacchettiArmat.frm`
    - `frmPacchettiArmat.frx`
    - `frmRelazCalc.frm`
    - `frmRelazCalc.frx`
    - `frmSollecitazSLE.frm`
    - `frmSollecitazSLE.frx`
    - `frmSollecitazSLU.frm`
    - `frmSollecitazSLU.frx`
    - `frmSplash.frm`
    - `frmSplash.frx`
    - `frmStabilità.frm`
    - `frmStabilità.frx`
    - `frmVerifSLE.frm`
    - `frmVerifSLE.frx`
    - `frmVisuSez.frm`
    - `frmVisuSez.frx`
    - `import_vba.ps1`
  - `witch main`

---

## JSON (struttura completa)
```json
{
  "name": "RD2229",
  "type": "dir",
  "children": [
    {
      "name": ".flake8",
      "type": "file"
    },
    {
      "name": ".gitignore",
      "type": "file"
    },
    {
      "name": ".pre-commit-config.yaml",
      "type": "file"
    },
    {
      "name": ".rd2229_config.yaml",
      "type": "file"
    },
    {
      "name": "AGGIIORNAMENTO_FOCUS.md",
      "type": "file"
    },
    {
      "name": "BLOCCO 01.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 02.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 03.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 04.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 05.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 06.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 07.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 08.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 09.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 10.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 11.txt",
      "type": "file"
    },
    {
      "name": "BLOCCO 12.txt",
      "type": "file"
    },
    {
      "name": "CHANGELOG.md",
      "type": "file"
    },
    {
      "name": "CONTRIBUTING.md",
      "type": "file"
    },
    {
      "name": "COPILOT_SEARCH_2229.md",
      "type": "file"
    },
    {
      "name": "IMPLEMENTATION_SUMMARY.md",
      "type": "file"
    },
    {
      "name": "MIGRATION.md",
      "type": "file"
    },
    {
      "name": "Makefile",
      "type": "file"
    },
    {
      "name": "PLANCODE.md",
      "type": "file"
    },
    {
      "name": "Piano di progetto.md",
      "type": "file"
    },
    {
      "name": "Plan_master.md",
      "type": "file"
    },
    {
      "name": "Plan_master2.md",
      "type": "file"
    },
    {
      "name": "R.D. 16.11.1939 n.2229.pdf",
      "type": "file"
    },
    {
      "name": "RD2229.code-workspace",
      "type": "file"
    },
    {
      "name": "README.md",
      "type": "file"
    },
    {
      "name": "Report_claude_DM92_DM96_Fuoco.md",
      "type": "file"
    },
    {
      "name": "Session_2_Result_Summary.md",
      "type": "file"
    },
    {
      "name": "Session_5_Prompt_RD2229.md",
      "type": "file"
    },
    {
      "name": "Session_5_Result_Summary_RD2229.md",
      "type": "file"
    },
    {
      "name": "Session_6_Result_Summary_RD2229_Refinement.md",
      "type": "file"
    },
    {
      "name": "Support",
      "type": "dir",
      "children": [
        {
          "name": "comparativa_norme_esistente.csv",
          "type": "file"
        },
        {
          "name": "comparativa_norme_esistente.json",
          "type": "file"
        },
        {
          "name": "comparativa_norme_esistente.md",
          "type": "file"
        },
        {
          "name": "riferimenti_eurocodici_ntc.txt",
          "type": "file"
        }
      ]
    },
    {
      "name": "__init__.py.disabled",
      "type": "file"
    },
    {
      "name": "__main__.py",
      "type": "file"
    },
    {
      "name": "analyze_sections_json.py",
      "type": "file"
    },
    {
      "name": "app",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "domain",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "materials.py",
              "type": "file"
            },
            {
              "name": "models.py",
              "type": "file"
            },
            {
              "name": "sections.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "entrypoints",
          "type": "dir",
          "children": [
            {
              "name": "run_demo.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "ui",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "csv_io.py",
              "type": "file"
            },
            {
              "name": "project_actions.py",
              "type": "file"
            },
            {
              "name": "rebar_calculator.py",
              "type": "file"
            },
            {
              "name": "suggestion_box.py",
              "type": "file"
            },
            {
              "name": "verification_table_app.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "verification",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "engine_adapter.py",
              "type": "file"
            },
            {
              "name": "methods_sle.py",
              "type": "file"
            },
            {
              "name": "methods_slu.py",
              "type": "file"
            },
            {
              "name": "methods_ta.py",
              "type": "file"
            }
          ]
        }
      ]
    },
    {
      "name": "app.log",
      "type": "file"
    },
    {
      "name": "apps",
      "type": "dir",
      "children": [
        {
          "name": "sections",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "app.py",
              "type": "file"
            },
            {
              "name": "config",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "constants.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "domain",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "base.py",
                  "type": "file"
                },
                {
                  "name": "shapes.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "io",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "csv_sections.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "models",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "sections.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "modules",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "saved_sections.csv",
              "type": "file"
            },
            {
              "name": "section_calculations.py.bak",
              "type": "file"
            },
            {
              "name": "section_graphics.py",
              "type": "file"
            },
            {
              "name": "services",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "area_calculations.py",
                  "type": "file"
                },
                {
                  "name": "calculations.py",
                  "type": "file"
                },
                {
                  "name": "debug_log_stream.py",
                  "type": "file"
                },
                {
                  "name": "event_bus.py",
                  "type": "file"
                },
                {
                  "name": "historical_calculations.py",
                  "type": "file"
                },
                {
                  "name": "notification.py",
                  "type": "file"
                },
                {
                  "name": "notification_settings.py",
                  "type": "file"
                },
                {
                  "name": "repository.py",
                  "type": "file"
                },
                {
                  "name": "search_helpers.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "shear_factors.py",
              "type": "file"
            },
            {
              "name": "storage.py",
              "type": "file"
            },
            {
              "name": "ui",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "code_settings_window.py",
                  "type": "file"
                },
                {
                  "name": "components",
                  "type": "dir",
                  "children": [
                    {
                      "name": "flow_wrap.py",
                      "type": "file"
                    }
                  ]
                },
                {
                  "name": "debug_viewer.py",
                  "type": "file"
                },
                {
                  "name": "frc_manager.py",
                  "type": "file"
                },
                {
                  "name": "frc_verification_window.py",
                  "type": "file"
                },
                {
                  "name": "historical_main_window.py",
                  "type": "file"
                },
                {
                  "name": "historical_material_window.py",
                  "type": "file"
                },
                {
                  "name": "main_window.py",
                  "type": "file"
                },
                {
                  "name": "module_selector.py",
                  "type": "file"
                },
                {
                  "name": "module_selector_view.py",
                  "type": "file"
                },
                {
                  "name": "modules_config.json",
                  "type": "file"
                },
                {
                  "name": "notification_center.py",
                  "type": "file"
                },
                {
                  "name": "notification_settings_window.py",
                  "type": "file"
                },
                {
                  "name": "section_manager.py",
                  "type": "file"
                },
                {
                  "name": "verification_comparator.py",
                  "type": "file"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "archive",
      "type": "dir",
      "children": [
        {
          "name": "historical_materials.json",
          "type": "file"
        },
        {
          "name": "sec_repository_backup.jsons",
          "type": "file"
        },
        {
          "name": "sections_backup.json",
          "type": "file"
        }
      ]
    },
    {
      "name": "calculations",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "pilastri",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "carico_punta.py",
              "type": "file"
            },
            {
              "name": "compressione_semplice.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "scale",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "solette",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "travi",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "flessione_semplice.py",
              "type": "file"
            }
          ]
        }
      ]
    },
    {
      "name": "config",
      "type": "dir",
      "children": [
        {
          "name": "README.md",
          "type": "file"
        },
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "calculation_codes",
          "type": "dir",
          "children": [
            {
              "name": "SLE.jsoncode",
              "type": "file"
            },
            {
              "name": "SLU.jsoncode",
              "type": "file"
            },
            {
              "name": "TA.jsoncode",
              "type": "file"
            }
          ]
        },
        {
          "name": "calculation_codes_loader.py",
          "type": "file"
        },
        {
          "name": "historical_materials",
          "type": "dir",
          "children": [
            {
              "name": "DM92.jsoncode",
              "type": "file"
            },
            {
              "name": "NTC2008.jsoncode",
              "type": "file"
            },
            {
              "name": "NTC2018.jsoncode",
              "type": "file"
            },
            {
              "name": "RD2229.jsoncode",
              "type": "file"
            }
          ]
        },
        {
          "name": "historical_materials_loader.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "core",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "verification_core.py",
          "type": "file"
        },
        {
          "name": "verification_engine.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "core_models",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "loads.py",
          "type": "file"
        },
        {
          "name": "materials.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "data",
      "type": "dir",
      "children": [
        {
          "name": "material_sources.json",
          "type": "file"
        },
        {
          "name": "notification_settings.json",
          "type": "file"
        }
      ]
    },
    {
      "name": "demo_config_system.py",
      "type": "file"
    },
    {
      "name": "demo_sections.json",
      "type": "file"
    },
    {
      "name": "demo_verification_engine.py",
      "type": "file"
    },
    {
      "name": "docs",
      "type": "dir",
      "children": [
        {
          "name": "AUTO_AGGIORNAMENTO_VERIFICATION_TABLE.md",
          "type": "file"
        },
        {
          "name": "CARICAMENTO_AUTOMATICO_STARTUP.md",
          "type": "file"
        },
        {
          "name": "CLAUDE.md",
          "type": "file"
        },
        {
          "name": "CONFIG_JSONCODE_SYSTEM.md",
          "type": "file"
        },
        {
          "name": "FIXES_WINDOW_AND_SEARCH.md",
          "type": "file"
        },
        {
          "name": "FRC_IMPLEMENTATION.md",
          "type": "file"
        },
        {
          "name": "GESTIONE_CAMPI_DINAMICI.md",
          "type": "file"
        },
        {
          "name": "IMPLEMENTAZIONE_PERSISTENZA.md",
          "type": "file"
        },
        {
          "name": "MEGAPLAN",
          "type": "dir",
          "children": [
            {
              "name": "FIRE_ANALISI_AVANZATA_L3_FEM.md",
              "type": "file"
            },
            {
              "name": "FIRE_BENCHMARK_2D_R120_AUTOMATICO.md",
              "type": "file"
            },
            {
              "name": "FIRE_BENCHMARK_2D_R90_AUTOMATICO.md",
              "type": "file"
            },
            {
              "name": "FIRE_CASE_STUDIO_2D_PARETE_R120.md",
              "type": "file"
            },
            {
              "name": "FIRE_CASE_STUDIO_2D_PARETE_R90.md",
              "type": "file"
            },
            {
              "name": "FIRE_CASE_STUDIO_L2_VS_L3_PILASTRO_R90.md",
              "type": "file"
            },
            {
              "name": "FIRE_CHECKLIST_TECNICO_LEGALE.md",
              "type": "file"
            },
            {
              "name": "FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md",
              "type": "file"
            },
            {
              "name": "FIRE_CODEMODULE_INCENDIO.md",
              "type": "file"
            },
            {
              "name": "FIRE_ESEMPIO_R60_PILASTRO.md",
              "type": "file"
            },
            {
              "name": "FIRE_ESTENSIONE_R90_R120.md",
              "type": "file"
            },
            {
              "name": "FIRE_GATE_RILASCIO_L3_FEM.md",
              "type": "file"
            },
            {
              "name": "FIRE_INTEGRAZIONE_L3_IN_CODEMODULE.md",
              "type": "file"
            },
            {
              "name": "FIRE_INTEGRAZIONE_SOFTWARE.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_ANALISI_COMPLETE_E_CONFRONTO_L2_L3.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_COSTITUTIVE_NONLINEARI.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP1_ANALISI_TERMICA.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP2_ANALISI_MECCANICA.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_STEP4_MODELLI_2D_PARETI.md",
              "type": "file"
            },
            {
              "name": "FIRE_L3_TEST_PYTEST_END_TO_END.md",
              "type": "file"
            },
            {
              "name": "FIRE_MASTER.md",
              "type": "file"
            },
            {
              "name": "FIRE_NEXT_STEPS_ROADMAP.md",
              "type": "file"
            },
            {
              "name": "FIRE_NORMATIVA_EC.md",
              "type": "file"
            },
            {
              "name": "FIRE_NORMATIVA_NTC.md",
              "type": "file"
            },
            {
              "name": "FIRE_PROGRAMMA_FUTURO_L3_FEM.md",
              "type": "file"
            },
            {
              "name": "FIRE_PROMPT_MASTER.md",
              "type": "file"
            },
            {
              "name": "FIRE_PROTOTIPO_LE_MINIMALE.md",
              "type": "file"
            },
            {
              "name": "FIRE_RELAZIONE_CALCOLO_TIPO_L3_2D_PARETI.md",
              "type": "file"
            },
            {
              "name": "FIRE_SOLVER_L3_FEM_CODICE.md",
              "type": "file"
            },
            {
              "name": "FIRE_TEORIA_CALCOLO.md",
              "type": "file"
            },
            {
              "name": "FIRE_TEST-PYTEST_SKELETON.md",
              "type": "file"
            },
            {
              "name": "FIRE_TESTS_AUTOMATICI_R60.md",
              "type": "file"
            },
            {
              "name": "FIRE_TESTS_PYTEST_AVANZATI.md",
              "type": "file"
            },
            {
              "name": "FIRE_VERIFICA_TRAVI_A_CALDO.md",
              "type": "file"
            },
            {
              "name": "MEGAPLAN_NTC2018_EC_con_risposte.md",
              "type": "file"
            },
            {
              "name": "MEGAPLAN_NTC2018_MasterPlan.md",
              "type": "file"
            },
            {
              "name": "PLAN_CALCOLO.md",
              "type": "file"
            },
            {
              "name": "PLAN_GUI.md",
              "type": "file"
            },
            {
              "name": "PLAN_INCENDIO_MASTER_REVISIONE_2026_Q1.md",
              "type": "file"
            },
            {
              "name": "PLAN_INPUT_COMUNE.md",
              "type": "file"
            },
            {
              "name": "PLAN_MASTER.md",
              "type": "file"
            },
            {
              "name": "PLAN_OUTPUT_COMUNE.md",
              "type": "file"
            },
            {
              "name": "PLAN__NTC2018_EC_Integrazoini.md",
              "type": "file"
            },
            {
              "name": "tree_no_dot_cache.txt",
              "type": "file"
            }
          ]
        },
        {
          "name": "MODIFICHE_5_OBIETTIVI.md",
          "type": "file"
        },
        {
          "name": "OFFLINE_INSTRUCTIONS.md",
          "type": "file"
        },
        {
          "name": "PERSISTENZA_COMPLETATA.md",
          "type": "file"
        },
        {
          "name": "PERSISTENZA_MATERIAL_COMPLETATA.md",
          "type": "file"
        },
        {
          "name": "PERSISTENZA_MATERIAL_REPOSITORY.md",
          "type": "file"
        },
        {
          "name": "PERSISTENZA_REPOSITORY.md",
          "type": "file"
        },
        {
          "name": "PERSISTENZA_SUMMARY.md",
          "type": "file"
        },
        {
          "name": "RIEPILOGO_FASE_3_CARICAMENTO_STARTUP.md",
          "type": "file"
        },
        {
          "name": "RIEPILOGO_NUOVE_SEZIONI_E_ROTAZIONE.md",
          "type": "file"
        },
        {
          "name": "ROADMAP.md",
          "type": "file"
        },
        {
          "name": "SECTION_MANAGER_IMPROVEMENTS.md",
          "type": "file"
        },
        {
          "name": "SHEAR_FORM_FACTORS.md",
          "type": "file"
        },
        {
          "name": "SINTESI_FINALE_7_OBIETTIVI.md",
          "type": "file"
        },
        {
          "name": "TEST_REPOSITORY_CANONICI.md",
          "type": "file"
        },
        {
          "name": "VERIFICATION_TABLE_KEYBOARD.md",
          "type": "file"
        },
        {
          "name": "VERIFICA_7_OBIETTIVI.md",
          "type": "file"
        },
        {
          "name": "VERIFICA_FINALE_COMPLETE_9_OBIETTIVI.md",
          "type": "file"
        },
        {
          "name": "WINDOW_MANAGEMENT_FIX.md",
          "type": "file"
        },
        {
          "name": "adr",
          "type": "dir",
          "children": [
            {
              "name": "0001-axis-conventions.md",
              "type": "file"
            },
            {
              "name": "0002-strategy-pattern.md",
              "type": "file"
            },
            {
              "name": "0003-repository-schema.md",
              "type": "file"
            }
          ]
        },
        {
          "name": "audit_report.md",
          "type": "file"
        },
        {
          "name": "consolidation-plan.md",
          "type": "file"
        },
        {
          "name": "consolidation.md",
          "type": "file"
        },
        {
          "name": "formulas.md",
          "type": "file"
        },
        {
          "name": "geometry.md",
          "type": "file"
        },
        {
          "name": "graphics.md",
          "type": "file"
        },
        {
          "name": "index.md",
          "type": "file"
        },
        {
          "name": "migration-quickstart.md",
          "type": "file"
        },
        {
          "name": "module_structure.md",
          "type": "file"
        },
        {
          "name": "perf.md",
          "type": "file"
        },
        {
          "name": "section-calculations.md",
          "type": "file"
        },
        {
          "name": "visual_basic",
          "type": "dir",
          "children": [
            {
              "name": "Impostazioni_INDEX.md",
              "type": "file"
            },
            {
              "name": "PrincipCA_TA_INDEX.md",
              "type": "file"
            }
          ]
        }
      ]
    },
    {
      "name": "esempio_pressoflessione_deviata.py",
      "type": "file"
    },
    {
      "name": "examples",
      "type": "dir",
      "children": [
        {
          "name": "demo_backup_system.py",
          "type": "file"
        },
        {
          "name": "demo_export_backup.py",
          "type": "file"
        },
        {
          "name": "demo_export_gui.py",
          "type": "file"
        },
        {
          "name": "demo_material_persistence.py",
          "type": "file"
        },
        {
          "name": "demo_persistenza.py",
          "type": "file"
        },
        {
          "name": "demo_recovery_system.py",
          "type": "file"
        },
        {
          "name": "demo_verification_table_auto_update.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "gui",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "materials_gui.py",
          "type": "file"
        },
        {
          "name": "section_gui.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "historical_materials.json",
      "type": "file"
    },
    {
      "name": "historical_materials.py",
      "type": "file"
    },
    {
      "name": "historical_ta",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "checks.py",
          "type": "file"
        },
        {
          "name": "geometry.py",
          "type": "file"
        },
        {
          "name": "materials.py",
          "type": "file"
        },
        {
          "name": "stress.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "libs",
      "type": "dir",
      "children": [
        {
          "name": "app_module",
          "type": "dir",
          "children": [
            {
              "name": "app.py",
              "type": "file"
            },
            {
              "name": "models",
              "type": "dir",
              "children": [
                {
                  "name": "sections.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "modules",
              "type": "dir",
              "children": [
                {
                  "name": "modules_config.json",
                  "type": "file"
                },
                {
                  "name": "registry.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "saved_sections.csv",
              "type": "file"
            },
            {
              "name": "services",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "area_calculations.py",
                  "type": "file"
                },
                {
                  "name": "calculations.py",
                  "type": "file"
                },
                {
                  "name": "debug_log_stream.py",
                  "type": "file"
                },
                {
                  "name": "event_bus.py",
                  "type": "file"
                },
                {
                  "name": "historical_calculations.py",
                  "type": "file"
                },
                {
                  "name": "notification.py",
                  "type": "file"
                },
                {
                  "name": "notification_settings.py",
                  "type": "file"
                },
                {
                  "name": "repository.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "ui",
              "type": "dir",
              "children": [
                {
                  "name": "code_settings_window.py",
                  "type": "file"
                },
                {
                  "name": "debug_viewer.py",
                  "type": "file"
                },
                {
                  "name": "historical_main_window.py",
                  "type": "file"
                },
                {
                  "name": "historical_material_window.py",
                  "type": "file"
                },
                {
                  "name": "main_window.py",
                  "type": "file"
                },
                {
                  "name": "module_selector_view.py",
                  "type": "file"
                },
                {
                  "name": "modules_config.json",
                  "type": "file"
                },
                {
                  "name": "notification_center.py",
                  "type": "file"
                },
                {
                  "name": "section_manager.py",
                  "type": "file"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "logs",
      "type": "dir",
      "children": [
        {
          "name": "README.md",
          "type": "file"
        }
      ]
    },
    {
      "name": "mat_repository",
      "type": "dir",
      "children": [
        {
          "name": "Mat_repository.jsonm",
          "type": "file"
        }
      ]
    },
    {
      "name": "material_sources.py",
      "type": "file"
    },
    {
      "name": "materials.json",
      "type": "file"
    },
    {
      "name": "materials_backup.json",
      "type": "file"
    },
    {
      "name": "materials_repository.py",
      "type": "file"
    },
    {
      "name": "mkdocs.yml",
      "type": "file"
    },
    {
      "name": "modules",
      "type": "dir",
      "children": [
        {
          "name": "carbon_fiber_placeholder.py",
          "type": "file"
        },
        {
          "name": "debug_viewer.py",
          "type": "file"
        },
        {
          "name": "frc_placeholder.py",
          "type": "file"
        },
        {
          "name": "geometry.py",
          "type": "file"
        },
        {
          "name": "historical_placeholder.py",
          "type": "file"
        },
        {
          "name": "material_editor.py",
          "type": "file"
        },
        {
          "name": "modules_config.json",
          "type": "file"
        },
        {
          "name": "registry.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "mypy.ini",
      "type": "file"
    },
    {
      "name": "nul",
      "type": "file"
    },
    {
      "name": "output_esempio.txt",
      "type": "file"
    },
    {
      "name": "patches",
      "type": "dir",
      "children": [
        {
          "name": "0001-Deprecate-sections.json-auto-migrate-to-sec_reposito.patch",
          "type": "file"
        }
      ]
    },
    {
      "name": "path",
      "type": "dir",
      "children": [
        {
          "name": "to",
          "type": "dir",
          "children": [
            {
              "name": "src",
              "type": "dir",
              "children": [
                {
                  "name": "main.py",
                  "type": "file"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "progetto.zip",
      "type": "file"
    },
    {
      "name": "project_tree.txt",
      "type": "file"
    },
    {
      "name": "pyproject.toml",
      "type": "file"
    },
    {
      "name": "pytest.ini",
      "type": "file"
    },
    {
      "name": "quantities_registry.csv",
      "type": "file"
    },
    {
      "name": "quantities_registry.py",
      "type": "file"
    },
    {
      "name": "reorganize_sections_app.py",
      "type": "file"
    },
    {
      "name": "requirements-dev.in",
      "type": "file"
    },
    {
      "name": "requirements-dev.txt",
      "type": "file"
    },
    {
      "name": "requirements.in",
      "type": "file"
    },
    {
      "name": "requirements.txt",
      "type": "file"
    },
    {
      "name": "scripts",
      "type": "dir",
      "children": [
        {
          "name": "apply_patch_and_test.ps1",
          "type": "file"
        },
        {
          "name": "auto_fix_bandit.py",
          "type": "file"
        },
        {
          "name": "auto_fix_bandit_extra.py",
          "type": "file"
        },
        {
          "name": "auto_fix_random_random.py",
          "type": "file"
        },
        {
          "name": "check_dynamic_fields.py",
          "type": "file"
        },
        {
          "name": "clean_trailing_whitespace.py",
          "type": "file"
        },
        {
          "name": "cleanup_precommit_cache.py",
          "type": "file"
        },
        {
          "name": "debug_combobox.py",
          "type": "file"
        },
        {
          "name": "debug_combobox2.py",
          "type": "file"
        },
        {
          "name": "debug_suggestions.py",
          "type": "file"
        },
        {
          "name": "debug_verification_input.py",
          "type": "file"
        },
        {
          "name": "demo_campi_dinamici.py",
          "type": "file"
        },
        {
          "name": "force_clear_precommit_cache.py",
          "type": "file"
        },
        {
          "name": "inspect_inverted_t.py",
          "type": "file"
        },
        {
          "name": "inspect_l.py",
          "type": "file"
        },
        {
          "name": "inspect_l2.py",
          "type": "file"
        },
        {
          "name": "inspect_materials.py",
          "type": "file"
        },
        {
          "name": "inspect_shapes.py",
          "type": "file"
        },
        {
          "name": "inspect_v_props.py",
          "type": "file"
        },
        {
          "name": "inspect_v_rects.py",
          "type": "file"
        },
        {
          "name": "manual_demo.py",
          "type": "file"
        },
        {
          "name": "materials_cli.py",
          "type": "file"
        },
        {
          "name": "remove_corrupt_repo_cache.py",
          "type": "file"
        },
        {
          "name": "replace_sigma.py",
          "type": "file"
        },
        {
          "name": "run-local.ps1",
          "type": "file"
        },
        {
          "name": "run-local.sh",
          "type": "file"
        },
        {
          "name": "run_concrete_tests.py",
          "type": "file"
        },
        {
          "name": "run_lint_from_venv.py",
          "type": "file"
        },
        {
          "name": "run_materials_demo.py",
          "type": "file"
        },
        {
          "name": "run_materials_gui.py",
          "type": "file"
        },
        {
          "name": "run_materials_runner.py",
          "type": "file"
        },
        {
          "name": "run_precommit_elevated.ps1",
          "type": "file"
        },
        {
          "name": "run_section_graphics_demo.py",
          "type": "file"
        },
        {
          "name": "run_verification_demo.py",
          "type": "file"
        },
        {
          "name": "smoke_imports.py",
          "type": "file"
        },
        {
          "name": "update_imports.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "sec_repository",
      "type": "dir",
      "children": [
        {
          "name": "sec_repository.jsons",
          "type": "file"
        },
        {
          "name": "sec_repository_backup.jsons",
          "type": "file"
        }
      ]
    },
    {
      "name": "sections.json",
      "type": "file"
    },
    {
      "name": "sections.json.bak",
      "type": "file"
    },
    {
      "name": "sections_app",
      "type": "dir",
      "children": []
    },
    {
      "name": "sections_tree.txt",
      "type": "file"
    },
    {
      "name": "softw_components",
      "type": "dir",
      "children": [
        {
          "name": "geometry_model_module",
          "type": "dir",
          "children": [
            {
              "name": "saved_sections.csv",
              "type": "file"
            }
          ]
        },
        {
          "name": "section_calculations_module",
          "type": "dir",
          "children": [
            {
              "name": "models",
              "type": "dir",
              "children": [
                {
                  "name": "sections.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "saved_sections.csv",
              "type": "file"
            },
            {
              "name": "services",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "area_calculations.py",
                  "type": "file"
                },
                {
                  "name": "calculations.py",
                  "type": "file"
                }
              ]
            }
          ]
        },
        {
          "name": "section_graphics_module",
          "type": "dir",
          "children": [
            {
              "name": "saved_sections.csv",
              "type": "file"
            }
          ]
        },
        {
          "name": "sections_app_module",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "saved_sections.csv",
              "type": "file"
            }
          ]
        },
        {
          "name": "shear_factors_module",
          "type": "dir",
          "children": [
            {
              "name": "saved_sections.csv",
              "type": "file"
            },
            {
              "name": "shear_factors.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "storage_module",
          "type": "dir",
          "children": [
            {
              "name": "saved_sections.csv",
              "type": "file"
            }
          ]
        }
      ]
    },
    {
      "name": "src",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "_io_disabled",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "core_calculus",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "contracts.py",
              "type": "file"
            },
            {
              "name": "core",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "examples_sections.py",
                  "type": "file"
                },
                {
                  "name": "frc.py",
                  "type": "file"
                },
                {
                  "name": "geometry.py",
                  "type": "file"
                },
                {
                  "name": "geometry_model.py",
                  "type": "file"
                },
                {
                  "name": "interpolation.py",
                  "type": "file"
                },
                {
                  "name": "materials.py",
                  "type": "file"
                },
                {
                  "name": "reinforcement.py",
                  "type": "file"
                },
                {
                  "name": "section_properties.py",
                  "type": "file"
                },
                {
                  "name": "verification_bas_adapter.py",
                  "type": "file"
                },
                {
                  "name": "verification_core.py",
                  "type": "file"
                },
                {
                  "name": "verification_engine.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "geometry_cache.py",
              "type": "file"
            },
            {
              "name": "lc_fc_adjustments.py",
              "type": "file"
            },
            {
              "name": "normative_registry.py",
              "type": "file"
            },
            {
              "name": "section_calculations.py",
              "type": "file"
            },
            {
              "name": "validation_engine.py",
              "type": "file"
            },
            {
              "name": "verification_engine.py",
              "type": "file"
            },
            {
              "name": "verification_service.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "domain",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "domain",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "materials.py",
                  "type": "file"
                },
                {
                  "name": "models.py",
                  "type": "file"
                },
                {
                  "name": "sections.py",
                  "type": "file"
                }
              ]
            }
          ]
        },
        {
          "name": "launcher",
          "type": "dir",
          "children": [
            {
              "name": "bootstrap.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "methods",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "checks_dm96.py",
              "type": "file"
            },
            {
              "name": "checks_fire_dm96.py",
              "type": "file"
            },
            {
              "name": "checks_ntc2018.py",
              "type": "file"
            },
            {
              "name": "checks_rd2229.py",
              "type": "file"
            },
            {
              "name": "prestress_models.py",
              "type": "file"
            },
            {
              "name": "protocols.py",
              "type": "file"
            },
            {
              "name": "ta.py",
              "type": "file"
            },
            {
              "name": "verification",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "dispatcher.py",
                  "type": "file"
                },
                {
                  "name": "engine_adapter.py",
                  "type": "file"
                },
                {
                  "name": "methods_sle.py",
                  "type": "file"
                },
                {
                  "name": "methods_slu.py",
                  "type": "file"
                },
                {
                  "name": "methods_ta.py",
                  "type": "file"
                },
                {
                  "name": "verification_controller.py",
                  "type": "file"
                }
              ]
            }
          ]
        },
        {
          "name": "rd2229",
          "type": "dir",
          "children": [
            {
              "name": "core",
              "type": "dir",
              "children": []
            },
            {
              "name": "gui",
              "type": "dir",
              "children": []
            },
            {
              "name": "sections_app",
              "type": "dir",
              "children": [
                {
                  "name": "models",
                  "type": "dir",
                  "children": []
                },
                {
                  "name": "services",
                  "type": "dir",
                  "children": []
                },
                {
                  "name": "ui",
                  "type": "dir",
                  "children": [
                    {
                      "name": "section_types",
                      "type": "dir",
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "name": "tools",
              "type": "dir",
              "children": []
            }
          ]
        },
        {
          "name": "repositories",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "data",
              "type": "dir",
              "children": [
                {
                  "name": "historical_materials.json",
                  "type": "file"
                },
                {
                  "name": "material_sources.json",
                  "type": "file"
                },
                {
                  "name": "materials.json",
                  "type": "file"
                },
                {
                  "name": "rd2229_table.csv",
                  "type": "file"
                },
                {
                  "name": "tables.schema.json",
                  "type": "file"
                }
              ]
            }
          ]
        },
        {
          "name": "ui",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "code_settings_window.py",
              "type": "file"
            },
            {
              "name": "debug_viewer.py",
              "type": "file"
            },
            {
              "name": "frc_manager.py",
              "type": "file"
            },
            {
              "name": "frc_verification_window.py",
              "type": "file"
            },
            {
              "name": "historical_main_window.py",
              "type": "file"
            },
            {
              "name": "historical_material_window.py",
              "type": "file"
            },
            {
              "name": "main_window.py",
              "type": "file"
            },
            {
              "name": "module_selector.py",
              "type": "file"
            },
            {
              "name": "notification_center.py",
              "type": "file"
            },
            {
              "name": "notification_settings_window.py",
              "type": "file"
            },
            {
              "name": "section_manager.py",
              "type": "file"
            },
            {
              "name": "ui",
              "type": "dir",
              "children": [
                {
                  "name": "__init__.py",
                  "type": "file"
                },
                {
                  "name": "comparator.py",
                  "type": "file"
                },
                {
                  "name": "csv_io.py",
                  "type": "file"
                },
                {
                  "name": "project_actions.py",
                  "type": "file"
                },
                {
                  "name": "rebar_calculator.py",
                  "type": "file"
                },
                {
                  "name": "suggestion_box.py",
                  "type": "file"
                },
                {
                  "name": "verification_table_app.py",
                  "type": "file"
                }
              ]
            },
            {
              "name": "verification_comparator.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "utils",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "background.py",
              "type": "file"
            }
          ]
        }
      ]
    },
    {
      "name": "tatus --porcelain",
      "type": "file"
    },
    {
      "name": "test_veloce_deviata.py",
      "type": "file"
    },
    {
      "name": "tests",
      "type": "dir",
      "children": [
        {
          "name": "golden_rd2229.json",
          "type": "file"
        },
        {
          "name": "test_adapter_and_properties.py",
          "type": "file"
        },
        {
          "name": "test_area_calculations.py",
          "type": "file"
        },
        {
          "name": "test_background_executor.py",
          "type": "file"
        },
        {
          "name": "test_comprehensive.py",
          "type": "file"
        },
        {
          "name": "test_core_and_graphics.py",
          "type": "file"
        },
        {
          "name": "test_core_improved.py",
          "type": "file"
        },
        {
          "name": "test_core_selection_scoring.py",
          "type": "file"
        },
        {
          "name": "test_crud_operations.py",
          "type": "file"
        },
        {
          "name": "test_csv_io.py",
          "type": "file"
        },
        {
          "name": "test_dm96_checks.py",
          "type": "file"
        },
        {
          "name": "test_domain_materials.py",
          "type": "file"
        },
        {
          "name": "test_domain_sections.py",
          "type": "file"
        },
        {
          "name": "test_fire_checks.py",
          "type": "file"
        },
        {
          "name": "test_geometry_cache.py",
          "type": "file"
        },
        {
          "name": "test_geometry_model_extra.py",
          "type": "file"
        },
        {
          "name": "test_golden_rd2229.py",
          "type": "file"
        },
        {
          "name": "test_graphics_flags.py",
          "type": "file"
        },
        {
          "name": "test_lc_fc_adjustments.py",
          "type": "file"
        },
        {
          "name": "test_main_window_gui.py",
          "type": "file"
        },
        {
          "name": "test_materials_cache.py",
          "type": "file"
        },
        {
          "name": "test_module_registry.py",
          "type": "file"
        },
        {
          "name": "test_module_registry_refresh.py",
          "type": "file"
        },
        {
          "name": "test_module_selector_controller.py",
          "type": "file"
        },
        {
          "name": "test_module_selector_integration.py",
          "type": "file"
        },
        {
          "name": "test_module_selector_ui.py",
          "type": "file"
        },
        {
          "name": "test_new_architecture.py",
          "type": "file"
        },
        {
          "name": "test_ntc2018_checks.py",
          "type": "file"
        },
        {
          "name": "test_persistence_edit_cycle.py",
          "type": "file"
        },
        {
          "name": "test_rd2229_checks.py",
          "type": "file"
        },
        {
          "name": "test_rebar_calculator.py",
          "type": "file"
        },
        {
          "name": "test_rotation_invariants.py",
          "type": "file"
        },
        {
          "name": "test_section_adapter_and_properties.py",
          "type": "file"
        },
        {
          "name": "test_section_calculations.py",
          "type": "file"
        },
        {
          "name": "test_section_calculations_extra.py",
          "type": "file"
        },
        {
          "name": "test_section_calculations_regression.py",
          "type": "file"
        },
        {
          "name": "test_section_calculations_rotation.py",
          "type": "file"
        },
        {
          "name": "test_section_graphics_extra.py",
          "type": "file"
        },
        {
          "name": "test_section_graphics_fake_canvas.py",
          "type": "file"
        },
        {
          "name": "test_section_graphics_transform.py",
          "type": "file"
        },
        {
          "name": "test_section_graphics_transform_extra.py",
          "type": "file"
        },
        {
          "name": "test_section_properties_wx_wy.py",
          "type": "file"
        },
        {
          "name": "test_section_shapes.py",
          "type": "file"
        },
        {
          "name": "test_section_to_geometry_types.py",
          "type": "file"
        },
        {
          "name": "test_shapely_integration.py",
          "type": "file"
        },
        {
          "name": "test_shapely_integration_optional.py",
          "type": "file"
        },
        {
          "name": "test_shear_areas_complete.py",
          "type": "file"
        },
        {
          "name": "test_shear_meta.py",
          "type": "file"
        },
        {
          "name": "test_shim_import.py",
          "type": "file"
        },
        {
          "name": "test_storage.py",
          "type": "file"
        },
        {
          "name": "test_ta_method.py",
          "type": "file"
        },
        {
          "name": "test_table_navigation.py",
          "type": "file"
        },
        {
          "name": "test_ui_background_compute.py",
          "type": "file"
        },
        {
          "name": "test_verification_dispatcher.py",
          "type": "file"
        },
        {
          "name": "test_verification_pipeline.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "tests_legacy",
      "type": "dir",
      "children": [
        {
          "name": "README.md",
          "type": "file"
        },
        {
          "name": "conftest.py",
          "type": "file"
        },
        {
          "name": "test_all_sections.py",
          "type": "file"
        },
        {
          "name": "test_auto_load_startup.py",
          "type": "file"
        },
        {
          "name": "test_backup_system.py",
          "type": "file"
        },
        {
          "name": "test_bas_adapter.py",
          "type": "file"
        },
        {
          "name": "test_canonical_repository_paths.py",
          "type": "file"
        },
        {
          "name": "test_concrete_strength.py",
          "type": "file"
        },
        {
          "name": "test_config_loaders.py",
          "type": "file"
        },
        {
          "name": "test_deviated_bending.py",
          "type": "file"
        },
        {
          "name": "test_drawing_geometry.py",
          "type": "file"
        },
        {
          "name": "test_export_backup.py",
          "type": "file"
        },
        {
          "name": "test_export_gui.py",
          "type": "file"
        },
        {
          "name": "test_frc_basic.py",
          "type": "file"
        },
        {
          "name": "test_frc_verification_window.py",
          "type": "file"
        },
        {
          "name": "test_gui_compatibility.py",
          "type": "file"
        },
        {
          "name": "test_historical_import_csv.py",
          "type": "file"
        },
        {
          "name": "test_historical_material_window.py",
          "type": "file"
        },
        {
          "name": "test_historical_materials.py",
          "type": "file"
        },
        {
          "name": "test_historical_ta.py",
          "type": "file"
        },
        {
          "name": "test_integration_persistence.py",
          "type": "file"
        },
        {
          "name": "test_json_wrappers.py",
          "type": "file"
        },
        {
          "name": "test_main_window_material_button.py",
          "type": "file"
        },
        {
          "name": "test_main_window_save.py",
          "type": "file"
        },
        {
          "name": "test_manual_demo.py",
          "type": "file"
        },
        {
          "name": "test_material_persistence.py",
          "type": "file"
        },
        {
          "name": "test_materials_frc.py",
          "type": "file"
        },
        {
          "name": "test_materials_repository.py",
          "type": "file"
        },
        {
          "name": "test_migration_sections_json.py",
          "type": "file"
        },
        {
          "name": "test_module_selector_frc_buttons.py",
          "type": "file"
        },
        {
          "name": "test_module_selector_material_button.py",
          "type": "file"
        },
        {
          "name": "test_module_selector_section_button.py",
          "type": "file"
        },
        {
          "name": "test_new_sections.py",
          "type": "file"
        },
        {
          "name": "test_notification_center.py",
          "type": "file"
        },
        {
          "name": "test_notification_service.py",
          "type": "file"
        },
        {
          "name": "test_notification_settings.py",
          "type": "file"
        },
        {
          "name": "test_notification_settings_ui.py",
          "type": "file"
        },
        {
          "name": "test_numerical_ta.py",
          "type": "file"
        },
        {
          "name": "test_persistence.py",
          "type": "file"
        },
        {
          "name": "test_recovery_system.py",
          "type": "file"
        },
        {
          "name": "test_repository_save.py",
          "type": "file"
        },
        {
          "name": "test_search_helpers_with_repo.py",
          "type": "file"
        },
        {
          "name": "test_section_manager_autorefresh.py",
          "type": "file"
        },
        {
          "name": "test_section_manager_columns.py",
          "type": "file"
        },
        {
          "name": "test_section_manager_new_button.py",
          "type": "file"
        },
        {
          "name": "test_section_manager_new_stays_open.py",
          "type": "file"
        },
        {
          "name": "test_section_manager_ui.py",
          "type": "file"
        },
        {
          "name": "test_section_parser_compat.py",
          "type": "file"
        },
        {
          "name": "test_sections.py",
          "type": "file"
        },
        {
          "name": "test_sections_properties.py",
          "type": "file"
        },
        {
          "name": "test_sections_random_demo.py",
          "type": "file"
        },
        {
          "name": "test_shear_areas.py",
          "type": "file"
        },
        {
          "name": "test_shear_help_button.py",
          "type": "file"
        },
        {
          "name": "test_startup_integration.py",
          "type": "file"
        },
        {
          "name": "test_torsion.py",
          "type": "file"
        },
        {
          "name": "test_verification_comparator_visuals.py",
          "type": "file"
        },
        {
          "name": "test_verification_frc_integration.py",
          "type": "file"
        },
        {
          "name": "test_verification_table.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_api.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_auto_update.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_autocomplete_and_events.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_combobox.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_csv.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_csv_roundtrip.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_dialogs.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_edgecases.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_import_mapping_and_logging.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_integration.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_jsonp.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_more.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_navigation.py",
          "type": "file"
        },
        {
          "name": "test_verification_table_suggestions_on_empty.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "tools",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "concrete_strength.py",
          "type": "file"
        },
        {
          "name": "materials_manager.py",
          "type": "file"
        },
        {
          "name": "profile_calculus.py",
          "type": "file"
        },
        {
          "name": "rd2229_calc.py",
          "type": "file"
        },
        {
          "name": "rewrite_sections_app_imports.py",
          "type": "file"
        },
        {
          "name": "run_mypy_ci.py",
          "type": "file"
        },
        {
          "name": "split_sections_app.py",
          "type": "file"
        },
        {
          "name": "sync_verifications.py",
          "type": "file"
        },
        {
          "name": "verify_softw_components.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "tree_output.txt",
      "type": "file"
    },
    {
      "name": "ui",
      "type": "dir",
      "children": [
        {
          "name": "module_selector.py",
          "type": "file"
        }
      ]
    },
    {
      "name": "verification_items.py",
      "type": "file"
    },
    {
      "name": "verification_items_repository.py",
      "type": "file"
    },
    {
      "name": "verification_project.py",
      "type": "file"
    },
    {
      "name": "verification_table.py",
      "type": "file"
    },
    {
      "name": "verifications",
      "type": "dir",
      "children": [
        {
          "name": "__init__.py",
          "type": "file"
        },
        {
          "name": "pilastri",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "rd2229",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            },
            {
              "name": "tensioni_ammissibili.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "scale",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "solette",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        },
        {
          "name": "travi",
          "type": "dir",
          "children": [
            {
              "name": "__init__.py",
              "type": "file"
            }
          ]
        }
      ]
    },
    {
      "name": "visual_basic",
      "type": "dir",
      "children": [
        {
          "name": "ApplyBasToWorkbook.ps1",
          "type": "file"
        },
        {
          "name": "CA_SLE.bas",
          "type": "file"
        },
        {
          "name": "CA_SLE.txt",
          "type": "file"
        },
        {
          "name": "CA_SLU.bas",
          "type": "file"
        },
        {
          "name": "CA_SLU.txt",
          "type": "file"
        },
        {
          "name": "ISTRUZIONI_IMPORTAZIONE_VBA.txt",
          "type": "file"
        },
        {
          "name": "Impostazioni.bas",
          "type": "file"
        },
        {
          "name": "Impostazioni.txt",
          "type": "file"
        },
        {
          "name": "PrincipCA_TA.bas",
          "type": "file"
        },
        {
          "name": "PrincipCA_TA.txt",
          "type": "file"
        },
        {
          "name": "frmAltriDati.frm",
          "type": "file"
        },
        {
          "name": "frmAltriDati.frx",
          "type": "file"
        },
        {
          "name": "frmDatiGene.frm",
          "type": "file"
        },
        {
          "name": "frmDatiGene.frx",
          "type": "file"
        },
        {
          "name": "frmDatiGene2.frm",
          "type": "file"
        },
        {
          "name": "frmDatiGene2.frx",
          "type": "file"
        },
        {
          "name": "frmGeomCalastr.frm",
          "type": "file"
        },
        {
          "name": "frmGeomCalastr.frx",
          "type": "file"
        },
        {
          "name": "frmGeomCalastrConfin.frm",
          "type": "file"
        },
        {
          "name": "frmGeomCalastrConfin.frx",
          "type": "file"
        },
        {
          "name": "frmGeomFRP.frm",
          "type": "file"
        },
        {
          "name": "frmGeomFRP.frx",
          "type": "file"
        },
        {
          "name": "frmGeomFRPconfin.frm",
          "type": "file"
        },
        {
          "name": "frmGeomFRPconfin.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezCircCA.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezCircCA.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezDoppioT.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezDoppioT.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezGenerica.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezGenerica.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezRettCA.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezRettCA.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezScat.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezScat.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezT.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezT.frx",
          "type": "file"
        },
        {
          "name": "frmGeomSezTrovescia.frm",
          "type": "file"
        },
        {
          "name": "frmGeomSezTrovescia.frx",
          "type": "file"
        },
        {
          "name": "frmInformaz.frm",
          "type": "file"
        },
        {
          "name": "frmInformaz.frx",
          "type": "file"
        },
        {
          "name": "frmMaterAcc.frm",
          "type": "file"
        },
        {
          "name": "frmMaterAcc.frx",
          "type": "file"
        },
        {
          "name": "frmMaterCA.frm",
          "type": "file"
        },
        {
          "name": "frmMaterCA.frx",
          "type": "file"
        },
        {
          "name": "frmMaterCAesist.frm",
          "type": "file"
        },
        {
          "name": "frmMaterCAesist.frx",
          "type": "file"
        },
        {
          "name": "frmMaterFRC.frm",
          "type": "file"
        },
        {
          "name": "frmMaterFRC.frx",
          "type": "file"
        },
        {
          "name": "frmMaterFRP.frm",
          "type": "file"
        },
        {
          "name": "frmMaterFRP.frx",
          "type": "file"
        },
        {
          "name": "frmPacchettiArmat.frm",
          "type": "file"
        },
        {
          "name": "frmPacchettiArmat.frx",
          "type": "file"
        },
        {
          "name": "frmRelazCalc.frm",
          "type": "file"
        },
        {
          "name": "frmRelazCalc.frx",
          "type": "file"
        },
        {
          "name": "frmSollecitazSLE.frm",
          "type": "file"
        },
        {
          "name": "frmSollecitazSLE.frx",
          "type": "file"
        },
        {
          "name": "frmSollecitazSLU.frm",
          "type": "file"
        },
        {
          "name": "frmSollecitazSLU.frx",
          "type": "file"
        },
        {
          "name": "frmSplash.frm",
          "type": "file"
        },
        {
          "name": "frmSplash.frx",
          "type": "file"
        },
        {
          "name": "frmStabilità.frm",
          "type": "file"
        },
        {
          "name": "frmStabilità.frx",
          "type": "file"
        },
        {
          "name": "frmVerifSLE.frm",
          "type": "file"
        },
        {
          "name": "frmVerifSLE.frx",
          "type": "file"
        },
        {
          "name": "frmVisuSez.frm",
          "type": "file"
        },
        {
          "name": "frmVisuSez.frx",
          "type": "file"
        },
        {
          "name": "import_vba.ps1",
          "type": "file"
        }
      ]
    },
    {
      "name": "witch main",
      "type": "file"
    }
  ]
}
```
