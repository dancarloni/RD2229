# PLAN_GUI_SECONDARY_ELEMENTS.md

Scope: GUI wireframe and file mapping for "Secondary Elements" workflow (MVP). GUI must remain thin — no normative logic in UI.

User flow (STEP 1 MVP)
1. User opens "Secondary elements" editor from project context.
2. User selects element type (e.g. parapet, partition, signage, chimney).
3. User fills geometry/loads metadata (form-driven; input validation only).
4. User clicks "Run verification" — GUI calls CodeModule via CodeModule API (see `CodeModule_CONTRACT.md`).
5. GUI displays `VerificationResultItem` in `RisultatiView` (only presentation).
6. User may export verification to project report — report builder reads `VerificationResultItem.norm_references[]` and `trace.run_id`.

File mapping (where widgets / controllers live)
- `src/gui/secondary_elements/window.py` — window/controller for the flow
- `src/gui/secondary_elements/editor.py` — editor/form bindings (MVP: schema -> form)
- `src/gui/secondary_elements/results_view.py` — results-only panel (read-only formatting)
- `src/gui/widgets/secondary_element_widgets.py` — small reusable widgets (preview, anchor diagram)
- `src/gui/widgets/norm_selector.py` — select calculation code (reads `config/calculation_codes`)

Acceptance criteria (MVP)
- GUI does not implement any calculation; it only serializes user inputs and displays `VerificationResultItem` returned by the core module.
- Every displayed verification MUST show `trace.run_id` and at least one `norm_references[]` entry (or display "TODO: reference missing").
- All fields that require normative values are marked with TODO and must not contain hard-coded normative numbers.

Developer notes
- Tests: `tests/gui/test_secondary_editor.py`, `tests/integration/test_gui_verification_flow.py`
- Keep UI logic minimal; business rules belong in `src/codes/ntc2018` and engine modules.
