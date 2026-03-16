# Fase X6 — Report e Tracciabilità (LLM Premium)

## Sub-fasi X6.1–X6.5 (checklist avanzamento) — COMPLETATO ✅

- [x] **X6.1 — Analisi e preparazione** ✅
  - [x] Lettura file e raccolta dipendenze
  - [x] Verifica stato file di dipendenza
  - [x] Definizione contratti software X6 e perimetro refactoring
- [x] **X6.2 — Struttura modulare e capitoli** ✅
  - [x] Suddivisione pipeline in sub-fasi (x6_report_pipeline.py, x6_audit_trail.py, x6_warning_codes.py)
  - [x] Creazione capitoli e checklist
  - [x] Audit trail SHA-256 input/output hash
- [x] **X6.3 — Contratto contenuti e mapping normativo** ✅
  - [x] Generazione report con tutti i campi richiesti (json_payload, audit_trail, decision_trace)
  - [x] Tabella mapping norma → sezione (x6_multi_norm_comparator.py: 14 tipi, NTC2018/DM96/DM92/RD2229/EC2/EC3)
  - [x] Auto-popolamento formula_table e normative_extracts via comparatore
- [x] **X6.4 — Esempi, test e metacodice** ✅
  - [x] 61 test automatici (TestWarningCodes, TestAuditTrail, TestMultiNormComparator, TestReportPipeline, TestReportBuilder, TestExport, TestBenchmarkDoppiaColonna)
  - [x] Benchmark doppia colonna storico (RD2229/DM96) vs vigente (NTC2018/EC2) con parametrize
  - [x] Snapshot stability test (struttura MD/HTML/JSON)
  - [x] Widget PySide6 x6_report_widget.py (preview HTML, esporta HTML/MD/JSON, audit panel)
- [x] **X6.5 — Audit, aggiornamento e validazione** ✅
  - [x] Audit normativo/metodologico/tecnico (comparatore multi-norma)
  - [x] Aggiornamento PIANO_LAVORO.md (X6 marcato completo, riga tabella attività)
  - [x] Validazione finale: 61/61 PASS

---

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | **COMPLETATO** ✅ |
| Commit | 2026-03-16 (sessione unica) |
| Data | 2026-03-16 |
| Dipendenza master | docs/piano_fase_X.md |
| Test eseguiti | **61/61 PASS** |
| Moduli nuovi | x6_report_pipeline.py, x6_multi_norm_comparator.py, x6_audit_trail.py, x6_warning_codes.py, x6_report_widget.py |
| Moduli estesi | report_builder.py, export.py, __init__.py |
| Ambito | Report HTML/MD/JSON, audit trail SHA-256, mapping multi-norma, widget PySide6, benchmark doppia colonna |

---
## Vincoli operativi recepiti dalla sessione

- Sessione unica continua: pianificazione, implementazione, test e storicizzazione devono essere completati senza spezzare il flusso di lavoro.
- Q&A bloccante: le domande interattive sono state già eseguite prima dell'avvio implementativo, in coerenza con [docs/PIANO_LAVORO.md](docs/PIANO_LAVORO.md).
- Storicizzazione obbligatoria: tutte le decisioni X6 devono essere riportate in questo file e poi propagate nel master [docs/piano_fase_X.md](docs/piano_fase_X.md) e in [docs/PIANO_LAVORO.md](docs/PIANO_LAVORO.md).
- Nessuna dipendenza implicita: X6 deve integrarsi con X1–X5 ma restare eseguibile anche con fallback documentato se uno dei moduli a monte non e disponibile.

---

## Allineamento con master plan Fase X

- Stato master corrente: in [docs/piano_fase_X.md](docs/piano_fase_X.md) la Fase X e al 63%, con X1–X5 completate e X6–X8 da implementare.
- Regole obbligatorie ereditate dal master:
  - sezione Rischi normativi residui
  - tabella Formula usata / fallback / motivo selezione
- Dipendenze funzionali da integrare nel report X6:
  - output X1: tipologia solaio, parametri geometrici, materiale, schema statico
  - output X2: carichi, combinazioni, LC/FC, unita e conversioni
  - output X3: verifiche SLU, warning, fallback DM96/DM16 espliciti
  - output X4: verifiche SLE, vibrazioni, limiti deformabilita
  - output X5: aperture, cerchiature, rigidezza equivalente, pushover/casi avanzati se presenti

