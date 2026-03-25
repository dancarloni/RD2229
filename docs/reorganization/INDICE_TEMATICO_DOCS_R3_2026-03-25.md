---
title: Indice Tematico Documentazione (R3)
date: 2026-03-25
phase: R3
status: in-progress
related:
  - docs/reorganization/MASTERPLAN_RISTRUTTURAZIONE_WORKSPACE_2026-03-25.md
  - docs/reorganization/INVENTARIO_R1_WORKSPACE_2026-03-25.md
---

# Indice tematico documentazione RD2229

## 1. Scopo

Definire una navigazione per temi della documentazione, separando contenuti vivi
(operativi) da contenuti storici (archivio).

## 2. Macro-domini target

| Dominio | Cartella target | Stato |
|---|---|---|
| Governance progetto | docs/PIANO_LAVORO.md, docs/PIANO_LAVORO_GUI.md | ATTIVO |
| Ristrutturazione workspace | docs/reorganization/ | ATTIVO |
| Architettura software | docs/architecture/ + docs/ARCHITETTURA_*.md | PARZIALE |
| GUI e UX | docs/ARCHITETTURA_GUI.md + docs/material_editor/ | PARZIALE |
| Moduli tecnici | docs/modules/, docs/normative/, docs/norms/ | ATTIVO |
| Audit per fase | docs/audit_fase_*.md | ATTIVO (da consolidare) |
| Piani per fase | docs/piano_fase_*.md | ATTIVO (da consolidare) |
| Tracciabilita/RTM | docs/RTM/, docs/EVIDENCE_LOG.md | ATTIVO |
| Storico sessioni e planning | docs/archived/ | ATTIVO |
| Output generati docs | docs/generated/ | ATTIVO |

## 3. Regole operative R3

1. Nuovi documenti operativi devono nascere in un dominio tematico esplicito.
2. I documenti storici non devono restare in root.
3. Le fonti di verita restano due:
   - docs/PIANO_LAVORO.md
   - docs/PIANO_LAVORO_GUI.md
4. I documenti in docs/archived non sono contratti di path per il codice.

## 4. Consolidamenti previsti (step successivi)

1. Accorpare audit/piano per fase in indici progressivi (non eliminativi).
2. Creare `docs/audit/INDEX_AUDIT.md` con puntatori per fase.
3. Creare `docs/modules/INDEX_MODULES.md` con mappa dominio -> file.
4. Creare `docs/gui/INDEX_GUI.md` con blueprint e mapping moduli/finestra.

## 5. Esito R3 parziale

- classificazione tematica disponibile;
- archivio storico gia avviato e operativo;
- prossima milestone: indici navigabili per audit/moduli/gui.
