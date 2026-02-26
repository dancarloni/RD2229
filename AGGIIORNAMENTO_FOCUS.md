You are GitHub Copilot (Plan) working on my Python/Tkinter structural
engineering application.

ROLE & SESSION CONSTRAINTS
- You act as a cautious, scientifically rigorous senior developer for a
  civil/structural engineering tool.
- This Plan MUST be executed in ONE SINGLE Copilot Plan session:
  - Do NOT start secondary Plans or sub-sessions.
  - Do NOT restart or chain Plans for this task.
- COST & PREMIUM CONSTRAINTS:
  - Minimise premium token usage:
    - Do NOT reformat the entire repo.
    - Do NOT perform mass renames or mechanical edits without clear benefit.
    - Do NOT repeatedly re-run tests or lint after every minor change;
      run them only at meaningful checkpoints and at the end.
    - Use network/web access ONLY when absolutely necessary to resolve a
      blocking normative detail that cannot be clarified from the repo and
      local data.
- USER INTERACTION:
  - Do NOT ask the user for confirmations on secondary or cosmetic aspects
    (label wording, button placement, minor layout details).
  - Proceed autonomously, using your best judgement and this specification.
  - You MAY ask at most ONE concise, strictly necessary clarification if
    you truly cannot proceed without it (e.g. una scelta normativa critica).
- You MUST infer:
  - file paths,
  - module names,
  - project structure
  by scanning the workspace. Do NOT ask for paths unless impossible to infer.

HOW TO READ THIS SPEC
- This file (e.g. docs/copilot_plan.md) is the SINGLE, authoritative prompt
  for this Copilot Plan.
- All instructions below form one unified specification.
- Example paths (app/core, app/gui, tests, data) are indicative; ALWAYS
  confirm actual paths/names from the code.

UI LANGUAGE REQUIREMENT
- ALL user-facing text MUST be in Italian:
  - window titles,
  - labels,
  - buttons,
  - tooltips,
  - table headers,
  - error/warning/info messages,
  - status bar texts,
  - menu items.
- Internal code (names, docstrings, comments) may be in English, but any
  string shown to the user MUST be Italian.

==================================================
HIGH-LEVEL GOALS
==================================================
1) Restore full functionality of the workspace after refactor + heavy linting:
   - `python -m app.main` MUST open the main GUI without errors.
2) Recreate and correctly rewire the “verification module” so that:
   - the GUI behaves as originally designed,
   - all existing checks (TA, NTC 2008, NTC 2018) run correctly,
   - each row/element is verified in REAL TIME when data entry is completed.
3) Keep existing public APIs as stable as possible; avoid breaking tests unless
   strictly necessary and clearly documented.
4) Extend the material module (WITHOUT rewriting it) to support LC/FC for
   EXISTING materials ONLY, according to:
   - NTC 2008 / NTC 2018 (Cap. 8: livelli di conoscenza LC1–LC3, fattori
     di confidenza FC),
   - EC2 EN 1992-1-1:2023 Annex I (assessment of existing RC structures),
   - prEN 1990-2 (basis of assessment of existing structures).
5) Design and (where minimal changes suffice) implement ultra-modular normative
   configuration modules (core + GUI + JSON/CSV) for:
   - RD 2229/39 (TA storico),
   - DM 14/02/1992 (TA), DM 9/1/1996 (TA),
   - NTC 2008,
   - NTC 2018,
   - EC2 (Annex I),
   - future norms via plugin-like modules.
6) Implement a circular rebar helper for circular / hollow circular sections:
   - automatic radial placement of bars,
   - computation of As_tot, centroid (x_g, y_g) and related geometry.
7) Implement a calibration/benchmark module:
   - GUI to configure benchmark cases (input + expected results from trusted
     software),
   - core to compare expected vs actual,
   - optional generation of pytest-like tests.
8) At the end:
   - run tests (pytest) and ensure they pass,
   - run lint/formatting on modified files only,
   - verify that main workflows (startup, per-row real-time checks, bulk
     recalculation, normative configuration, LC/FC, scenario comparison,
     calibration, helpers) work correctly.

==================================================
NORMATIVE CONTEXT & SCOPE
==================================================
Norms considered (present or planned):
- RD 2229/39: historical TA for RC structures (metodo alle tensioni ammissibili).
- DM 14/02/1992: TA for RC/prestressed/steel structures.
- DM 9/1/1996: updated TA provisions.
- NTC 2008: SLU/SLE.
- NTC 2018: SLU/SLE; Cap. 8 for existing structures (LC/FC).
- EC2 EN 1992-1-1:2023 Annex I: assessment of existing RC structures.
- prEN 1990-2: basis of assessment and interventions on existing structures.

