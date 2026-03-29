# Fase C — Pipeline di Calcolo e Gestione Progetti

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | `c24f6f2` |
| **Data completamento** | 2026-03-07 |
| **Test aggiunti** | ~25 |
| **Norma/e di riferimento** | Multi-norma (orchestrazione) |

---

## Descrizione

Implementa l'**orchestratore della pipeline di calcolo** (step 1–8) e il sistema di **gestione dei progetti** con versionamento dello schema JSON. La pipeline connette tutti i moduli: dalla lettura dei dati di input fino alla generazione del report, passando per la selezione del metodo di calcolo (TA/SLU/DM96).

---

## Teoria e fondamenti strutturali

### Architettura pipeline

Il pattern adottato è una **pipeline funzionale a step**: ogni step è una funzione pura che riceve un input tipizzato e restituisce un output tipizzato. Non ci sono effetti collaterali tra step.

```text
Input utente
   │
   ▼
Step 1 — Caricamento materiali     (MaterialRepository)
   │
   ▼
Step 2 — Caricamento sezioni       (SectionRepository)
   │
   ▼
Step 3 — Definizione carichi       (CarichieCombinazioniInput)
   │
   ▼
Step 4 — Combinazioni              (GestoreCombinazioni)
   │
   ▼
Step 5 — Calcolo sollecitazioni    (step5_adapter → metodo norma)
   │
   ▼
Step 6 — Verifiche                 (checks_<norma>.py)
   │
   ▼
Step 7 — Raccolta risultati        (ResultsModel)
   │
   ▼
Step 8 — Generazione report        (TabulatoCalcolo)
```

### Adapter pattern per Step 5

Step 5 è il punto di variazione principale: diversi algoritmi (TA, SLU, DM96) hanno interfacce simili ma non identiche. `step5_adapter.py` implementa l'**Adapter pattern**:

```text
step5_adapter(input: Step5Input, norma: Norma) → Step5Output
   ├── se norma in {RD2229, DM72, DM92, DM96} → calcola_ta(input)
   ├── se norma == NTC2018                     → calcola_slu(input)
   └── se norma == EC2                         → calcola_ec2(input)
```

### Schema versioning progetti

```text
ProjectModel (JSON)
├── schema_version: "1.1"    ← campo sentinel per migrazione
├── created_at: ISO8601
├── materials: [...]
├── sections: [...]
├── loads: [...]
└── results: ResultsModel

Migrazione v1.0 → v1.1:
  - Aggiunta campo schema_version
  - Conversione material_id da int a str UUID
  - Aggiunta campo source_refs in ogni materiale
```

---

## Diagramma dipendenze subfasi

```text
C.1 — Orchestrazione pipeline (pipeline.py + step5_adapter.py)
C.2 — Gestione progetti (ProjectModel + ProjectRepository + migrazione)
```

Nota: C.1 e C.2 sono parallele (nessuna dipendenza reciproca).

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo in Fase C |
| --- | --- | --- |
| `src/materials/material_repository.py` | Repository materiali | Step 1 pipeline |
| `src/sections/section_repository.py` | Repository sezioni | Step 2 pipeline |
| `src/methods/ntc2018/checks.py` | Verifiche NTC2018 | Step 6 via step5_adapter |
| `src/methods/rd2229/checks.py` | Verifiche RD2229 | Step 6 via step5_adapter |
| `src/report/tabulati_calcolo.py` | Report | Step 8 pipeline |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| **Martin**, "Clean Architecture" | Pipeline funzionale, adapter pattern |
| **Fowler**, "Patterns of Enterprise Application Architecture" | Schema versioning, migrazione dati |
| **NTC2018** | Combinazioni di carico per Step 3-4 |

---

## Struttura file/directory

```text
src/core_calculus/
├── pipeline.py           (~300 righe — orchestratore step 1-8)
├── step5_adapter.py      (~150 righe — adapter metodo calcolo)
├── contracts.py          (~200 righe — CalcInput, SingleCheckResult, VerificationTemplate)
└── project_repository.py (~200 righe — ProjectModel, ResultsModel, CRUD, migrazione)

tests/
├── test_pipeline.py           (~150 righe)
└── test_project_repository.py (~100 righe)
```