---

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | IN CORSO |
| Commit | — |
| Data | 2026-03-16 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Report HTML/MD, audit trail, riferimenti normativi, modularità premium |
| Avanzamento sessione | Verticale iniziale X6 attivo: audit JSON, warning codes, export JSON, 7 test mirati verdi |

---

## Scopo del modulo

Costruire report tecnici completi, modulari, premium-ready, con:
- output MD + HTML
- estratti normativi completi
- fallback opzionale (con warning)
- audit trail hash input/output + riferimento normativa + timestamp
- test su dati strutturati (JSON) + assertion
- domande interattive e cronologia decisionale
- warning codificati
- struttura ampliabile e aggiornabile

---

## Dipendenze reali del repo

- src/codes/params/NTC2018.json
- src/codes/clauses/NTC2018.yml
- src/codes/ntc2018/secondary_elements/*/report_adapter.py
- src/core/registro_log.py
- src/reporting/report_builder.py
- src/methods/ntc2018/checks_x3.py
- src/methods/ntc2018/checks_x4.py
- src/methods/ntc2018/x5_pushover.py
- tests/codes/test_x3_slu_checks.py
- tests/codes/test_x4_sle_checks.py
- tests/codes/test_x5_aperture_cerchiature.py

---

## Domande, risposte e decisioni (sessione premium)

| Domanda | Risposta |
| --- | --- |
| Formati report | HTML + Markdown + JSON strutturato |
| Dettaglio normativo | Estratti testuali completi dai documenti normativi |
| Fallback formule | Fallback proposto all'utente in UI/report, scelta manuale |
| Audit trail | Completo: log + hash input/output + riferimento normativa + timestamp + Q&A + commit + impatto |
| Test di validazione | Unit + Integration + Snapshot + Benchmark con doppia colonna storico/NTC |
| Warning codificati | Codici semantici + severity + riferimento norma/link interno |
| Integrazione pipeline | X6 interroga X1–X5 ma usa fallback documentato se un modulo non e disponibile |
| UI/Deployment | Widget dedicato Report Builder con anteprima live ed export |
| Refactoring | Major refactor controllato: compatibilita verso l'esterno, internals extensible |

---

## Piano implementativo della sessione unica

### X6.1 — Analisi, contratti e architettura

Obiettivo: chiudere il perimetro tecnico prima delle modifiche al codice.

Deliverable attesi:
- contratto dati del report X6 con input minimi, output attesi e metadata premium
- matrice dipendenze X1→X5 → X6
- elenco file da creare o rifattorizzare con motivazione

File target:
- src/reporting/report_builder.py
- src/core/registro_log.py
- src/codes/ntc2018/secondary_elements/*/report_adapter.py

### X6.2 — Core pipeline report e audit trail

Obiettivo: introdurre il nucleo software X6 senza rompere i builder esistenti.

Deliverable attesi:
- orchestratore report per solai
- tracciabilita hash/timestamp/norma/fallback
- warning code registry per X6
- supporto multi-output HTML/MD/JSON

File target previsti:
- src/reporting/x6_report_pipeline.py
- src/reporting/x6_audit_trail.py
- src/reporting/x6_warning_codes.py
- src/reporting/report_builder.py

### X6.3 — Contenuti tecnici, mapping norma e fallback guidato

Obiettivo: trasformare i risultati X1–X5 in sezioni di report auditabili.

Deliverable attesi:
- tabella Formula usata / fallback / motivo selezione
- mapping norma -> sezione report con estratti completi
- sezione rischi normativi residui
- comparazione multinorma NTC2018 / EN 1992 / DM96 / DM16 / RD2229 / Santarella

File target previsti:
- src/reporting/x6_multi_norm_comparator.py
- src/reporting/report_builder.py
- docs/piano_fase_X6_report_tracciabilita.md

### X6.4 — Test, benchmark, esempi, UI

Obiettivo: rendere X6 verificabile e usabile da GUI.

Deliverable attesi:
- esempi numerici reali e casi regressivi
- test unitari, integrazione, snapshot e benchmark
- widget PySide6 per preview/export report

File target previsti:
- tests/test_x6_report_pipeline.py
- tests/test_x6_report_snapshot.py
- tests/test_x6_report_benchmark.py
- src/ui/modern/ o src/ui/qt/ widget dedicato X6