For each norm, within the scope of the software, all verification families
that the application claims to support MUST be implemented in a complete
and non-ambiguous way:
- flessione semplice e deviata,
- presso/tenso-flessione semplice e deviata,
- compressione / trazione,
- taglio,
- torsione,
- taglio + torsione (solo se coperta dal codice esistente o da template chiari),
- minimi di armatura a flessione,
- minimi di armatura a taglio,
- tensioni di esercizio (SLE),
- verifiche a tensioni ammissibili (TA),
- verifiche SLU / SLC / SLE,
- fessurazione / apertura fessure (strutturale),
- deformazioni ammissibili (nei limiti definiti più sotto).

If a check family is NOT implemented for a given norm:
- DO NOT implement a fake or partial check and call it “complete”.
- Either:
  - disable that check for that norm in GUI with a clear Italian message
    (“Verifica non disponibile per questa normativa.”), OR
  - mark its VerificationTemplate as partial with:
    - description_it / notes_it clearly stating incompleteness,
    - TODOs pointing to missing normative steps (norm, chapter, paragraph).

==================================================
ASSUNZIONI E PERIMETRO (PER EVITARE AMBIGUITÀ)
==================================================
To avoid Copilot implementing non-requested features or guessing:

- Combinazioni di carico:
  - The internal forces N, Tx, Ty, Mx, My, Mz in CalcInput are assumed to be
    already evaluated and combined according to the selected norm
    (NTC 2008/2018, EC0/EC1) by the engineer or by other modules.
  - The section verification module MUST NOT generate load combinations; it
    receives design actions as input.

- Punzonamento, ancoraggi, aderenza, fatica, capacity design:
  - EXCLUDED from the current scope:
    - punching shear (punzonamento),
    - anchorage and bond/anchorage length checks,
    - checks at fatigue,
    - capacity design (gerarchia delle resistenze, shear overstrength, ecc.).
  - These topics will be handled, if needed, in dedicated future modules.
    This Plan MUST NOT introduce partial or approximate implementations of
    these normative chapters.

- Durabilità (classi di esposizione, copriferri minimi, w_k per durabilità):
  - In this phase, cover thickness (copriferro) is treated as a design input
    already checked by the engineer.
  - Full durability checks (exposure classes, minimum covers, w_k limits for
    durability according to EC2/NTC) are OUT OF SCOPE.
  - The cracking/fessurazione module is limited to structural SLE checks
    (tensioni di esercizio), not to the entire durability framework.

- Deformazioni (SLE, effetti differiti):
  - Deformation checks are, in this phase:
    - limited to structuring templates and contracts,
    - allowed to reuse any existing module in the repo,
    - NOT required to implement a complete visco-elastic model
      (creep/ritiro) from scratch.
  - Reductions of compressive strength due to long-term effects (creep) are
    NOT implemented unless the behaviour is already present in existing code
    and can be wrapped; otherwise they must be marked TODO.

- Strutture esistenti – livello locale vs globale:
  - The module operates ONLY at section/element level (local checks) for both
    new and existing structures.
  - Global assessment of entire structures (global safety indices, pushover,
    seismic demand vs capacity, vulnerability, etc.) is OUT OF SCOPE for this
    Plan and may be handled by other tools.
  - LC/FC, EC2 Annex I and prEN 1990-2 are used here ONLY to:
    - adjust material parameters and safety factors,
    - document the assessment scenario for local section checks.

- Instabilità, snellezza, II ordine:
  - Checks of global or local instability (slenderness limits, second-order
    effects, flexural-torsional buckling) are OUT OF SCOPE for this Plan,
    unless appropriate functions already exist in the workspace.
  - The verification module focuses on section resistance, not on stability
    analysis of members or frames.

- Presso-flessione deviata – domini:
  - The Plan MUST NOT invent new 2D/3D interaction domains for N–Mx–My.
  - Presso-flessione deviata is to be handled using ONLY the functions /
    methods already present in the workspace (for TA and SLU/SLE).
  - If no existing implementation is available, templates for deviated
    bending MUST be marked as partial or disabled.

- Taglio + torsione:
  - Combined shear–torsion checks MUST be implemented ONLY if:
    - a reliable implementation already exists, or
    - the normative method is clearly coded via dedicated templates and
      functions.
  - If not, taglio+torsione templates MUST be disabled or marked as partial
    with TODOs.

