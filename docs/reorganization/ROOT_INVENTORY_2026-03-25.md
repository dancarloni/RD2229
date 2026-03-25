---
title: Root Inventory Workspace RD2229
date: 2026-03-25
phase: R2
status: in-progress
related:
  - docs/reorganization/MASTERPLAN_RISTRUTTURAZIONE_WORKSPACE_2026-03-25.md
  - docs/reorganization/INVENTARIO_R1_WORKSPACE_2026-03-25.md
---

# Root Inventory 2026-03-25

## Regole

- KEEP: file operativi correnti.
- MOVE: file validi ma in posizione non coerente.
- ARCHIVE: storico documentale.
- DELETE: artifact/log temporanei rigenerabili.

## Tabella operativa

| Elemento | Categoria | Azione | Motivazione |
|---|---|---|---|
| README.md | governance utente | KEEP | entrypoint ufficiale |
| pyproject.toml, pytest.ini, requirements*.txt | build/test config | KEEP | necessario a CI e locale |
| src/, tests/, data/, config/, docs/, scripts/ | prodotto | KEEP | core repository |
| examples/projects/* | demo progetto | KEEP | destinazione corretta |
| examples/reports/* | demo output | KEEP | destinazione corretta |
| docs/generated/ci/* | artifact CI | KEEP (generated) | tracciabilità report |
| Plan_master*.md, PLANCODE.md (root) | stub transitori | KEEP TEMP | redirect compatibilità, rimozione pianificata |
| app.log, rd2229_agent.log, .tmp_pytest_*.txt | log/artifact temporanei | DELETE | non contrattuali |
| tree_*.txt, project_tree.txt | snapshot struttura | MOVE -> docs/archived/snapshots | storico non operativo |
| apply_from_chat_plan.patch | patch storico | MOVE -> docs/archived/patches | mantenere tracciabilità |

## Decisioni aperte

1. Data di rimozione stub root `Plan_master*.md` / `PLANCODE.md`.
2. Politica definitiva per snapshot testuali in root.
