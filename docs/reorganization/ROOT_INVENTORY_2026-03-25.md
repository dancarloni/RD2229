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

1. Data di rimozione stub root definita: 2026-04-01 (finestra transitoria 7 giorni).
2. Politica snapshot testuali: vietati in root, consentiti solo in `docs/archived/snapshots/`.

## Delta implementato (sessione 2026-03-25)

- Creata quarantena tecnica: `archive/quarantine/2026-03-25_root_cleanup/`.
- Spostati in quarantena file accidentali/output/log: `.tmp_pytest_1.txt`, `app.log`, `rd2229_agent.log`, `pytest_output.txt`, `output_esempio.txt`, `tmp_test.csv`, `tatus --porcelain`, `witch main`, `pyproject.toml.txt`, `.workspace_inspect_app.py`.
- Spostati in quarantena anche script demo/debug root per purge controllato (policy terminale senza delete diretto): `analyze_sections_json.py`, `debug_material_suggest.py`, `debug_material_suggest2.py`, `demo_config_system.py`, `demo_matplotlib_integration.py`, `demo_sections.json`, `demo_verification_engine.py`, `esempio_pressoflessione_deviata.py`, `launch_material_editor.py`, `reorganize_sections_app.py`, `test_veloce_deviata.py`, `progetto.zip`.
- Spostata documentazione storica root in `docs/archived/root_cleanup_2026-03-25/`.
- Spostato riferimento normativo PDF in `docs/references/legislation/`.
- Rinominati stub planning root in forma transitoria con deadline: `Plan_master.STUB.deprecated.remove-2026-04-01.md`, `Plan_master2.STUB.deprecated.remove-2026-04-01.md`, `PLANCODE.STUB.deprecated.remove-2026-04-01.md`.
