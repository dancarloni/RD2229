<<<<<<< HEAD
# Modulo: `project`

## 1. Scopo e ambito

Modello dati centrale del progetto strutturale (`ProjectModel` Pydantic), repository per caricamento/salvataggio su file JSON/JSONP, migrazione versioni schema.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `schema.py` (120 righe) ha modelli Pydantic completi con tutti i sub-model. `repository.py` (410 righe) implementa I/O reale, migrazione versioni (1.0.0→1.1.0), validazione. Test su 10+ file.

## 3. Evidenze

- `src/project/schema.py` — `ProjectModel`, `ProjectInfo`, `GeometryEntry`, `MaterialEntry`, `LoadEntry`, `SeismicInputs`, `CodeSettings`, `WindInputs`, `FireInputs`, `PipelineSteps`
- `src/project/repository.py` — `load_project(path)`, `save_project(model, path)`, `migrate_dict()`
- `src/project/repository.py:248-267` — logica migrazione versione
- Test: `tests/test_project_roundtrip.py`, `tests/test_migration.py`, `tests/test_pipeline_smoke.py` (+7)

## 4. Input/parametri

- `load_project(path: str | Path) -> ProjectModel` — legge JSON/JSONP
- `save_project(model: ProjectModel, path: str | Path)` — scrive JSON

## 5. Output

- `ProjectModel` — modello Pydantic completo
- File JSON su disco

## 6. Dipendenze

- Pydantic ≥ 2.0 (dipendenza non sempre installata in CI — vedere KNOWN LIMITATIONS)

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/project/schema.py` — `norm_code` default `"RD2229"` |
| NTC2018 | `src/project/schema.py` — `SeismicInputs`, `CodeSettings` |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Dipendenza da Pydantic ≥ 2.0 può non essere installata (CI blockers pre-esistenti)
- Schema versioning a 1.1.0 — versioni future richiedono nuove migration
- `GeometryEntry` e `LoadEntry` hanno campi TBD in alcuni sotto-schema

## 9. Next steps

- [ ] Documentare ogni campo di `ProjectModel` con tipo, default e significato strutturale
- [ ] Aggiungere migrazione verso versione 1.2.0 quando necessario
- [ ] Risolvere dipendenza Pydantic in CI (issue debito tecnico separata)
=======
# Documentazione Modulo: `project`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `project` |
| **Path** | `src/project` |
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
| `tests/test_project_roundtrip.py` | TBD | — |
| `tests/test_project_store.py` | TBD | — |

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
