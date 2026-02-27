# Migrazione Tkinter → PySide6 (Qt)

Questo documento riepiloga la migrazione graduale della GUI da Tkinter a PySide6.

Attivazione legacy (solo manuale):

- Per avviare la UI legacy (Tkinter) usare:

```
RD2229_LEGACY_UI=1 python -m rd2229.ui_legacy.module_selector
```

Note:
- `ui_legacy/` contiene il codice Tkinter deprecato e non deve essere importato da default.
- `rd2229` ora avvia la shell Qt minima (`ui_qt`) quando disponibile.
