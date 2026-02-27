# Migration quickstart — geometry / graphics consolidation

3-step quick guide for maintainers who need to migrate code to the canonical modules.

1) Update imports (one-liner)
- Replace any local/package copies with the canonical modules:
  - `SectionGeometry`, `SectionProperties` → `src.core_calculus.core.geometry_model`
  - `SectionViewTransform`, `SectionGraphicsController` → `apps.sections.section_graphics`

Example (search/replace):
- search: `from apps.sections.geometry_model import SectionGeometry`
- replace: `from src.core_calculus.core.geometry_model import SectionGeometry`

2) Verify behavior with small runtime smoke-test
- Create a minimal `SectionGeometry` using `from_rectangle`, compute properties and
  call `SectionGraphicsController.draw_all` (or use a headless fake-canvas in tests).

3) Run test & lint checks
- Run `pytest -q`, `ruff .`, `mypy .` and fix reported problems.

If you need help updating multiple files, grep for `geometry_model` or
`SectionViewTransform` to find remaining import sites.

Tip: when writing new code, import `SectionGeometry` from the canonical module — this
keeps the codebase consistent and avoids future duplication.
