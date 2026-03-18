# Controller centrale — Design e utilizzo

Questa pagina descrive il `ControllerBase` generale e il `MaterialEditorController` specifico per la Material Editor GUI.

## ControllerBase (`src/core/controller_base.py`)

- Fornisce un pattern leggero di controller con lifecycle (`start`/`stop`), storage di stato (`set_state`/`get_state`) e un semplice pub/sub (`on`/`off`/`emit`).
- Deve essere esteso da tutti i controller dei vari moduli dell'applicazione per garantire coerenza e riutilizzabilità.

API principale:
- `on(event, callback)` — registra un listener per un evento.
- `emit(event, *args)` — notifica i listener.
- `set_state(key, value)` — salva stato e notifica `state_changed`.

## MaterialEditorController (`src/ui/qt/material_editor/controller.py`)

- Estende `ControllerBase` e coordina i widget del Material Editor: la `MaterialTableWidget`, il `MaterialDetailFrame`, e il `MaterialExportWidget`.
- Non esegue operazioni Qt all'import; i widget vengono collegati a runtime tramite i metodi `attach_table`, `attach_detail`, `attach_export`.

Funzionalità implementate:
- Selezione tabella -> popolamento frame dettaglio (`_on_table_selection_changed`).
- Salvataggio dettaglio -> `on_save_clicked` aggiunge/aggiorna il materiale nel repository e aggiorna il widget export.
- Cancel -> `on_cancel_clicked` ripristina i valori originali.

Uso tipico (nel codepath UI):

1. Creare i widget `MaterialTableWidget`, `MaterialDetailFrame`, `MaterialExportWidget`.
2. Instanziare `MaterialEditorController()`.
3. `attach_table(table)` / `attach_detail(detail)` / `attach_export(export)`.
4. Avviare il controller se necessario con `start()`.

Notes:
- Per evitare import che carichino moduli Qt a livello di package, il controller carica il repository e logic senza dipendenze Qt. Il controller stesso stabilisce connessioni ai widget a runtime.
- Il `ControllerBase` è pensato per essere il punto di partenza per future centralizzazioni di controller di altri moduli.
