**0) Executive Summary**
- Stato corrente coerente con la direzione architetturale: SPEC LOCKED presenti, MVP isolato su SQLite attivo, test MVP verdi.
- È confermata la strategia B: accettare temporaneamente 2 test rossi preesistenti, ma formalizzando blocco, workaround e criteri di uscita.
- Priorità ora: trasformare il lavoro in backlog eseguibile in batch da Agent, con stream A–E indipendenti ma sequenziati.
- Stream A stabilizza packaging/import/entrypoint e punta a chiudere i 2 blocker.
- Stream B riduce rischio tecnico-legale: da placeholder a verifica minima semi-reale con trace completo e TODO normativi espliciti.
- Stream C avvia migrazione VBA con 1 macro bandiera e golden tests.
- Stream D standardizza MODULE_SPEC/.jsoncode per compatibilità e discovery affidabile.
- Stream E proposto in due opzioni ad alto valore: E1 reportistica tracciabile, E2 integrazione launcher.
- Output sotto include due bozze complete pronte da incollare in docs/specs/PLAN_NEXT_IMPLEMENTATION.md e docs/specs/BLOCKERS.md.

**1) Stato LOCKED vs OPEN**
- **LOCKED**
- Offline mono-utente, un progetto alla volta.
- Separazione Model/Engine/Persistence/UI.
- SQLite come persistence primaria MVP con schema versioning.
- Trace obbligatorio in output (`run_id`, `norm_references[]`).
- Plugin/discovery mantenuto ed esteso via MODULE_SPEC.
- Nessun valore normativo inventato; TODO normativi espliciti.
- Modulo incendio separato dal core strutturale.
- **OPEN**
- Chiusura dei 2 test rossi preesistenti di import/package.
- Porting “macro bandiera” VBA e soglie tolleranza definitive.
- Validazione `.jsoncode` completa (schema rigoroso + provenance completa).
- Scelta stream E (E1 Reportistica vs E2 Launcher integration) come priorità immediata.

**2) Sezione A — Packaging / import / entrypoint**
- **Scopo**
- Rendere robusto avvio/import (`rd2229`, `python -m rd2229`, test runner) e chiudere i 2 blocker.
- **Task**
- Allineare strategia import per src-layout e test discovery.
- Consolidare entrypoint runtime/test (CLI, Qt app, fallback no-PySide).
- Definire policy unica di esecuzione test locali/CI.
- **File toccati (pianificati)**
- pyproject.toml, pytest.ini, test_app_launch.py, test_entrypoint_no_pyside.py, __main__.py, app.py.
- **Acceptance Criteria**
- I 2 test rossi passano in ambiente standard CI senza workaround manuali.
- `python -m rd2229` e script `rd2229` coerenti su exit code e messaggi.
- Nessuna regressione nei test MVP/Qt smoke.
- **Rischi / Mitigazioni**
- Rischio mismatch tra ambienti locali/CI → mitigare con matrice esplicita comandi supportati.
- Rischio fix fragile lato test-only → mitigare privilegiando root cause packaging.

**3) Sezione B — MVP meno placeholder**
- **Scopo**
- Introdurre 1 verifica minima (semi-reale) al posto del puro placeholder, mantenendo tracciabilità legale.
- **Task**
- Definire check “MVP_REAL_MIN” con input deterministici e formula dichiarata.
- Trace arricchito con provenienza parametri e TODO(NTC/EC/RD) dove manca riferimento certo.
- Conservare fallback placeholder per backward compatibility temporanea.
- **File toccati (pianificati)**
- engine.py, contracts.py, models.py, MVP_PLACEHOLDER.jsoncode, test_mvp_result_trace_contract.py, test_mvp_end_to_end.py.
- **Acceptance Criteria**
- Almeno 1 check non-placeholder con output ripetibile.
- Ogni result conserva `run_id`, `norm_references[]`, `method_id`, assumptions/warnings.
- TODO normativi etichettati formalmente.
- **Rischi / Mitigazioni**
- Rischio “finta precisione normativa” → mitigare con TODO espliciti + claim limitati.
- Rischio rottura compatibilità test esistenti → mitigare con doppio path (legacy placeholder + real-min).

