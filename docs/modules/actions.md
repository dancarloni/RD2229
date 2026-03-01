<<<<<<< HEAD
# Modulo: `actions`

## 1. Scopo e ambito

TBD — nessuna docstring di modulo trovata in `src/actions/__init__.py` o `src/actions/action_repo.py`.  
Dal codice: contiene `VerificationAction`, `ActionRepository`, esempi stub (`FlexureCheckAction`). Sembra destinato a rappresentare azioni di verifica strutturale come oggetti eseguibili.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `src/actions/action_repo.py` è esplicitamente marcato "STUB S2". Il metodo `VerificationAction.run()` contiene `raise NotImplementedError("Azione di verifica non implementata.")`. Tutti i metodi di `ActionRepository` hanno corpo `# TODO`.

## 3. Evidenze

- `src/actions/action_repo.py` — ~160 righe; "STUB S2" dichiarato
- `src/actions/action_repo.py:run()` → `raise NotImplementedError`
- Nessun import da altri moduli attivi

## 4. Input/parametri

TBD — firma `run(self, inputs: dict) -> dict` vista nel codice ma nessuno schema validato.

## 5. Output

TBD — `run()` dovrebbe restituire `dict` ma non implementato.

## 6. Dipendenze

- `src/actions/__init__.py` — re-esporta da `action_repo`
- Nessuna dipendenza da altri moduli `src/`

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Tutti i metodi sono TODO/NotImplementedError
- Nessun test
- Nessun entry point attivo

## 9. Next steps

- [ ] Implementare `VerificationAction.run()` con logica concreta
- [ ] Aggiungere test unitari per `ActionRepository`
- [ ] Collegare al dispatcher in `src/methods/verification/`
=======
# Documentazione Modulo: `actions`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `actions` |
| **Path** | `src/actions` |
| **Tipo** | package |
| **File .py rilevati** | 2 |
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
