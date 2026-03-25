---
title: Protocollo Operativo Standard Sera Mattina
last_sync: 2026-03-25
maintainers:
  - Daniele Carloni
tags: [handoff, protocollo, continuita]
source_of_truth: docs/PIANO_LAVORO.md, docs/PIANO_LAVORO_GUI.md
status: active
---

# Protocollo Operativo Standard

## Chiusura sera obbligatoria
1. Aggiornare PIANO_LAVORO e PIANO_LAVORO_GUI.
2. Salvare delta pipeline in docs/pipelines.
3. Compilare handoff con stato rischi e prossimi step.
4. Commit atomico e push remoto.

## Ripartenza mattino
1. Pull branch remoto.
2. Leggere PIANO_LAVORO poi PIANO_LAVORO_GUI.
3. Leggere docs/pipelines/MASTER_MATRIX.md.
4. Ripartire dai primi 3 task dell handoff.

## Template handoff minimo
- Data e ora
- Branch e commit
- Stato fasi
- Decisioni bloccanti
- Rischi aperti
- Prime 3 azioni

## Checklist compatta
- Repo allineato
- Fonti di verita aggiornate
- Pipeline docs aggiornate
- Commit e push eseguiti
