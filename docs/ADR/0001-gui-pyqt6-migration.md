# ADR 0001 – GUI Framework Migration: PySide6 → PyQt6

**Date:** 2025
**Status:** Accepted
**Deciders:** RD2229 core team

---

## Context

The application previously used **PySide6 ≥ 6.6** as its optional GUI
dependency.  Several issues emerged:

- PySide6 wheel sizes are larger and licensing differs (LGPL only, no
  commercial-friendly option for downstream packaging).
- PyQt6 has better ecosystem support for headless/CI environments and
  is more commonly available in conda-forge / system package managers.
- PyQt6 6.4+ provides essentially the same API surface (both wrap Qt 6.x).

---

## Decision

Replace **PySide6** with **PyQt6 ≥ 6.4** in:

1. `pyproject.toml` optional dependency `[gui]`
2. The primary GUI entry point `src/ui/modern/app.py`

The old `src/ui/app.py` (PySide6) is retained as a **deprecated shim** and
will be removed in a future major version.

---

## Consequences

### Positive

- Smaller install footprint in typical CI/CD environments.
- `rd2229-gui` entry point now uses `PyQt6`.
- The `RD2229_UI_TEST=1` env-var allows smoke-testing without starting the
  event loop (safe in headless CI).

### Negative

- Users who have only PySide6 installed must switch or install both.
- Some PySide6-specific signal/slot syntax differences may surface in
  future UI code (mitigated by using the common Qt6 API subset).

---

## Migration

```bash
# Remove old dep
pip uninstall PySide6 -y

# Install new dep
pip install "rd2229[gui]"
# equivalent: pip install "PyQt6>=6.4" "PyYAML>=6.0"
```

See `legacy/README_LEGACY.md` for a full deprecation table.