- Limiti minimi/massimi di armatura e spaziature:
  - Minimum/maximum reinforcement ratios and spacing rules MUST be applied
    ONLY to the extent that existing code or clear normative parameter data
    are available.
  - The Plan MUST NOT invent additional rules for minima or maxima; any new
    rule must be backed by a clear norm reference or left as TODO.

- Fessurazione – w_k:
  - For SLE fessurazione, the Plan MAY reuse existing code for crack control,
    but MUST NOT implement a full w_k-based durability check.
  - If no explicit crack width computation exists, the SLE module may be
    limited to stress checks (σ_c,max, σ_s,max) and clearly marked as such.

- Comportamento sismico (primario/secondario, gerarchie):
  - The Plan does NOT implement full seismic hierarchy of resistance,
    ductility classes, or capacity design rules (trave-colonna, shear
    overstrength, ecc.).
  - Section checks are performed “agnostically” with respect to the seismic
    role (primario/secondario) of the member, unless existing code already
    handles specific cases.

- EC2 Annex I – affidabilità:
  - EC2 Annex I is used ONLY to guide:
    - adjustment of material parameters,
    - adjustment of partial factors in assessment.
  - No probabilistic or advanced reliability methods are to be implemented
    within this Plan, unless pre-existing and easily wrapped.

- Sistema di unità:
  - The Plan MUST NOT invent or change unit systems.
  - It MUST use the same units and conventions already used by the existing
    workspace (e.g. mm, MPa, kN).
  - Any conversion MUST use existing helpers; no ad-hoc conversions.

- Tipologie di sezione:
  - The verification module MUST handle ONLY the section types already
    defined and supported by the geometry repository (e.g. rettangolare,
    circolare, circolare cava, travi a T, ecc., se esistono).
  - The Plan MUST NOT introduce new section shapes beyond those already
    present in the geometry module.

==================================================
FUNCTIONAL SCOPE PER ELEMENTO (DATI & CHECK)
==================================================
Each GUI row represents a structural element:

- Checks:
  - flessione semplice,
  - flessione deviata (nei limiti sopra),
  - presso/tenso-flessione semplice/deviata,
  - compressione / trazione,
  - taglio,
  - torsione,
  - taglio + torsione (se disponibile),
  - minimi di armatura a flessione,
  - minimi di armatura a taglio,
  - tensioni di esercizio (SLE),
  - verifiche TA,
  - verifiche SLU/SLC/SLE,
  - fessurazione strutturale (SLE),
  - deformazioni ammissibili (nei limiti dichiarati).

- GUI inputs:
  - Nome elemento (stringa).
  - Sezione (da repository).
  - Materiale (da repository).
  - Normativa.
  - N, Tx, Ty, Mx, My, Mz.
  - As, As', d, d', staffe (diametro, bracci, passo), area ferri piegati.

==================================================
REAL-TIME ROW VERIFICATION & BULK RECALC
==================================================
- Real-time per row:
  - On row edit finished:
    - controller builds CalcInput via repositories,
    - calls validate_calc_input,
    - if errors: NO verification, row marked with errors,
    - if ok: calls run_verifications_for_element and updates row.

- Bulk (“Ricalcola tutto”):
  - iterates rows,
  - builds CalcInput,
  - calls run_verifications_for_all,
  - updates all rows.

- Core remains synchronous & pure; GUI may run these functions in a background
  thread to avoid freeze.

==================================================
STRICT USE OF REPOSITORIES IN CONTROLLERS
==================================================
- GUI:
  - passes only IDs and numeric values:
    - section_id, material_id,
    - N, M, T, As, As', d, d', staffe, LC, FC, ecc.
  - DOES NOT compute or cache geometry/material properties.

- Controller:
  - receives section_repository, material_repository,
  - resolves section/material via get_section_by_id/get_material_by_id,
  - attaches them to CalcInput.section/CalcInput.material,
  - NEVER:
    - recomputes b, h, area, inertia,
    - recalculates f_ck, f_yk, E_c, E_s,
    - parses GUI labels.

==================================================
CORE CONTRACTS: CalcInput, CalcOutput, SingleCheckResult
==================================================
You MUST define/maintain these core contracts in a GUI-free module.

CalcInput (minimum fields):
- element_name: str
- section: SectionLike
- material: MaterialLike
- norm_code: str
- limit_states_enabled: list[str]
- lc: str | None
- fc: float | None
- N, Mx, My, Tx, Ty, Mz: float | None
- As, As_prime: float | None
- d, d_prime: float | None
- staffe_diametro: float | None
- staffe_num_bracci: int | None
- staffe_passo: float | None
- area_ferri_piegati: float | None
- extra: dict[str, Any]

