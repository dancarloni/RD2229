You are GitHub Copilot (Plan) working on my Python/Tkinter structural engineering app.

ROLE & SESSION CONSTRAINTS

- You act as a experienced and cautious senior developer for a civil/structural
  engineering tool.
- This Plan must be completed within a SINGLE Copilot Plan session:
  - Do NOT start secondary plans or sub-sessions.
  - Do NOT perform trivial, mechanical tasks that waste premium capacity
    (e.g. reformatting the entire repo, mass renaming without necessity,
    adding boilerplate everywhere).
- You MUST infer:
  - file paths,
  - module names,
  - package structure
  directly from the workspace by scanning the repo. Do NOT ask me for paths unless
  it is absolutely impossible to infer them from the codebase.
- You may ask follow-up questions ONLY when strictly necessary and in a compact way,
  within this single Plan session.

HOW TO READ THIS SPEC

- These instructions are stored in a file inside the repository (e.g. docs/copilot_plan.md).
- Treat this file as the authoritative source of requirements for this Plan.
- Do NOT assume examples of paths or names are correct; always confirm by scanning the
  actual workspace structure.

UI LANGUAGE REQUIREMENT

- ALL user-facing interface text MUST be in Italian, including:
  - window titles,
  - labels,
  - buttons,
  - tooltips,
  - table headers,
  - error/warning/info messages,
  - status bar texts,
  - menu items.
- Internal code (function names, variables, comments, docstrings) can remain in English,
  but any text shown to the user must be Italian.

GLOBAL PRINCIPLES

- Respect existing architecture and separation of concerns:
  - GUI (Tkinter) separated from core calculations.
  - Geometry module and material module are already correct and must not be changed
    except for essential wiring.
- Many calculation codes already exist in the workspace, especially for:
  - verifiche a tensioni ammissibili,
  - NTC 2008,
  - NTC 2018.
  Your job is to REUSE these implementations and, if needed, refactor them minimally
  for better modularity, NOT to re-implement them from scratch.
- NEVER invent structural rules or normative values:
  - If a normative detail is ambiguous, mark it clearly with a TODO and a short
    explanation in comments/docstrings.
  - Prefer asking me a targeted clarification rather than guessing.

========================================
GOAL
========================================

1) Restore full functionality of the existing workspace after a refactor and heavy
   linting that currently prevent the software from starting.
2) Recreate and properly rewire the “verification module” so that:
   - the GUI behaves as originally designed,
   - all existing checks run correctly,
   - each row/element is verified in REAL TIME as soon as data entry for that row
     is completed.
3) Keep public APIs stable as much as possible and avoid breaking existing tests.
4) Introduce a small, well-scoped extension for **existing materials**:
   - add LC/FC management for existing materials (NTC 2008, NTC 2018, EC2 Annex I,
     prEN 1990-2, in line with their role for existing structures),
   - restrict LC/FC to materials classified as “existing”,
   - ensure materials classified as “new” do NOT expose LC/FC settings.
5) Design and, where minimal changes suffice, implement **ultra-modular normative
   configuration modules** (core + GUI + JSON/CSV “database”) to manage parameters
   and coefficients for:
   - RD 2229/39 (tensioni ammissibili storico),
   - DM 1992 (TA), DM 1996 (TA),
   - NTC 2008,
   - NTC 2018,
   - EC2 (second generation, Annex I for existing structures),
   - future norms via plug-in-like modules.
6) Ensure that every important module (verification, normative configuration, LC/FC,
   scenario comparison, reports, helpers) has a corresponding GUI entry point
   (button/menu/dialog) reachable from the existing interface, with minimal and
   non-disruptive changes.
7) At the end of the Plan:
   - run the repository’s linting/formatting tools on the modified files,
   - verify that the program starts and main workflows function correctly and fully,
   - run and pass the entire pytest suite, including new granular tests.

========================================
CONTEXT & REPO (TO BE INFERRED FROM WORKSPACE)
========================================

- Language: Python 3.x
- GUI: Tkinter
- Domain: civil/structural engineering (sections, materials, checks TA/SLU/SLE).
- Repository:
  - You MUST discover real paths by scanning the workspace.
  - Example structure (DO NOT assume blindly; confirm by scanning):
    - app/main or similar entry point for `python -m app.main`
    - core modules under something like app/core/
    - GUI modules under something like app/gui/
    - geometry and materials modules in core
    - verification logic somewhere in core (may have been refactored)
    - tests under tests/
    - normative data JSON/CSV in a data/ or resources/ folder.
- Existing calculation code:
  - Already implements:
    - tensioni ammissibili,
    - NTC 2008,
    - NTC 2018 checks (at least partially).
  - Your tasks:
    - map these implementations,
    - centralise shared normative parameters where appropriate,
    - avoid duplication.

========================================
FUNCTIONAL SCOPE OF VERIFICATION
========================================

The verification engine must support, per structural element:

- flessione semplice
- flessione deviata
- presso/tenso-flessione semplice
- presso/tenso-flessione deviata
- compressione / trazione
- taglio
- torsione
- taglio + torsione
- minimi di armatura a flessione
- minimi di armatura a taglio
- tensioni di esercizio
- verifiche a tensioni ammissibili
- verifiche a stato limite ultimo
- verifiche a stato limite di collasso
- apertura delle fessure / fessurazione
- stato limite di operatività
- deformazioni ammissibili

For each structural element, the GUI must allow efficient input (with existing
automation where available) for at least:

- Nome dell’elemento (input diretto).
- Sezione: selezione da repository sezioni (geometry module).
- Materiale: selezione da repository materiali (material module).
- Normativa applicata: selezione da archivio normative (structured via modules).
- Azioni interne: N, Tx, Ty, Mx, My, Mz.
- Armature:
  - As, As' (input diretto o helper già presente).
  - d, d' (altezze utili dal lembo superiore, con controlli di compatibilità
    geometrica rispetto alla sezione scelta).
  - Diametro staffe, numero di bracci, passo staffe.
  - Area ferri piegati (helper o input diretto, rispettando limitazioni RD 2229/39
    e altre norme).

All these user-facing fields, labels, buttons, tooltips, and messages MUST be in
Italian (“Nome elemento”, “Sezione”, “Materiale”, “Normativa”, “Azioni interne”,
“Ricalcola tutto”, etc.).

COMPLETENESS OF CHECKS PER NORM

- For each supported norm (RD 2229/39, DM 1992, DM 1996, NTC 2008, NTC 2018, EC2, etc.)
  the implementation of checks MUST be complete with respect to that norm, within the
  scope of this software. In particular:
  - When a norm is selected as “active” (e.g. NTC 2018), all core verification types
    relevant to that norm MUST be fully implemented (not partially), including at least:
    - flessione (semplice e deviata, presso/tenso-flessione),
    - taglio,
    - torsione,
    - combinazioni taglio + torsione, dove richiesto,
    - verifiche delle tensioni (tensioni di esercizio / stati limite di esercizio),
    - minimi di armatura (a flessione e a taglio),
    - ulteriori stati limite specifici della norma (SLU, SLC, SLE, operatività,
      deformazioni ammissibili), per quanto rientra nell’ambito del software.
  - “Complete” means:
    - the check must follow the normative method and its main conditions/limitations,
    - the code must not arbitrarily omit parts of the procedure required by the norm
      (e.g. shear/torsion interaction, minimum reinforcement rules, stress limits),
    - approximations or simplifications must be clearly documented and justified.
- When a verification is not yet fully implemented for a given norm:
  - the software must:
    - either disable that specific check for that norm (with a clear Italian message
      to the user explaining that the check is not yet available),
    - or include explicit TODOs in the code with comments explaining what part of the
      normative method is still missing.
  - Under no circumstances should the software silently perform a partial or incomplete
    check while presenting it as “full” compliance with the norm.
- The set of VerificationTemplate objects for each norm must reflect this completeness
  requirement:
  - for example, if a norm prescribes:
    - a bending verification,
    - shear and torsion checks,
    - minimum reinforcement checks,
    then the normative registry for that norm must expose templates covering ALL of
    these families, not just a subset.

REAL-TIME PER-ROW VERIFICATION + BULK RECALC

- For each row in the GUI table representing a structural element:
  - As soon as data entry for that row is completed (e.g. focus leaves the row,
    or the user confirms with Enter/Tab on the last field), the app MUST:
    - validate the row data,
    - build a CalcInput-like structure,
    - call the verification core,
    - update the results fields (tassi di utilizzo, esito verifica, ecc.) for that row.
- There MUST also be:
  - a “Ricalcola tutto” (bulk recalc) button that:
    - re-runs verification for all current rows/elements,
    - useful after changes to global normative settings or material definitions.
- Real-time per-row verification must:
  - NOT freeze the GUI,
  - reuse existing threading/async patterns if present,
  - avoid redundant recalculations (e.g. reusing cached sectional properties).

========================================
GRAPHICAL MODULES / UI PANELS TO PROVIDE
========================================

Without redesigning the entire GUI, introduce or complete the following GUI modules
(panels/dialogs), all with Italian labels and texts, and reachable via buttons or
menu entries placed where logically appropriate:

1) Main Verification Panel (existing, to be fixed/enhanced)
   - A table or grid where each row corresponds to a structural element.
   - Fields: nome elemento, sezione, materiale, normative, azioni interne (N, Tx, Ty,
     Mx, My, Mz), armature (As, As', d, d', staffe, ferri piegati), esito verifica,
     tassi di utilizzo.
   - Features:
     - real-time per-row verification after data entry completion,
     - a “Ricalcola tutto” button to run all checks in bulk,
     - keyboard navigation (Tab, Enter, arrows),
     - sorting/filtering where already supported.
   - All column headers and buttons in Italian (e.g. “Ricalcola tutto”, “Verifica”).

2) Normative Configuration Panel (“Pannello normative”)
   - Implementation hint (GUI module):
     - Create a dedicated Tkinter module for this panel, e.g. something like:
       - app/gui/normative_panel.py (actual path/name MUST be inferred from workspace).
     - Implement a class similar to:
       - class NormativeConfigPanel(tk.Toplevel) or class NormativeConfigFrame(ttk.Frame)
         depending on existing patterns.
   - Responsibilities:
     - Display the list of available norms from the core normative registry:
       - es. RD 2229/39, DM 14/02/1992, DM 9/1/1996, NTC 2008, NTC 2018, EC2, etc.
     - Allow the user to:
       - select the active norm for verification,
       - inspect high-level properties and parameters of each norm,
       - see applicable scope (nuova costruzione / esistente),
       - see at a glance the key normative references (capitoli, paragrafi).
     - Provide contextual help and tooltips with:
       - Norma, capitolo, paragrafo, formula, where known.
   - Suggested widget layout (all labels and strings in Italian):
     - A list or tree on the left:
       - columns or fields:
         - "Norma" (e.g. "NTC 2018", "RD 2229/39"),
         - "Versione",
         - "Stato" (es. "vigente", "sostituita", "bozza"),
         - "Ambito" (es. "nuove opere", "opere esistenti").
     - A details panel on the right with:
       - a header label: "Dettagli normativa selezionata",
       - a read-only text area or form showing:
         - descrizione sintetica,
         - principali tipi di verifiche supportate (SLU, SLE, TA),
         - parametri chiave (es. fattori parziali, limiti di tensione, LC/FC).
       - a specific sub-section for normative references:
         - labels like:
           - "Capitolo:",
           - "Paragrafo:",
           - "Formula di riferimento:".
     - A row of buttons at the bottom, for example:
       - "Imposta come normativa attiva" (set as active norm),
       - "Aggiorna" (if required),
       - "Chiudi".
     - A small help button (e.g. with a "?" icon) that opens:
       - a help dialog “Guida normativa”, with:
         - una breve spiegazione del ruolo delle norme,
         - elenco dei riferimenti principali (Norma, capitolo, paragrafo, formula)
           per l’uso nel software.
   - Tooltips & help (in Italian, using the global HELP & TOOLTIP REQUIREMENTS):
     - Each row in the list/tree of norms should have a tooltip summarising:
       - "Norma: …, Capitolo principale: …, Ambito: …".
     - In the details panel, key labels (es. “Stati limite”, “Tensioni ammissibili”,
       “Livelli di conoscenza”) should have tooltips like:
       - "Riferimento: NTC 2018, Cap. 8, § C8.5.4 (LC/FC)."
       - "Riferimento: RD 2229/39, Cap. II, formula σ = M/W."
     - The help dialog content should be constructed from metadata provided by
       the normative registry, not hard-coded everywhere.
   - Core integration:
     - The panel must interact with the core normative registry, via functions like:
       - list_available_norms() → list of NormRecord / NormPlugin
       - get_norm(code, version=None) → NormPlugin / NormParameters
     - NormRecord / NormPlugin should include:
       - code (e.g. "NTC 2018"),
       - version (e.g. "2018-01-17"),
       - status ("current", "replaced", "draft"),
       - scope_existing (bool),
       - core_topics (e.g. ["SLU", "SLE", "TA"]),
       - a list of NormReference objects, each with:
         - norm_code,
         - chapter,
         - paragraph,
         - formula_label or a short formula string,
         - a short Italian description for tooltips/help.
     - The panel must:
       - retrieve this metadata from the core,
       - show it in the GUI,
       - use it to build tooltips and help texts without duplicating logic.
   - Events and state:
     - When the user selects a norm and clicks "Imposta come normativa attiva":
       - the panel should call a core function to set the active norm (e.g.
         normative_registry.set_active_norm(code, version)).
       - optionally, update a status bar or label in the main window with an
         Italian message, e.g.:
         - "Normativa attiva: NTC 2018 (opere nuove)", or
         - "Normativa attiva: NTC 2018 – Valutazione opere esistenti".
     - The currently active norm should be highlighted in the list/tree.
   - Coding style:
     - Keep the class relatively thin:
       - GUI-only responsibilities,
       - no direct calculation inside the panel class.
     - Delegate:
       - data loading and normative metadata to core services,
       - any long-running operation (if any) via existing threading patterns.
     - Docstrings in Google style for the main class and methods.
     - All user-facing text strictly in Italian.

3) Existing Material LC/FC Dialog (“Livelli di conoscenza e fattori di confidenza”)
   - A dialog attached to the material selection flow, only active for materials
     flagged as “esistenti”.
   - Allows selection of:
     - Livello di conoscenza (LC1–LC3),
     - Fattore di confidenza (FC tipici 1.35 / 1.20 / 1.00 per NTC2018).
   - Shows brief Italian descriptions and references (short text, no full norm copy).
   - Updates the core LC/FC configuration for the selected existing material.

4) Scenario Comparison Dialog (“Confronto scenari normativi”)
   - A dialog that:
     - allows selection of one or more scenarios (norma + LC/FC),
     - shows, for a chosen element/row:
       - utilisation ratios,
       - safety factors,
       - key result indicators for each scenario.
   - Uses the scenario comparison functions in the core.
   - Useful to compare TA (RD2229/Santarella/Giangreco) vs SLU/SLE (NTC2008/2018/EC2).

5) Report Viewer Panel (“Report di verifica”)
   - A panel or dialog that displays:
     - a structured, human-readable summary of:
       - input data,
       - main intermediate results (es. posizione asse neutro),
       - final results and utilisation ratios,
       - normative references (e.g. “NTC 2018, Cap. 4, §x.x” where available).
   - Driven by the “report object” emitted by core helpers.
   - Initially can be a simple text/Markdown-like view.

6) Normative Data Browser (“Riferimenti normativi”)
   - Optional but recommended small panel/dialog that:
     - lists available norms and their metadata (status, scope, link info),
     - reads from the comparative JSON (e.g. comparativa_norme_esistente.json).
   - Provides quick access to see which norms are applicable to existing structures.

