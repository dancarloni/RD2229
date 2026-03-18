# Material Editor GUI — Panoramica

La Material Editor GUI di RD2229 consente la gestione completa di materiali strutturali (calcestruzzi, acciai, legno, muratura, compositi, terreni) tramite un'interfaccia a schede (tab), con tabella personalizzabile, frame dettaglio, batch editing, esportazione/importazione rapida, audit trail, override manuale dei parametri calcolati, e navigazione avanzata da tastiera.

## Obiettivi
- Massima rapidità e visibilità nell'editing
- Gestione di materiali eterogenei e parametri extra
- Personalizzazione layout e esportazione flessibile
- Sicurezza e tracciabilità (audit, conferme, undo/redo)

## Struttura workspace
- docs/material_editor/ — documentazione dettagliata
- src/ui/qt/material_editor/ — codice GUI e logica
- tests/material_editor/ — test Qt e casi d'uso

## Schema di interfaccia
Vedi docs/material_editor/02_wireframe.md

## Funzionalità principali
- Tab per tipologia materiale
- Tabella ordinabile, filtrabile, drag&drop colonne
- Frame dettaglio con override manuale
- Batch editing, esportazione/importazione rapida
- Audit trail, undo/redo, conferme operazioni
- Personalizzazione layout, reset layout
- Navigazione da tastiera, shortcut
- Help contestuale, tema dark/light

---

Per dettagli, vedi i file nelle sottocartelle.