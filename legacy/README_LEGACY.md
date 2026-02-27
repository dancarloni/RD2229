# Legacy Components – Deprecation Guide

This document lists deprecated entry points and modules in RD2229 v0.1.0,
and describes the new equivalents to migrate to.

---

## Deprecated Entry Points

| Old command / path | Status | New equivalent |
|--------------------|--------|----------------|
| `structcalc` (→ `src.ui.app:main`) | **Deprecated** | `rd2229-gui` (→ `src.ui.modern.app:main`) |
| `rd2229-demo` (→ `src.rd2229.cli:main`) | **Deprecated** | `rd2229` (→ `src.cli:main`) |

Both old entry points are kept as shims and will be removed in a future major
version.  They emit a `DeprecationWarning` at runtime.

---

## Deprecated Python Modules / Functions

| Module / symbol | Deprecated since | Replacement |
|-----------------|-----------------|-------------|
| `src.ui.app:main` | v0.1.0 | `src.ui.modern.app:main` |
| `src.rd2229.cli:main` | v0.1.0 | `src.cli:main` |

---

## GUI Framework Migration: PySide6 → PyQt6

The optional GUI dependency was changed from **PySide6** to **PyQt6**.

```
# Old (deprecated)
pip install "rd2229[gui]"   # installed PySide6>=6.6

# New
pip install "rd2229[gui]"   # installs PyQt6>=6.4 + PyYAML>=6.0
```

See [docs/ADR/0001-gui-pyqt6-migration.md](../docs/ADR/0001-gui-pyqt6-migration.md)
for the full rationale.

---

## Plugin System

The new plugin system (v0.1.0) replaces ad-hoc feature registration.
Old code using `src.ui.modern.features.registry.FeatureSpec` still works but
should be migrated to `src.plugins.PluginSpec` / `src.plugins.PluginRegistry`.

See `plugins/` for example plugin packages.