7) Preliminary Design Helpers Panel (“Strumenti di pre-dimensionamento”)
   - A panel or dialog that:
     - lets the user run helper functions for preliminary sizing (As, As', staffe),
       clearly labelled as “strumenti di pre-dimensionamento (non sostituiscono le
       verifiche normative)”.
   - Uses dedicated core helper functions.
   - Always logs in detail that these are suggestions, not checks.

For each of these modules:

- Use Italian texts for any label/title/button/menu string.
- Integrate them into existing menus/toolbars logically (e.g. a menu “Verifiche”,
  “Normative”, “Strumenti”).
- Do NOT break existing, working GUI parts; only extend/wire where necessary.

HELP & TOOLTIP REQUIREMENTS

- All help and tooltip texts shown in the GUI MUST be in Italian.
- For every verification-related field, result, or setting, tooltips/help texts SHOULD,
  whenever reasonably known, explicitly include:
  - the normative reference code (e.g. "RD 2229/39", "DM 14/02/1992", "DM 9/1/1996",
    "NTC 2008", "NTC 2018", "EN 1992-1-1:2023", "prEN 1990-2"),
  - the chapter and/or section (e.g. "Cap. 4", "Cap. 8", "§ 4.1.2.3"),
  - the paragraph or clause identifier, if available (e.g. "§ C8.5.4"),
  - the formula label or a short symbolic representation (e.g. "σ = M/W", "MRd = ...").
- Examples of tooltip/help content (in Italian):
  - "Limite di tensione di esercizio secondo NTC 2018, Cap. 4, § 4.x.x (formula σ_c,max)."
  - "Verifica a flessione con metodo alle tensioni ammissibili, RD 2229/39, Cap. II,
     formula σ = M/W (diagramma elastico)."
  - "Fattore di confidenza FC per opere esistenti secondo NTC 2018, Cap. 8, § C8.5.4."
- When the precise paragraph or formula is not currently known:
  - include a TODO in the code with a short explanation,
  - provide a generic but still normative-aware tooltip, e.g.:
    - "Riferimento normativo da dettagliare (TODO: indicare paragrafo/formula esatta)."
- Help buttons ("?") should open small dialogs in Italian that:
  - show a short textual explanation of the related parameter or check,
  - list the normative references used (Norma, capitolo, paragrafo, formula),
  - optionally include a brief note on the engineer’s responsibility to verify
    coherence with the latest normative text.
- The normative configuration and verification templates in the core should expose
  enough metadata (e.g. NormReference objects) to allow the GUI to build these
  tooltips/help texts dynamically.

========================================
TASKS (WHAT YOU MUST DO IN THIS SINGLE PLAN)
========================================

1) CODE MAP & DIAGNOSIS (LIGHTWEIGHT, NO BUSYWORK)

- Scan the workspace (ignoring .venv, .cache, build output) to identify:
  - the true entry point used for `python -m app.main` (or equivalent),
  - separation between GUI modules and core calculation modules,
  - geometry and material repositories, and where their public APIs are defined,
  - existing verification logic (tensioni ammissibili, NTC 2008, NTC 2018).
- Detect the reasons why the app no longer starts:
  - broken imports,
  - moved/renamed modules,
  - signature mismatches,
  - missing symbols.
- Produce a concise internal map (e.g. small markdown note or docstring in the main
  module) describing:
  - how the main GUI is started,
  - how verification is triggered (pipeline input → core → output),
  - which modules implement the values for TA, NTC2008, NTC2018.

1) RESTORE STARTUP (`python -m app.main`)

- Apply the MINIMAL changes required so that:
  - `python -m app.main` runs successfully and opens the GUI.
- Constraints:
  - Do NOT reformat the entire codebase; only touch the necessary lines.
  - Do NOT break existing imports that are still valid.
  - Preserve logging:
    - Python `logging` with size-based rotation.
    - DEBUG togglable via config/env if already supported.
  - Keep public APIs stable wherever possible; if a change is unavoidable:
    - add a small compatibility wrapper,
    - document it.

1) RECREATE / FIX THE VERIFICATION MODULE

- Reconnect the existing calculation code (TA, NTC2008, NTC2018) into a coherent
  verification service, with strict separation:
  - Core layer: pure Python functions/classes, no Tkinter.
  - GUI layer: Tkinter controllers/wiring only; they:
    - collect and validate user input,
    - build input structures (e.g. CalcInput dataclasses),
    - call the core verification service,
    - display CalcOutput (tassi di utilizzo, asse neutro, ecc.).
- Reuse as much of the existing code as possible:
  - If an old verification module still exists but is broken:
    - fix imports and wiring instead of rewriting it.
  - If it has been split or refactored:
    - centralise shared parts into a service module (e.g. under a core/services-like
      package) while preserving public behaviour.
- Ensure for each element/row:
  - verification is executed immediately after its data entry is complete (real-time),
  - bulk recalculation is available via a dedicated button (“Ricalcola tutto”).
- Optimise calculations:
  - avoid duplicate work,
  - reuse intermediate results (e.g. sectional properties, transformation matrices),
  - keep core functions pure; side effects are isolated.

1) CHECK AND REPAIR GUI WIRING (INCL. REAL-TIME & BULK BUTTON)

- Without redesigning the GUI:
  - Ensure input fields/combos/tables are correctly bound to:
    - section repository (geometry),
    - material repository (materials),
    - normative repository (to be created/refined).
  - Implement or fix:
    - row-level event handling (e.g. “editing finished” on a row) that:
      - triggers validation,
      - calls the verification service for that row.
    - a “Ricalcola tutto” button:
      - placed in a logical position in the existing interface (toolbar, panel, etc.),
      - wired to a bulk verification routine.
- Preserve:
  - existing layout and responsiveness,
  - sorting/filtering capabilities in tables,
  - keyboard navigation (Tab/Enter/Arrows),
  - tooltips and helpers already implemented.
- Only modify controllers and bindings where necessary.
- For every new core feature (normative configuration panels, scenario comparison,
  report viewers, helpers):
  - create a minimal GUI entry point (button/menu/dialog) with Italian labels,
    integrated into the existing UI without disruptive redesign.

1) EXTEND MATERIAL MODULE FOR EXISTING STRUCTURES (LC/FC)

- The material module is already correct and must NOT be rewritten.
- Add only a small, clearly scoped extension:
  - new pure functions and/or a small helper class that:
    - distinguish between “new” and “existing” materials,
    - for existing materials:
      - handle Livelli di Conoscenza (LC1–LC3),
      - handle Fattori di Confidenza (FC, e.g. 1.35 / 1.20 / 1.00 in NTC 2018),
      - adjust effective design values according to the selected norm and LC/FC.
- Behaviour:
  - For materials classified as “new”:
    - do NOT expose LC/FC in the UI,
    - do NOT alter current behaviour.
  - For materials classified as “existing”:
    - integrate LC/FC selection in the existing material selection flow (GUI),
    - compute adjusted properties in the core using:
      - NTC 2008 and NTC 2018 (Cap. 8: LC/FC),
      - EC2 EN 1992-1-1:2023 Annex I (assessment of existing structures – materials,
        uncertainty, in-situ tests),
      - prEN 1990-2 (assessment principles for existing structures), where applicable.
- Implementation:
  - Load normative meta-data from JSON (e.g. comparativa_norme_esistente.json or
    similar, discovered by scanning the repo).
  - Keep new functions pure (no Tkinter, no direct file I/O inside them).
  - Use a small loader/helper to read the JSON/CSV centrally.
- Add a small GUI panel or dialog (launched from the material selection area) for:
  - configuring LC/FC for existing materials,
  - visualising normative references (short textual hints, not full documents).

1) ULTRA-MODULAR NORMATIVE CONFIGURATION MODULES (CORE + GUI)

- Design and implement (where changes are minimal but useful) a modular structure
  for normative parameters and coefficients (normative registry, templates, validation,
  scenario comparison, report objects, helpers), as already detailed above.
- All new GUI elements must:
  - use Italian labels and texts,
  - be integrated with minimal changes to existing GUI modules.

1) LOGGING & TRACEABILITY

- Ensure verification services provide detailed logging:
  - Inputs:
    - geometry, materials, internal forces (N, Tx, Ty, Mx, My, Mz),
    - reinforcement (As, As', d, d', staffe, ferri piegati),
    - selected norm, LC/FC if applicable.
  - Intermediate results:
    - posizione asse neutro,
    - internal stress distributions,
    - design resistance values,
    - partial safety factors and utilisation ratios.
  - Normative references:
    - clearly state which norm and (if known) which clause or section motivated
      a particular coefficient or check (e.g. “NTC 2018 §C8.5.4, FC=1.20”).
- Keep logging:
  - using Python logging with rotating file handler (size-based),
  - with DEBUG togglable via configuration; INFO as the default.

1) TESTS & QUALITY (INCLUDING GRANULAR TESTS BY NORM)

- Add or update pytest tests, with particular attention to **granularity** and
  alignment with different normative families:

  8.1 Granular Tests for RD 2229/39 (Tensioni Ammissibili Storiche)
  - Unit tests that:
    - verify allowable stress checks in bending and shear for concrete,
      against the configured RD2229 limit values (no normative text replication,
      just correctness vs configured parameters).
    - test minimum reinforcement checks where implemented (bending and shear).
    - cover edge cases:
      - stress just below the allowable limit,
      - stress just above the allowable limit.

  8.2 Granular Tests for TA Methods (Santarella, Giangreco, DM 14/02/1992, DM 9/1/1996)
  - Unit tests for the TA implementation based on:
    - classical linear-elastic assumptions for concrete and steel,
    - stress distributions compatible with Santarella/Giangreco formulations.
  - Map tests to:
    - DM 14/02/1992 and DM 9/1/1996 rules where they remain applicable for TA,
      without copying normative text but ensuring:
      - allowable stress definitions are respected,
      - time-dependent effects (viscosità, ritiro, etc.) are recognised where
        already implemented.
  - Cover:
    - flexure,
    - combined N + M,
    - simple shear,
    - a representative service stress case (tensioni di esercizio TA).

  8.3 Granular Tests for NTC 2008 and NTC 2018 (SLU/SLE)
  - Unit tests for:
    - SLU bending checks under NTC 2008 and NTC 2018,
    - shear and torsion in SLU for at least one representative section,
    - SLE checks for stress limitations (σ_c,max, σ_s,max).
  - Integration tests that:
    - exercise the full path:
      - build CalcInput,
      - run verification,
      - inspect CalcOutput for utilisation ratios and classification (OK/NON OK).
  - Add “comparison tests” where:
    - the same section is checked:
      - with TA (RD2229/Santarella/Giangreco),
      - with SLU/SLE under NTC 2008/2018.
    - tests assert:
      - coherent ordering of safety (SLU typically more demanding than TA),
      - internal consistency of the implementation.

  8.4 Scenario Comparison & LC/FC Tests
  - Tests that:
    - for a given existing element:
      - run verification with LC1, LC2, LC3 (NTC 2008/2018),
      - confirm the expected ordering of utilisation ratios (higher FC → more severe).
    - for the same element:
      - compare NTC 2008 vs NTC 2018 vs EC2 where coherent, ensuring that:
        - mapping of parameters is consistent,
        - differences are reflected in the results.

  8.5 Validation Engine Tests
  - Unit tests that:
    - assert correct detection of geometric inconsistencies (e.g. d > h of the
      section, reinforcement area exceeding feasible limits),
    - check that:
      - warnings vs errors are correctly classified,
      - GUI can consume these results via stable structures.

  8.6 End-to-End Test
  - An end-to-end integration test (without GUI if possible) that:
    - constructs a representative CalcInput using repositories,
    - calls the verification service,
    - asserts CalcOutput.ok and checks neutral axis position and utilisation ratios.

- Ensure:
  - `pytest -q` passes.
  - Formatting:
    - Black/Ruff (or repo tools) compliant,
    - no line > 100 chars,
    - no trailing whitespace.
  - NO network calls.

  ========================================
REFERENCE EXAMPLES & NUMERICAL BENCHMARK TESTS
========================================
To enforce correctness of the implementation and prevent shortcuts, you MUST anchor
the code to numerical benchmark examples derived from normative/technical references
and/or existing repository code.

A) Benchmark philosophy

- For each normative family:
  - RD 2229/39 + TA historical (including Santarella/Giangreco),
  - DM 14/02/1992, DM 9/1/1996 (TA),
  - NTC 2008,
  - NTC 2018,
  - EC2 (EN 1992-1-1:2023, Annex I where applicable),
  you MUST define and test a small set of “benchmark problems”:
  - representative sections (e.g. sezione rettangolare, trave T, pilastro),
  - typical reinforcement layouts (As, As', staffe),
  - representative load cases (N, M, T),
  - and expected utilisation/safety values, derived from:
    - hand-calculated examples,
    - existing validated code (e.g. previous RD2229 tensioni ammissibili project), [17](https://standards.globalspec.com/std/14656108/din-en-1990-2)
    - or authoritative technical examples where available.

B) Granular benchmark tests (per normative family)

- For RD 2229/39 and TA methods (Santarella, Giangreco, DM 1992/1996):
  - Create pytest tests that:
    - define 2–3 benchmark sections (e.g. trave a flessione semplice, sezione rettangolare),
    - apply bending, shear and combined actions,
    - compare:
      - computed stresses (σ, τ),
      - and ratios vs allowable stresses (σ_amm, τ_amm),
    against reference values:
      - either from existing validated code (if present in the repo),
      - or from manual calculations following RD2229 + Santarella/Giangreco style. [1](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2025-08/2025_2G-Eurocodes-Workshop_EN%201990-2_TPL_website.pdf)[14](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2025-08/2025_2G-Eurocodes-Workshop_EN1992_Final_website.pdf)[15](https://www.ivysci.com/en/articles/9793389__Assessment_of_existing_PC_structures_according_to_EN_1992112023)

- For NTC 2008 / NTC 2018:
  - Create benchmark tests that:
    - check SLU bending, shear, torsion on a set of typical sections,
    - check SLE stresses (σ_c,max, σ_s,max) and/or crack width/deformations where
      the code already implements such checks,
    - compare results (e.g. utilisation, γ_sicurezza) to:
      - the existing code’s known behaviour,
      - or numerical examples extracted from trusted technical material on NTC08/NTC18. [6](https://www.cpr-ingegneria.it/wp-content/uploads/2018/02/DM-17-01-2018-Testo-NTC-2018.pdf)[7](https://www.mauromalizia.it/wp-content/uploads/Norme-tecniche-costruzioni.pdf)[8](https://www.studiotecnicopagliai.it/regio-decreto-16-novembre-1939-n-2229/)[9](https://www.sttan.it/norme/Storiche/1939_11_10_RDL_n_2229_norme_CA.pdf)

- For EC2 (EN 1992-1-1:2023, Annex I) and prEN 1990-2 (existing structures):
  - As these may be newer and less fully integrated, focus on:
    - material assessment factors,
    - partial factor adjustments,
    - handling of uncertainty/dispersion,
  - Add benchmark tests based on:
    - simplified assessment examples where available,
    - consistent with EC2 Annex I principles. [10](https://www.tecnesconsult.it/wp-content/uploads/2022/11/DM-14-2-92.pdf)[18](https://www.marcodepisapia.com/tensioni-ammissibili-e-stato-limite-ultimo-sezioni-calcestruzzo-armato/)[12](https://www.airesingegneria.it/site/assets/files/1155/1996a_dm96_strutture.pdf)
  - If full numerical reference examples are not easily extractable:
    - implement only those aspects for which you can define controlled tests,
    - clearly mark TODO for other parts.

C) Behaviour when benchmarks cannot be fully defined

- If you cannot derive an unambiguous numerical benchmark for a given check:
  - DO NOT rely solely on “logic” tests (e.g. result > 0).
  - Instead:
    - implement minimal structure only (VerficationTemplate, plumbing),
    - mark the numerical core as TODO with comments explaining:
      - which norm,
      - which chapter/paragraph/formula are missing,
      - which type of example would be needed.
- In other words, absence of a reliable reference example is a reason to:
  - keep the implementation partial and clearly marked,
  - NOT to guess a formula or arbitrary expected result.

D) Regression tests to prevent silent changes

- Once benchmark tests are passing:
  - treat them as regression tests:
    - any change to the implementation that alters these results MUST be considered
      carefully and justified.
  - If you need to adjust an implementation due to a normative re-interpretation:
    - first, update or add benchmark tests with new reference values,
    - second, adjust the code,
    - third, document the rationale in CHANGELOG and comments, including normative
      references (NormReference).
``

1) FINAL LINTING & FUNCTIONAL VERIFICATION

- After all code changes and tests have been added:
  - Run the project’s standard formatting/linting tools:
    - Black/Ruff or repo-specific tools.
    - Prefer running them only on modified files or relevant packages to avoid
      unnecessary churn and premium usage.
  - Confirm that:
    - `python -m app.main` starts successfully,
    - main workflows are usable:
      - opening verification GUI,
      - inserting rows/elements,
      - triggering real-time per-row checks,
      - running bulk recalculation,
      - opening normative configuration / LC/FC / scenario comparison / report /
        helper GUIs where implemented.
  - If any issue is detected:
    - fix it with the smallest possible change,
    - update or add tests if necessary.

========================================
DELIVERABLES FROM THIS PLAN
========================================

1) Unified diffs (patch-style) for every changed file, with minimal file churn.
2) New/updated pytest tests (core + at least one integration test) including the
   granular tests described above.
3) Docstrings in Google style for public functions/classes, plus inline comments
   for non-trivial logic.
4) A concise CHANGELOG entry summarising:
   - restored startup,
   - restored verification workflow (including real-time per-row checks and bulk
     recalculation),
   - new LC/FC handling for existing materials,
   - normative configuration scaffolding (registry, templates, validation, scenarios,
     reports, helpers),
   - introduction of granular tests for RD2229/TA/Santarella/Giangreco and NTC 2008/2018.
5) Short migration notes (only if any public API behaviour changed) with:
   - what changed,
   - how to adapt.
6) Final recap (in the Plan result):
   - what changed,
   - which assumptions you made,
   - how to revert if needed.

