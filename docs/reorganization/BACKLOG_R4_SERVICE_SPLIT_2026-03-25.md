---
title: Backlog R4 Service Split GUI moderna
date: 2026-03-25
phase: R4
status: drafted
sources:
  - src/ui/modern/services/__init__.py
  - src/ui/modern/main_window.py
---

# Backlog R4 - segmentazione servizi applicativi

## 1. Problema corrente

`src/ui/modern/services/__init__.py` contiene responsabilita eterogenee:

- Project I/O;
- esecuzione pipeline;
- export risultati/report;
- preset dimostrativi e operativi;
- orchestrazioni specialistiche (vento, FEM, cross-pozzati, ecc.).

Questo aumenta accoppiamento, costo di test e complessita di manutenzione.

## 2. Split target proposto

### 2.1 Service layer

1. `project_io_service.py`
   - new/open/save project
2. `pipeline_execution_service.py`
   - run pipeline, export results
3. `report_orchestration_service.py`
   - build/export report html/md
4. `preset_execution_service.py`
   - preset dashboard, demo controllate
5. `module_launch_service.py`
   - apertura moduli specialistici con stato progetto

### 2.2 Model layer servizi

1. `action_report.py`
   - dataclass ActionReport
2. `service_errors.py`
   - eccezioni applicative servizi

### 2.3 Facade retrocompatibile

Mantenere `src/ui/modern/services/__init__.py` come facade temporanea
che re-esporta i simboli storici per non rompere i test durante la migrazione.

## 3. Backlog operativo

| ID | Task | Priorita | Dipendenza |
|---|---|---|---|
| R4.1 | Estrarre ActionReport in modulo dedicato | Alta | nessuna |
| R4.2 | Estrarre ProjectIOService | Alta | R4.1 |
| R4.3 | Estrarre CalculationService in pipeline_execution_service | Alta | R4.2 |
| R4.4 | Estrarre export report in report_orchestration_service | Alta | R4.3 |
| R4.5 | Isolare PresetExecutionService | Alta | R4.4 |
| R4.6 | Ridurre dipendenze dirette da main_window.py | Media | R4.5 |
| R4.7 | Aggiungere test unitari per ogni servizio estratto | Alta | R4.2-R4.6 |
| R4.8 | Introdurre facade __init__.py retrocompatibile | Alta | R4.2-R4.6 |

## 3.1 Stato esecuzione in sessione

Completato:

- [x] R4.1 Estratto `ActionReport` in `src/ui/modern/services/action_report.py`
- [x] R4.2 Estratto `ProjectIOService` in `src/ui/modern/services/project_io_service.py`
- [x] R4.3 Estratto `CalculationService` in `src/ui/modern/services/calculation_service.py`
- [x] R4.8 `src/ui/modern/services/__init__.py` mantenuto come facade retrocompatibile

Verifica:

- sanity import runtime eseguita con python venv locale;
- test mirato `tests/test_modern_ui_nongui.py` eseguito: 29 passed, 0 failed.

## 4. Impatto su GUI

`src/ui/modern/main_window.py` dovra consumare servizi tramite interfacce piu
stabili e piccole, facilitando:

- stato condiviso dashboard;
- wiring dei moduli specialistici;
- testability del flusso UI.

## 5. Criteri di accettazione R4

1. Nessuna regressione sui test che usano API storiche servizi.
2. `main_window.py` non dipende da logica operativa monolitica.
3. Preset e servizi core sono testabili in modo indipendente.
4. Facade temporanea presente e documentata.