**4) Sezione C — Migrazione VBA (macro bandiera)**
- **Scopo**
- Avviare migrazione credibile e verificabile con una macro pilota ad alto valore.
- **Task**
- Selezione macro bandiera (criteri: frequenza uso, rischio, indipendenza Excel).
- Redazione scheda macro completa (input/output/unità/tolleranze/dipendenze).
- Golden tests baseline (VBA output di riferimento) vs nuova routine.
- **File toccati (pianificati)**
- SPEC_05_VBA_Migration_and_TestStrategy.md, docs/specs/PLAN_NEXT_IMPLEMENTATION.md, test_golden_rd2229.py (o file golden dedicato), cartella doc macro in visual_basic.
- **Acceptance Criteria**
- Macro bandiera tracciata end-to-end con baseline fissata.
- Golden tests stabili con tolleranze documentate.
- Stato migrazione macro aggiornato a livello spec/backlog.
- **Rischi / Mitigazioni**
- Rischio differenze numeriche/rounding → mitigare con policy tolleranze per famiglia calcolo.
- Rischio dipendenza da Excel non replicabile → mitigare con snapshot input/output statici.

**5) Sezione D — Plugin/MODULE_SPEC + `.jsoncode`**
- **Scopo**
- Rendere contratti plugin/config rigorosi e verificabili.
- **Task**
- Normalizzare schema MODULE_SPEC (id/version/entrypoints/capabilities/contracts).
- Definire validazione `.jsoncode` minima obbligatoria + opzionale estesa.
- Introdurre provenance parameter chain: default norma → profilo progetto → override utente.
- **File toccati (pianificati)**
- plugin_registry.py, plugins.py, jsoncode_loader.py, SPEC_04_Plugins_and_jsoncode.md, MVP_PLACEHOLDER.jsoncode.
- **Acceptance Criteria**
- Plugin non compatibile viene disabilitato con warning tracciato.
- `.jsoncode` non valido fallisce con errore esplicito e messaggio chiaro.
- Provenance disponibile in trace/report metadata.
- **Rischi / Mitigazioni**
- Rischio overengineering schema → mitigare con validazione a livelli (minimo/strict).
- Rischio breaking change plugin → mitigare con compat versioning policy.

**6) Sezione E — Quinto stream (2 opzioni)**
- **E1 (raccomandata prudente): Reportistica e audit trail**
- **Scopo**: standardizzare result contract + export JSON/HTML/PDF con metadati di audit.
- **File**: reporting, SPEC_05_VBA_Migration_and_TestStrategy.md, nuovi test reporting.
- **AC**: report include versione norma/plugin, hash input, timestamp, severity.
- **Rischio**: aumento scope output; mitigare con MVP report JSON first.
- **E2 (alternativa): Launcher integration del nuovo MVP**
- **Scopo**: collegare pipeline MVP al launcher Qt come flow tecnico dimostrativo.
- **File**: app.py, pages, verification_adapter.py.
- **AC**: run MVP da UI con feedback stato/log.
- **Rischio**: dipendenza da stabilità stream A; mitigare posticipando dopo chiusura blocker.
- **Raccomandazione**: partire da E1 per chiudere audit/compliance prima dell’integrazione UI.

**7) Sequenza consigliata (Roadmap 1..N)**
- 1) Stream A: chiusura blocker import/entrypoint e allineamento test runtime.
- 2) Stream D: hardening MODULE_SPEC + `.jsoncode` validation/provenance.
- 3) Stream B: verifica semi-reale + trace completo con TODO normativi.
- 4) Stream C: macro bandiera + golden baseline.
- 5) Stream E1 (raccomandata): report/audit standardizzati.
- 6) Regressione full suite + consolidamento docs LOCKED/OPEN.
- 7) Solo dopo: eventuale E2 launcher integration.

**8) Checklist PR/commit (>=3 commit logici)**
- **Commit 1 — `packaging+tests-hardening`**
- Scope: stream A + aggiornamento blocker state.
- Exit: 2 test rossi chiusi o formalmente confinati con workaround deterministico.
- **Commit 2 — `plugin-jsoncode-contracts`**
- Scope: stream D.
- Exit: validation/provenance attive, compat policy documentata.
- **Commit 3 — `mvp-real-check+trace`**
- Scope: stream B.
- Exit: check semi-reale funzionante, trace completo, test verdi mirati.
- **Commit 4 — `vba-flagship-golden`** (raccomandato)
- Scope: stream C.
- Exit: golden tests macro bandiera.
- **Commit 5 — `report-audit-contract`** (se E1)
- Scope: stream E1.
- Exit: output standard con metadati audit.

**9) Test strategy (mirati + regressione)**
- **Per A**
- Mirati: test_app_launch.py, test_entrypoint_no_pyside.py.
- Regressione: smoke Qt + `pytest -q` completo.
- **Per D**
- Mirati: test su registry/jsoncode loader + compat fallback.
- Regressione: test plugin/logging e MVP e2e.
- **Per B**
- Mirati: test_mvp_result_trace_contract.py, test_mvp_end_to_end.py, invarianti dominio.
- Regressione: subset pipeline + full.
- **Per C**
- Mirati: golden macro test + tolleranze.
- Regressione: check correlati famiglia calcolo.
- **Per E1/E2**
- E1: test report contract + trace completeness.
- E2: test UI integration smoke + no regression launcher.