========================================
INTERACTION & SAFETY
========================================

- Do NOT invent structural rules or normative values.
- If you are unsure about a normative choice:
  - clearly mark TODO,
  - explain the ambiguity in a short comment,
  - you may ask me a single, precise clarification within this Plan.
- Keep reasoning visible in:
  - comments,
  - docstrings,
  - test names and descriptions.

  ========================================
MODULE BOUNDARIES & DEPENDENCY DIRECTION
========================================
To preserve extreme modularity and avoid circular dependencies, you MUST respect
a clear layering of modules and dependency directions.

A) Layering (conceptual)

- From lowest to highest layers:
  1) Domain data & contracts:
     - geometry (sections),
     - materials,
     - CalcInput / CalcOutput,
     - NormReference,
     - VerificationTemplate,
     - ValidationIssue / ValidationResult.
  2) Normative registry & services:
     - NormPlugin implementations,
     - loaders for JSON/CSV normative data,
     - verification functions per norm (pure calculations).
  3) Orchestration services:
     - Validation Engine (validate_calc_input),
     - Verification Service (run_verifications_for_element / for_all).
  4) GUI layer (Tkinter):
     - views,
     - controllers,
     - dialogs/panels (normative panel, LC/FC dialog, scenario comparison, etc.).

B) Allowed dependencies (direction)

- geometry and materials:
  - MUST NOT depend on GUI, norms, validation or verification services.
- contracts (CalcInput, CalcOutput, NormReference, VerificationTemplate,
  ValidationIssue/Result):
  - MUST NOT depend on GUI or specific norm implementations.
- normative registry & services:
  - MAY depend on:
    - contracts,
    - geometry/materials ONLY via public APIs,
    - loaders for JSON/CSV,
  - MUST NOT depend on GUI.
- orchestration services (validation, verification):
  - MAY depend on:
    - contracts,
    - normative registry & services,
    - geometry/materials via contracts and public APIs,
  - MUST NOT depend directly on Tkinter.
- GUI:
  - MAY depend on any core module (read-only usage),
  - MUST NOT contain core business logic (no normative formulas, no heavy calculations).

C) Adapters (if needed)

- If existing code in geometry or materials uses older interfaces that do not fit
  CalcInput / CalcOutput perfectly, you MUST:
  - introduce small adapter functions in a dedicated adapter module (e.g. core.adapters),
  - NOT modify geometry/material modules except for strictly necessary wiring.
- These adapters:
  - convert from older internal representations to the new contracts,
  - keep the old code working while enabling modular evolution.

========================================
DATA LOADING & CACHING FOR JSON/CSV
========================================

To keep data access modular and testable, you MUST centralise JSON/CSV loading and
avoid scattered file reads across the codebase.

A) Central loader modules

- Introduce or refine loader modules in the core, for example:
  - app/core/norms/loader.py
  - app/core/data_loader.py
- These loaders are responsible for:
  - reading JSON/CSV files (UTF-8),
  - parsing them into:
    - NormReference instances,
    - NormParameters,
    - VerificationTemplate definitions,
  - handling file-not-found or parse errors gracefully.

B) API for loaders

- Provide clear, re-usable functions, e.g.:
  - load_norm_references() -> dict[str, list[NormReference]]
    - key: norm_code or some composite key.
  - load_norm_parameters() -> dict[str, NormParameters]
  - load_verification_templates() -> list[VerificationTemplate]

- All other modules (registry, verification, validation) MUST use these functions
  instead of reading files directly.

C) Caching strategy

- To avoid unnecessary repeated I/O:
  - implement in-memory caching in the loader modules:
    - on first call, read and parse JSON/CSV,
    - on subsequent calls, reuse the in-memory data.
- Caching MUST:
  - be thread-safe for read-only usage,
  - be transparent to callers (no need for them to manage lifecycle).
- If hot-reload of data files is needed in the future, you can add explicit
  “reload” functions, but do NOT introduce implicit magic reloads.

D) Testing loaders

- Add unit tests that:
  - load normative JSON/CSV from test fixtures,
  - verify:
    - correct creation of NormReference,
    - correct mapping into NormParameters and VerificationTemplate instances,
  - do NOT depend on GUI.

========================================
NORMATIVE COMPLIANCE & NO-SHORTCUT POLICY
========================================

This project is a professional civil/structural engineering tool. For all checks
(flessione, taglio, torsione, tensioni, minimi di armatura, SLU/SLE/SLC, etc.),
you MUST strictly respect the relevant normative methods (RD 2229/39, DM 14/02/1992,
DM 9/1/1996, NTC 2008, NTC 2018, EN 1992-1-1:2023, prEN 1990-2, etc.) and the
existing calculation code in the repository.

A) No invented formulas or methods

- You MUST NOT invent:
  - new formulas,
  - new factors,
  - new “simplified” procedures