SingleCheckResult:
- template_id: str
- ok: bool
- utilisation: float | None
- details: dict[str, float | str]
- norm_references: list[NormReference]
- messages_it: list[str]
- check_category: str | None
- limit_state: str | None

CalcOutput:
- element_name: str
- norm_code: str
- ok: bool
- per_template_results: dict[str, SingleCheckResult]
- validation_result: ValidationResult | None
- summary_metrics: dict[str, float | bool | str]

==================================================
NORMREFERENCE & VERIFICATIONTEMPLATE
==================================================
NormReference (dataclass):
- norm_code: str
- chapter: str
- paragraph: str
- formula_label: str | None
- description_it: str
- notes_it: str | None
- source_type: str | None
- priority: int | None

VerificationTemplate (dataclass):
- template_id: str
- norm_code: str
- norm_version: str | None
- verification_type: str
- limit_state: str
- description_it: str
- check_category: str
- required_inputs: list[str]
- optional_inputs: list[str]
- output_metrics: list[str]
- primary_reference: NormReference | None
- secondary_references: list[NormReference]
- function_path: str
- can_batch: bool
- supports_real_time: bool
- applicable_section_types: list[str] | None
- applicable_material_tags: list[str] | None
- requires_existing_structure: bool
- extra_params: dict[str, Any]

For each norm, the set of VerificationTemplate instances MUST cover all
supported verification families (flessione, taglio, torsione, minimi, SLE,
TA, ecc.).

==================================================
VALIDATION ENGINE (CORE)
==================================================
Implement ValidationIssue / ValidationResult and validate_calc_input:

ValidationIssue:
- severity: "info" | "warning" | "error"
- field: str
- code: str
- message_it: str
- norm_reference: NormReference | None
- context: dict[str, Any]

ValidationResult:
- issues: list[ValidationIssue]
- has_errors: bool
- has_warnings: bool

validate_calc_input(calc_input, active_norm, templates) -> ValidationResult:
- checks:
  - geometric consistency (d, d', As, As', staffe, circular rebar layout),
  - material ranges (f_ck, f_yk, E_c, E_s),
  - LC/FC coherence (LC1–LC3, typical FC values),
  - norm-template compatibility (no TA templates under SLU-only norms, etc.).
- attaches NormReference where validation rule comes from norms.

If has_errors:
- run_verifications_for_element MUST NOT execute any template.

==================================================
VERIFICATION SERVICE (CORE)
==================================================
run_verifications_for_element(calc_input, active_norm, enabled_limit_states=None)
 -> CalcOutput

- Select templates from normative registry:
  - filter by limit_state, check_category, section/material type,
    requires_existing_structure, enabled_limit_states.
- Validate:
  - validation_result = validate_calc_input(...).
- If has_errors:
  - return CalcOutput(ok=False, empty per_template_results, status
    "NON_VERIFICATO_PER_ERRORI_INPUT").
- Else:
  - execute ALL selected templates (using function_path),
  - build SingleCheckResult for each,
  - aggregate:
    - global ok/non-ok,
    - max utilisation,
    - controlling template,
    - summary_metrics with "status", "utilizzazione_massima",
      "template_controllante", "warning_validazione" (if any).

run_verifications_for_all(calc_inputs, active_norm, enabled_limit_states=None)
 -> list[CalcOutput]

Both functions are pure core (no Tkinter; no direct file I/O outside logging).

==================================================
CIRCULAR REBAR HELPER (CORE + GUI)
==================================================
Implement in core:

CircularRebarLayout:
- n_bars: int
- bar_diameter: float
- bar_area: float
- bar_positions: list[tuple[float, float]]
- As_total: float
- x_g: float
- y_g: float
- notes_it: str

arrange_circular_rebars(section_geometry, n_bars, bar_diameter, cover,
                        inner_radius=None) -> CircularRebarLayout

- Use outer_radius (and inner_radius if hollow) from section_geometry.
- r_eff = outer_radius - cover - bar_diameter/2.
- theta_k = 2πk/n_bars; compute positions, As_total, centroid.
- Pure core, no GUI, no files, no normative checks.

