# DEPRECATION REGISTER

> Aggiornato: 2026-02-26

## Formato record

| ID | Modulo/File | Motivo | Sostituto | Fase rimozione | Impatto test | Stato |
|----|------------|--------|-----------|---------------|-------------|-------|

## Registro corrente

| ID | Modulo/File | Motivo | Sostituto | Fase rimozione | Impatto test | Stato |
|----|------------|--------|-----------|---------------|-------------|-------|
| DEP-001 | `src/core_calculus/section_calculations.py` importa da `apps/sections/` | Viola confini architetturali (src → apps) | Adattatore in `src/core_calculus/` che non dipende da `apps` | Beta | Test in `tests/test_step5_adapter_smoke.py` | OPEN — da rifattorizzare |
| DEP-002 | `apps/sections/` come entrypoint predefinito GUI | Superseded da `src/ui/modern/` (MVVM) | `src/ui/modern/main_window.py` + builtin_features | Beta | Test con marker `gui` | OPEN |
| DEP-003 | `src/rd2229/mvp/engine.py::PlaceholderVerificationEngine` check `MVP_PLACEHOLDER` | Sostituito da `MVP_REAL_MIN` per default | `MVP_REAL_MIN` in stesso engine; `MVP_PLACEHOLDER` rimane fallback | Alpha | `test_mvp_end_to_end.py` | IN_PROGRESS |

## Regole governance

1. Ogni deprecazione ha `ID`, `motivo`, `sostituto` e `fase di rimozione`.
2. Shim di compatibilità obbligatori fino alla fase di rimozione dichiarata.
3. Nessuna deprecazione senza sostituto operativo.
4. Aggiornare questo registro ad ogni batch Agent e ogni release candidate.
