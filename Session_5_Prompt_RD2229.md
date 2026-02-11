Session_5_Prompt_RD2229
I am starting a NEW Claude Code session.

CONTEXT
- This repository is a Python/Tkinter structural engineering application.
- The single authoritative specification is the file: AGGIIORNAMENTO_FOCUS.md.
- In previous sessions, you completed the core architecture and partial/complete implementations for NTC 2018, LC/FC, validation engine, verification pipeline, and initial normative registry support.

GOAL OF THIS SESSION (SESSION 5 – RD 2229/39)
Your task in this session is to implement support for the historical Italian normative RD 2229/1939 (Tensioni Ammissibili – TA storico), strictly following the constraints and rules in AGGIIORNAMENTO_FOCUS.md.

You must:
1. Read AGGIIORNAMENTO_FOCUS.md carefully, respecting:
   - NO-INVENTION POLICY
   - scope limits
   - strict use of repositories
   - validation-before-verification
   - pure core architecture (NO GUI inside core functions)
   - all user-facing text in Italian
   - minimal token usage, no mass refactors

2. Read the FINAL SESSION SUMMARY from the previous session (I will paste it below).
   - Identify the current repository structure and what components already exist for normative checks.

3. Produce a short “Session 5 Roadmap – RD 2229/39” that includes:
   - Which RD 2229/39 checks are realistically implementable with the existing workspace
   - Which should remain PARTIAL with TODOs
   - Expected modules/files to be created or modified
   - How templates will be registered in the normative registry
   - Which tests must be created

4. After the roadmap, EXECUTE it in this session with the following priorities:

==================================================
PRIORITY A — DEFINE RD 2229/39 VERIFICATION FUNCTIONS (TA)
==================================================
Implement ONLY checks that can be supported WITHOUT inventing formulas, using clear NormReference entries and TODO notes.

Typical checks allowed under RD 2229 TA:
- Tensione di calcolo (σ) = N/A, M/W
- Confronto con tensioni ammissibili fornite dal materiale
- Taglio TA if clearly present in the repo
- Minimi di armatura (ONLY if supported by existing normative helpers)

For each implemented function:
- Place them in an appropriate module such as:
  `src/methods/checks_rd2229.py`
- Use Italian messages and warnings
- Use NormReference from RD 2229
- FULL compliance with the "NO-INVENTION" rule:
  - If the repository does not contain explicit formulas or normative helpers that match RD 2229/39, you MUST mark the check as PARTIAL with clear Italian TODOs and references.
  - DO NOT improvise tension limits.

==================================================
PRIORITY B — CREATE VERIFICATIONTEMPLATE ENTRIES
==================================================
In `src/core_calculus/normative_registry.py` (or equivalent):

- Add `get_rd2229_templates()`
- Define templates for each RD 2229 check you implement:
  - template_id
  - norm_code="RD2229"
  - verification_type="tensioni_ammissibili"
  - limit_state="TA"
  - Italian description_it and notes_it
  - function_path to your check functions
  - implementation_status ("complete", "partial")

==================================================
PRIORITY C — CONNECT VALIDATION RULES
==================================================
In `src/core_calculus/validation_engine.py`:

- Add or refine validation rules SPECIFIC for TA RD 2229, for example:
  - presence of necessary reinforcement data
  - consistency of section type with TA checks
- If normative detail is missing, attach RD2229 NormReference and add TODO.

==================================================
PRIORITY D — IMPLEMENT TESTS
==================================================
Create or extend tests to validate RD 2229 functionality:

- New file: `tests/test_rd2229_checks.py`
- Test cases:
  - Valid TA check (σ < σ_amissibile) → OK
  - Non-OK case (σ > σ_amissibile)
  - Validation errors prevent execution
  - Template selection for RD 2229

Tests must run through:
`CalcInput → validate_calc_input → run_verifications_for_element`

==================================================
PRIORITY E — REGISTRY + CONTROLLER INTEGRATION
==================================================
- Ensure RD 2229 templates are recognized when norm_code="RD2229"
- VerificationController must correctly route TA verifications

==================================================
CONSTRAINTS
==================================================
YOU MUST:
- Keep ALL user-facing messages in ITALIANO
- Respect core/GUI separation
- Mark missing checks with PARTIAL + TODO
- Avoid inventing formulas or interpolations

YOU MUST NOT:
- Implement rules or formulas not explicitly supported by the existing workspace
- Mass-reformat the repository
- Run tests repeatedly after tiny edits

==================================================
FINAL OUTPUT FOR THIS SESSION
==================================================
At the end, print a “Session 5 – RD 2229/39 Result Summary” with:
- List of RD 2229/39 checks implemented, partial, or left as TODO
- Template entries created
- Tests created and their results
- Remaining work for future sessions

Now I will paste the FINAL SESSION SUMMARY from Session 4.
Do NOT start implementation until you have:
- Read AGGIIORNAMENTO_FOCUS.md
- Read the Summary
- Printed the Roadmap for Session 5.

=== BEGIN PREVIOUS FINAL SESSION SUMMARY ===
Session 2 Complete! ✅
I've successfully completed all priorities for NTC 2018 verification implementation. Here's what was accomplished:

Completed Priorities:
✅ Priority B - Minimi Armatura Flessione

Replaced 0.15% fixed percentage with full NTC 2018 formula
Implemented f_ctm extraction/computation from f_ck
Formula: As,min = max(0.26*f_ctm/f_yk*b*d, 0.0013*b*d)
✅ Priority A - Flessione SLU

Replaced x=0.3*d with proper neutral axis solver
Handles singly and doubly reinforced sections
Checks ductility limit (x/d ≤ 0.45)
✅ Priority C - Taglio SLU

Complete V_Rd calculation per NTC 2018 § 4.1.2.1.3.2
V_Rd,s (stirrup resistance) + V_Rd,max (strut limit)
Conservative θ=21.8°
✅ Priority D - Minimi Armatura Taglio

New check function + template added
Formula: Asw,min/s = 0.08*√f_ck/f_yk*b
✅ Priority E - Validation Rules

NTC 2018-specific validation in validation_engine.py
Warns for missing As, d, or stirrup data
✅ Priority F - Comprehensive Tests

16 new tests in test_ntc2018_checks.py
All tests passing ✅
Quality Metrics:
Tests: 16/16 passing (NTC 2018) + 15/15 passing (related verification)
Lint: Zero errors ✅
Templates: 4 templates, all marked "complete"
Italian messages: 100% coverage
NormReference: Every check linked to norm paragraphs
Files Modified:
src/methods/checks_ntc2018.py - ~750 lines (3 functions completed + 1 new)
src/core_calculus/normative_registry.py - Updated 4 templates
src/core_calculus/validation_engine.py - Added NTC 2018 validation rules
tests/test_ntc2018_checks.py - 580 lines of comprehensive tests
Documentation:
📄 Session_2_Result_Summary.md - Complete session documentation with:

Detailed implementation notes for each priority
Code examples and formulas
Test coverage analysis
LC/FC integration verification
Remaining TODOs for future sessions
All Session 2 goals achieved! The NTC 2018 SLU verification checks are now production-ready with full normative compliance, Italian messages, LC/FC support, and comprehensive test coverage.
=== END PREVIOUS FINAL SESSION SUMMARY ===