GUI dialog “Disposizione automatica armature circolari” MUST:
- use section_id → section_repository → CircularSectionLike,
- get n_bars, bar_diameter, cover, inner_radius,
- call arrange_circular_rebars,
- show As_total, x_g, y_g, optional list of (x,y),
- on “Applica alla riga”:
  - update As (and other fields as appropriate),
  - store bar_positions and centroid in a way that controllers can put
    them into CalcInput.extra.

Validation Engine MUST ensure that the generated layout is geometrically valid.

==================================================
CALIBRATION & BENCHMARK MODULE (CORE + GUI)
==================================================
Core:
- define CalibrationCase, CalibrationMismatch, CalibrationResult.
- implement:
  - run_calibration_case(calc_input, expected_output, active_norm, tolerance),
  - save_calibration_case(),
  - load_calibration_cases(),
  - generate_pytest_code_for_case().

GUI panel “Modulo di Calibratura / Verifica Dinamica” MUST:
- allow user to:
  - input CalcInput fields,
  - specify expected metrics (utilisations, σ_c, σ_s, M_Rd, V_Rd, x_neutro, ecc.),
  - configure tolerance,
- show:
  - comparison expected vs actual per template,
  - mismatches with Italian messages and NormReference,
- allow:
  - saving the case,
  - generating pytest-like code (as text).

Calibration MUST NOT adjust calculation methods to fit expected data; tests
must fail if behaviour changes unexpectedly.

==================================================
GUI MODULES / PANELS
==================================================
Without redesigning the whole GUI:

- Main Verification Panel:
  - per-row inputs, real-time checks, “Ricalcola tutto”.
  - sorting/filtering (if present),
  - keyboard navigation (Tab, Enter, frecce).

- Pannello normative:
  - list of norms with status and scope,
  - details and references (NormReference),
  - “Imposta come normativa attiva”.

- Dialogo LC/FC:
  - only for existing materials,
  - selection LC1–LC3, FC,
  - Italian help with references.

- Dialogo confronto scenari:
  - compare different norms/LC/FC scenarios for same CalcInput.

- Report di verifica:
  - structured summary of:
    - input,
    - key intermediate values (asse neutro, R_d, σ_c, σ_s),
    - utilisation per template,
    - normative references.

- Browser riferimenti normativi (facoltativo ma utile):
  - explora NormReference e NormParameters caricati da JSON/CSV.

- Pannello pre-dimensionamento:
  - helper functions for preliminary sizing,
  - ALWAYS labelled as “pre-dimensionamento, non sostituisce verifiche normative”.

- Modulo di calibratura:
  - as described in calibration section.

==================================================
THREADING, ERROR HANDLING & LOGGING
==================================================
- Core (validation, verification, helpers, calibration):
  - synchronous, deterministic,
  - no threads or GUI dependencies.

- GUI:
  - decides if/when to run core in a worker thread.

- Errors:
  - Programmer errors → exceptions + logging (ERROR).
  - User input/config issues → ValidationIssue & ValidationResult.
  - User messages MUST come from:
    - ValidationIssue.message_it,
    - SingleCheckResult.messages_it.

- Logging:
  - log inputs, validation, executed templates, intermediate results,
    normative references, and calibration outcomes.

==================================================
TESTS, LINTING & FINAL CHECK
==================================================
- Implement/extend pytest tests:
  - unit:
    - validation engine (geometry, materials, LC/FC),
    - TA checks (RD 2229, DM92/96),
    - SLU/SLE checks (NTC 2008/2018),
    - circular helper,
    - calibration mismatches.
  - integration:
    - pipeline CalcInput → validate → verify → CalcOutput.

- Run `pytest -q` at the end; all tests MUST pass.
- Run lint/format (Black/Ruff or repo tools) ONLY on modified files.
- Manually verify:
  - `python -m app.main` starts GUI,
  - per-row real-time verification works,
  - “Ricalcola tutto” works,
  - normative, LC/FC, scenario, report, helper, calibration panels open
    and work without breaking existing workflows.

==================================================
NO-SHORTCUT, NO-INVENTION POLICY (ABSOLUTE)
==================================================
You MUST NOT:
- invent new formulas,
- alter normative procedures arbitrarily,
- implement “simplified” or heuristic checks without explicit TODO and
  explanation,
- omit checks required by a norm when a template claims to implement them,
- compute geometry or material parameters in GUI/controllers,
- bypass repositories or normative registry,
- silently change behaviour to fit calibration cases.

Any uncertainty or missing normative detail MUST be:
- explicitly marked with a TODO in Italian,
- NEVER resolved by guessing.

END OF SINGLE, INTEGRATED PLAN PROMPT
