# Changelog

All notable changes to this project will be documented in this file.

## Unreleased
- Quality & architecture overhaul: refactor into `src/` layout, add typing, tests, docs, and CI improvements.
- Consolidated geometry and graphics modules: canonical `SectionGeometry`/`SectionProperties` in `src/core_calculus/core/geometry_model.py` and `SectionGraphicsController` in `apps/sections/section_graphics.py`. Removed duplicate/shim implementations and updated imports across the codebase.
- Cleanup: removed legacy duplicate/deprecated modules in `libs/` and `softw_components/` (graphics and other legacy copies); where imports remained, replaced duplicates with minimal compatibility shims that re-export the canonical implementation and emit a `DeprecationWarning`. No runtime impact expected; full test‑suite runs green. (PR #23 — branch: `cleanup/remove-deprecated-graphics`)