for any verification, even if they look plausible.
- All formulas and methods MUST come from at least one of the following:
  1) Existing code in the repository (especially the current modules for:
     - RD 2229/39 tensioni ammissibili,
     - DM 1992 / DM 1996 TA,
     - NTC 2008,
     - NTC 2018).
  2) Authoritative normative sources or well-known technical literature, such as:
     - RD 16/11/1939 n. 2229 (“Norme per le opere in conglomerato cementizio”) [1](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2025-08/2025_2G-Eurocodes-Workshop_EN%201990-2_TPL_website.pdf)[2](https://www.en-standard.eu/din-en-1990-2-eurocode-grundlagen-der-planung-von-tragwerken-und-geotechnischen-bauwerken-teil-2-bewertung-von-bestandsbauten-deutsche-und-englische-fassung-pren-1990-2-2024/)
     - DM 14/02/1992 e DM 9/1/1996 per il metodo alle tensioni ammissibili [3](https://biblus.acca.it/download/norme-tecniche-per-le-costruzioni-2018-ntc-2018-pdf/)[4](http://www.calcoli-online.it/dimostrativo/cementoa/cementoa.htm)[5](https://books.google.com/books/about/Cemento_Armato_la_Tecnica_E_la_Statica.html?id=lzKF72lvFyMC)
     - NTC 2008 e NTC 2018 (e relative Circolari) [6](https://www.cpr-ingegneria.it/wp-content/uploads/2018/02/DM-17-01-2018-Testo-NTC-2018.pdf)[7](https://www.mauromalizia.it/wp-content/uploads/Norme-tecniche-costruzioni.pdf)[8](https://www.studiotecnicopagliai.it/regio-decreto-16-novembre-1939-n-2229/)[9](https://www.sttan.it/norme/Storiche/1939_11_10_RDL_n_2229_norme_CA.pdf)
     - EC2 EN 1992-1-1:2023 (in particolare Annex I per strutture esistenti) [10](https://www.tecnesconsult.it/wp-content/uploads/2022/11/DM-14-2-92.pdf)[11](https://www.dighe.eu/normativa/allegati/2008_D_Min_Infrastrutture_14-01-NTC.pdf)
     - prEN 1990-2 per la valutazione delle strutture esistenti [12](https://www.airesingegneria.it/site/assets/files/1155/1996a_dm96_strutture.pdf)[13](https://www.legislazionetecnica.it/54007/normativa-edilizia-appalti-professioni-tecniche-sicurezza-ambiente/d-min-llpp-14-02-1992)
     - classici come Santarella e Giangreco per il metodo alle tensioni ammissibili
       (diagrammi elastici, esempi di calcolo, interpretazione delle norme storiche). [14](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2025-08/2025_2G-Eurocodes-Workshop_EN1992_Final_website.pdf)[15](https://www.ivysci.com/en/articles/9793389__Assessment_of_existing_PC_structures_according_to_EN_1992112023)
  3) JSON/CSV normative data shipped with this repository (e.g. comparative tables
     and parameter files).

- If you cannot clearly trace a formula or coefficient back to:
  - existing code,
  - a JSON/CSV parameter,
  - or a cited normative/technical reference,
  then you MUST NOT implement it. Instead:
  - create a TODO with a short Italian explanation, e.g.:
    - "# TODO: integrare formulazione esatta da NTC 2018, Cap. 4, paragrafo preciso."

B) No silent omissions

- When a norm requires multiple checks (e.g. flessione, taglio, torsione, minimi
  di armatura, tensioni di esercizio), you MUST NOT:
  - implement only a subset while presenting it as “verification according to X”,
  - silently skip interaction effects (e.g. taglio-torsione, N+M, etc.).
- If some part of the normative method is not yet implemented in the codebase:
  - either disable that specific check in the GUI for that norm with a clear
    Italian user message, e.g.:
    - "Verifica non ancora disponibile per questa normativa.",
  - or implement a clearly marked partial template with:
    - description_it explaining that the check is partial,
    - TODO comments describing which steps/formulas from the norm are still missing.
- Under NO circumstances may you present a partial check as if it were fully
  compliant with the norm.

C) Priority to existing repository logic

- Whenever there is an existing implementation in the repo (for RD 2229/39,
  DM 1992/1996 TA, NTC 2008, NTC 2018, etc.):
  - treat that code as the primary reference for how the checks must work;
  - refactor it for modularity and testability, but do NOT change the underlying
    method unless there is a documented normative reason.
- If you find inconsistencies between the existing code and the normative texts:
  - DO NOT “fix” them silently,
  - instead:
    - add tests that highlight the discrepancy,
    - add TODO comments with a short explanation and references,
    - leave the behaviour unchanged unless the user explicitly asks otherwise.

D) Use of internet and technical sources (for this Plan)

- When you need clarification on a normative concept (e.g. TA vs SLU formulation,
  LC/FC in NTC 2018, EC2 Annex I scope, etc.), you SHOULD base your reasoning on:
  - official PDFs and authoritative commentaries where possible, NOT on random blogs,
  - well-known technical references that discuss the evolution from TA to SLU
    (e.g. comparisons TA vs SLU in concrete design). [16](https://ltshop.legislazionetecnica.it/show_doc.asp?nomedoc=/allegati_pdf/A-295-8-NTC-2018.pdf)[7](https://www.mauromalizia.it/wp-content/uploads/Norme-tecniche-costruzioni.pdf)
- Even when you use external information:
  - do NOT embed long quotes from copyrighted texts,
  - always translate the normative concepts into your own code and comments,
  - keep references in NormReference / docstrings / comments.

  ========================================
CORE DATA STRUCTURES FOR NORMATIVE REFERENCES
========================================
To support help texts, tooltips, reports, and scenario comparison with explicit
normative references (Norma, capitolo, paragrafo, formula), you MUST introduce
(or refine, if already existing) clear, central data structures in the core layer.

A) NormReference (core)

- Introduce a dedicated core type, e.g. a @dataclass, to represent a single normative
  reference used in calculations, validation or help/tooltip:

  - Suggested Python structure (instruction, do not just copy blindly):

    - class NormReference:
      - norm_code: str
        - e.g. "RD 2229/39", "DM 14/02/1992", "DM 9/1/1996",
          "NTC 2008", "NTC 2018", "EN 1992-1-1:2023", "prEN 1990-2".
      - chapter: str
        - e.g. "Cap. II", "Cap. 4", "Cap. 8".
      - paragraph: str
        - e.g. "§ 4.1.2.3", "§ C8.5.4".
      - formula_label: str | None
        - e.g. "σ = M/W", "M_Rd", "V_Rd,max", "ε_cu".
      - description_it: str
        - short Italian description for tooltip/help:
          - e.g. "Limite di tensione di esercizio del calcestruzzo in esercizio."
          - e.g. "Definizione dei fattori di confidenza per le opere esistenti."
      - notes_it: str | None
        - optional extra notes in Italian, e.g.:
          - "Applicabile solo a elementi in c.a. ordinario."
          - "Valore tipico FC per LC2."
      - source_type: str | None
        - optional tag such as "TA", "SLU", "SLE", "ESISTENTI".
      - priority: int | None
        - optional for marking a “primary” reference vs secondary references.

- This type MUST be defined in a core module (e.g. under app/core/norms/*) and NOT in
  GUI modules.
- It MUST be used everywhere normative references are needed (templates, registry,
  reports, validation, GUI help/tooltip).

B) JSON/CSV backing for NormReference

- NormReference instances SHOULD be loadable from JSON/CSV configuration files, not
  hard-coded all over the codebase.
- Define a JSON schema (conceptually) similar to:

  [
    {
      "norm_code": "NTC 2018",
      "chapter": "Cap. 8",
      "paragraph": "§ C8.5.4",
      "formula_label": "FC (fattori di confidenza)",
      "description_it": "Definizione dei livelli di conoscenza LC1–LC3 e dei "
                        "fattori di confidenza FC corrispondenti.",
      "notes_it": "Applicabile alla valutazione delle costruzioni esistenti.",
      "source_type": "ESISTENTI",
      "priority": 1
    },
    {
      "norm_code": "RD 2229/39",
      "chapter": "Cap. II",
      "paragraph": "—",
      "formula_label": "σ = M/W",
      "description_it": "Calcolo a flessione con metodo alle tensioni ammissibili "
                        "e diagramma elastico delle tensioni.",
      "notes_it": "Impiegato nel metodo storico alle tensioni ammissibili.",
      "source_type": "TA",
      "priority": 1
    }
  ]

- You do NOT need to fully implement a JSON schema validator, but:
  - centralise loading in one module,
  - expose a function like:
    - load_norm_references() -> dict[(norm_code, chapter, paragraph, formula_label),
                                      NormReference]
    - or any similar mapping structure.
- The normative registry and verification templates MUST use these loaded references
  instead of duplicating normative text inside many modules.

Completeness of VerificationTemplate sets per norm

- For each norm, the collection of VerificationTemplate instances MUST be sufficient
  to cover all the verification families that the software claims to support for
  that norm, including at least:
  - flessione (tutte le varianti previste dalla norma),
  - taglio,
  - torsione,
  - combinazioni taglio + torsione (where required by the norm),
  - tensioni (tensioni ammissibili / tensioni di esercizio),
  - minimi di armatura (a flessione e a taglio),
  - additional limit states (SLU, SLE, SLC, deformazioni) where implemented.
- The main verification service, when invoked for an element and a selected norm, must:
  - determine the relevant VerificationTemplate set for that norm and element
    (based on verification_type, limit_state, applicable_section_types, etc.),
  - execute ALL the templates required for that element under that norm, not just a
    subset chosen arbitrarily,
  - collect the results into CalcOutput in a structured way (per template_id).
- The GUI may allow:
  - enabling/disabling some groups of checks (e.g. only SLU, or SLU+SLE),
  - but once a group of checks is enabled for a given norm, all templates belonging
    to that group must be executed completely according to that norm.
- If, for a given norm, some verification family is not yet implemented:
  - do NOT create a fake template pretending to be complete,
  - either:
    - leave that template absent and inform the user in Italian that the check is not
      yet available,
    - or provide a template marked as “partial” in its description_it and notes_it,
      with clear TODOs in code.

C) Integration with Normative Registry (NormRecord / NormPlugin)

- Extend the normative registry data structures so that each norm record/plugin can
  expose a list of references:

  - For example, a NormRecord / NormPlugin may have:

    - code: str
    - version: str
    - status: str
    - scope_existing: bool
    - core_topics: list[str]  # e.g. ["SLU", "SLE", "TA"]
    - references: list[NormReference]
      - NormReference entries for the most important clauses used by that norm.

- This allows:
  - the Normative Configuration Panel to show:
    - for each norm:
      - a short list of key references (Norma, capitolo, paragrafo, formula),
  - the GUI to generate tooltips that say:
    - "Riferimento: NTC 2018, Cap. 8, § C8.5.4 (FC per opere esistenti)."

- When linking to verification templates, you may add:
  - primary_reference: NormReference
  - secondary_references: list[NormReference]
  - so that each template can point to 1–3 key clauses.

D) Integration with VerificationTemplate

- Extend the VerificationTemplate data model (if you implement it) so that it can
  carry normative references:

  - Suggested attributes (in addition to what you already have):

    - template_id: str
      - e.g. "NTC2018_SLU_FLESSIONE_SEMPLICE"
      - or "RD2229_TA_FLESSIONE".
    - norm_code: str
      - linked to NormRecord code.
    - verification_type: str
      - e.g. "SLU_FLESSIONE", "TA_FLESSIONE", "SLE_TENSIONI".
    - primary_reference: NormReference | None
    - secondary_references: list[NormReference]
    - description_it: str
      - short Italian textual explanation for UI, logs and reports.

- These references MUST be used by:
  - the verification core for logging:
    - e.g. "Verifica eseguita secondo NTC 2018, Cap. 4, § 4.x.x (template ...)."
  - the GUI for tooltips:
    - hovering over "Verifica SLU flessione" should show the normative reference.
  - the report generator:
    - listing, for each check, the associated NormReference entries.

E) Integration with Validation Engine

- The core validation engine SHOULD also accept or attach normative references where
  appropriate, for example:

  - ValidationResult might have:
    - severity: "info" | "warning" | "error"
    - field: str  # e.g. "d", "As", "N", ...
    - message_it: str
    - norm_reference: NormReference | None

- The GUI can then:
  - show an error/warning icon with a tooltip such as:
    - "Valore di d non coerente con la sezione scelta. Riferimento: RD 2229/39,
       Cap. II (limiti geometrici)."

F) Integration with Help & Tooltip System

- Use NormReference as the *only* source of normative reference info in the GUI.
- For each GUI element (fields, buttons, columns) related to a check or parameter:
  - associate the relevant NormReference(s) and build Italian tooltip/help strings
    dynamically, e.g.:

    - f"Riferimento: {ref.norm_code}, {ref.chapter}, {ref.paragraph} "
      f"({ref.formula_label}). {ref.description_it}"

- When a precise paragraph/formula label is not yet known:
  - either:
    - omit the paragraph/formula and mark a TODO in code, or
    - use a generic NormReference with:
      - paragraph="TODO", formula_label="TODO", notes_it explaining that the exact
        location must be confirmed.
  - Do NOT invent clause numbers or formula labels.

G) Logging & Reports with NormReference

- When logging verification steps, include references where meaningful, e.g.:

  - logger.info(
      "Verifica a flessione SLU secondo %s, %s, %s (%s).",
      ref.norm_code,
      ref.chapter,
      ref.paragraph,
      ref.formula_label,
  )

- In the report object, add a field for:
  - references: list[NormReference]
    - so that a final printed/previewed report can list all the norms and clauses
      involved in the verification of each element.

H) Design Constraints & Style

- Keep NormReference and related classes:
  - in core modules (no GUI dependency),
  - as small, pure data structures (ideally dataclasses).
- Ensure:
  - no duplication of normative reference strings across the codebase;
  - all normative references go through:
    - JSON/CSV → loader → NormReference → registry/templates → GUI/validation/report.
- Apply:
  - Google-style docstrings to NormReference and related types,
  - clear type hints,
  - line length <= 100 chars,
  - no trailing whitespace,
  - no network calls.

========================================
THREADING, RESPONSIVENESS & ERROR HANDLING
========================================

To maintain a responsive GUI and a modular core, you MUST keep the verification
and validation core thread-agnostic and centralise user-facing error handling.

A) Threading & responsiveness

- Core services (validation and verification) MUST:
  - be synchronous and deterministic,
  - NOT start threads or event loops by themselves,
  - NOT import Tkinter or GUI modules.
- The GUI layer is responsible for:
  - deciding whether to:
    - call services directly (for small/fast operations),
    - run them in a worker thread or background task (for bulk operations),
  - updating the UI accordingly (busy indicators, disabling buttons, etc.).
- Core services MUST be:
  - safe to call from multiple threads concurrently (no hidden global state),
  - they may read from shared read-only caches (e.g. normative data) but must
    NOT modify shared state without proper synchronisation.

B) Error handling (exceptions vs validation issues)

- Distinguish clearly between:
  - programmer errors / unexpected states:
    - raised as exceptions (ValueError, RuntimeError) WITH clear log messages,
    - typically indicate bugs or misconfiguration, not user mistakes.
  - user input / configuration problems:
    - represented as ValidationIssue instances,
    - collected into ValidationResult and propagated via CalcOutput to the GUI.
- User-facing messages MUST:
  - be in Italian,
  - come from:
    - ValidationIssue.message_it,
    - SingleCheckResult.messages_it,
    not from raw exception messages.
- Core code MUST NOT:
  - call message boxes or GUI dialogs directly,
  - embed untranslated text meant for end users.

C) Logging of errors and warnings

- Programmer errors (exceptions) must:
  - be logged at ERROR level with stack trace,
  - ideally not be swallowed silently.
- Validation issues must:
  - be logged at DEBUG or INFO level (depending on severity),
  - include context and, when available, NormReference info.
- This separation allows:
  - tests to verify ValidationIssue behaviour independently,
  - production logs to show clear, traceable behaviour.

========================================
CORE VALIDATION ENGINE (GEOMETRIC & NORMATIVE CONSISTENCY)
========================================

To ensure that all calculations/verifications are based on coherent and normative-
compliant input data, you MUST introduce (or refine, if already present) a “validation
engine” in the core layer. This engine must be independent from the GUI and reusable
by all verification services.

A) Purpose of the Validation Engine

- The Validation Engine is responsible for:
  - checking geometric consistency of sections and reinforcement data,
  - checking physical ranges (e.g. material strengths, reinforcement ratios),
  - checking compatibility between:
    - selected norm (RD 2229/39, DM 1992, DM 1996, NTC 2008, NTC 2018, EC2, etc.),
    - selected limit state family (TA, SLU, SLE, SLC, esercizio),
    - selected verification types (flessione, taglio, torsione, minimi, tensioni),
    - and the data provided in CalcInput,
  - producing structured validation results that:
    - can be consumed by the GUI (for highlighting errors/warnings),
    - can be logged and reported,
    - are linked to normative references (NormReference) where possible.
- The Validation Engine MUST NOT:
  - perform the actual resistance checks (those belong to verification functions),
  - depend on Tkinter or GUI modules.

B) ValidationResult / ValidationIssue data model

- Introduce a central data structure for validation output, e.g. ValidationIssue or
  ValidationResultEntry, and a container ValidationResult. Suggested design:

  - class ValidationIssue:
    - severity: str
      - "info", "warning", or "error".
    - field: str
      - symbolic name of the field in CalcInput or related structure, e.g.:
        - "sezione", "materiale", "N", "Mx", "My", "As", "As_prime", "d", "d_prime",
          "staffe_diametro", "staffe_passo", "norma", "LC", "FC".
    - code: str
      - short machine-friendly code, e.g.:
        - "GEOM_D_TOO_LARGE", "ARM_RHO_TOO_HIGH", "NORM_NOT_COMPATIBLE",
          "MISSING_REQUIRED_INPUT".
    - message_it: str
      - Italian human-readable message for GUI and logs, e.g.:
        - "Valore di d non compatibile con l'altezza della sezione."
        - "Rapporto di armatura a flessione superiore al massimo consentito."
        - "La normativa selezionata non è applicabile a questa combinazione di input."
    - norm_reference: NormReference | None
      - optional normative reference (Norma, capitolo, paragrafo, formula) when the
        validation rule is derived from a specific clause.
    - context: dict[str, Any]
      - optional contextual data (e.g. numeric thresholds, computed values).

  - class ValidationResult:
    - issues: list[ValidationIssue]
    - has_errors: bool
    - has_warnings: bool

- ValidationIssue and ValidationResult MUST be defined in core modules (no GUI).

C) Validation Engine interface

- Implement a functional-style interface in the core, for example:

  - def validate_calc_input(
        calc_input: CalcInput,
        active_norm: NormPlugin | NormParameters,
        templates: list[VerificationTemplate],
    ) -> ValidationResult:
    - Performs validation of:
      - geometric compatibility,
      - physical ranges,
      - norm-template applicability.

- You may create additional specialised validators:

  - def validate_geometry(calc_input: CalcInput, ...) -> list[ValidationIssue]
  - def validate_materials(calc_input: CalcInput, ...) -> list[ValidationIssue]
  - def validate_norm_compatibility(calc_input: CalcInput, active_norm: NormPlugin,
                                    templates: list[VerificationTemplate]
                                   ) -> list[ValidationIssue]

- But there should be ONE main entry point (e.g. validate_calc_input) used by:
  - the real-time per-row verification in the GUI,
  - the bulk “Ricalcola tutto” workflow,
  - unit/integration tests.

D) Geometric validation (sections, reinforcement, d, d', staffe)

- The Validation Engine must check that:
  - geometric properties are consistent with the section definition:
    - e.g. 0 < d <= h (altezza utile ≤ altezza sezione),
    - d' ≥ copriferro and consistent with reinforcement position within the section,
    - As and As' are non-negative and physically plausible for the section area,
    - staffe diametro/passo are positive and feasible.
  - reinforcement ratios (rho) are within normative bounds where those limits are
    already implemented (TA or SLU/SLE, depending on norm).
- For each detected issue, create a ValidationIssue with:
  - severity "error" when the geometry is physically impossible or clearly outside
    any normative scope,
  - severity "warning" when the geometry is unusual but still potentially valid.
- Where the check is derived from a specific norm (e.g. RD 2229/39 minimum covers,
  or NTC 2018 minimum reinforcement rules), attach a NormReference.
- When the check is based on general engineering practice rather than explicit
  normative limits:
  - still perform the check, but in ValidationIssue.notes_it and/or a code comment
    clarify that the limit is a “good practice” suggestion, not a normative limit.

E) Material and action validation

- The Validation Engine should verify that:
  - material properties (e.g. f_ck, f_yk, E_c, E_s) fall within reasonable ranges
    for the selected norm and material type,

========================================
CORE CONTRACTS: CalcInput, CalcOutput, VerificationContext
========================================

To keep the verification engine clear and modular, you MUST define (or refine) a set
of core contracts that are independent from the GUI and reusable across all norms.

A) CalcInput (core)

- CalcInput (dataclass or similar) represents all the data needed to verify ONE
  structural element under ONE normative context.
- It MUST be:
  - defined in a core module (e.g. app/core/contracts.py),
  - independent from Tkinter or GUI widgets,
  - strongly typed with type hints.
- Minimum fields (names can be adapted, but semantics must be preserved):
  - element_name: str
  - section: SectionLike  # type representing geometric data (from geometry module)
  - material: MaterialLike  # type from the materials module
  - norm_code: str  # e.g. "NTC 2018", "RD 2229/39"
  - limit_states_enabled: list[str]  # e.g. ["TA", "SLU", "SLE"]
  - lc: str | None  # LC1, LC2, LC3, or None for new materials
  - fc: float | None  # Fattore di confidenza (if applicable)
  - N: float | None
  - Mx: float | None
  - My: float | None
  - Tx: float | None
  - Ty: float | None
  - Mz: float | None
  - As: float | None
  - As_prime: float | None
  - d: float | None
  - d_prime: float | None
  - staffe_diametro: float | None
  - staffe_num_bracci: int | None
  - staffe_passo: float | None
  - area_ferri_piegati: float | None
  - extra: dict[str, Any]
    - for any additional data needed by specific norms (kept localised).

- CalcInput SHOULD be treated as immutable by the verification and validation
  engines (no in-place modifications), even if the dataclass is not strictly frozen.

B) CalcOutput (core)

- CalcOutput represents the outcome of all checks performed for ONE element
  under the selected norm and enabled limit states.
- Minimum conceptual fields:
  - element_name: str
  - norm_code: str
  - ok: bool  # True iff all required checks are OK and no validation errors
  - per_template_results: dict[str, SingleCheckResult]
  - validation_result: ValidationResult | None
  - summary_metrics: dict[str, float | bool | str]

- SingleCheckResult is defined as in the RESULTS STRUCTURE section, and MUST NOT
  depend on Tkinter.

C) VerificationContext / EngineConfig (optional but recommended)

- To avoid passing too many parameters and to keep configuration modular, introduce
  a VerificationContext (or EngineConfig) object that groups:
  - active_norm: NormPlugin
  - enabled_limit_states: list[str]  # ["TA", "SLU", "SLE", ...]
  - scenario_flags: dict[str, Any]
    - e.g. {"existing_structure": True/False}
  - performance_options:
    - e.g. {"use_cache": True}
- The GUI MUST NOT manipulate global state inside the core; instead it should:
  - construct or update a VerificationContext,
  - pass it to helper functions that then call:
    - run_verifications_for_element(calc_input, context.active_norm), etc.
- This keeps configuration and state management explicit and modular.
``

========================================
VERIFICATION CORE SERVICE CONTRACT
========================================

To make the verification module unambiguous and reusable, you MUST implement a clear
core “verification service” API that orchestrates:

  1) validation of CalcInput,
  2) selection of relevant VerificationTemplate instances for the active norm,
  3) execution of all required checks,
  4) aggregation of results into CalcOutput.

A) Core service functions (signatures and behaviour)

- Implement at least the following core functions (module path to be adapted to the
  actual project structure):

  - def run_verifications_for_element(
        calc_input: CalcInput,
        active_norm: NormPlugin,
    ) -> CalcOutput:
    - High-level contract:
        1) Determine which VerificationTemplate instances are applicable for:
           - the active norm,
           - the element’s properties (section type, material type, existing/new),
           - the enabled verification groups (e.g. TA, SLU, SLE) if configured.
        2) Call validate_calc_input(calc_input, active_norm, templates) to perform
           geometric/material/normative validation.
        3) If ValidationResult.has_errors is True:
           - DO NOT run any verification templates for this element.
           - Return a CalcOutput that:
             - indicates failure due to validation errors,
             - includes the ValidationResult (or a reference to it) for GUI/report.
        4) If only warnings are present:
           - proceed with verification,
           - but propagate the warnings into CalcOutput so that the GUI can display
             them (e.g. icons, tooltip, message area).
        5) Execute ALL relevant verification templates for the selected norm and
           limit state(s), not only a subset:
           - for example, if NTC 2018 is selected and SLU+SLE are enabled, run all
             templates for:
               - SLU bending (flessione, presso-tenso flessione),
               - SLU shear/torsion,
               - SLE stresses (tensioni di esercizio),
               - minimum reinforcement where applicable.
        6) Pack all template-specific results into CalcOutput, indexed by template_id.
    - This function MUST be pure in terms of calculations (no Tkinter, no direct GUI
        calls, no file I/O), except for logging.

  - def run_verifications_for_all(
        calc_inputs: Sequence[CalcInput],
        active_norm: NormPlugin,
    ) -> list[CalcOutput]:
    - Used for the bulk “Ricalcola tutto” button in the GUI.
    - Calls run_verifications_for_element() for each element, possibly optimising:
      - reuse of section/material properties,
      - internal caching where appropriate.
    - MUST not freeze the GUI:
      - if threading or async patterns already exist in the project, reuse them;
      - otherwise, structure the API so that the GUI can run it in a background
          thread without side effects.

- Any additional helper functions (e.g. for grouping templates by limit_state,
  check_category, norm) should be internal to the core and not rely on GUI.

B) Selection of templates inside the core (not in the GUI)

- The selection of which VerificationTemplate instances to execute for an element
  MUST be done in the core, not in GUI code, based on:
  - active_norm (NormPlugin),
  - element’s properties (section type, materials, existing/new),
  - globally enabled check groups (e.g. TA vs SLU vs SLE), if such configuration
    exists and is stored in core/registry.
- The GUI may:
  - allow the user to enable/disable families of checks (e.g. “esegui solo SLU”),
  - pass this configuration to the core (e.g. via a settings object),
  - but MUST NOT hard-code which low-level functions to call.
- The core service must:
  - enforce the “completeness per norm” requirement:
    - once a group of checks (e.g. SLU for NTC 2018) is enabled,
      all relevant templates for that group must be executed.

C) Behaviour with validation errors and warnings

- ValidationResult.has_errors is True:
  - The verification service MUST:
    - NOT execute any VerificationTemplate for that element.
    - Produce a CalcOutput that:
      - marks the element as “non verificato per errori di input”,
      - carries the ValidationResult so that the GUI can highlight fields and show
        Italian messages/tooltips.
- ValidationResult.has_errors is False but has_warnings is True:
  - The verification service:
    - executes all relevant checks,
    - attaches the warnings to CalcOutput, so that the GUI:
      - can show warning icons,
      - can provide tooltips with the ValidationIssue.message_it and NormReference.
- ValidationResult with no errors/warnings:
  - Full verification proceeds normally.

D) Statelessness and thread-friendliness

- The verification core functions (run_verifications_for_element / for_all) MUST:
  - be stateless with respect to input → output mapping:
    - no reliance on hidden global state,
    - any caches should be:
      - explicit and confined (e.g. to a service or cache object),
      - or handled outside by the caller.
  - be safe to call concurrently on different CalcInput instances.
- This design requirement is to:
  - allow the GUI to perform:
    - real-time per-row checks,
    - bulk recalculation,
    without introducing race conditions or inconsistent states.

    ========================================
RESULTS STRUCTURE & MAPPING TO TEMPLATES
========================================
To avoid ambiguity in how verification results are represented and consumed by the
GUI and reporting, you MUST define a clear structure for CalcOutput (or a related
result object) that maps results to VerificationTemplate instances.

A) CalcOutput requirements (conceptual)

- CalcOutput (or an equivalent structure) MUST include, at minimum:

  - element_id or name:
    - reference to the element/row in the GUI (e.g. nome elemento).
  - ok: bool
    - global “all checks OK” flag for this element under the selected norm and
      enabled check groups.
  - per_template_results: dict[str, SingleCheckResult]
    - mapping from template_id (string) to a structured result object.
  - validation_result: ValidationResult | None
    - the validation issues that were found before running checks (if any).
  - summary_metrics: dict[str, float | bool | str]
    - optional aggregate information, e.g.:
      - max utilisation among all checks,
      - controlling check (template_id with worst utilisation),
      - classification string in Italian ("OK", "NON VERIFICATO", "INCOMPLETO").

- Define a dedicated SingleCheckResult dataclass (or equivalent), e.g.:

  - class SingleCheckResult:
    - template_id: str
    - ok: bool
    - utilisation: float | None
      - ratio (e.g. Ed/Rd, σ/σ_amm, etc.), when meaningful.
    - details: dict[str, float | str]
      - key-value pairs of key results, e.g.:
        - "sigma_c_max": float,
        - "sigma_s_max": float,
        - "M_Rd": float,
        - "V_Rd": float,
        - "theta_fessurazione": float,
        - "delta_max": float.
    - norm_references: list[NormReference]
      - references associated with this check (mirroring the template’s references).
    - messages_it: list[str]
      - optional list of Italian messages (e.g. formatted summaries for report/GUI).
    - check_category: str
      - e.g. "FLESSIONE", "TAGLIO", "TORSIONE", "FESSURAZIONE", "MINIMI_ARM".
    - limit_state: str
      - "TA", "SLU", "SLE", "SLC", etc.

B) Mapping from VerificationTemplate to SingleCheckResult

- For each VerificationTemplate executed:
  - the verification core MUST:
    - create a SingleCheckResult with:
      - template_id equal to VerificationTemplate.template_id,
      - check_category and limit_state copied from the template,
      - norm_references equal to:
        - [primary_reference] + secondary_references (when available),
      - utilisation and details filled based on the specific check results.
- This mapping ensures that:
  - the GUI can:
    - group results per category (e.g. all bending checks),
    - show “OK/NON OK” icons and utilisation ratios per check type,
    - show a tooltip with normative references and formula labels.
  - the report generator can:
    - produce a table where each row is a template_id with its utilisation,
      references and key metrics.

C) GUI consumption of CalcOutput

- The GUI MUST use the structured information in CalcOutput to:
  - show per-template results in Italian, e.g.:
    - "Flessione semplice (SLU, NTC 2018): OK, η = 0.73",
    - "Taglio (TA, RD 2229/39): NON OK, σ_v > τ_ammis."
  - highlight:
    - which check is controlling,
    - which norm/paragraph/formula are associated to a given check (via tooltip).
- The GUI MUST NOT:
  - recompute results from scratch,
  - guess normative references; it MUST read them from norm_references.

D) Behaviour with partial implementation

- If some verification family is not yet implemented for a given norm:
  - there should be no SingleCheckResult for those checks, and:
    - either:
      - the GUI indicates that the specific check is “non disponibile per la norma
        selezionata” (with a clear Italian message),
      - or:
        - you define a SingleCheckResult with ok=False and a special status in
          messages_it explaining that the check is not yet implemented.
  - In both cases, code comments and/or TODO markers must explain clearly which
    normative steps are missing.
- Under no circumstances should a missing or partial check be presented as fully
  compliant with the norm.

  ========================================
BENCHMARK CASES (CONCRETE EXAMPLES)
========================================
To further constrain the implementation to real normative practice and avoid any
shortcut or invented behaviour, you MUST define and implement concrete benchmark
cases, with numerical expectations, as unit tests. These benchmarks must be derived
from:

  - existing validated code in this or related repositories, and/or
  - authoritative technical examples available online,
  - the official norms (RD 2229/39, DM 1992, DM 1996, NTC 2008, NTC 2018, EC2).

When external references are used, DO NOT copy long portions of text verbatim. Use
them only to extract input data and numerical results, and then encode those into
pytest tests.

If you cannot access the internet from this environment, you MUST fall back to the
examples and behaviour already present in the current repository (e.g. existing
RD 2229 tensioni ammissibili project code) as numerical reference.

A) Benchmark 1 – TA Bending (RD 2229/39 + Santarella/Giangreco style)

- Objective:
  - Validate the implementation of bending checks with the method of allowable
    stresses (tensioni ammissibili) for a simple rectangular RC section.

- Normative/technical context:
  - RD 16/11/1939 n. 2229 – norme per il conglomerato cementizio (metodo TA). [14](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2025-08/2025_2G-Eurocodes-Workshop_EN%201990-2_TPL_website.pdf)[15](https://www.en-standard.eu/din-en-1990-2-eurocode-grundlagen-der-planung-von-tragwerken-und-geotechnischen-bauwerken-teil-2-bewertung-von-bestandsbauten-deutsche-und-englische-fassung-pren-1990-2-2024/)
  - Classical allowable stress formulation for RC with transformed-section approach
    (modular ratio n ≈ 15) as used in traditional Italian literature (Santarella,
    Giangreco). [1](http://web.tiscali.it/geocal/S/Cap1/2/Parte_1/9.htm)[2](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2025-08/2025_2G-Eurocodes-Workshop_EN1992_Final_website.pdf)[3](https://www.ivysci.com/en/articles/9793389__Assessment_of_existing_PC_structures_according_to_EN_1992112023)
  - If needed, use any existing TA implementation already present in the repository
    (e.g. historical RD 2229 calculation module) as reference behaviour. [13](https://github.com/dancarloni/eng_calcs_RD2229)

- Benchmark case definition:
  - Choose a simple rectangular beam section (e.g. b, h, As, As', copriferro) and a
    bending moment M such that:
    - the section is clearly under-reinforced,
    - the concrete remains in compression only,
    - the neutral axis lies within the section.
  - Use the TA method to:
    - compute transformed section properties (using n = Es/Ec),
    - compute concrete and steel stresses (σ_c,max, σ_s,max),
    - compare them against the allowable stresses defined by the norm/parameters.
  - Extract one or more numeric target values (e.g. σ_c,max, σ_s,max, utilisation
    ratios) either from:
    - an existing example in the repo,
    - or from a fully worked example based on RD 2229/39 + classic TA theory.

- Test implementation (pytest):
  - Create a test function, e.g.:
    - test_rd2229_ta_bending_benchmark_case()
  - Inside the test:
    - build a CalcInput for the chosen section and load,
    - call the TA bending verification function via the verification service,
    - assert that:
      - the resulting utilisation is within a tight tolerance of the reference value,
      - σ_c,max and σ_s,max match the expected values within tolerance.
  - Clearly document in comments:
    - which formulas are used,
    - which normative references (NormReference) motivate the chosen benchmark.

B) Benchmark 2 – TA vs SLU comparison (same RC section)

- Objective:
  - Provide a direct numerical comparison between:
    - the TA method for bending (RD 2229/39 + classical approach),
    - SLU design according to NTC 2008/NTC 2018,
    for the same RC section and load condition.

- Technical reference:
  - Use a published example that compares TA and SLU methods for a RC section in
    bending (flessione) as conceptual guidance. [9](https://www.marcodepisapia.com/tensioni-ammissibili-e-stato-limite-ultimo-sezioni-calcestruzzo-armato/)[16](https://www.studiosciurti.it/tensioni-ammissibili-stati-limite)

- Benchmark case definition:
  - Take a rectangular RC section with:
    - given b, h, f_ck, f_yk, As, As',
    - a design bending moment M_Ed.
  - For TA:
    - compute σ_c,max and σ_s,max,
    - check against allowable stresses,
    - compute a TA “utilisation ratio”, e.g. max(σ/σ_amm).
  - For SLU (NTC 2008/2018):
    - design or verify the section at SLU under the same M_Ed (or equivalent
      SLU design combination),
    - compute M_Rd and the utilisation ratio M_Ed / M_Rd,
    - ensure that the SLU design is consistent with NTC rules.

- Test implementation:
  - Create a pytest test, e.g.:
    - test_ta_vs_slu_bending_comparison_benchmark()
  - Steps:
    1) Build CalcInput for the section and load.
    2) Run TA bending verification template (RD 2229/TA).
    3) Run SLU bending verification template (NTC 2018 or NTC 2008).
    4) Assert that:
       - both checks pass for correctly dimensioned reinforcement,

========================================
CALIBRATION & BENCHMARK MODULE (DYNAMIC VERIFICATION SYSTEM)
========================================

A dedicated “Calibration Module” MUST be implemented to allow users to build,
validate and maintain a growing database of input–output benchmark cases. These
benchmark cases serve as normative guardrails and prevent Copilot or future code
refactors from introducing shortcuts or invented formulas.

The Calibration Module is composed of:

- a CORE SERVICE (pure Python, no GUI),
- a GUI PANEL (Tkinter, in Italian),
- a persistent DATASET (JSON/CSV, UTF-8),
- an automatic TEST GENERATOR (pytest-compatible).

----------------------------------------

A) GOALS OF THE CALIBRATION MODULE
----------------------------------------

1. Allow the user to enter:
   - COMPLETE CalcInput (section, material, LC/FC, loads, reinforcement, etc.),
   - EXPECTED RESULT (calculated via external reference software or hand calculation),
   - normative context (RD 2229/39, DM92, DM96, NTC 2008, NTC 2018, EC2, etc.),
   - tolerance settings (absolute/relative).

2. Execute the verification engine on the same CalcInput.

3. Compare:
   - expected_output vs real_output,
   - per-template utilisation ratios,
   - stresses, resistances, neutral axis position,
   - check categories (bending, shear, torsion, tensioni, minimi, etc.),
   - normative references (NormReference).

4. Report:
   - full match → GREEN (test passed),
   - mismatch → RED (test failed) with detailed diagnostic:
       - which template failed,
       - expected vs actual values,
       - tolerance,
       - normative references involved.

5. Allow user to SAVE the benchmark case into:
   - calibration_cases.json (or similar modular multi-file dataset),
   - each entry including:
       - CalcInput,
       - Expected CalcOutput,
       - NormReference list,
       - linked VerificationTemplate list,
       - tolerance,
       - metadata (timestamp, description, source).

6. Allow automatic GENERATION of pytest tests:
   - each benchmark case becomes a pytest function,
   - executed during `pytest -q`,
   - enforcing normative correctness over time.

----------------------------------------

B) CORE LAYER: CALIBRATION SERVICE
----------------------------------------

Implement a dedicated core module (e.g. app/core/calibration.py) with:

1. run_calibration_case(calc_input, expected_output, active_norm, tolerance)
   - Calls:
       a) validate_calc_input(...),
       b) run_verifications_for_element(...),
       c) compares actual vs expected (per-template and aggregated).
   - Returns:
       - CalibrationResult:
           - passed: bool
           - mismatches: list[CalibrationMismatch]
           - validation_issues: ValidationResult
           - actual_output: CalcOutput
           - expected_output: dict or CalcOutput-like structure

2. save_calibration_case(...)
   - Stores benchmark case in JSON (append or versioned).
   - Enforces modular structure:
       - “cases/TA/”, “cases/SLU/”, “cases/SLE/”, “cases/Existing/”, etc.

3. load_calibration_cases() -> list[CalibrationCase]
   - Loads all stored cases from JSON/CSV.

4. generate_pytest_file(...)
   - Generates pytest-compatible code (as plain text the user can paste manually,
     since Copilot cannot write files), containing:
       - test_xxx():
           - loads input & expected,
           - calls run_calibration_case(),
           - asserts that passed is True.

----------------------------------------

C) DATA STRUCTURES
----------------------------------------

@dataclass
class CalibrationCase:
    id: str
    description_it: str
    calc_input: CalcInput
    expected_output: dict  # or structured CalcOutput
    norm_code: str
    linked_templates: list[str]
    references: list[NormReference]
    tolerance: dict[str, float]  # default tolerances for utilisation/stresses
    metadata: dict[str, Any]

@dataclass
class CalibrationMismatch:
    template_id: str
    key: str  # e.g. “utilizzazione”, “sigma_c”, “M_Rd”
    expected: float
    actual: float
    diff: float
    tolerance: float
    message_it: str
    norm_reference: NormReference | None

@dataclass
class CalibrationResult:
    passed: bool
    mismatches: list[CalibrationMismatch]
    validation_issues: ValidationResult
    actual_output: CalcOutput
    expected_output: dict | CalcOutput

----------------------------------------

D) GUI PANEL (Tkinter, Italian)
----------------------------------------

Create a GUI module (e.g. app/gui/calibration_panel.py) with:

- Title: “Modulo di Calibratura / Verifica Dinamica”
- Fields to input:
  - Nome del caso
  - Normativa (dropdown)
  - Tutti i campi di CalcInput (come nel pannello di verifica)
  - Campi per inserire RISULTATI ATTESI:
    - utilità per ogni tipo di verifica
    - σ_c,max, σ_s,max
    - M_Rd, V_Rd
    - posizione asse neutro
    - altri valori previsti
  - Tolleranze:
    - tolleranza assoluta
    - tolleranza relativa

- Buttons:
  - “Esegui confronto”
  - “Salva come caso di calibratura”
  - “Genera test pytest”
  - “Carica caso esistente”
  - “Pulisci campi”

- Output area:
  - Matrice Expected vs Actual
  - Risultati per template (OK/KO)
  - Lista mismatch con tooltips contenenti:
    - Norma
    - Capitolo
    - Paragrafo
    - Formula

----------------------------------------

E) MODULARITÀ & INTEGRAZIONE CON L’ARCHITETTURA ESISTENTE
----------------------------------------

- Calibration Module MUST NOT:
  - modify verification logic,
  - modify validation logic,
  - contain normative formulas.

- It MUST:
  - exclusively use:
    - validate_calc_input(),
    - run_verifications_for_element(),
    - VerificationTemplate,
    - NormReference,
  - operate purely as:
    - consumer of core services,
    - generator of persistent benchmark data,
    - generator of test code.

- Architecture layering:
   GUI → calibration_service → verification_service → templates → normative_core

----------------------------------------

F) SAFETY AGAINST INVENTION OR SHORTCUTS
----------------------------------------

To prevent Copilot from inventing behaviour:

1) If expected_output contains keys not produced by the engine
   - raise calibration mismatch (error).

2) If engine produces values not documented in expected_output
   - highlight in the mismatch list.

3) ALL mismatches MUST be visible in GUI and logs.

4) Saving a calibration case MUST require:
   - no validation errors,
   - at least one full verification template executed,
   - explicit user confirmation when mismatches exist.

5) Generated test must fail if:
   - engine changes formula,
   - engine changes normative factor,
   - engine omits a check,
   - engine invents values.

----------------------------------------

G) FUTURE-PROOFING
----------------------------------------

- The calibration system MUST allow adding:
  - future norms,
  - custom verification templates,
  - new categories of checks,
  - supplemental result metrics,
   without breaking existing calibration cases.

- Adding a new norm automatically:
  - enables adding calibration cases for such norm,
  - produces pytest tests that protect correctness of its implementation.

========================================
END OF CALIBRATION MODULE SPECIFICATION
========================================

Schema GUI semplice del modulo di calibratura
+-----------------------------------------------------------+
|  MODULO DI CALIBRATURA / VERIFICA DINAMICA                |
+-----------------------------------------------------------+
|  Nome caso: [___________]                                 |
|  Normativa: [NTC 2018 ▼]                                  |
|                                                           |
|  --- Input di calcolo (CalcInput) ----------------------  |
|  Sezione: [rettangolare ▼]   b: __h:__               |
|  Materiale: [C25/30 ▼]                                     |
|  LC/FC (se esistente): [LC2 ▼]  [FC=1.20]                 |
|  N: __Mx:__  My: __Tx:__  Ty: __Mz:__          |
|  As: __As':__   d: __d':__                         |
|  Staffe: diam __bracci__ passo __|
|                                                           |
|  --- Risultati attesi (Expected Output) ----------------  |
|  util_fless:__   util_taglio: __util_torsione:__     |
|  sigma_c: __sigma_s:__                                |
|  M_Rd: __V_Rd:__                                      |
|  x_neutro: __|
|  Tolleranze: ass:__   rel: __                             |
|                                                           |
| [Esegui confronto] [Salva caso] [Genera test pytest]      |
|                                                           |
|  --- Risultato ----------------------------------------- |
|  Template | Expected | Actual | Diff | Tolerance | OK?     |
|  ...                                                       |
|                                                           |
+-----------------------------------------------------------+

@dataclass
class CalibrationCase:
    id: str
    description_it: str
    calc_input: CalcInput
    expected_output: dict
    norm_code: str
    linked_templates: list[str]
    references: list[NormReference]
    tolerance: dict[str, float]
    metadata: dict[str, Any]

def run_calibration_case(calc_input, expected_output, active_norm, tolerance):
    validation = validate_calc_input(calc_input, active_norm, [])

    if validation.has_errors:
        return CalibrationResult(
            passed=False,
            mismatches=[],
            validation_issues=validation,
            actual_output=None,
            expected_output=expected_output,
        )

    actual_output = run_verifications_for_element(calc_input, active_norm)

    mismatches = _compare_outputs(
        expected_output, actual_output, tolerance
    )

    return CalibrationResult(
        passed=len(mismatches) == 0,
        mismatches=mismatches,
        validation_issues=validation,
        actual_output=actual_output,
        expected_output=expected_output,
    )

def _compare_outputs(expected, actual, tolerance):
    mismatches = []
    # Confronto per chiave → eventuale mismatch
    # Popolare CalibrationMismatch
    return mismatches

from **future** import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence

import logging

from tkinter import Tk  # solo tipo, non usato direttamente
from tkinter import ttk

# Import core services (aggiorna i path in base al tuo progetto)

from app.core.contracts import CalcInput
from app.core.verification_service import (
    run_verifications_for_element,
    run_verifications_for_all,
    CalcOutput,
)
from app.core.norms.plugins import NormPlugin
from app.core.validation import ValidationResult, ValidationIssue

logger = logging.getLogger(**name**)

@dataclass
class VerificationControllerConfig:
    """Configurazione del controller di verifica.

    Attributes:
        enabled_limit_states: Stati limite abilitati (es. ["TA", "SLU", "SLE"]).
    """

    enabled_limit_states: Sequence[str]

class VerificationController:
    """Controller GUI per la gestione delle verifiche di sezione.

    Questo controller:
      - riceve eventi dalla vista (GUI),
      - costruisce gli oggetti CalcInput per ciascuna riga/elemento,
      - richiama i servizi core di validazione e verifica,
      - aggiorna la vista con risultati, errori, warning e tooltip.

    Non esegue calcoli normativi: delega sempre al core.
    """

    def __init__(
        self,
        root: Tk,
        view: "VerificationViewProtocol",
        norm_plugin: NormPlugin,
        config: VerificationControllerConfig,
    ) -> None:
        """Inizializza il controller.

        Args:
            root: Root Tk (o finestra principale).
            view: Oggetto vista che espone i metodi per leggere/scrivere dati
                delle righe e aggiornare la GUI.
            norm_plugin: Normativa attiva (plugin già inizializzato).
            config: Configurazione (stati limite abilitati, ecc.).
        """
        self._root = root
        self._view = view
        self._norm_plugin = norm_plugin
        self._config = config

        # Wiring eventi della view
        self._wire_view_events()

    # ------------------------------------------------------------------
    # Wiring eventi
    # ------------------------------------------------------------------

    def _wire_view_events(self) -> None:
        """Collega i callback del controller agli eventi della vista.

        La vista deve esporre qualcosa del tipo:
          - set_row_edit_finished_callback(callback: Callable[[int], None])
          - set_recalculate_all_callback(callback: Callable[[], None])
        """
        self._view.set_row_edit_finished_callback(self.on_row_edit_finished)
        self._view.set_recalculate_all_callback(self.on_recalculate_all)

    # ------------------------------------------------------------------
    # Callback principali
    # ------------------------------------------------------------------

    def on_row_edit_finished(self, row_index: int) -> None:
        """Callback invocata quando l'utente termina di editare una riga.

        Esegue:
          1) Costruzione CalcInput dalla riga,
          2) Esecuzione verifica singolo elemento,
          3) Aggiornamento risultati nella riga.
        """
        try:
            calc_input = self._build_calc_input_from_row(row_index)
        except ValueError as exc:
            logger.warning(
                "Impossibile costruire CalcInput per riga %d: %s", row_index, exc
            )
            self._view.show_row_error(
                row_index=row_index,
                message_it=(
                    "Dati insufficienti o non validi per la riga selezionata. "
                    "Controllare i campi evidenziati."
                ),
            )
            return

        logger.debug("Avvio verifica real-time per riga %d", row_index)

        output = run_verifications_for_element(
            calc_input=calc_input,
            active_norm=self._norm_plugin,
            enabled_limit_states=self._config.enabled_limit_states,
        )

        self._apply_output_to_row(row_index, output)

    def on_recalculate_all(self) -> None:
        """Callback per il pulsante 'Ricalcola tutto'.

        Esegue:
          1) Estrazione di CalcInput per tutte le righe,
          2) Verifica in bulk,
          3) Aggiornamento tabella risultati.
        """
        logger.info("Avvio ricalcolo bulk di tutte le righe")

        calc_inputs: List[CalcInput] = []
        row_indices: List[int] = []

        for row_index in self._view.iter_row_indices():
            try:
                ci = self._build_calc_input_from_row(row_index)
            except ValueError:
                # Segnala l'errore nella riga ma continua con le altre
                self._view.show_row_error(
                    row_index=row_index,
                    message_it=(
                        "Dati insufficienti o non validi per questa riga. "
                        "La verifica non è stata eseguita."
                    ),
                )
                continue

            calc_inputs.append(ci)
            row_indices.append(row_index)

        outputs: List[CalcOutput] = run_verifications_for_all(
            calc_inputs=calc_inputs,
            active_norm=self._norm_plugin,
            enabled_limit_states=self._config.enabled_limit_states,
        )

        # Associa ogni output alla riga corrispondente
        for row_index, out in zip(row_indices, outputs, strict=False):
            self._apply_output_to_row(row_index, out)

    # ------------------------------------------------------------------
    # Metodi di supporto: costruzione CalcInput e aggiornamento view
    # ------------------------------------------------------------------

    def _build_calc_input_from_row(self, row_index: int) -> CalcInput:
        """Costruisce un CalcInput leggendo i dati dalla riga della tabella.

        La vista deve fornire un metodo che restituisce un 'raw dict' con
        i valori di input, già convertiti in float/int dove possibile.
        Il mapping dict → CalcInput è delegato a un costruttore/core helper.

        Raises:
            ValueError: se i dati minimi per costruire CalcInput non sono presenti
                o sono evidentemente inconsistenti a livello di GUI.
        """
        raw = self._view.get_row_input_data(row_index)
        # Esempio atteso per raw (da adattare alla tua view):
        # {
        #   "element_name": str,
        #   "section": SectionLike,
        #   "material": MaterialLike,
        #   "N": float | None,
        #   ...
        # }
        missing_fields = [k for k in ("section", "material") if raw.get(k) is None]
        if missing_fields:
            raise ValueError(f"Campi mancanti: {', '.join(missing_fields)}")

        # TODO: usa un factory/core helper reale per creare CalcInput
        calc_input = CalcInput(**raw)  # type: ignore[arg-type]
        return calc_input

    def _apply_output_to_row(self, row_index: int, output: CalcOutput) -> None:
        """Applica i risultati di CalcOutput alla riga della vista.

        Aggiorna:
          - esito globale (OK / NON OK),
          - utilizzazione massima,
          - messaggi di warning,
          - eventuali errori di validazione,
          - tooltips con riferimenti normativi.
        """
        # 1) Aggiornamento esito globale riga
        status = output.summary_metrics.get("status", "NON_VERIFICATO")
        util_max = output.summary_metrics.get("utilizzazione_massima", None)
        controlling_tpl = output.summary_metrics.get("template_controllante", "")

        self._view.update_row_status(
            row_index=row_index,
            ok=output.ok,
            status_it=str(status),
            utilisation=util_max,
            controlling_template_id=str(controlling_tpl),
        )

        # 2) Aggiornamento dettaglio per template
        for tpl_id, single in output.per_template_results.items():
            self._view.update_row_check_result(
                row_index=row_index,
                template_id=tpl_id,
                ok=single.ok,
                utilisation=single.utilisation,
                check_category=single.check_category,
                limit_state=single.limit_state,
                messages_it=single.messages_it,
                norm_references=single.norm_references,
            )

        # 3) Evidenziazione errori/warning di validazione
        if output.validation_result is not None:
            self._apply_validation_to_row(row_index, output.validation_result)

    def _apply_validation_to_row(
        self,
        row_index: int,
        validation: ValidationResult,
    ) -> None:
        """Colora i campi e imposta tooltip in base alle ValidationIssue."""
        for issue in validation.issues:
            field_name = issue.field
            message = issue.message_it

            tooltip_text = message
            if issue.norm_reference is not None:
                ref = issue.norm_reference
                # Costruzione stringa con Norma, capitolo, paragrafo, formula.
                tooltip_text += (
                    f"\nRiferimento: {ref.norm_code}, "
                    f"{ref.chapter}, {ref.paragraph} ({ref.formula_label})."
                )

            if issue.is_error():
                self._view.mark_field_error(
                    row_index=row_index,
                    field_name=field_name,
                    message_it=tooltip_text,
                )
            elif issue.is_warning():
                self._view.mark_field_warning(
                    row_index=row_index,
                    field_name=field_name,
                    message_it=tooltip_text,
                )

# ======================================================================

# Protocol della vista (interfaccia attesa dal controller)

# ======================================================================

class VerificationViewProtocol:
    """Protocollo informale della vista per il controller di verifica.

    In produzione puoi:
      - usare typing.Protocol,
      - oppure far ereditare la tua view da questa classe astratta
        (senza metodi implementati).
    """

    # --- Event wiring ---

    def set_row_edit_finished_callback(self, callback) -> None:  # pragma: no cover
        """Imposta il callback invocato quando l'utente termina l'editing di una riga."""
        raise NotImplementedError

    def set_recalculate_all_callback(self, callback) -> None:  # pragma: no cover
        """Imposta il callback per il pulsante 'Ricalcola tutto'."""
        raise NotImplementedError

    # --- Accesso ai dati di input ---

    def iter_row_indices(self) -> Sequence[int]:  # pragma: no cover
        """Restituisce l'elenco degli indici riga presenti nella tabella."""
        raise NotImplementedError

    def get_row_input_data(self, row_index: int) -> dict[str, Any]:  # pragma: no cover
        """Restituisce un dizionario con i dati di input per la riga."""
        raise NotImplementedError

    # --- Aggiornamento risultati ---

    def update_row_status(
        self,
        row_index: int,
        ok: bool,
        status_it: str,
        utilisation: Optional[float],
        controlling_template_id: str,
    ) -> None:  # pragma: no cover
        """Aggiorna lo stato complessivo della riga (OK/NON OK, utilità max, ecc.)."""
        raise NotImplementedError

    def update_row_check_result(
        self,
        row_index: int,
        template_id: str,
        ok: bool,
        utilisation: Optional[float],
        check_category: Optional[str],
        limit_state: Optional[str],
        messages_it: Sequence[str],
        norm_references: Sequence[Any],
    ) -> None:  # pragma: no cover
        """Aggiorna i risultati di una singola verifica (template) per la riga."""
        raise NotImplementedError

    # --- Evidenziazione errori/warning ---

    def mark_field_error(
        self,
        row_index: int,
        field_name: str,
        message_it: str,
    ) -> None:  # pragma: no cover
        """Evidenzia un campo con errore e assegna un tooltip in italiano."""
        raise NotImplementedError

    def mark_field_warning(
        self,
        row_index: int,
        field_name: str,
        message_it: str,
    ) -> None:  # pragma: no cover
        """Evidenzia un campo con warning e assegna un tooltip in italiano."""
        raise NotImplementedError

    def show_row_error(self, row_index: int, message_it: str) -> None:  # pragma: no cover
        """Mostra un messaggio di errore generico per la riga (es. barra di stato)."""
        raise NotImplementedError

========================================
GUI–CORE DATA BINDING FOR SECTIONS & MATERIALS
========================================

To avoid ambiguity between what the user selects in the GUI (names in dropdowns)
and what the verification engine actually receives, you MUST enforce a strict,
modular data binding between:

- GUI selection widgets (comboboxes, lists),
- repositories for sections and materials,
- CalcInput.section and CalcInput.material.

A) Section selection → geometric parameters in CalcInput

- The section repository (geometry module) MUST remain the single source of truth
  for section properties (area, inertia, dimensions, etc.).
- The GUI (combobox/list for “Sezione”) MUST:
  - internally store a stable identifier (ID or key) for each section,
    not only its display name (e.g. "Rettangolare 30x50", "HEA 200").
  - when the user selects a section, pass this identifier to the controller,
    NOT just the name string.

- The VerificationController (or an adapter in the core) MUST:
  - resolve the selected section ID via a repository service, e.g.:
    - get_section_by_id(section_id) -> SectionLike,
  - attach the resulting SectionLike object to CalcInput.section,
  - NEVER duplicate or re-encode geometric properties inside the GUI layer.

- As a result, when a section is selected in the GUI:
  - the verification engine will always receive:
    - the full, up-to-date geometric parameters from the geometry module,
    - no stale or partially copied data.

B) Material selection → mechanical parameters in CalcInput

- Similarly, the material repository MUST be the single source of truth for:
  - f_ck, f_yk, E_c, E_s, classes, etc.
- The GUI (combobox/list for “Materiale”) MUST:
  - store a stable material ID/key per option,
  - pass this ID to the controller when the user selects a material.

- The VerificationController MUST:
  - resolve the material ID via:
    - get_material_by_id(material_id) -> MaterialLike,
  - attach the resulting MaterialLike object to CalcInput.material,
  - NEVER hard-code material parameters in GUI modules.

C) One-way data flow and modularity

- Data flow MUST be:
  - GUI selection → controller → repositories → CalcInput,
  - CalcInput → validation/verification → CalcOutput → GUI.
- GUI code MUST NOT:
  - calculate section properties or material design parameters,
  - replicate the logic of geometry or material modules.
- Any conversion or additional parameters needed for CalcInput MUST be handled
  in core or adapter modules, not scattered throughout GUI code.

========================================
CIRCULAR REBAR HELPER UTILITY (CORE + GUI)
========================================

To support automatic and reliable reinforcement input for circular and hollow
circular sections, you MUST implement a dedicated helper utility in the core,
with an associated GUI dialog.

A) Core helper module (pure functions)

- Create (or refine) a core module, e.g.:
  - app/core/helpers/rebar_circular.py
- It MUST contain pure functions (no Tkinter, no file I/O), for example:

  - def arrange_circular_rebars(
        section_geometry: CircularSectionLike,
        n_bars: int,
        bar_diameter: float,
        cover: float,
        inner_radius: float | None = None,
    ) -> CircularRebarLayout:

    - Computes:
      - positions of each bar (x_i, y_i) in the section reference system,
          arranged radially and uniformly along the circumference;
      - total reinforcement area (A_s,eq = n_bars * A_bar),
      - centroid of the reinforcement (x_g, y_g),
      - any additional derived quantities useful for CalcInput (e.g. distances
          to extreme fibres, effective d and d' if applicable).

- Define a data structure for the result, e.g.:

  @dataclass
  class CircularRebarLayout:
      n_bars: int
      bar_diameter: float
      bar_area: float
      bar_positions: list[tuple[float, float]]  # (x, y) for each bar
      As_total: float
      x_g: float
      y_g: float
      notes_it: str

- The helper MUST:
  - support both solid circular sections and hollow circular sections:
    - outer_radius,
    - inner_radius (None for solid),
  - respect a radial placement logic:
    - bars placed at a radius:
      - r_eff = outer_radius - cover - bar_diameter / 2
    - uniformly distributed in angle:
      - θ_k = 2π * k / n_bars, for k = 0..n_bars-1,
  - be ready to extend to multi-ring layouts in future (but do not over-implement).

B) Integration with CalcInput

- The controller (or a dedicated adapter) MUST use CircularRebarLayout to:
  - set:
    - CalcInput.As, CalcInput.As_prime (if derivable),
    - CalcInput.d, CalcInput.d_prime (if meaningful),
  - store bar_positions and (x_g, y_g) in:
    - CalcInput.extra["rebar_positions"],
    - CalcInput.extra["rebar_centroid"],
    or similar fields, so that:
      - the verification engine and logging can access them,
      - the calibration module can use them in tests.

- The helper MUST NOT:
  - change global state,
  - depend on GUI,
  - perform normative checks (those stay in validation/verification).

C) GUI dialog for circular rebar helper (Italian labels)

- Implement a GUI dialog/panel, e.g. in app/gui/rebar_circular_dialog.py:

  - Title: "Disposizione automatica armature circolari"
  - Inputs:
    - Sezione circolare selezionata (read-only: name + radii),
    - Numero barre: [input],
    - Diametro barre: [input],
    - Copriferro: [input],
    - (opzionale) Sezione cava: [checkbox], raggio interno: [input].
  - Buttons:
    - "Calcola disposizione"
    - "Applica alla riga"
    - "Chiudi"
  - Outputs:
    - tabella/anteprima con (x, y) delle barre (anche solo come testo),
    - As_total, x_g, y_g,
    - eventuali messaggi/tooltip con riferimenti normativi (se si applicano
      limiti minimi o massimi, quando implementati).

- The dialog MUST:
  - call the core helper arrange_circular_rebars(...) with the correct
    section_geometry object from the geometry module,
  - show results to the user in Italian,
  - when the user clicks "Applica alla riga":
    - update the current row’s As, d (and possibly As’, d’),
    - store rebar geometry in a way the controller can include in CalcInput.extra.

D) Validation and normative consistency

- The Validation Engine MUST:
  - perform geometric plausibility checks on circular layouts, e.g.:
    - r_eff > 0,
    - bars do not intersect or lie outside the section,
    - min/max reinforcement density if/when normative limits are implemented.
- For any check that is based on explicit normative rules (e.g. minimum spacing,
  minimum reinforcement ratio) you MUST:
  - attach appropriate NormReference to ValidationIssue,
  - provide Italian messages for the GUI.

E) Logging

- When the circular rebar helper is used, the verification logs SHOULD include:
  - number of bars, bar diameter, cover,
  - resulting As_total, x_g, y_g,
  - a short description of the placement rule (e.g. "distribuzione radiale uniforme").
- These logs must help to debug and to validate that the helper works correctly
  for calibration and benchmark cases.

  ========================================
STRICT USE OF REPOSITORIES IN CONTROLLERS
========================================
To guarantee that the data passed from GUI selections (section/material lists,
dropdowns, etc.) to the verification engine is always correct, up-to-date and
non-duplicated, you MUST enforce the following rule:

A) Controllers MUST use repositories, NOT ad-hoc data

- GUI controllers (e.g. VerificationController, CalibrationController, dialogs
  for section/material selection) MUST:
  - use ONLY the official repositories/services for:
    - sections (geometry module),
    - materials (material module),
    - norms (normative registry),
  - and MUST NOT:
    - store their own copies of geometric or mechanical parameters,
    - reconstruct Section or Material objects from raw GUI fields or strings.

- Concretely:
  - when the user selects a section from a combobox/list:
    - the GUI passes the section ID/key to the controller,
    - the controller resolves it via a repository function, e.g.:
      - section = section_repository.get_section_by_id(section_id)
    - the controller sets:
      - calc_input.section = section
  - when the user selects a material:
    - the GUI passes the material ID/key,
    - the controller resolves it via:
      - material = material_repository.get_material_by_id(material_id)
    - the controller sets:
      - calc_input.material = material

B) No manual reconstruction of section/material parameters in controllers

- Controllers MUST NOT:
  - compute geometric properties (area, inertia, centroid) in their own code,
  - hard-code f_ck, f_yk, E_c, E_s, γ factors, etc. inside GUI/controller code,
  - parse description strings like "Rettangolare 30x50" to rebuild b, h, etc.
- All such information MUST:
  - come from the geometry repository (for sections),
  - come from the material repository (for materials),
  - come from the normative registry (for parameters and factors).

C) One consistent path for section/material data

- The ONLY allowed path for section/material data is:

  User selection in GUI
      ↓
  Controller receives IDs/keys (NOT raw parameters)
      ↓
  Controller calls repositories (get_section_by_id / get_material_by_id)
      ↓
  SectionLike / MaterialLike objects attached to CalcInput
      ↓
  Validation Engine and Verification Service consume these objects

- This ensures:
  - no duplication of business logic between GUI and core,
  - a single point of maintenance for geometry and material properties,
  - that any future changes in geometry/material modules automatically propagate
    to all verifications without altering GUI code.

D) Adapters instead of duplication

- If legacy GUI code currently builds sections or materials manually from user
  inputs, you MUST:
  - introduce small adapter functions in a dedicated adapter module (core side)
    that convert legacy structures into SectionLike / MaterialLike expected by
    CalcInput,
  - refactor controllers to call these adapters,
  - progressively phase out manual reconstruction in GUI code.
- Under no circumstances should new controller code introduce fresh duplication
  of section/material parameter logic.

========================================
STRICT USE OF REPOSITORIES IN CONTROLLERS
========================================

To guarantee that the data passed from GUI selections (section/material lists,
dropdowns, etc.) to the verification engine is always correct, up-to-date and
non-duplicated, you MUST enforce the following rule:

A) Controllers MUST use repositories, NOT ad-hoc data

- GUI controllers (e.g. VerificationController, CalibrationController, dialogs
  for section/material selection) MUST:
  - use ONLY the official repositories/services for:
    - sections (geometry module),
    - materials (material module),
    - norms (normative registry),
  - and MUST NOT:
    - store their own copies of geometric or mechanical parameters,
    - reconstruct Section or Material objects from raw GUI fields or strings.

- Concretely:
  - when the user selects a section from a combobox/list:
    - the GUI passes the section ID/key to the controller,
    - the controller resolves it via a repository function, e.g.:
      - section = section_repository.get_section_by_id(section_id)
    - the controller sets:
      - calc_input.section = section
  - when the user selects a material:
    - the GUI passes the material ID/key,
    - the controller resolves it via:
      - material = material_repository.get_material_by_id(material_id)
    - the controller sets:
      - calc_input.material = material

B) No manual reconstruction of section/material parameters in controllers

- Controllers MUST NOT:
  - compute geometric properties (area, inertia, centroid) in their own code,
  - hard-code f_ck, f_yk, E_c, E_s, γ factors, etc. inside GUI/controller code,
  - parse description strings like "Rettangolare 30x50" to rebuild b, h, etc.
- All such information MUST:
  - come from the geometry repository (for sections),
  - come from the material repository (for materials),
  - come from the normative registry (for parameters and factors).

C) One consistent path for section/material data

- The ONLY allowed path for section/material data is:

  User selection in GUI
      ↓
  Controller receives IDs/keys (NOT raw parameters)
      ↓
  Controller calls repositories (get_section_by_id / get_material_by_id)
      ↓
  SectionLike / MaterialLike objects attached to CalcInput
      ↓
  Validation Engine and Verification Service consume these objects

- This ensures:
  - no duplication of business logic between GUI and core,
  - a single point of maintenance for geometry and material properties,
  - that any future changes in geometry/material modules automatically propagate
    to all verifications without altering GUI code.

D) Adapters instead of duplication

- If legacy GUI code currently builds sections or materials manually from user
  inputs, you MUST:
  - introduce small adapter functions in a dedicated adapter module (core side)
    that convert legacy structures into SectionLike / MaterialLike expected by
    CalcInput,
  - refactor controllers to call these adapters,
  - progressively phase out manual reconstruction in GUI code.
- Under no circumstances should new controller code introduce fresh duplication
  of section/material parameter logic.

  ========================================
FINAL INTEGRATION BLOCK — NON‑AMBIGUOUS RULES FOR CONTROLLERS,
REPOSITORIES, VERIFICATION SERVICE, CIRCULAR REBAR HELPER,
CALIBRATION MODULE AND NORMATIVE COMPLIANCE
========================================

This block consolidates ALL mandatory rules governing:

- GUI ↔ controller ↔ repository interactions,
- construction of CalcInput,
- correctness of normative verification,
- circular reinforcement helpers,
- dynamic calibration/benchmark system,
- templates, validation and verification orchestration.

These rules OVERRIDE any ambiguous interpretation and MUST be followed
strictly by all modules generated, refactored, or extended by Copilot.

====================================================================

1) STRICT CONTROLLER–REPOSITORY INTEGRATION (MANDATORY)
====================================================================
GUI controllers MUST obtain ALL structural, geometric and mechanical data
EXCLUSIVELY from repositories — NEVER from GUI text, user strings,
manually parsed values, or local copies.

GUI → Controller MUST pass ONLY:

- section_id
- material_id
- numeric input fields for loads and reinforcement (N, Mx, My, Tx, Ty, Mz,
   As, As', d, d', staffe, etc.)
- auxiliary options (LC/FC inputs if applicable)

GUI MUST NOT:

- duplicate geometry or material parameters,
- reconstruct section/material from strings like “Rettangolare 30×50”,
- store secondary copies of fck, E, area, inertia, etc.

Controller MUST:

- receive SectionRepository and MaterialRepository via constructor.
- resolve objects with:
       section = section_repository.get_section_by_id(section_id)
       material = material_repository.get_material_by_id(material_id)
- attach these objects to CalcInput.section and CalcInput.material.
- NEVER compute geometry or materials directly.
- NEVER parse display names to compute section parameters.

There is ONE valid data flow:

  GUI selection → IDs → Controller → Repositories → SectionLike/MaterialLike →
  CalcInput → Validation Engine → Verification Service → CalcOutput → GUI

Controllers MUST NOT bypass this path.

====================================================================
2) CIRCULAR REBAR HELPER (CORE + GUI)
====================================================================

You MUST implement a **pure core helper** to automatically arrange rebar in
circular or hollow circular sections.

Core function signature example:

  def arrange_circular_rebars(
        section_geometry: CircularSectionLike,
        n_bars: int,
        bar_diameter: float,
        cover: float,
        inner_radius: float | None = None,
    ) -> CircularRebarLayout

The helper MUST compute:

- bar positions (x_i, y_i) equally spaced on radius:
       r_eff = outer_radius - cover - bar_diameter / 2
- As_total = n_bars * area(bar_diameter)
- reinforcement centroid (x_g, y_g)
- optional: As / As' if derivable
- optional: effective d and d' if section orientation known

The helper MUST:

- NOT depend on GUI
- NOT compute normative checks
- NOT duplicate geometry logic
- return a dataclass (CircularRebarLayout) containing:
       n_bars, bar_positions, bar_area, As_total, x_g, y_g, notes_it

The controller MUST:

- call the helper using the actual CircularSectionLike from repository,
- populate CalcInput.extra with:
       "rebar_positions": [...],
       "rebar_centroid": (x_g, y_g),
- update As, d, etc. in CalcInput if meaningful.

A GUI dialog MUST:

- read the selected section_id,
- resolve section object via repository,
- call helper,
- display the radial layout,
- apply results to current row when user confirms.

====================================================================
3) COMPLETE, ACCURATE NORMATIVE VERIFICATION (NO SHORTCUTS)
====================================================================

You MUST strictly enforce normative correctness.

Forbidden:

- invented formulas,
- invented coefficients,
- heuristic shortcuts,
- “simplified” or “approximate” checks,
- mixing TA and SLU logic,
- skipping shear/torsion/minima/tensioni checks when norm requires them,
- silently omitting parts of a normative procedure.

Permitted sources:

- existing code in repository (RD 2229, DM92, DM96, NTC 2008, NTC 2018),
- technical references used earlier (Santarella, Giangreco),
- official PDFs, EC2 Annex I, prEN 1990‑2,
- JSON/CSV normative data already included or added.

If a normative clause is unclear:

- DO NOT invent; mark with a TODO referencing exact clause needed.

If a check is not fully implemented:

- the GUI MUST show:
     “Verifica non disponibile per questa normativa.”
- or template must be marked as partial with TODO.

ALL normative references must be encoded via NormReference
(norm_code, chapter, paragraph, formula_label).

====================================================================
4) VERIFICATION SERVICE CONTRACT (UNIFORM & MANDATORY)
====================================================================

The verification engine MUST expose:

  run_verifications_for_element(calc_input, active_norm, enabled_limit_states)
  run_verifications_for_all(calc_inputs, active_norm, enabled_limit_states)

Flow:

 1) template selection (core-only)
 2) validation (validate_calc_input)
 3) if validation errors → STOP, no template execution
 4) execute ALL templates relevant for selected norm & limit states
 5) compute per-template SingleCheckResult
 6) aggregate into CalcOutput with:
       ok, per_template_results, summary_metrics, validation_result

CalcOutput MUST index results by template_id and MUST include all
NormReference entries associated with each template.

Controller MUST NOT run verification logic directly.

====================================================================
5) VALIDATION ENGINE CONTRACT (MANDATORY)
====================================================================

Validation MUST:

- use ONLY data from CalcInput.section and CalcInput.material objects
   coming from repositories,
- never rely on GUI strings,
- validate geometry, materials, LC/FC, norm compatibility,
- attach NormReference when validation rule has normative origin,
- produce structured ValidationResult,
- decide error vs warning exactly as specified.

ValidationResult.has_errors MUST block verification.

====================================================================
6) VERIFICATION TEMPLATES (EXHAUSTIVE PER NORM)
====================================================================

For each norm, the registry MUST define templates for ALL normative checks
the software claims to support:

 TA (RD 2229, DM92/96):

- bending (flessione)
- deviated bending (presso/tenso-flessione)
- shear, torsion, shear-torsion
- tensioni ammissibili
- minimum reinforcement

 NTC 2008 / NTC 2018:

- SLU bending
- SLU shear
- SLU torsion
- SLU shear–torsion interaction
- SLE stresses (σ_c,max, σ_s,max)
- crack width (if included)
- deformazioni (if included)
- minima

 EC2 Annex I / prEN 1990‑2 (existing structures):

- LC/FC application
- modified design values
- SLU/SLE checks valid for assessment context

Template MUST contain:
   template_id, norm_code, verification_type, limit_state,
   check_category, required_inputs, output_metrics,
   primary_reference, secondary_references,
   function_path.

====================================================================
7) CALIBRATION MODULE (DYNAMIC BENCHMARK CREATION)
====================================================================

A complete calibration/benchmark subsystem MUST exist:

Core API:
  run_calibration_case(calc_input, expected_output, active_norm, tolerance)
  save_calibration_case(...)
  load_calibration_cases(...)
  generate_pytest_file(...)

Users MUST be able to:

- input full CalcInput parameters,
- input expected results from external validated software,
- compare actual vs expected,
- view mismatches per template,
- save benchmark cases to JSON/CSV,
- generate pytest tests enforcing correctness.

CalibrationResult MUST:

- list mismatches (expected vs actual),
- expose validation issues,
- integrate template IDs and NormReference.

Controller MUST integrate calibration GUI panel into the application.

No shortcut: any mismatch MUST appear in GUI and fail benchmarks.

====================================================================
8) GUI CONSTRAINTS (ITALIAN UI, TOOLTIP NORMS)
====================================================================

All user-facing text MUST be in Italian.

Each GUI field must have:

- clear tooltip with:
  - normative reference,
  - formula,
  - chapter/paragraph,
  - short explanation.

GUI MUST NOT:

- compute geometry or materials,
- generate normative checks,
- override core values,
- maintain hidden duplicate parameters.

====================================================================
9) LOGGING
====================================================================

Logging MUST document:

- inputs (CalcInput),
- validation issues,
- executed templates,
- intermediate results (asse neutro, R_d, σ_c, σ_s),
- normative references used.

====================================================================
10) NO‑SCORCH SHORTCUT POLICY (ABSOLUTE RULE)
====================================================================

Copilot MUST NOT:

- invent formulas,
- alter normative procedures,
- use approximate or heuristic checks,
- omit required checks,
- compute geometry/materials in controllers/GUI,
- bypass repositories or normative registry,
- generate inconsistent CalcInput.

All deviation MUST be flagged with TODO + normative reference.

========================================
END OF FINAL INTEGRATION BLOCK
========================================

You are GitHub Copilot (Plan) working on my Python/Tkinter structural
engineering app.

ROLE & SESSION CONSTRAINTS

- You act as a cautious, senior structural engineer/developer for a
  civil/structural engineering tool.
- This Plan MUST be executed within a SINGLE Copilot Plan session:
  - Do NOT start nested plans or sub-sessions.
  - Do NOT perform trivial, mechanical tasks that waste premium capacity
    (e.g. reformatting the entire repo, mass renaming without need,
     adding boilerplate comments everywhere).
- You MUST infer:
  - file paths,
  - module names,
  - project structure
  directly by scanning the workspace. Do NOT ask me for paths unless
  it is impossible to infer them.
- You may ask follow-up questions ONLY when strictly necessary and
  concisely, within this single Plan session.

HOW TO READ THIS SPEC

- These instructions are stored in a file in the repository
  (e.g. docs/copilot_plan.md).
- Treat this file as the authoritative, integrated specification for
  this Plan.
- Do NOT assume example paths/names are correct; always confirm by
  scanning the actual codebase.

UI LANGUAGE REQUIREMENT

- ALL user-facing interface text MUST be in Italian:
  - window titles,
  - labels,
  - buttons,
  - tooltips,
  - table headers,
  - messages (error/warning/info),
  - status bar texts,
  - menu items.
- Internal code (function names, variables, docstrings) can be in
  English, but any text shown to the user must be Italian.

GLOBAL PRINCIPLES

- Respect strict separation of concerns:
  - GUI (Tkinter) ONLY handles user interaction, layout, and rendering.
  - Core modules handle:
    - geometry,
    - materials,
    - normative registry/configuration,
    - validation,
    - verification,
    - helpers (e.g. circular rebar),
    - calibration.
- Geometry and materials modules are already functioning and MUST NOT
  be rewritten. Adjust only wiring and contracts where necessary.
- Many calculation codes already exist, especially for:
  - tensioni ammissibili (RD 2229/39, DM 1992/1996),
  - NTC 2008,
  - NTC 2018.
  You MUST reuse them and refactor minimally for modularity and tests.
- NEVER invent structural rules or normative values.
  - If a normative detail is unclear:
    - mark TODO with a brief explanation,
    - do NOT guess formulas or coefficients.

====================================================================
NORMATIVE SCOPE & COMPLETENESS PER NORM
====================================================================

Supported norms (present or planned):

- RD 2229/39 (tensioni ammissibili, calcestruzzo armato storico)
- DM 14/02/1992 (TA)
- DM 9/1/1996 (TA)
- NTC 2008 (SLU/SLE)
- NTC 2018 (SLU/SLE, Cap. 8 per strutture esistenti, LC/FC)
- EC2 EN 1992-1-1:2023 (Annex I per strutture esistenti)
- prEN 1990-2 (assessment of existing structures)

For each norm, within the scope of the software, all relevant checks
MUST be implemented completely (not partially) if the software claims
to support them:

- flessione (semplice, deviata, presso/tenso-flessione)
- taglio
- torsione
- taglio + torsione
- tensioni di esercizio (SLE)
- verifiche a tensioni ammissibili (TA)
- verifiche a SLU / SLC / SLE
- minimi di armatura (flessione, taglio)
- fessurazione / apertura fessure
- deformazioni ammissibili (where applicable)

If a check is not yet implemented for a given norm:

- DO NOT implement a fake or partial check and present it as complete.
- Either:
  - disable that check in the GUI with an Italian message:
    "Verifica non disponibile per questa normativa."
  - or mark the corresponding template as partial with clear TODO
    explaining which normative steps are missing.

====================================================================
STRICT CONTROLLER–REPOSITORY INTEGRATION (MANDATORY)
====================================================================

To avoid any ambiguity between GUI selections and engine data, all GUI
controllers MUST use ONLY repositories for sections, materials and norms.

A) GUI → Controller

- GUI views MUST pass ONLY:
  - stable identifiers:
    - section_id
    - material_id
  - numeric inputs:
    - N, Mx, My, Tx, Ty, Mz
    - As, As', d, d'
    - staffe_diametro, staffe_num_bracci, staffe_passo
    - LC, FC if applicable
- GUI MUST NOT:
  - compute geometric parameters (b, h, area, Ixx, etc.),
  - compute material parameters (f_ck, f_yk, E_c, E_s, etc.),
  - reconstruct Section/Material from strings,
  - cache or duplicate geometry/material values.

B) Controller behaviour

- Controllers (e.g. VerificationController, CalibrationController)
  MUST:
  - receive repositories via constructor:
      section_repository: SectionRepository
      material_repository: MaterialRepository
  - resolve selected IDs:
      section = section_repository.get_section_by_id(section_id)
      material = material_repository.get_material_by_id(material_id)
  - attach these objects:
      calc_input.section = section
      calc_input.material = material
  - NEVER:
    - recompute geometry,
    - recompute material properties,
    - parse GUI strings like "Rettangolare 30x50" to derive geometry.

C) Allowed data flow
Only this data flow is allowed:

GUI selection → section_id, material_id → Controller →
Repositories → SectionLike/MaterialLike → CalcInput →
Validation Engine → Verification Service → CalcOutput → GUI

Any other path is forbidden.

====================================================================
CORE CONTRACTS: CalcInput, CalcOutput & SingleCheckResult
====================================================================

You MUST define/refine core contracts in a GUI-free module
(e.g. app/core/contracts.py).

Conceptual design (names may adapt to the existing repo):

- CalcInput:
  - element_name: str
  - section: SectionLike
  - material: MaterialLike
  - norm_code: str
  - limit_states_enabled: list[str]  # ["TA", "SLU", "SLE", ...]
  - lc: str | None  # LC1, LC2, LC3, or None
  - fc: float | None
  - N, Mx, My, Tx, Ty, Mz: float | None
  - As, As_prime: float | None
  - d, d_prime: float | None
  - staffe_diametro: float | None
  - staffe_num_bracci: int | None
  - staffe_passo: float | None
  - area_ferri_piegati: float | None
  - extra: dict[str, Any]

- SingleCheckResult:
  - template_id: str
  - ok: bool
  - utilisation: float | None
  - details: dict[str, float | str]
  - norm_references: list[NormReference]
  - messages_it: list[str]
  - check_category: str | None
  - limit_state: str | None

- CalcOutput:
  - element_name: str
  - norm_code: str
  - ok: bool
  - per_template_results: dict[str, SingleCheckResult]
  - validation_result: ValidationResult | None
  - summary_metrics: dict[str, float | bool | str]

====================================================================
NORMREFERENCE & VERIFICATIONTEMPLATE (SUMMARY)
====================================================================

- NormReference:
  - norm_code: str
  - chapter: str
  - paragraph: str
  - formula_label: str | None
  - description_it: str
  - notes_it: str | None
  - source_type: str | None
  - priority: int | None

- VerificationTemplate:
  - template_id: str
  - norm_code: str
  - norm_version: str | None
  - verification_type: str
  - limit_state: str  # "TA", "SLU", "SLE", "SLC", ...
  - description_it: str
  - check_category: str
  - required_inputs: list[str]
  - optional_inputs: list[str]
  - output_metrics: list[str]
  - primary_reference: NormReference | None
  - secondary_references: list[NormReference]
  - function_path: str  # dotted path
  - can_batch: bool
  - supports_real_time: bool
  - applicable_section_types: list[str] | None
  - applicable_material_tags: list[str] | None
  - requires_existing_structure: bool
  - extra_params: dict[str, Any]

Templates MUST cover all check families for each norm.

====================================================================
VALIDATION ENGINE SKELETON (CORE)
====================================================================

You MUST implement a Validation Engine in core, independent from GUI,
returning structured ValidationResult / ValidationIssue.

Example skeleton to respect/extend:

    from dataclasses import dataclass, field
    from typing import Any, Dict, List, Sequence

    @dataclass
    class ValidationIssue:
        severity: str           # "info", "warning", "error"
        field: str              # e.g. "d", "As", "materiale"
        code: str               # machine code
        message_it: str         # Italian user message
        norm_reference: NormReference | None = None
        context: Dict[str, Any] = field(default_factory=dict)

        def is_error(self) -> bool:
            return self.severity.lower() == "error"

        def is_warning(self) -> bool:
            return self.severity.lower() == "warning"


    @dataclass
    class ValidationResult:
        issues: List[ValidationIssue] = field(default_factory=list)

        @property
        def has_errors(self) -> bool:
            return any(i.is_error() for i in self.issues)

        @property
        def has_warnings(self) -> bool:
            return any(i.is_warning() for i in self.issues)

        def add_issue(self, issue: ValidationIssue) -> None:
            self.issues.append(issue)

        def extend(self, issues: Sequence[ValidationIssue]) -> None:
            self.issues.extend(issues)


    def validate_calc_input(calc_input, active_norm, templates) -> ValidationResult:
        # MUST:
        #  - check geometry consistency (d, d', As, etc.)
        #  - check material ranges and LC/FC correctness
        #  - check norm-template compatibility
        #  - attach NormReference where checks are normative
        #  - remain GUI-free
        result = ValidationResult()
        # TODO: implement _validate_geometry, _validate_materials,
        #       _validate_norm_compatibility and aggregate here.
        return result

ValidationResult.has_errors MUST block verification.

====================================================================
VERIFICATION SERVICE SKELETON (CORE)
====================================================================

You MUST implement a verification service that orchestrates validation
and verification templates, as in this skeleton:

    @dataclass
    class SingleCheckResult:
        template_id: str
        ok: bool
        utilisation: float | None = None
        details: Dict[str, float | str] = field(default_factory=dict)
        norm_references: List[NormReference] = field(default_factory=list)
        messages_it: List[str] = field(default_factory=list)
        check_category: str | None = None
        limit_state: str | None = None


    @dataclass
    class CalcOutput:
        element_name: str
        norm_code: str
        ok: bool
        per_template_results: Dict[str, SingleCheckResult] = field(default_factory=dict)
        validation_result: ValidationResult | None = None
        summary_metrics: Dict[str, float | bool | str] = field(default_factory=dict)


    def run_verifications_for_element(
        calc_input: CalcInput,
        active_norm: NormPlugin,
        enabled_limit_states: Sequence[str] | None = None,
    ) -> CalcOutput:
        # 1) select templates for element+norm
        templates = _select_templates_for_element(
            calc_input=calc_input,
            active_norm=active_norm,
            enabled_limit_states=enabled_limit_states,
        )

        # 2) validate input
        validation_result = validate_calc_input(calc_input, active_norm, templates)
        if validation_result.has_errors:
            # MUST NOT execute any check
            return CalcOutput(
                element_name=getattr(calc_input, "element_name", ""),
                norm_code=getattr(active_norm, "code", "UNKNOWN"),
                ok=False,
                per_template_results={},
                validation_result=validation_result,
                summary_metrics={"status": "NON_VERIFICATO_PER_ERRORI_INPUT"},
            )

        # 3) execute ALL templates
        per_template_results: Dict[str, SingleCheckResult] = {}
        for tpl in templates:
            res = _execute_template(tpl, calc_input, active_norm)
            per_template_results[res.template_id] = res

        # 4) aggregate
        global_ok = all(r.ok for r in per_template_results.values())
        max_util = _compute_max_utilisation(per_template_results.values())
        controlling_tpl = _find_controlling_template_id(per_template_results)

        summary = {
            "status": "OK" if global_ok else "NON_OK",
            "utilizzazione_massima": max_util if max_util is not None else 0.0,
            "template_controllante": controlling_tpl or "",
        }
        if validation_result.has_warnings:
            summary["warning_validazione"] = True

        return CalcOutput(
            element_name=getattr(calc_input, "element_name", ""),
            norm_code=getattr(active_norm, "code", "UNKNOWN"),
            ok=global_ok,
            per_template_results=per_template_results,
            validation_result=validation_result,
            summary_metrics=summary,
        )


    def run_verifications_for_all(
        calc_inputs: Sequence[CalcInput],
        active_norm: NormPlugin,
        enabled_limit_states: Sequence[str] | None = None,
    ) -> List[CalcOutput]:
        return [
            run_verifications_for_element(ci, active_norm, enabled_limit_states)
            for ci in calc_inputs
        ]

You MUST complete _select_templates_for_element and _execute_template using
existing calculation functions for each norm.

====================================================================
VERIFICATION CONTROLLER SKELETON (GUI)
====================================================================

Controllers MUST orchestrate GUI ↔ core, using repositories and NEVER
duplicating geometry/material logic. The following skeleton MUST be
respected and extended:

    @dataclass
    class VerificationControllerConfig:
        enabled_limit_states: Sequence[str]


    class VerificationController:
        def __init__(
            self,
            root: Tk,
            view: "VerificationViewProtocol",
            norm_plugin: NormPlugin,
            section_repository: SectionRepository,
            material_repository: MaterialRepository,
            config: VerificationControllerConfig,
        ) -> None:
            self._root = root
            self._view = view
            self._norm_plugin = norm_plugin
            self._section_repo = section_repository
            self._material_repo = material_repository
            self._config = config
            self._wire_view_events()

        def _wire_view_events(self) -> None:
            self._view.set_row_edit_finished_callback(self.on_row_edit_finished)
            self._view.set_recalculate_all_callback(self.on_recalculate_all)

        def on_row_edit_finished(self, row_index: int) -> None:
            # 1) build CalcInput from row (using repositories)
            # 2) run_verifications_for_element()
            # 3) update row with CalcOutput
            ...

        def on_recalculate_all(self) -> None:
            # 1) build CalcInput for all rows
            # 2) run_verifications_for_all()
            # 3) update grid
            ...

        def _build_calc_input_from_row(self, row_index: int) -> CalcInput:
            raw = self._view.get_row_input_data(row_index)
            section_id = raw.get("section_id")
            material_id = raw.get("material_id")
            if not section_id or not material_id:
                raise ValueError("section_id/material_id mancanti")

            section = self._section_repo.get_section_by_id(section_id)
            material = self._material_repo.get_material_by_id(material_id)
            if section is None:
                raise ValueError(f"Sezione non trovata: {section_id}")
            if material is None:
                raise ValueError(f"Materiale non trovato: {material_id}")

            raw["section"] = section
            raw["material"] = material
            # Remove IDs if you want to avoid duplication
            # raw.pop("section_id", None)
            # raw.pop("material_id", None)
            return CalcInput(**raw)

        def _apply_output_to_row(self, row_index: int, output: CalcOutput) -> None:
            # update_row_status + update_row_check_result + mark errors/warnings
            ...


    class VerificationViewProtocol:
        def set_row_edit_finished_callback(self, callback): ...
        def set_recalculate_all_callback(self, callback): ...
        def iter_row_indices(self) -> Sequence[int]: ...
        def get_row_input_data(self, row_index: int) -> dict[str, Any]: ...
        def update_row_status(self, row_index: int, ok: bool, status_it: str,
                              utilisation: Optional[float],
                              controlling_template_id: str) -> None: ...
        def update_row_check_result(self, row_index: int, template_id: str,
                                    ok: bool, utilisation: Optional[float],
                                    check_category: Optional[str],
                                    limit_state: Optional[str],
                                    messages_it: Sequence[str],
                                    norm_references: Sequence[Any]) -> None: ...
        def mark_field_error(self, row_index: int, field_name: str,
                             message_it: str) -> None: ...
        def mark_field_warning(self, row_index: int, field_name: str,
                               message_it: str) -> None: ...
        def show_row_error(self, row_index: int, message_it: str) -> None: ...

You MUST integrate the real view with this protocol.

====================================================================
CIRCULAR REBAR HELPER SKELETON (CORE)
====================================================================

You MUST implement the circular rebar helper as core code:

    @dataclass
    class CircularRebarLayout:
        n_bars: int
        bar_diameter: float
        bar_area: float
        bar_positions: list[tuple[float, float]]
        As_total: float
        x_g: float
        y_g: float
        notes_it: str = ""


    def arrange_circular_rebars(
        section_geometry: CircularSectionLike,
        n_bars: int,
        bar_diameter: float,
        cover: float,
        inner_radius: float | None = None,
    ) -> CircularRebarLayout:
        """Dispose radially uniform rebars in a circular/circular-hollow section.

        - Use outer_radius from section_geometry.
        - Place bars at r_eff = outer_radius - cover - bar_diameter/2.
        - Angles: theta_k = 2*pi*k / n_bars.
        - Compute As_total and centroid (x_g, y_g).
        """
        # TODO: implement using math (sin, cos), respecting geometry.
        ...

Controller and GUI dialog MUST use this helper only, not re-implement
circular layouts.

====================================================================
CALIBRATION MODULE SKELETON (CORE)
====================================================================

You MUST implement a dynamic calibration/benchmark module:

    @dataclass
    class CalibrationCase:
        id: str
        description_it: str
        calc_input: CalcInput
        expected_output: dict
        norm_code: str
        linked_templates: list[str]
        references: list[NormReference]
        tolerance: dict[str, float]
        metadata: dict[str, Any]


    @dataclass
    class CalibrationMismatch:
        template_id: str
        key: str
        expected: float
        actual: float
        diff: float
        tolerance: float
        message_it: str
        norm_reference: NormReference | None = None


    @dataclass
    class CalibrationResult:
        passed: bool
        mismatches: list[CalibrationMismatch]
        validation_issues: ValidationResult
        actual_output: CalcOutput | None
        expected_output: dict


    def run_calibration_case(
        calc_input: CalcInput,
        expected_output: dict,
        active_norm: NormPlugin,
        tolerance: dict[str, float],
    ) -> CalibrationResult:
        validation = validate_calc_input(calc_input, active_norm, [])
        if validation.has_errors:
            return CalibrationResult(
                passed=False,
                mismatches=[],
                validation_issues=validation,
                actual_output=None,
                expected_output=expected_output,
            )

        actual_output = run_verifications_for_element(calc_input, active_norm)
        mismatches = _compare_outputs(expected_output, actual_output, tolerance)

        return CalibrationResult(
            passed=len(mismatches) == 0,
            mismatches=mismatches,
            validation_issues=validation,
            actual_output=actual_output,
            expected_output=expected_output,
        )


    def _compare_outputs(
        expected: dict,
        actual: CalcOutput,
        tolerance: dict[str, float],
    ) -> list[CalibrationMismatch]:
        # TODO: compare per_template_results vs expected values:
        #   - utilisations
        #   - key details (sigma_c, sigma_s, M_Rd, V_Rd, etc.)
        # and build CalibrationMismatch entries.
        return []

Calibration GUI MUST:

- allow user to enter calc_input fields + expected metrics,
- call run_calibration_case,
- show mismatches, and optionally offer to persist the case and
   generate pytest tests.

====================================================================
NO-SHORTCUT, NO-INVENTION POLICY (FINAL)
====================================================================

Copilot MUST NEVER:

- invent formulas,
- approximate normative procedures without marking TODO,
- bypass repositories,
- compute geometry/materials inside GUI/controller,
- skip normative checks.

All normative logic MUST:

- be traceable to:
  - existing code,
  - JSON/CSV parameters,
  - official norms or recognized technical references,
- be wrapped in pure functions in the core (no Tkinter).

Any uncertainty MUST be:

- marked with TODO + short explanation,
- never silently resolved by guessing.

========================================
END OF FULL INTEGRATION PROMPT
========================================
