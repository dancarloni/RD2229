---
title: Mapping Archive RD2229
date: 2026-03-25
phase: R2-R3
status: active
related:
  - docs/archived/README.md
  - docs/reorganization/ROOT_INVENTORY_2026-03-25.md
---

# Archive Mapping

## Obiettivo

Separare con chiarezza archivio tecnico da archivio documentale storico.

## Mappa

| Area | Contenuto | Regola |
|---|---|---|
| docs/archived/ | storico decisionale/documentale (session notes, planning, summaries) | leggibile, non fonte operativa |
| docs/generated/ | output generati utili (es. CI report) | rigenerabile, non editare manualmente |
| archive/ | backup tecnici e snapshot dati non operativi | evitare uso runtime |

## Vincoli

1. Nessun modulo di produzione deve leggere da `docs/archived/` o `archive/`.
2. Le fonti di verità restano `docs/PIANO_LAVORO.md` e `docs/PIANO_LAVORO_GUI.md`.
3. Ogni move verso archivio deve essere registrato nel masterplan di ristrutturazione.
