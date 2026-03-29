# MANIFEST_APPLICAZIONE.md

Source: derived from docs/MEGAPLAN/CHAT_PLAN.md (entire session)
Purpose: actionable manifest of CREATE/UPDATE/REPLACE operations required to sync the repository

Format:

- file_path: relative path in repo
- action: CREATE | UPDATE | REPLACE
- source_pointer: short pointer to CHAT_PLAN.md section that mandates the change
- notes: why / constraints / TODO tokens retained

---

- file_path: docs/MEGAPLAN/MANIFEST_APPLICAZIONE.md
  action: CREATE
  source_pointer: "CHAT_PLAN.md — PROCESS (MANDATORY), step 1"
  notes: manifest file (this file)

- file_path: docs/MEGAPLAN/APPLICATION_REPORT.md
  action: CREATE
  source_pointer: "User request: APPLICATION_REPORT.md in final deliverables"
  notes: summary report of applied changes + pending TODOs

- file_path: docs/MEGAPLAN/CodeModule_CONTRACT.md
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'CodeModule — scelte di contratto'"
  notes: API contract (SPEC only — no implementation)

- file_path: docs/MEGAPLAN/TEST_PLAN_NTC2018.md
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'Testing, validation and documentation'"
  notes: golden cases + coverage threshold (SPEC only)

- file_path: docs/MEGAPLAN/SPEC_SecondaryElementSpec.md
  action: REPLACE
  source_pointer: "CHAT_PLAN.md — 'SPEC_SecondaryElementSpec.md' (final approved content)"
  notes: replace excerpt with full approved SPEC (includes trace/run_id, norm_references[])

- file_path: docs/MEGAPLAN/PLAN_GUI_SECONDARY_ELEMENTS.md
  action: UPDATE
  source_pointer: "CHAT_PLAN.md — 'GUI secondary elements' (wireframe + file mapping)"
  notes: expand to include file mappings and widget location (`src/gui/secondary_elements`)

- file_path: docs/MEGAPLAN/GUI_RISULTATI_TO_RELAZIONE_BINDING.md
  action: UPDATE
  source_pointer: "CHAT_PLAN.md — updated binding rules (configurable inclusion, na_handling, trace)"
  notes: ensure configurable defaults + run_id + norm_references[] present (kept if already updated)

- file_path: config/calculation_codes/NTC2018.jsoncode
  action: CREATE
  source_pointer: "CHAT_PLAN.md — config/calculation_codes/NTC2018.jsoncode (skeleton)"
  notes: skeleton only; no normative values invented; TODO entries where required

- file_path: config/codes/ntc2018/secondary_elements.jsoncode
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'secondary_elements.jsoncode' (templates registry skeleton)"
  notes: template registry skeleton; placeholders/TODO preserved

- file_path: src/codes/ntc2018/__init__.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'codes/ntc2018' package"
  notes: package docstring referencing MEGAPLAN; skeleton only

- file_path: src/codes/ntc2018/code_module.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'CodeModule contract' (interface)"
  notes: class skeleton + docstring; no normative logic

- file_path: src/codes/ntc2018/checks_vrdc.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'RC_SLU_VRDc_NoStirrups' (spec/stub)"
  notes: stub/skeleton only; tests will reference fixtures

- file_path: src/codes/ntc2018/secondary_elements/__init__.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'codes/ntc2018/secondary_elements' package"
  notes: package skeleton

- file_path: src/codes/ntc2018/secondary_elements/models.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'SecondaryElementSpec schema (models)'"
  notes: datamodel skeleton (fields documented); no implementation logic

- file_path: src/codes/ntc2018/secondary_elements/checks.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'secondary elements checks (identifiers)'"
  notes: check identifiers / orchestration skeleton only

- file_path: src/codes/ntc2018/secondary_elements/storage_adapter.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'storage adapter for secondary_elements'"
  notes: persistence adapter skeleton (document references to MEGAPLAN)

- file_path: src/core/combinations/ntc2018_combinations.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'core/combinations NTC2018 generator (skeleton)'"
  notes: skeleton only

- file_path: src/core/materials/ntc2018_adapter.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'material registry & adapter NTC2018'"
  notes: skeleton only; uses existing loaders (documented)

- file_path: src/gui/ntc2018_selector.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'GUI selector norma (skeleton)'"
  notes: widget skeleton; GUI thin rule enforced

- file_path: src/gui/secondary_elements/window.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'GUI secondary_element_window.py (MVP)'"
  notes: UI flow controller skeleton

- file_path: src/gui/secondary_elements/editor.py
  action: UPDATE
  source_pointer: "CHAT_PLAN.md — 'secondary_element_editor UI mapping'"
  notes: fill module docstring + bindings reference to SPEC_SecondaryElementSpec.md

- file_path: src/gui/secondary_elements/results_view.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'secondary_element_results UI (results panel)'"
  notes: read‑only results panel skeleton

- file_path: src/gui/widgets/secondary_element_widgets.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'widgets/secondary_element_widgets.py (preview, anchor diagram)'"
  notes: widget skeletons

- file_path: src/gui/widgets/norm_selector.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'widgets/norm_selector.py (reads config/calculation_codes/*)'"
  notes: skeleton only

- file_path: tests/codes/test_vrdc_no_stirrups.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'Test fixtures for V_Rd,c (golden cases)'"
  notes: test skeletons + references to SPEC_RC_SLU_VRDc_NoStirrups.md

- file_path: tests/codes/test_secondary_elements_cantilever.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'Secondary elements tests (templates)'"
  notes: placeholder tests referencing TEST_PLAN_SECONDARY_ELEMENTS.md

- file_path: tests/codes/test_secondary_elements_signage.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'Secondary elements tests (templates)'"
  notes: placeholder

- file_path: tests/codes/test_secondary_elements_partition.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'Secondary elements tests (templates)'"
  notes: placeholder

- file_path: tests/codes/test_secondary_elements_chimney.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'Secondary elements tests (templates)'"
  notes: placeholder

- file_path: tests/gui/test_secondary_editor.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'GUI tests for secondary editor'"
  notes: placeholder tests (no normative checks)

- file_path: tests/integration/test_gui_verification_flow.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'E2E GUI verification flow scenarios'"
  notes: placeholder

- file_path: tests/gui/test_norm_selector.py
  action: CREATE
  source_pointer: "CHAT_PLAN.md — 'GUI norm selector tests'"
  notes: placeholder

---
Notes:

- All created source files are *skeletons only* (docstrings + TODO markers) as required.
- All normative numeric values remain ONLY in SPEC files that explicitly contain them in CHAT_PLAN.md.
- Any items in CHAT_PLAN.md left as non‑final remain PENDING and are explicitly referenced in APPLICATION_REPORT.md.
