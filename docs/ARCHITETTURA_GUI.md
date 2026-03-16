# ARCHITETTURA GUI — RD2229 V1

## Obiettivo

Rendere il software avviabile e operativo in GUI con una shell unica tab-based e integrazione completa con pipeline, report e moduli specialistici.

## Entry point

- Principale: `python -m src.ui.modern.app`
- Package-level: `python -m rd2229` (delegato alla GUI moderna)
- Legacy interno: `src/ui/qt/entrypoint.py` (modulare, non entrypoint primario)

## Struttura a tab

1. Dashboard: preset rapidi, I/O progetto, export risultati/report, log operativo
2. Progetto: editor completo `ProjectModel` (info, geometria, materiali, carichi, code settings, seismic, fire)
3. Verifica: `PipelineRunnerWindow` con `QThread`, progress, tabella risultati, log, export CSV/JSON
4. Report: `ReportViewerWindow` con `QWebEngineView` e fallback `QTextBrowser`
5. Materiali: `EditorMaterialeWidget`
6. Sezioni: `SectionManagerWindow` + `VisualizzatoreSezione`
7. FEM/Telai: `CordoliWidget` (estendibile con telaio completo)
8. Vento: preset NTC2018 con log dedicato
9. Utility: Code Settings e Notification Center

## Persistenza GUI

- File progetto: JSON/JSONP (`src/project/repository.py`)
- Config utente: `~/.rd2229/config.json` (`src/core/user_config.py`)
- Index multi-progetto: `~/.rd2229/projects.db` (`src/core/persistence.py`)

## Flusso operativo principale

1. Carica/crea progetto nel tab Progetto
2. Esegui pipeline nel tab Verifica o Dashboard
3. Visualizza artefatto nel tab Report
4. Esporta JSON/MD/HTML da Dashboard o Verifica/Report

## Compatibilità

- Qt backend: PyQt6 preferito, fallback PySide6
- Report HTML embedded: `PyQt6-WebEngine` opzionale
- Modalità headless supportata per CI e smoke test

## Stato V1

- 6 moduli GUI stub convertiti in implementazioni operative
- Main window migrata a shell tab-based
- Suite test completa verde
