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

2) RESTORE STARTUP (`python -m app.main`)
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

3) RECREATE / FIX THE VERIFICATION MODULE
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

4) CHECK AND REPAIR GUI WIRING (INCL. REAL-TIME & BULK BUTTON)
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

5) EXTEND MATERIAL MODULE FOR EXISTING STRUCTURES (LC/FC)
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

6) ULTRA-MODULAR NORMATIVE CONFIGURATION MODULES (CORE + GUI)
- Design and implement (where changes are minimal but useful) a modular structure
  for normative parameters and coefficients (normative registry, templates, validation,
  scenario comparison, report objects, helpers), as already detailed above.
- All new GUI elements must:
  - use Italian labels and texts,
  - be integrated with minimal changes to existing GUI modules.

7) LOGGING & TRACEABILITY
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

8) TESTS & QUALITY (INCLUDING GRANULAR TESTS BY NORM)
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

9) FINAL LINTING & FUNCTIONAL VERIFICATION
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

