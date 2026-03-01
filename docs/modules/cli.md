<<<<<<< HEAD
# Modulo: `cli`

## 1. Scopo e ambito

Interfaccia a riga di comando (CLI) Typer per il programma RD2229. Espone 5 comandi: `new`, `load`, `run`, `export`, `info`.

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: `src/cli/entrypoint.py` (~90 righe) ha tutti e 5 i comandi implementati. `new`/`load`/`info` funzionano indipendentemente dalla pipeline. `run` e `export` dipendono da `src/core/pipeline.run_pipeline()` e `src/reporting` (entrambi PARZIALE). Test: `tests/test_cli_new.py` copre help, `new`, `load`, `info`.

## 3. Evidenze

- `src/cli/entrypoint.py` — Typer CLI; 5 comandi; corpo implementato
- `src/cli/__init__.py:12` — importa e riesporta `main`
- Test: `tests/test_cli_new.py` — import `src.cli`, invoca `--help`, `new`, `load`, `info`
- Entry point pyproject.toml: TBD (non verificato direttamente)

## 4. Input/parametri

- `new [PATH]` — crea nuovo project file JSON
- `load [PATH]` — carica project file esistente
- `run [PATH]` — esegue pipeline su project
- `export [PATH] [--format html|md]` — esporta report
- `info [PATH]` — mostra info progetto

## 5. Output

- Console: testo/JSON risultati
- File: HTML/MD report (tramite `src/reporting/export.py`)

## 6. Dipendenze

- `src/core/pipeline` — `run_pipeline()`
- `src/project/repository` — `load_project()`, `save_project()`
- `src/reporting` — `build_report()`, `export_report_html()`, `export_report_md()`

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/cli/entrypoint.py` — docstring help text |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Comandi `run` e `export` dipendono da pipeline non completamente implementata
- Nessun test E2E per il flusso `run` → `export`

## 9. Next steps

- [ ] Aggiungere test E2E per `run` con project fixture minimale
- [ ] Verificare entry point `rd2229` in `pyproject.toml`
- [ ] Documentare formato input atteso per ciascun comando
=======
# Documentazione Modulo: `cli`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `cli` |
| **Path** | `src/cli` |
| **Tipo** | package |
| **File .py rilevati** | 2 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

> Descrivere in 2-3 righe il *perché* esiste questo modulo e quale problema risolve.

TBD

---

## 3. File / Classi / Funzioni principali

> Elencare i simboli pubblici rilevanti. Non inventare: se non si conosce la firma esatta, annotare TBD.

| File | Classe/Funzione | Descrizione |
|------|-----------------|-------------|
| TBD | TBD | TBD |

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | TBD | TBD |
| Output | TBD | TBD |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/test_cli_new.py` | TBD | — |

---

## 6. Fonti normative

> Solo riferimenti a ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`. NESSUN testo copiato.

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| TBD | TBD | — |

---

## 7. Dipendenze interne

> Moduli `src/` da cui questo modulo dipende (import diretti).

- TBD

---

## 8. Note e TODO

- [ ] Compilare sezioni TBD
- [ ] Verificare test correlati
- [ ] Tracciare fonti normative di riferimento
>>>>>>> d5ef881 (feat: audit/docs infrastructure - audit_repo, RTM, governance, normative catalog, module docs)
