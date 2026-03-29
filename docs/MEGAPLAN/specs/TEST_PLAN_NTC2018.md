# TEST_PLAN_NTC2018.md

Scope: tests and golden fixtures required to validate the NTC2018 code modules and GUI integration (SPEC‑only)

Principles

- Golden numeric fixtures must be provided by standards owners (TODO). Tests in this repository will reference those fixtures but will be skipped until fixtures are available.
- All tests must assert `VerificationResultItem.trace.run_id` presence and at least one `norm_references[]` entry.
- GUI smoke tests validate that selection → run → results pipeline works (no normative assertions in GUI tests).

Test types

1. Unit tests (code modules)
   - test_vrdc_no_stirrups.py (golden cases) — placeholders
   - test_secondary_elements_*.py — structural and non‑structural examples
2. Integration tests
   - GUI verification flow (selection + run + view + report binding)
3. Contract tests
   - CodeModule contract conformance (available_checks + run_check)

Execution

- pytest -q (unit + integration)
- CI should skip golden numeric assertions when fixtures are missing; but must fail if `trace.run_id` or `norm_references` are absent.

TODOs

- Add golden numeric fixtures for V_Rd,c and secondary elements (owner: standards team).
- Convert placeholders to real tests after first normative implementation PR.