---

## Subfasi, checklist e storico

### C.1 — Orchestrazione pipeline

**Stato**: COMPLETATO — commit `c24f6f2`

- [x] `pipeline.py` — `Pipeline` class con metodi `run_step(n)` e `run_all()`
- [x] Step 1-8 definiti come funzioni pure con tipi espliciti
- [x] `step5_adapter.py` — routing norma → algoritmo calcolo
- [x] Gestione errori per step: ogni step può fallire indipendentemente (eccezione con step ID)
- [x] Passaggio risultati: ogni step riceve l'output dello step precedente come input
- [x] Test: `tests/test_pipeline.py` — pipeline end-to-end su caso rettangolare semplice

**Dipendenze**: Fase A (materiali), Fase B (sezioni)

---

### C.2 — Gestione progetti

**Stato**: COMPLETATO — commit `c24f6f2`

- [x] `ProjectModel` — dataclass con tutti i dati di un progetto (materiali, sezioni, carichi, risultati)
- [x] `ResultsModel` — contenitore risultati verifiche per asta/elemento
- [x] Campo `schema_version: str` nel JSON header
- [x] `ProjectRepository.migrate_schema(data)` — migrazione automatica v1.0 → v1.1 a caricamento
- [x] CRUD completo su filesystem (save, load, list, delete)
- [x] Test: `tests/test_project_repository.py` — round-trip JSON, migrazione v1.0 → v1.1

**Dipendenze**: Fase A, Fase B

---

## File creati/modificati

| File | Righe | Descrizione |
| --- | --- | --- |
| `src/core_calculus/pipeline.py` | ~300 | Orchestratore step 1-8 |
| `src/core_calculus/step5_adapter.py` | ~150 | Adapter metodo calcolo |
| `src/core_calculus/contracts.py` | ~200 | CalcInput, SingleCheckResult, VerificationTemplate |
| `src/core_calculus/project_repository.py` | ~200 | ProjectModel, ResultsModel, CRUD, migrazione |
| `tests/test_pipeline.py` | ~150 | Test pipeline end-to-end |
| `tests/test_project_repository.py` | ~100 | Test CRUD e migrazione |

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Pipeline come funzioni pure (non OOP) | Testabilità: ogni step testabile indipendentemente senza mock complessi |
| `step5_adapter` separato dalla pipeline | Isola la logica dei metodi normativi — aggiungere una norma = aggiungere un ramo nell'adapter |
| `schema_version` nel JSON (non nel nome file) | Forward compatibility: il contenuto determina la versione, non il path |
| Migrazione automatica a caricamento | L'utente non deve fare nulla manualmente; vecchi progetti sempre caricabili |
| `contracts.py` come interfaccia comune | Tutti i moduli di verifica usano la stessa firma — dispatcher multinorma di Fase J possibile |

---

## Bug corretti durante lo sviluppo

| Bug | File | Descrizione |
| --- | --- | --- |
| Migrazione v1.0 falliva su progetti senza campo `materials` | `project_repository.py` | `materials` era opzionale in v1.0 ma richiesto dalla migrazione; aggiunto check con default `[]` |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-07

Implementazione autonoma da specifiche — nessun Q&A esplicito.

| Decisione | Motivazione |
| --- | --- |
| Step 5 come adapter separato (non inline in pipeline) | La norma è la variazione principale — ogni nuova norma richiede un nuovo ramo, non una modifica alla pipeline |
| ResultsModel come dataclass (non dict) | Type safety: l'IDE verifica i campi; migliore leggibilità |

---

## Note storiche/archivio

La pipeline a step fissi (1-8) è intenzionalmente rigida: garantisce che ogni progetto segua lo stesso flusso di calcolo, riproducibile e auditabile. L'adapter di step 5 è il punto di estensione principale — ogni nuova norma viene aggiunta lì senza toccare il resto. Questo riflette il principio Open/Closed: aperto all'estensione, chiuso alla modifica.
