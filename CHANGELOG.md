# Changelog

All notable changes to this project will be documented in this file.

## Unreleased
- Quality & architecture overhaul: refactor into `src/` layout, add typing, tests, docs, and CI improvements.
- Consolidated geometry and graphics modules: canonical `SectionGeometry`/`SectionProperties` in `src/core_calculus/core/geometry_model.py` and `SectionGraphicsController` in `apps/sections/section_graphics.py`. Removed duplicate/shim implementations and updated imports across the codebase.
