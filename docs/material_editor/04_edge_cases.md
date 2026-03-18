# Material Editor GUI — Edge cases

## Parametri extra e verifiche al fuoco
- Parametri extra sempre esportati e mantenuti.
- Parametri per verifiche al fuoco sempre colonne della tabella.

## Modifica batch
- Selezione multipla (Ctrl+clic, Shift+clic).
- Menù contestuale “modifica batch” su qualsiasi colonna.
- Applicazione rapida del valore.

## Materiali incompleti
- Riga evidenziata se mancano parametri obbligatori della tipologia.

## Conflitto ID/codice
- ID unico e automatico, codice duplicato consentito con warning.
- Import massivo: ID uguale → sovrascrivi, ID diverso → aggiungi.

## Navigazione rapida
- Evidenziazione campi modificati/non salvati.
- Undo/redo, shortcut, focus automatico.

## Audit trail
- Override sempre consentito con warning.
- Tracciamento override manuale.

## Parametri calcolati
- Override manuale tramite flag.
- Audit e evidenziazione override.

---

Per altri edge-case, vedi docs/material_editor/06_batch_edit.md e 08_audit.md.