# Evidence Log

## A) Evidence: Issue/PR analysis
- Issue #42 analyzed: mega refactoring issue with modular architecture
- Sub-issues merged: secondary elements gating, check registry, normative registry
- Pattern adopted: adapter-based verification with contracts

## B) Evidence: Repository discovery
- `src/core_calculus/contracts.py` — data contracts (NormReference, CalcInput, CalcOutput)
- `src/checks/registry.py` — CheckRegistry with CheckSpec
- `src/core_calculus/normative_registry.py` — VerificationTemplate registry
- `src/core_calculus/core/verification_engine.py` — legacy engine (TA/SLU/SLE)
- `src/codes/ntc2018/secondary_elements/` — secondary element models+checks
- `tests/conftest.py` — tkinter/Qt skip patterns
- `.github/workflows/python-ci.yml` — CI: pytest (gating), ruff/mypy (advisory)

## C) Evidence: Normative references
- Internal references in `src/core_calculus/normative_registry.py`
- NormReference schema: {norm_code, chapter, paragraph, formula_label, description_it}
- Extended for adapters: each SingleCheckResult includes norm_references[]

## D) Evidence: Checks & CI
- Baseline: all tests pass (500+ tests, 3 skipped)
- New tests: 31 tests in `test_verification_adapters.py` — all pass
- Full suite: all pass, no regressions
- Repo-specific: `PYTHONPATH=".:src" python -m pytest -q --tb=short`