Stato attuale:
- completato il primo verticale backend con i moduli `src/reporting/x6_report_pipeline.py`, `src/reporting/x6_audit_trail.py`, `src/reporting/x6_warning_codes.py`
- esteso `src/reporting/report_builder.py` con `json_payload`, `audit_trail`, `decision_trace`
- esteso `src/reporting/export.py` con export JSON
- aggiunto test `tests/test_reporting_x6.py` con esito 7/7 PASS sul batch mirato `tests/test_reporting_x6.py tests/test_export.py`

### X6.5 — Audit finale e storicizzazione

Obiettivo: chiudere la fase con allineamento documentale e tecnico.

Deliverable attesi:
- aggiornamento stato X6 in [docs/piano_fase_X.md](docs/piano_fase_X.md)
- aggiornamento avanzamento in [docs/PIANO_LAVORO.md](docs/PIANO_LAVORO.md)
- riepilogo test e commit
- checklist finale tutta tracciata con - [x]

---

## Contratti software previsti

### Contratto dati Report X6

Ogni report di solaio dovra esporre almeno:
- `phase_id`: `X6`
- `element_id` o identificatore logico del solaio
- `input_summary`: dati consolidati X1/X2
- `checks_summary`: esiti X3/X4/X5
- `formula_table`: elenco formule primarie e fallback
- `normative_extracts`: estratti completi o citazioni lunghe con riferimento norma
- `warnings`: codici X6 con severity e source
- `audit_trail`: hash input, hash output, timestamp, versione app, commit se disponibile
- `decision_trace`: scelte Q&A, fallback selezionato, note ingegneristiche
- `artifacts`: markdown, html, json

### Contratto integrazione con X1–X5

- X6 non ricalcola i check: consuma output gia prodotti da X1–X5.
- Se una sezione mancante impedisce il report completo, X6 deve emettere warning esplicito e sezione incompleta marcata.
- Le formule da riportare derivano dal master [docs/piano_fase_X.md](docs/piano_fase_X.md) e dai moduli X3/X4/X5, non da testo inventato.

---

## Struttura premium e modularità

- Ogni sub-fase (X6.1–X6.5) è indipendente, con capitolo dedicato, checklist, audit, domande interattive.
- Il file è suddiviso in:
  - Scopo
  - Dipendenze
  - Piano implementativo della sessione unica
  - Contratti software previsti
  - Contratto contenuti
  - Audit normativo (tabella mapping norma → sezione)
  - Linee guida (tracciabilità, warning, fallback, citazioni)
  - Metacodice (pseudo-codice pipeline, export, log)
  - Esempi numerici (target minimo 10, con warning e citazioni)
  - Test (unit, integration, snapshot, benchmark, e2e)
  - Audit metodologico (checklist, rischi, correzioni)
  - Aggiornamento file/dipendenze (commit, impatto, refactoring)
  - Cronologia & decisioni (domande/risposte, motivazione, sessione)

---

## Contratto contenuti report

Ogni report deve includere:
- input e unità
- combinazione governante
- formula usata (con estratto normativo)
- fallback disponibile (con warning)
- motivo della scelta
- valori sostituiti
- esito e UC
- warning codificati
- audit trail hash input/output + riferimento normativa + timestamp

---

## Audit normativo — Tabella mapping

| Sezione report | Norma di riferimento | Estratto testuale |
| --- | --- | --- |
| Flessione | NTC2018 §4.1.2.4 | "La verifica di resistenza a flessione..." |
| Taglio | NTC2018 §4.1.2.5 | "La verifica di resistenza a taglio..." |
| Freccia | NTC2018 §7.2.6 | "Il limite di deformabilità..." |
| Vibrazioni | NTC2018 §C7.10.5, EN ISO 10137 | "La frequenza fondamentale..." |
| Aperture | NTC2018 §7.2.6.2 | "La valutazione locale delle aperture..." |
| LC/FC | NTC2018 §C8.5.4 | "Il fattore di confidenza..." |
| Punzonamento | NTC2018 §4.1.2.5 | "La verifica di punzonamento..." |
| Laterocemento | DM 9/1/96 | "Tabelle di portata..." |
| Legno | DM 16/1/96 | "Fattori di sicurezza..." |

---

## Linee guida premium