**10) BOZZA COMPLETA DI FILE MD (testo pronto)**

- **docs/specs/PLAN_NEXT_IMPLEMENTATION.md**

```markdown
# PLAN NEXT IMPLEMENTATION (Batch-ready)

## 1. Scope e principi
- Fonte vincolante: docs/MEGAPLAN/AGGREGAZIONE.md + SPEC LOCKED in docs/specs/.
- Modalità: implementazione incrementale in stream A–E con tracciabilità completa.
- Divieto: nessun valore normativo inventato; usare TODO(NTC/EC/RD) espliciti.

## 2. Stato iniziale
- MVP isolato presente (SQLite + pipeline + test MVP verdi).
- Strategia B attiva: 2 test rossi preesistenti accettati temporaneamente e tracciati in BLOCKERS.md.

## 3. Stream A — Packaging / Import / Entrypoint
### Task A1
- Scopo: allineare import/runtime per src-layout.
- File: pyproject.toml, pytest.ini, tests/test_app_launch.py, tests/test_entrypoint_no_pyside.py, src/rd2229/__main__.py, src/rd2229/ui_qt/app.py.
- Acceptance:
  - test_app_launch e test_entrypoint_no_pyside verdi in CI standard.
  - coerenza tra avvio `rd2229` e `python -m rd2229`.
- Rischi/Mitigazioni:
  - differenze ambiente locale/CI -> matrice esecuzione esplicita.

### Task A2
- Scopo: formalizzare policy test runtime.
- File: docs/specs/BLOCKERS.md (stato), docs/ARCHITECTURE.md (nota runtime).
- Acceptance: policy unica documentata.

## 4. Stream D — Plugin/MODULE_SPEC + .jsoncode
### Task D1
- Scopo: standard MODULE_SPEC.
- File: src/rd2229/plugin_registry.py, src/rd2229/mvp/plugins.py, docs/specs/SPEC_04_Plugins_and_jsoncode.md.
- Acceptance:
  - schema minimo uniforme (id, version, entrypoints, capabilities, contracts).
  - fallback su incompatibilità con warning tracciato.
- Rischi/Mitigazioni:
  - breaking plugin -> compat matrix + version gating.

### Task D2
- Scopo: validazione `.jsoncode` + provenance.
- File: src/rd2229/mvp/jsoncode_loader.py, config/calculation_codes/MVP_PLACEHOLDER.jsoncode, docs/specs/SPEC_04_Plugins_and_jsoncode.md.
- Acceptance:
  - chiavi obbligatorie validate.
  - catena provenienza parametro disponibile in trace metadata.

## 5. Stream B — MVP meno placeholder
### Task B1
- Scopo: introdurre check semi-reale minimo.
- File: src/rd2229/mvp/engine.py, src/rd2229/mvp/contracts.py, src/rd2229/mvp/models.py.
- Acceptance:
  - almeno un check non-placeholder con output deterministico.
  - trace completo con run_id + norm_references[].
- Rischi/Mitigazioni:
  - rischio interpretazione normativa -> TODO(NTC/EC/RD) obbligatori.

### Task B2
- Scopo: consolidare test di contratto.
- File: tests/test_mvp_result_trace_contract.py, tests/test_mvp_end_to_end.py, tests/test_mvp_domain_invariants.py.
- Acceptance: test mirati verdi + regressione subset.

## 6. Stream C — Migrazione VBA (macro bandiera)
### Task C1
- Scopo: selezione macro bandiera e scheda tecnica.
- File: docs/specs/SPEC_05_VBA_Migration_and_TestStrategy.md, docs/visual_basic/*.
- Acceptance:
  - macro selezionata con input/output/unità/tolleranze.
  - baseline definita.

### Task C2
- Scopo: golden tests per macro bandiera.
- File: tests/test_golden_rd2229.py (o test dedicato), artefatti baseline.
- Acceptance:
  - confronto stabile entro tolleranza documentata.
- Rischi/Mitigazioni:
  - rounding/separator -> policy tolleranze per famiglia calcolo.

## 7. Stream E (scegliere)
### E1 (raccomandata): Reportistica + Audit
- Scopo: output standard JSON/HTML/PDF con metadati audit.
- File: src/reporting/*, docs/specs/SPEC_05_VBA_Migration_and_TestStrategy.md.
- Acceptance:
  - report include norma/plugin/version/hash input/timestamp/severity.

### E2: Launcher integration MVP
- Scopo: run MVP da launcher Qt.
- File: src/rd2229/ui_qt/app.py, src/rd2229/ui_qt/pages/*, src/rd2229/verification_adapter.py.
- Acceptance:
  - esecuzione MVP da UI con feedback stato/log.

## 8. Roadmap consigliata
1) A
2) D
3) B
4) C
5) E1 (o E2 se priorità prodotto UI)

## 9. Commit plan
- Commit 1: packaging+tests-hardening
- Commit 2: plugin-jsoncode-contracts
- Commit 3: mvp-real-check+trace
- Commit 4: vba-flagship-golden
- Commit 5: report-audit-contract (se E1)

## 10. Test plan sintetico
- A: test_app_launch + test_entrypoint_no_pyside + full
- D: plugin/jsoncode tests + mvp e2e
- B: mvp trace/invariants/e2e
- C: golden macro + correlati
- E1/E2: report contract o UI smoke + regressione finale
```

