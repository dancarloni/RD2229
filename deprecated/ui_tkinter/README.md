# Deprecated Tkinter UI – Migration README

> **Status: DEPRECATED** — All Tkinter-based UI components have been migrated
> to PySide6/PyQt6. This directory retains the migration history and stubs for
> backward compatibility documentation.

## Migration Status

| Original path | Status | Replacement |
|---|---|---|
| `src/rd2229/ui_legacy/main_window.py` | ✅ Replaced by shim | `src/ui/qt/entrypoint.py` |
| `src/rd2229/ui_legacy/module_selector.py` | ✅ Replaced by shim | `src/ui/qt/module_selector.py` |
| `src/rd2229/ui_legacy/section_manager.py` | ✅ Replaced by shim | `src/ui/qt/section_manager.py` |
| `src/rd2229/ui_legacy/notification_center.py` | ✅ Replaced by shim | `src/ui/qt/notification_center.py` |
| `src/rd2229/ui_legacy/historical_main_window.py` | ✅ Replaced by shim | Qt-based history viewer |
| `src/legacy/ui/` | Preserved (legacy) | `src/ui/qt/` |
| `src/legacy/sections_app/ui/` | Preserved (legacy) | `src/ui/qt/` |

## Policy

- **No `import tkinter`** is allowed in any production file outside `src/legacy/`.
- The `tests/test_no_tkinter_imports.py` test enforces this policy automatically.
- The `src/rd2229/ui_legacy/` shims use **lazy imports** (via `importlib.import_module`)
  so that Tkinter is never imported at module load time.

## Migration Guide

### Before (Tkinter)

```python
import tkinter as tk
root = tk.Tk()
win = MainWindow(root, repository=..., serializer=...)
root.mainloop()
```

### After (PySide6/PyQt6)

```python
from src.ui.qt.entrypoint import run_gui
run_gui()
```

Or with the CLI:

```bash
python -m src.rd2229 --gui
```

## DiagnosticsService Hook (GUI Integration)

The PySide6 GUI integrates with `DiagnosticsService` for event querying:

```python
from src.rd2229.diagnostics import get_diagnostics

diag = get_diagnostics()
# In a Qt widget:
events = diag.query_events(source="verifier", limit=100)
# Display in QListView / QTableView
```

See `src/ui/qt/` for the active Qt implementation.

## References

- `docs/MIGRATION_TKINTER_TO_QT.md` – detailed migration documentation
- `tests/test_no_tkinter_imports.py` – automated tkinter-free enforcement
- `src/rd2229/ui_legacy/` – lazy shims (do not remove – used for backward compatibility)