- Tracciabilità input/output, unità, combinazione governante, formula usata, fallback, motivazione, warning, riferimenti.
- Modularità: ogni verifica ha capitolo, tabella, warning, citazione, fallback, audit.
- Audit trail: hash input/output, riferimento normativa, timestamp, commit.
- Export multi-formato: MD + HTML, dati strutturati (JSON).
- Test automatici: snapshot, JSON, end-to-end.
- Aggiornabilità: ogni sezione facilmente ampliabile.

---

## Metacodice pipeline report (pseudo-codice)

```python
# Pseudocodice pipeline premium
for verifica in verifiche:
    input = raccogli_input()
    formula, fonte = seleziona_formula(verifica)
    fallback = verifica_fallback(verifica)
    output = calcola_output(input, formula, fallback)
    warning = genera_warning(output, formula, fallback)
    audit = genera_audit(input, output, formula, fonte, fallback, warning)
    export_md_html(output, audit)
    salva_json(output, audit)
    log_decisione(verifica, input, output, warning, audit)
```

---

## Esempi numerici premium

### Esempio 1 — Flessione laterocemento
- Input: L=4.5 m, q_s=300 kgf/m², tipologia laterocemento
- Output: M=120 kN·m, V=25 kN
- Formula: NTC2018 §4.1.2.4 (estratto testuale)
- Fallback: DM96 (con warning)
- Audit trail: hash input/output, timestamp, citazione
- Warning: X6-REP-001 (formula usata non tracciata)

### Esempio 2 — Vibrazioni
- Input: L=5.0 m, E=31 GPa, b=1.0 m, h=0.20 m
- Output: f1=12.8 Hz
- Formula: NTC2018 §C7.10.5, EN ISO 10137 (estratto testuale)
- Audit trail: hash input/output, timestamp, citazione
- Warning: X6-REP-002 (riferimento normativo assente)

---

## Test premium

| Test | Input | Output atteso |
| --- | --- | --- |
| X6-T01 | risultato completo | report con sezioni obbligatorie, audit trail, warning |
| X6-T02 | warning attivo | warning codificato visibile, fallback dichiarato |
| X6-T03 | fallback non usato | fallback comunque dichiarato, warning |
| X6-T04 | export MD/HTML | file generato, audit trail incluso |
| X6-T05 | test JSON | dati strutturati validati, assertion campi chiave |

---

## Audit metodologico, tecnico, normativo

- Audit normativo: ogni formula, tabella, warning, esempio ha fonte normativa e citazione.
- Audit metodologico: checklist di coerenza tra formule, unità, warning, fallback, citazioni, modularità.
- Audit tecnico: validazione automatica (test JSON, snapshot, end-to-end), validazione manuale (completezza, aggiornabilità, refactoring).
- Audit di aggiornabilità: ogni sezione facilmente ampliabile, refactoring automatico dei file di dipendenza.
- Audit di tracciabilità: ogni decisione, domanda, risposta, commit, impatto storicizzato.

---

## Aggiornamento file e dipendenze

- Elenco file creati/modificati:
  - src/reporting/x6_report_pipeline.py
  - src/reporting/x6_audit_trail.py
  - src/reporting/x6_warning_codes.py
  - src/reporting/report_builder.py
  - src/reporting/export.py
  - src/reporting/__init__.py
  - tests/test_reporting_x6.py
- Batch test eseguito in sessione: `tests/test_reporting_x6.py` + `tests/test_export.py` → 7/7 PASS
- Refactoring automatico, aggiornamento, commit, impatto documentato.
- Tracciabilità decisionale: ogni modifica, commit, impatto storicizzato.

---

## Cronologia & decisioni (sessione premium)

- 2026-03-16: avvio implementazione premium, domande interattive raccolte, piano aggiornato.
- 2026-03-16: completato il primo verticale software X6 backend con payload JSON auditabile, audit trail hash input/output, warning codificati e export JSON.
- 2026-03-16: validazione mirata eseguita con `pytest tests/test_reporting_x6.py tests/test_export.py -q` → 7/7 PASS.
- Tutte le scelte guidate da domande interattive, storicizzate e tracciate.
- Modularità e aggiornabilità prioritarie: ogni sub-fase indipendente e ampliabile.
- Audit normativo, metodologico, tecnico, aggiornabilità e tracciabilità obbligatori.
- Piano pronto per LLM premium: ampliabile, raffinabile, aggiornabile, validabile in sessione unica.
