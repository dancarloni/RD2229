<<<<<<< HEAD
# Modulo: `legacy`

## 1. Scopo e ambito

Codice legacy preservato: applicazione Tkinter completa, repository materiali storici, verifica TA storica, sezioni, utilities. Designato come "DO NOT MODIFY" dall'architettura.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: 28+ file Python reali con logica estesa. `historical_materials.py` (576 righe) e `material_sources.py` (657 righe) hanno dati e logica materiali reali. `ui/` sub-package è un'applicazione Tkinter funzionale. Legacy è designata DO NOT MODIFY.

## 3. Evidenze

- `src/legacy/historical_materials.py` — 576 righe; dati materiali storici
- `src/legacy/material_sources.py` — 657 righe; sorgenti materiali
- `src/legacy/ui/` — GUI Tkinter completa (main_window, module_selector, section_manager, ecc.)
- `src/legacy/__main__.py` — entry point legacy
- `src/legacy/ui/__main__.py` — entry point UI legacy
- Nessun test nella nuova suite `tests/` importa da `src.legacy`

## 4. Input/parametri

TBD — GUI Tkinter; input via form utente; file `.jsonp` per persistenza.

## 5. Output

TBD — report su console/file; GUI Tkinter.

## 6. Dipendenze

- Tkinter (stdlib)
- Matplotlib (opzionale, per grafici sezione)
- File dati JSON locali in `src/legacy/`

## 7. Fonti normative collegate

TBD — codice legacy non scansionato per riferimenti normativi in questa pass. Presumibilmente contiene riferimenti a RD2229, DM92, DM96.

## 8. Gap/TODO/Limitazioni

- DO NOT MODIFY per policy architetturale
- Non testato via nuova suite
- Dipendenze Tkinter impediscono test in CI headless

## 9. Next steps

- [ ] TBD — nessun next step pianificato per il legacy (DO NOT MODIFY)
- [ ] Documentare i riferimenti normativi presenti nel legacy (scan futuro)
=======
# Documentazione Modulo: `legacy`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `legacy` |
| **Path** | `src/legacy` |
| **Tipo** | package |
| **File .py rilevati** | 43 |
| **Stato** | INCOMPLETO |
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
