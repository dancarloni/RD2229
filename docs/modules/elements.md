# Documentazione Modulo: `elements`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `elements` |
| **Path** | `src/elements` |
| **Tipo** | package |
| **File .py rilevati** | 4 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

Modello elemento strutturale (`Element`) e repository (`ElementRepository`). Funzione `resolve_verification_inputs()` per risolvere riferimenti sezione/materiale per gli elementi.

---

## 3. Evidenze

- `src/elements/element_repo.py` — "STUB S2"; tutti metodi TODO
- `src/elements/element_model.py` — "STUB S2"; `Element` dataclass con metodi TODO
- `src/elements/resolve_inputs.py` — logica parziale (itera elementi, delega a repository stub)
- Test: `src/tests/test_elements_repo.py`, `src/tests/test_resolve_inputs.py` (marcati STUB S2)

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | `Element` dataclass | `element_id`, `element_type`, `section_id`, `material_id`, `loads` |
| Input | `resolve_verification_inputs(elements, mat_repo, sec_repo) -> List[VerificationInput]` | Risoluzione riferimenti |
| Output | `Element` objects | Dal repository |
| Output | `List[VerificationInput]` | Da `resolve_inputs` |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `src/tests/test_elements_repo.py` | TBD | — |
| `src/tests/test_resolve_inputs.py` | TBD | — |

---

## 6. Fonti normative

Nessuna trovata nel codice del modulo. TODO: aggiungere riferimenti se identificati.

---

## 7. Dipendenze interne

- `src/materials/material_repo` — `MaterialRepository` (anch'esso STUB)
- `src/calc/shear_area_registry` — `compute_shear_area()`
- Importato da `src/tools/verify_cli.py`

---

## 8. Gap / TODO / Limitazioni

- Repository completamente non funzionale
- `resolve_inputs` delega a stub — non produce output reale
- Test verificano solo che le classi esistano (smoke STUB)

---

## 9. Next steps

- [ ] Implementare `ElementRepository` con storage in-memory o JSON
- [ ] Collegare `resolve_verification_inputs()` a repository funzionanti
- [ ] Aggiungere test di integrazione con dati reali
- [ ] Compilare sezioni TBD
