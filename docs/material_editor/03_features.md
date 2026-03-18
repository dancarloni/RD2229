# Material Editor GUI — Funzionalità dettagliate

## Tab e tipologie
- Ogni tipologia di materiale (calcestruzzi, acciai, legno, muratura, compositi, terreni) ha una propria tab.
- Ogni tab contiene tabella, filtri, frame dettaglio, esportazione/importazione.

## Tabella materiali
- Colonne dinamiche, ordinabili, drag&drop, personalizzabili.
- Evidenziazione materiali incompleti (sfondo giallo).
- Parametri calcolati, parametri extra, parametri per verifiche al fuoco sempre visibili.
- Override manuale con flag, audit trail.
- Batch editing via selezione multipla e menù contestuale.

## Frame dettaglio
- Editing rapido, navigazione da tastiera (Tab, Shift+Tab, Enter, frecce).
- Shortcut Ctrl+S per salvataggio, Enter per avanzamento campo e salvataggio.
- Evidenziazione campi modificati/non salvati.
- Undo/redo locale.
- Override manuale parametri calcolati.
 - Validazione soft: la validazione viene eseguita alla selezione di una riga e dopo il salvataggio. Gli avvisi e i campi mancanti vengono mostrati nel pannello dettaglio (`warning_label`) ma non bloccano il salvataggio. Le regole di validazione sono definite in `src/ui/qt/material_editor/logic/material_validation_logic.py`.

## Esportazione/importazione
- Formato selezionabile (HTML, Markdown, CSV, testo semplice), persistente.
- Area testuale pronta da copiare.
- Importazione rapida tramite incolla di testo ordinato.
- Batch export/import con template.

## Personalizzazione layout
- Drag&drop colonne, ordine e visibilità.
- Reset layout con conferma.

## Sicurezza e tracciabilità
- Audit trail sempre attivo.
- Conferma esplicita per operazioni distruttive.
- Log visuale, notifiche non intrusive.

## Help e tema
- Tooltips, help contestuale, anteprima verifiche.
- Tema dark/light selezionabile.

---

Per edge-case e shortcut, vedi docs/material_editor/04_edge_cases.md e 05_shortcuts.md.