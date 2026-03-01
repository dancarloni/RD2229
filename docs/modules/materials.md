<<<<<<< HEAD
# Modulo: `materials`

## 1. Scopo e ambito

Modello materiale (`Material`) e repository (`MaterialRepository`) per accesso ai dati di materiali strutturali (calcestruzzo, acciaio).

## 2. Stato reale

**STUB**

Motivazione oggettiva: `material_repo.py` è marcato STUB S2. `MaterialRepository.add()`, `get_by_id()`, `get_by_name()`, `get_all()` hanno tutti corpo `# TODO`. `material_model.py` è STUB S2: dataclass con campi ma nessun metodo implementato.

## 3. Evidenze

- `src/materials/material_repo.py` — "STUB S2"; tutti metodi TODO
- `src/materials/material_model.py` — "STUB S2"; `Material` dataclass, metodi TODO
- `src/materials/validation.py` — logica parziale di validazione
- Test: `src/tests/test_material_repo.py`, `src/tests/test_resolve_inputs.py` (STUB S2)

## 4. Input/parametri

- `Material` dataclass: `material_id`, `name`, `fck`, `fyk`, `density`, `type`
- `MaterialRepository.get_by_id(mid: str) -> Material | None`

## 5. Output

- `Material` objects
- `list[Material]`

## 6. Dipendenze

- Importato da `src/tools/verify_cli.py`, `src/elements/resolve_inputs.py`

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Repository completamente non funzionale (tutti TODO)
- Nessun accesso ai dati JSON in `src/repositories/data/materials.json`
- `validation.py` non collegato al repository

## 9. Next steps

- [ ] Implementare `MaterialRepository` con lettura da `src/repositories/data/materials.json`
- [ ] Aggiungere test con materiali reali (C25/30, B450C)
- [ ] Collegare `validation.py` alla pipeline di caricamento
=======
# Documentazione Modulo: `materials`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `materials` |
| **Path** | `src/materials` |
| **Tipo** | package |
| **File .py rilevati** | 4 |
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
| `tests/test_domain_materials.py` | TBD | — |
| `tests/test_materials_cache.py` | TBD | — |

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
