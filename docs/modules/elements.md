# Modulo: `elements`

## 1. Scopo e ambito

Modello elemento strutturale (`Element`) e repository (`ElementRepository`). Funzione `resolve_verification_inputs()` per risolvere riferimenti sezione/materiale per gli elementi.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `element_repo.py` è marcato STUB S2. `ElementRepository.add()`, `get_by_id()`, `get_all()`, `get_by_type()` hanno tutti corpo `# TODO`. `element_model.py` è STUB S2: dataclass con campi ma metodi TODO.

## 3. Evidenze

- `src/elements/element_repo.py` — "STUB S2"; tutti metodi TODO
- `src/elements/element_model.py` — "STUB S2"; `Element` dataclass con metodi TODO
- `src/elements/resolve_inputs.py` — logica parziale (itera elementi, delega a repository stub)
- Test: `src/tests/test_elements_repo.py`, `src/tests/test_resolve_inputs.py` (marcati STUB S2)

## 4. Input/parametri

- `Element` dataclass: `element_id`, `element_type`, `section_id`, `material_id`, `loads`
- `resolve_verification_inputs(elements, mat_repo, sec_repo) -> List[VerificationInput]`

## 5. Output

- `Element` objects dal repository
- `List[VerificationInput]` da `resolve_inputs`

## 6. Dipendenze

- `src/materials/material_repo` — `MaterialRepository` (anch'esso STUB)
- `src/calc/shear_area_registry` — `compute_shear_area()`
- Importato da `src/tools/verify_cli.py`

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Repository completamente non funzionale
- `resolve_inputs` delega a stub — non produce output reale
- Test verificano solo che le classi esistano (smoke STUB)

## 9. Next steps

- [ ] Implementare `ElementRepository` con storage in-memory o JSON
- [ ] Collegare `resolve_verification_inputs()` a repository funzionanti
- [ ] Aggiungere test di integrazione con dati reali
