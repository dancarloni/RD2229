# Material Editor GUI — README

Questa cartella contiene il codice della Material Editor GUI per RD2229.

## Struttura
- material_editor_main.py — entry point/finestra principale
- widgets/ — widget custom (tabella, frame dettaglio, batch edit, esportazione)
- logic/ — logica di gestione materiali, override, audit, layout
- theme/ — gestione tema dark/light
 - controller.py — controller specifico `MaterialEditorController` che coordina widget e repository

## Dipendenze
- PySide6
- src/materials/adapter.py
- src/core/registro_log.py

## Avvio
La finestra Material Editor può essere lanciata direttamente dalla main window del software.

## Controller
Usare `MaterialEditorController` per collegare i widget al repository e gestire eventi/interazioni.
Vedi `docs/material_editor/13_controller.md` per dettagli d'uso.

---

Per la documentazione completa, vedi docs/material_editor/README.md.