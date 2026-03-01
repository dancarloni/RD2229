<<<<<<< HEAD
# Modulo: `calc`

## 1. Scopo e ambito

TBD — nessuna docstring di modulo trovata.  
Dal codice: `section_registry.py` intende registrare tipi di sezione; `shear_area_registry.py` calcola il fattore di taglio κ per diverse forme di sezione.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `src/calc/section_registry.py` definisce `SECTION_REGISTRY: dict = {}` (dizionario vuoto) con funzioni TODO. `src/calc/shear_area_registry.py` è marcato "STUB S2"; contiene solo un fallback minimale con `DEFAULT_KAPPA = 5/6` e gestori specializzati tutti TODO.

## 3. Evidenze

- `src/calc/section_registry.py` — "STUB S2"; `SECTION_REGISTRY = {}`
- `src/calc/shear_area_registry.py` — "STUB S2"; `DEFAULT_KAPPA = 5/6`; gestori specializzati TODO
- `compute_shear_area()` chiamato da `src/elements/element_model.py`
- Test minimale: `src/tests/test_shear_area.py` (marcato STUB S2)

## 4. Input/parametri

- `compute_shear_area(section_type: str, params: dict) -> float` (da `shear_area_registry.py`)

## 5. Output

- `float` — area di taglio effettiva

## 6. Dipendenze

- `src/elements/element_model.py` importa `compute_shear_area`

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- `SECTION_REGISTRY` vuoto — nessun tipo di sezione registrato
- Gestori forme specifiche (rettangolare, T, circolare) tutti TODO
- Test minimale (solo smoke su fallback)

## 9. Next steps

- [ ] Implementare gestori sezioni rettangolari e circolari in `shear_area_registry.py`
- [ ] Popolare `SECTION_REGISTRY` con tipi sezione supportati
- [ ] Aggiungere test con valori attesi per κ per ciascun tipo
=======
# Documentazione Modulo: `calc`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `calc` |
| **Path** | `src/calc` |
| **Tipo** | package |
| **File .py rilevati** | 3 |
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
| `tests/test_area_calculations.py` | TBD | — |
| `tests/test_rebar_calculator.py` | TBD | — |

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
