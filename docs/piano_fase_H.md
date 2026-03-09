# Fase H — Riorganizzazione methods/

## Stato: COMPLETATO ✅ — commit: (corrente)

## Subfasi, checklist e storico

- [x] Package per norma creati: `rd2229/`, `ntc2018/`, `dm96/`, `ec2/`
- [x] Migrazione `checks_rd2229.py` → `src/methods/rd2229/checks.py`
- [x] Migrazione `checks_ntc2018.py` → `src/methods/ntc2018/checks.py`
- [x] Migrazione `checks_dm96.py` → `src/methods/dm96/checks.py`
- [x] Migrazione `checks_fire_dm96.py` → `src/methods/dm96/fire.py`
- [x] Package `src/methods/ec2/__init__.py` creato come placeholder
- [x] Tutti gli import aggiornati (test, moduli, normative_registry.py, pressoflessione/slu.py)
- [x] File flat originali eliminati
- [x] 2278 test passati, 0 falliti

---

## Struttura finale `src/methods/`

```text
src/methods/
├── __init__.py
├── protocols.py
├── prestress_models.py
├── section_fiber.py
├── ta.py
├── rd2229/
│   ├── __init__.py
│   ├── checks.py          ← ex checks_rd2229.py
│   ├── instabilita.py
│   └── torsione.py
├── ntc2018/
│   ├── __init__.py
│   └── checks.py          ← ex checks_ntc2018.py
├── dm96/
│   ├── __init__.py
│   ├── checks.py          ← ex checks_dm96.py
│   └── fire.py            ← ex checks_fire_dm96.py
├── ec2/
│   └── __init__.py        ← placeholder per implementazione futura
├── muratura/
│   └── ...
└── verification/
    └── ...
```

---

## Storicizzazione domande/risposte e decisioni

| Data       | Domanda | Risposta | Decisione |
|------------|---------|----------|-----------|
| 2026-03-09 | Q1 Strategia migrazione | Best judgment | Sposta + elimina flat + aggiorna tutti import (opzione B) |
| 2026-03-09 | Q2 Package ec2/ | Best judgment | Placeholder `__init__.py` |
| 2026-03-09 | Q3 checks_fire_dm96.py | Best judgment | `src/methods/dm96/fire.py` |
| 2026-03-09 | Q4 Import rotti | A | Aggiorna tutti import globalmente incluso normative_registry.py |

### Nota tecnica

Il file `src/core_calculus/normative_registry.py` usa `import_module()` dinamico con path-stringa —
aggiornati tutti i path da `src.methods.checks_*` a `src.methods.<norma>.checks.*`.

---

## Note storiche/archivio (appendice)

Pre-esistenti (non introdotti da questa fase):

- `tests/test_cantonale_muratura.py` — errore encoding UTF-8 in `muratura/cantonale.py` (riga 415)
- `tests/test_carote.py` — `ModuleNotFoundError: No module named 'scipy'`
