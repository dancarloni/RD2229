# BLOCKERS — Test rossi preesistenti (Strategia B)

## Stato

- Strategia attiva: **B** (accettazione temporanea con formalizzazione del debito).
- Vincolo: i blocker possono restare aperti solo se non peggiorano e sono tracciati con owner/exit criteria.
- Obiettivo: chiusura completa nello stream A.
- Aggiornamento batch corrente: i blocker A sono **chiusi** (suite: 510 passed, 0 failed).

## Blocker 1 (CHIUSO)

- Test: `tests/test_app_launch.py::test_app_launch`
- Sintomo: `ModuleNotFoundError: No module named 'rd2229'` in specifici contesti runtime/test.
- Root cause (ipotesi confermata dai piani): disallineamento tra src-layout, package discovery e configurazione test/runtime.
- Impatto: smoke launch non affidabile su tutte le pipeline.
- Workaround temporaneo: esecuzione in ambiente con package installato in editable mode coerente.
- Azioni eseguite:
  1. Package discovery allineata in `pyproject.toml` (`where=["src"]`, `include=["rd2229*"]`).
  2. Path pytest allineati (`pythonpath` include `src`).
  3. Rivalidazione test runtime Qt/no-Qt completata.
- Chiusura:
  - Test verde in ambiente standard.
  - Ripetibilità locale confermata.

## Blocker 2 (CHIUSO)

- Test: `tests/test_entrypoint_no_pyside.py::test_entrypoint_graceful_no_pyside`
- Sintomo: errore import package `rd2229` nel test fallback no-GUI.
- Root cause: stessa classe di problema packaging/import del blocker 1.
- Impatto: fallback no-GUI non verificabile in modo stabile.
- Workaround temporaneo: esecuzione in ambiente con package risolto e fixture controllata.
- Azioni eseguite:
  1. Consolidato import path su namespace `rd2229`.
  2. Rivalidato fallback no-GUI con exit code e messaggio.
  3. Stabilizzato smoke Qt in test mode (`RD2229_UI_TEST=1`).
- Chiusura:
  - Test verde in ambiente standard.
  - Validazione fallback confermata.

## Aggiornamento batch 2026-02-26

- Blocker 1/2: CHIUSI dal batch precedente.
- Suite corrente: `479 passed`, `9 skipped`, `0 failed` (CI headless senza PySide6/Qt).
- Nuovi blocker: nessuno introdotto.
- Documenti di specifica aggiunti in `docs/specs/`: ARCH_BOUNDARIES_AND_DEPENDENCIES.md, MODULE_CONTRACTS.md, REPOSITORY_CONTRACTS.md, GUI_INTEGRATION_RULES.md, DEPRECATION_REGISTER.md, AGENT_EXECUTION_CONTEXT.md.

## Governance

- Nessun workaround senza owner, scadenza e criterio di uscita.
- Nessuna scorciatoia normativa per bypassare test.
- Aggiornare questo file ad ogni release candidate/agent batch.

## Owner e stato corrente

- Owner tecnico corrente: batch Agent A (packaging/import hardening).
- Stato corrente: chiuso, monitorato in regressione completa.
