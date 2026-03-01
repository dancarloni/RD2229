<<<<<<< HEAD
# Modulo: `repositories`

## 1. Scopo e ambito

TBD — nessuna logica Python. Container di dati JSON/CSV: materiali storici, sorgenti materiali, materiali, tabella RD2229.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `src/repositories/__init__.py` è una sola riga di docstring. Nessun codice Python. Solo file dati in `data/`.

## 3. Evidenze

- `src/repositories/__init__.py` — 1 riga: `"""Repository abstractions for persistence of materials/sections."""`
- `src/repositories/data/historical_materials.json` — dati materiali storici
- `src/repositories/data/material_sources.json` — sorgenti materiali
- `src/repositories/data/materials.json` — catalogo materiali
- `src/repositories/data/rd2229_table.csv` — tabella RD2229
- `src/repositories/data/tables.schema.json` — schema tabelle
- Nessun test

## 4. Input/parametri

TBD — dati consumati da altri moduli tramite lettura file diretta.

## 5. Output

TBD.

## 6. Dipendenze

- `src/legacy/historical_materials.py` potrebbe leggere questi file
- `src/materials/material_repo.py` (STUB) potrebbe usarli

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Nessuna API Python di accesso ai dati
- Nessun test di validazione dei file JSON/CSV
- Relazione con `src/materials/` non chiara (entrambi gestiscono materiali)

## 9. Next steps

- [ ] Implementare `load_materials(path) -> list[Material]` in `__init__.py`
- [ ] Aggiungere test di validazione schema per i file dati
- [ ] Chiarire la relazione con `src/materials/material_repo.py`
=======
# Documentazione Modulo: `repositories`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `repositories` |
| **Path** | `src/repositories` |
| **Tipo** | package |
| **File .py rilevati** | 1 |
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
