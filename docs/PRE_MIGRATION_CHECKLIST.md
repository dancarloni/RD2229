# Pre-migration checklist: Tkinter → Qt (PySide6)

1. **Backup**
   - Eseguire backup completo di libs/app_module/ui/, verification_table.py, modules/ legacy.

2. **Test baseline**
   - Eseguire tutti i test esistenti su Tkinter per avere baseline di regressione.

3. **Congelamento legacy**
   - Spostare i file Tkinter in legacy/ con chiaro avviso.
   - Aggiornare ogni import nei moduli attivi per puntare solo a src/ui/qt/.

4. **Aggiornamento registry**
   - Aggiornare registry.py e modules_config.json per puntare ai nuovi moduli Qt.

5. **Stub moduli Qt**
   - Creare tutti i file stub in src/ui/qt/ secondo mapping.

6. **Aggiornamento documentazione**
   - Annotare in MIGRATION_TKINTER_TO_QT.md ogni differenza/deroga.
   - Aggiornare README, docs/USAGE_GUI.md, screenshots.

7. **Validazione ambiente**
   - Verificare che PySide6 sia installato e funzionante.
   - Aggiornare requirements.txt/requirements-dev.txt.

8. **Test di avviabilità**
   - Eseguire pytest-qt e test_regression_gui_cli.py.

9. **Pulizia**
   - Eliminare ogni riferimento residuo a tkinter/ttk nei moduli attivi.

10. **Comunicazione**

- Notificare il team della migrazione e delle nuove entrypoint GUI.
