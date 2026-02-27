# RD2229 – Mappatura Moduli/Funzioni da Documentazione

Questa tabella elenca tutti i moduli, servizi, finestre e componenti richiesti dalla documentazione (docs/) per la nuova GUI/CLI, con percorso suggerito, categoria, dipendenze e fonte documentale.

| Categoria                | Nome Modulo/Finestra         | Percorso Sorgente                        | Dipendenze principali         | Fonte (docs/)                         |
|--------------------------|------------------------------|------------------------------------------|-------------------------------|----------------------------------------|
| Progetto                 | Project Editor               | modules/project_editor.py                 | ProjectModel, ProjectService  | PLAN_02.md, module_structure.md        |
| Progetto                 | Project Service              | src/project/service.py                    | ProjectModel                  | PLAN_02.md, ARCHITECTURE.md            |
| Sezioni                  | Section Manager              | src/ui/qt/section_manager.py              | CsvSectionSerializer          | PLAN_02.md, VERIFICA_7_OBIETTIVI.md    |
| Materiali                | Historical Material Editor   | modules/material_editor.py                | MaterialRepository            | PLAN_02.md, module_structure.md        |
| Materiali                | Material Repository          | src/materials/repository.py               | -                             | PLAN_02.md, ARCHITECTURE.md            |
| Calcoli/Verifiche        | Pipeline Runner              | modules/pipeline_runner.py                | ProjectModel, ResultsModel    | PLAN_02.md, module_structure.md        |
| Calcoli/Verifiche        | Verification Table           | libs/app_module/ui/verification_table.py  | ProjectModel                  | PLAN_02.md, VERIFICATION_TABLE_KEYBOARD.md |
| Calcoli/Verifiche        | Fire Check Module            | src/fire/rc_fire_check.py (+ GUI)         | ProjectModel                  | PLAN_02.md                             |
| Calcoli/Verifiche        | Wind Analysis Module         | src/wind/ntc2018.py (+ GUI)               | ProjectModel                  | PLAN_02.md                             |
| Report                   | Report Viewer                | modules/report_viewer.py                  | ResultsModel, ReportBuilder   | PLAN_02.md, module_structure.md        |
| Report                   | Report Builder Service       | src/reporting/report_builder.py           | ResultsModel                  | PLAN_02.md, ARCHITECTURE.md            |
| Codici/Config            | Code Settings Dialog         | modules/code_settings.py                  | ProjectModel                  | PLAN_02.md                             |
| Plugin/Estensioni        | Plugin Registry              | src/ui/modern/registry.py                 | -                             | PLAN_02.md, module_structure.md        |
| Plugin/Estensioni        | Notification Center          | libs/app_module/ui/notification_center.py | -                             | PLAN_02.md                             |
| Utility/Supporto         | Debug Viewer                 | libs/app_module/ui/debug_viewer.py        | -                             | PLAN_02.md, module_structure.md        |
| Utility/Supporto         | Module Selector              | src/ui/qt/module_selector.py              | ProjectService, registry      | PLAN_02.md, WINDOW_MANAGEMENT_FIX.md   |

> Generato automaticamente da analisi docs/ (PLAN_02.md, module_structure.md, ARCHITECTURE.md, WINDOW_MANAGEMENT_FIX.md, VERIFICA_7_OBIETTIVI.md, VERIFICATION_TABLE_KEYBOARD.md)

## Note
- Ogni modulo deve esportare `MODULE_SPEC` e una factory `create_module()`.
- I moduli GUI vanno migrati in Qt (PySide6) e registrati nel nuovo registry.
- I servizi (repository, builder, service) sono singleton o factory condivise.
- I moduli legacy Tkinter vanno spostati in legacy/ o eliminati.
- Aggiornare modules_config.json e test di registry/launch per ogni nuovo modulo.
