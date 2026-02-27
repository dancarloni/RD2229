# MIGRAZIONE GUI RD2229: DOCUMENTAZIONE OPERATIVA

## Passaggi di migrazione Tkinter → Qt (PySide6)

1. **Identificazione file Tkinter**
   - Tutti i file in libs/app_module/ui/ e verification_table.py che usano tkinter/ttk.
   - Mapping diretto verso src/ui/qt/ (es: SectionManager → section_manager.py).

2. **Creazione package src/ui/qt/**
   - Struttura modulare: ogni finestra/feature in un file dedicato.
   - Pattern MVVM e registry come in src/ui/modern/.

3. **Stub e placeholder**
   - Ogni modulo Qt inizia come stub con MODULE_SPEC e factory create_module.
   - Placeholder temporanei per logica non ancora migrata.

4. **Porting logica e UI**
   - Ricreare le finestre principali (ModuleSelector, ProjectEditor, PipelineRunner, ReportViewer, ecc.) in PySide6.
   - Sostituire ogni uso di tkinter/ttk/dialog con widget Qt equivalenti.
   - Integrare ProjectService e MaterialRepository come singleton/context.

5. **Registry e modules_config.json**
   - Aggiornare registry.py per includere i nuovi moduli Qt.
   - Aggiornare modules_config.json con chiavi, ordine e abilitazione.

6. **Rimozione Tkinter**
   - Spostare i file legacy in legacy/ o rimuovere.
   - Eliminare ogni import tkinter/ttk dal codice attivo.
   - Aggiornare README e docs per riflettere la nuova architettura.

7. **Test e validazione**
   - Eseguire tests/test_regression_gui_cli.py e pytest-qt.
   - Validare che ogni modulo Qt sia avviabile e funzioni.

8. **Aggiornamento riferimenti**
   - Sostituire ogni riferimento a Tkinter nei commenti, docstring, README, docs/ con PySide6/Qt.
   - Annotare in MIGRATION_TKINTER_TO_QT.md ogni eccezione o differenza rispetto al comportamento originale.

## Note operative
- La migrazione è atomica: nessun modulo Tkinter rimane attivo nella mainline.
- I test di regressione sono obbligatori per ogni feature migrata.
- La documentazione utente (docs/USAGE_GUI.md) deve riflettere i nuovi flussi Qt.
- I moduli legacy sono mantenuti solo per consultazione/storia.
