# CodeModule_CONTRACT.md

Purpose: define the *interface* and responsibilities for code modules implementing a normative check
(PLANNED / SPEC ONLY — no implementation here).

Responsibilities
- expose `available_checks()` -> list of check identifiers and metadata
- expose `run_check(check_id, input_dict)` -> returns `VerificationResultItem` (must include `trace.run_id` and `norm_references[]`)
- perform input validation and raise `ValueError` for invalid inputs
- be deterministic and pure (no global state mutations)

Data contracts
- VerificationResultItem (summary)
  - ok: bool
  - value: numeric or string result
  - steps: list of intermediate steps (for traceability)
  - trace: { run_id: str, timestamp: ISO8601 }
  - norm_references: list[str]

Error handling
- All exceptions must be well-documented and typed.

Example (interface sketch)
```
class CodeModule:
    def available_checks(self) -> List[Dict]:
        """Return available checks: id, short_descr, inputs_schema"""

    def run_check(self, check_id: str, inputs: dict) -> VerificationResultItem:
        """Run a named check and return a VerificationResultItem"""
```

Notes
- The GUI and report builder must rely only on this contract to integrate with normative code modules.
- Keep each module self-contained; unit tests must exercise both `available_checks` and `run_check` semantics.
- Do not include normative numbers in this contract (kept in SPEC files).
