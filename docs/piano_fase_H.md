# Fase H — Riorganizzazione `src/methods/`

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | corrente (2026-03-09) |
| Data completamento | 2026-03-09 |
| Test totali | 2278 test passati, 0 falliti |
| File principali | `src/methods/` (tutti i package per norma) |

---

## Descrizione

La Fase H è una **fase di refactoring architetturale**: riorganizza i file di verifica strutturale da una struttura flat (`checks_*.py` nella root di `src/methods/`) a package separati per norma. Questo migliora la modularità, facilita l'aggiunta di nuove norme e chiarisce le dipendenze tra moduli.

**Nessuna logica di calcolo è stata modificata**: solo spostamento di file e aggiornamento degli import.

---

## Diagramma dipendenze (prima → dopo)

```text
PRIMA (struttura flat):
  src/methods/
  ├── checks_rd2229.py      ← import diretto
  ├── checks_ntc2018.py     ← import diretto
  ├── checks_dm96.py        ← import diretto
  └── checks_fire_dm96.py   ← import diretto

DOPO (package per norma):
  src/methods/
  ├── rd2229/
  │   ├── __init__.py
  │   ├── checks.py         ← ex checks_rd2229.py
  │   ├── instabilita.py
  │   └── torsione.py
  ├── ntc2018/
  │   ├── __init__.py
  │   └── checks.py         ← ex checks_ntc2018.py
  ├── dm96/
  │   ├── __init__.py
  │   ├── checks.py         ← ex checks_dm96.py
  │   └── fire.py           ← ex checks_fire_dm96.py
  ├── ec2/
  │   └── __init__.py       ← placeholder
  ├── muratura/
  │   └── ...
  └── verification/
      └── ...
```

---

## Dipendenze da altri moduli

| Modulo | Impatto migrazione |
| --- | --- |
| `tests/test_*.py` (tutti) | Import aggiornati da `src.methods.checks_*` a `src.methods.<norma>.checks` |
| `src/core_calculus/normative_registry.py` | Path stringa in `import_module()` aggiornati |
| `src/pressoflessione/slu.py` | Import aggiornati |
| Fase F — `checks.py` per norma | Struttura target creata in questa fase |
| Fase J — pressoflessione deviata | Usa `src.methods.rd2229.checks`, `src.methods.ntc2018.checks` |

---

## Struttura file finale `src/methods/`

```text
src/methods/
├── __init__.py
├── protocols.py              # ChecksProtocol ABC — interfaccia comune
├── prestress_models.py       # Modelli precompresso
├── section_fiber.py          # Sezione a fibre
├── ta.py                     # Utilità tensioni ammissibili
├── rd2229/
│   ├── __init__.py
│   ├── checks.py             ← ex checks_rd2229.py
│   ├── instabilita.py        # Coefficienti ω, omega_ca
│   └── torsione.py           # Torsione TA (RD2229 §62)
├── ntc2018/
│   ├── __init__.py
│   └── checks.py             ← ex checks_ntc2018.py
├── dm96/
│   ├── __init__.py
│   ├── checks.py             ← ex checks_dm96.py
│   └── fire.py               ← ex checks_fire_dm96.py
├── ec2/
│   └── __init__.py           ← placeholder implementazione futura
├── muratura/
│   ├── cinematica.py         # Fase E
│   ├── cantonale.py          # Fase E.6
│   └── ...
└── verification/
    └── ...
```

---

## Subfasi, checklist e storico

### H.1 — Migrazione package per norma

**Stato**: ✅ COMPLETATO

- [x] Package `rd2229/` creato con `__init__.py`
- [x] `checks_rd2229.py` → `src/methods/rd2229/checks.py`
- [x] `instabilita.py` e `torsione.py` già nel package `rd2229/`
- [x] Package `ntc2018/` creato con `__init__.py`
- [x] `checks_ntc2018.py` → `src/methods/ntc2018/checks.py`
- [x] Package `dm96/` creato con `__init__.py`
- [x] `checks_dm96.py` → `src/methods/dm96/checks.py`
- [x] `checks_fire_dm96.py` → `src/methods/dm96/fire.py`
- [x] Package `ec2/` creato come placeholder (`__init__.py` vuoto)

### H.2 — Aggiornamento import

**Stato**: ✅ COMPLETATO

- [x] Tutti i test aggiornati (`tests/test_*.py`)
- [x] `src/core_calculus/normative_registry.py` — path stringa `import_module()` aggiornati
- [x] `src/pressoflessione/slu.py` — import aggiornati
- [x] File flat originali eliminati (`checks_rd2229.py`, `checks_ntc2018.py`, `checks_dm96.py`, `checks_fire_dm96.py`)

### H.3 — Verifica

**Stato**: ✅ COMPLETATO

- [x] 2278 test passati, 0 falliti dopo migrazione

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Package per norma (non per elemento strutturale) | Ogni norma ha logica autonoma e versioning indipendente |
| Elimina file flat (non mantieni alias) | Zero ambiguità su quale modulo viene usato |
| `ec2/` come placeholder | EC2 sarà implementato in Fase S; il package esiste per futura aggiunta senza refactoring |
| `normative_registry.py` con `import_module()` dinamico | Routing norma configurabile senza modifica del codice chiamante |
| Migrazione globale (non incrementale) | Evita stato misto: tutti gli import aggiornati in un singolo commit |

---

## Bug corretti

| Bug | Causa | Fix |
| --- | --- | --- |
| `ModuleNotFoundError` dopo migrazione | Import vecchi `src.methods.checks_rd2229` | Aggiornamento globale con grep+replace |
| `normative_registry.py` path sbagliati | Stringhe hardcoded `"src.methods.checks_*"` | Aggiornate a `"src.methods.<norma>.checks"` |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Data | Domanda | Risposta | Decisione |
| --- | --- | --- | --- |
| 2026-03-09 | Q1 Strategia migrazione | Best judgment | Sposta + elimina flat + aggiorna tutti import (opzione B) |
| 2026-03-09 | Q2 Package ec2/ | Best judgment | Placeholder `__init__.py` |
| 2026-03-09 | Q3 `checks_fire_dm96.py` | Best judgment | `src/methods/dm96/fire.py` |
| 2026-03-09 | Q4 Import rotti | A | Aggiorna tutti import globalmente incluso `normative_registry.py` |

---

## Note storiche/archivio

- Pre-esistenti (non introdotti da questa fase, segnalati come warning):
  - `tests/test_cantonale_muratura.py` — errore encoding UTF-8 in `muratura/cantonale.py` (riga 415)
  - `tests/test_carote.py` — `ModuleNotFoundError: No module named 'scipy'`
- `normative_registry.py` usa `import_module()` dinamico: vantaggi (nessuna dipendenza hardcoded), svantaggi (errori solo a runtime se path sbagliato — coperti da test)
- La struttura creata in questa fase è la base su cui le Fasi F, G, J costruiscono le verifiche multinorma
