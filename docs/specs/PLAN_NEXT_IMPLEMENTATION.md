# PLAN NEXT IMPLEMENTATION (Batch-ready)

## 1. Scope e principi
- Fonte vincolante: `docs/MEGAPLAN/AGGREGAZIONE.md` + specifiche LOCKED in `docs/specs/`.
- Modalità: implementazione incrementale in stream A–E con tracciabilità completa.
- Divieto: nessun valore normativo inventato; usare `TODO(NTC/EC/RD)` espliciti.
- Strategia B: i 2 test rossi preesistenti restano accettati solo se confinati/documentati in `docs/specs/BLOCKERS.md`.

## 2. Stato iniziale
- MVP isolato presente (`src/rd2229/mvp/`) con SQLite + pipeline + test MVP verdi.
- Estensione plugin registry già introdotta con `ModuleSpec` mantenendo API esistenti (`register/get/list_plugins`).
- Suite completa con 2 fail preesistenti: `tests/test_app_launch.py`, `tests/test_entrypoint_no_pyside.py`.

## 2A. Stato esecuzione batch corrente
- Stream A: completato (packaging/import/entrypoint hardening + test runtime verdi).
- Stream D: completato a livello minimo (validazione `.jsoncode` estesa, provenance minima, compatibilità plugin).
- Stream B: completato a livello minimo (`MVP_REAL_MIN`, trace contract rinforzato, fallback `MVP_PLACEHOLDER`).
- Stream E2 (baseline): avviato con launcher operativo (catalogo moduli, input configurabili, selezioni, output run).
- Regressione: suite completa verde (`510 passed`, `0 failed`).

## 3. Stream A — Packaging / Import / Entrypoint

### Task A1 — Stabilità import runtime
- Scopo: allineare import/runtime per src-layout.
- File target: `pyproject.toml`, `pytest.ini`, `src/rd2229/__main__.py`, `src/rd2229/cli.py`.
- Next actionable:
  - Rendere robusta la risoluzione del package `rd2229` senza dipendenze da `PYTHONPATH` manuale.
  - Allineare configurazione pytest tra `pytest.ini` e `[tool.pytest.ini_options]`.
- Acceptance:
  - Avvio coerente in ambiente standard.
  - `python -m rd2229` e script `rd2229` allineati.
- Rischi/Mitigazioni:
  - Mismatch locale/CI: definire matrice comandi unica nel file blockers/backlog.

### Task A2 — Chiusura blocker test runtime
- Scopo: chiudere i 2 test rossi preesistenti.
- File target: `tests/test_app_launch.py`, `tests/test_entrypoint_no_pyside.py`, `tests/test_ui_qt_smoke.py`.
- Next actionable:
  - Confermare root cause packaging/import prima di eventuali fix test-side.
- Acceptance:
  - Entrambi i test verdi in CI standard.
- Rischi/Mitigazioni:
  - Fix cosmetico sui test: vietato senza root-cause fix.

## 4. Stream D — Plugin/MODULE_SPEC + jsoncode

### Task D1 — Contratto MODULE_SPEC
- Scopo: standardizzare `id/version/entrypoints/capabilities/contracts`.
- File target: `src/rd2229/plugin_registry.py`, `src/rd2229/mvp/plugins.py`, `docs/specs/SPEC_04_Plugins_and_jsoncode.md`.
- Next actionable:
  - Introdurre gating di compatibilità (discovery stabile, disabilitazione plugin incompatibili con warning tracciato).
- Acceptance:
  - Incompatibilità gestita in modo esplicito e non distruttivo.
- Rischi/Mitigazioni:
  - Breaking plugin legacy: usare default compat e fallback.

### Task D2 — Validazione jsoncode + provenance
- Scopo: validare `.jsoncode` e tracciare provenance parametri.
- File target: `src/rd2229/mvp/jsoncode_loader.py`, `config/calculation_codes/MVP_PLACEHOLDER.jsoncode`, `docs/CONFIG_JSONCODE_SYSTEM.md`.
- Next actionable:
  - Estendere validazione minima (`threshold`, `norm_references`) e introdurre metadato provenance in trace.
- Acceptance:
  - Errori schema espliciti e deterministici.
  - Provenance disponibile nei metadati risultato.
- Rischi/Mitigazioni:
  - Over-strict iniziale: livello minimo ora, strict futuro.

## 5. Stream B — MVP meno placeholder

### Task B1 — Introduzione check semi-reale
- Scopo: almeno un controllo non-placeholder, deterministicamente testabile.
- File target: `src/rd2229/mvp/engine.py`, `src/rd2229/mvp/contracts.py`, `src/rd2229/mvp/models.py`, `config/calculation_codes/MVP_PLACEHOLDER.jsoncode`.
- Next actionable:
  - Aggiungere `MVP_REAL_MIN` (formula deterministica tracciabile, non claim normativo).
  - Mantenere fallback `MVP_PLACEHOLDER` per compat.
- Acceptance:
  - Check semi-reale attivo e tracciato.
  - `run_id`, `norm_references[]`, `method_id`, assumptions/warnings sempre presenti.
  - `TODO(NTC/EC/RD)` espliciti quando necessario.
- Rischi/Mitigazioni:
  - Rischio claim normativi eccessivi: labeling prudente e note TODO.

### Task B2 — Result contract e severità
- Scopo: standardizzare esiti `OK/WARN/FAIL` e contratto minimo.
- File target: `src/rd2229/mvp/contracts.py`, `tests/test_mvp_result_trace_contract.py`, `tests/test_mvp_end_to_end.py`.
- Acceptance:
  - Contratto rispettato da tutti i risultati MVP.

## 6. Stream C — Migrazione VBA (macro bandiera)
### Task C1
- Scopo: selezionare 1 macro pilota e scheda tecnica completa.
- Acceptance: input/output/unità/tolleranze/dipendenze dichiarati.

### Task C2
- Scopo: baseline golden test VBA vs motore moderno.
- Acceptance: test stabile con tolleranze esplicite.

## 7. Stream E — Alpha output e integrazione
### E1 — Reportistica e audit trail
- Scopo: output JSON/HTML con metadati audit.
- Acceptance: norma, plugin versions, timestamp, hash input, severity.

### E2 — Integrazione launcher Alpha
- Scopo: flusso end-to-end da launcher PyQt6.
- Acceptance: apri progetto, lanci run, consulti risultato/log.

## 8. Sequenza consigliata
1) A
2) D
3) B
4) C
5) E1
6) E2
7) regressione full + allineamento docs
8) alpha freeze

## 9. Commit plan
- Commit 1: `specs-backlog-and-blockers`
- Commit 2: `packaging-and-runtime-hardening` (A)
- Commit 3: `plugin-jsoncode-contract-hardening` (D)
- Commit 4: `mvp-real-check-and-result-contract` (B)
- Commit 5: `vba-flagship-golden-baseline` (C)
- Commit 6: `reporting-and-launcher-alpha` (E)

## 10. Test plan sintetico
- A: `test_app_launch`, `test_entrypoint_no_pyside`, `test_ui_qt_smoke`, full suite.
- D: plugin registry/jsoncode invalid cases + regressione plugin/logging.
- B: trace contract/domain invariants/end-to-end MVP.
- C: golden macro tests.
- E: report contract tests + launcher smoke.