- **docs/specs/BLOCKERS.md**

```markdown
# BLOCKERS — Test Rossi Preesistenti (Strategia B)

## Stato
- Strategia attiva: B (accettazione temporanea con formalizzazione del debito).
- Obiettivo: confinare il rischio e chiudere i blocker nello stream A.

## Blocker 1
- Test: tests/test_app_launch.py::test_app_launch
- Sintomo: ModuleNotFoundError: No module named 'rd2229'
- Root cause ipotizzata:
  - disallineamento import path/package discovery tra src-layout, ambiente test e install mode.
- Impatto:
  - falso negativo su smoke launch; riduce affidabilità CI su entrypoint.
- Workaround temporaneo:
  - esecuzione in ambiente con package installato editable oppure policy test runtime documentata.
- Next steps:
  - allineare pyproject/pytest import strategy e verificare in matrice CI.
- Criteri chiusura:
  - test verde in CI standard senza workaround manuale.
  - ripetibilità locale documentata.

## Blocker 2
- Test: tests/test_entrypoint_no_pyside.py::test_entrypoint_graceful_no_pyside
- Sintomo: ModuleNotFoundError: No module named 'rd2229'
- Root cause ipotizzata:
  - stessa classe di problema packaging/import del blocker 1.
- Impatto:
  - non verificabile in modo stabile il fallback “graceful no-PySide”.
- Workaround temporaneo:
  - esecuzione in ambiente con package path risolto; mantenere test separato in stage runtime.
- Next steps:
  - consolidare entrypoint/import path e fixture di test coerenti.
- Criteri chiusura:
  - test verde in CI standard.
  - comportamento fallback validato su exit code + messaggio utente.

## Vincoli di governance
- Nessuna modifica normativa implicita.
- Ogni workaround deve avere scadenza e owner nel PR stream A.
- Aggiornare questo file ad ogni release candidate.
```

**Domande bloccanti (max 7, multiple-choice)**
- 1) Priorità stream E?
- A) E1 Reportistica/Audit (raccomandata)
- B) E2 Launcher Integration
- C) Entrambe in parallelo
- D) Nessuna nel prossimo ciclo
- E) Altro

- 2) Chiusura blocker A in questo ciclo?
- A) Obbligatoria prima di ogni altro stream (raccomandata prudente)
- B) Dopo stream D
- C) Dopo stream B
- D) In ciclo successivo
- E) Altro

- 3) Macro bandiera VBA: criterio primario di scelta?
- A) Maggior frequenza d’uso (raccomandata)
- B) Maggior rischio numerico
- C) Maggior impatto commerciale
- D) Più facile da migrare
- E) Altro

- 4) Livello rigore `.jsoncode` subito?
- A) Minimo obbligatorio + warning (raccomandata)
- B) Strict schema completo immediato
- C) Solo validazione sintattica
- D) Nessuna validazione addizionale
- E) Altro

- 5) Policy TODO normativi in stream B?
- A) Obbligatori con etichetta `TODO(NTC/EC/RD): ...` (raccomandata)
- B) Facoltativi
- C) Solo nei documenti, non nel trace
- D) Rimandare al ciclo compliance
- E) Altro

- 6) Strategia commit?
- A) 5 commit (uno per stream principale, raccomandata)
- B) 3 commit compressi
- C) 1 mega commit
- D) Squash finale senza granularità
- E) Altro

Se vuoi, nel prossimo messaggio preparo una versione “ultra-compatta” dello stesso backlog pensata per essere usata direttamente come prompt Agent batch (senza cambiare contenuto).