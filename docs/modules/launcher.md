<<<<<<< HEAD
# Modulo: `launcher`

## 1. Scopo e ambito

Bootstrap dell'applicazione: configurazione logging e avvio dell'app tramite import dinamico di `apps.sections.app`.

## 2. Stato reale

**INCOMPLETO**

Motivazione oggettiva: Singolo file `bootstrap.py` (~50 righe) con logica reale ma dipendenza da `apps.sections.app` che si trova fuori da `src/`. Nessun `__init__.py` rilevato (non è un package Python corretto). Nessun test.

## 3. Evidenze

- `src/launcher/bootstrap.py` — `configure_logging()`, `run_app()` reali
- Dipendenza da `apps.sections.app` (fuori `src/`)
- Nessun `__init__.py` nella cartella
- Nessun test

## 4. Input/parametri

TBD — `run_app()` senza parametri espliciti.

## 5. Output

TBD — avvia l'applicazione Tkinter.

## 6. Dipendenze

- `apps.sections.app` (fuori `src/`, percorso non standard)
- `src.rd2229.logging_bridge` — `setup_logging()`

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/launcher/bootstrap.py` — menzione nel logging |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Nessun `__init__.py` — non importabile come package
- Dipendenza su percorso `apps/` fuori da `src/`
- Nessun test
- Non integrato nel pipeline principale

## 9. Next steps

- [ ] Aggiungere `__init__.py` per renderlo importabile
- [ ] Valutare se spostare `apps/sections/app.py` dentro `src/`
- [ ] Aggiungere test smoke per `configure_logging()`
=======
# Documentazione Modulo: `launcher`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `launcher` |
| **Path** | `src/launcher` |
| **Tipo** | namespace |
| **File .py rilevati** | 1 |
| **Stato** | STUB |
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
| — | — | Nessun test rilevato meccanicamente. |

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
