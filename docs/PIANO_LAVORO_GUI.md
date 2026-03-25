---
title: PIANO LAVORO GUI — RD2229
last_sync: 2026-03-25 (allineamento GUI con estensione R2 e quality gates CI)
maintainers:
  - Daniele Carloni
tags: [piano, roadmap, gui, design, dashboard, todo-sync]
---

# PIANO LAVORO GUI — RD2229

> Fonte di verita tecnica per la GUI moderna.
> Il file `docs/PIANO_LAVORO.md` resta il registro generale cross-modulo.

## Scopo e perimetro

Questo documento governa in dettaglio l'implementazione GUI:
- architettura e layout di navigazione;
- dipendenze, file interessati e contratti tra moduli;
- fasi e sub-fasi GUI con stato operativo;
- note tecniche e motivazioni progettuali;
- checklist TODO sincronizzabile via script.

Nota operativa: quando una modifica impatta l'architettura o il flusso utente GUI, aggiornare prima questo file, poi il registro generale.

## Allineamento con il masterplan workspace

La GUI moderna non e piu trattata come iniziativa isolata: la sua evoluzione e ora parte del
programma di ristrutturazione complessiva del repository.

Documento di riferimento trasversale:

- `docs/reorganization/MASTERPLAN_RISTRUTTURAZIONE_WORKSPACE_2026-03-25.md`

Implicazioni operative:

- le scelte GUI devono essere coerenti con la root minimale e con la nuova tassonomia documentale;
- i moduli Qt reali vanno ricondotti a un flusso unico centrato su dashboard, stato condiviso e servizi applicativi separati;
- la priorita architetturale immediata resta l'integrazione di Progetto e Dati, Materiali e Sezioni.

Delta esecuzione collegato alla ristrutturazione workspace:

- file demo progetto/report spostati da root in `examples/projects` e `examples/reports`;
- output CI XML spostato in `docs/generated/ci`;
- aggiornati i path di avvio demo in `README.md`.
- note di sessione e blocchi storici rimossi dalla root e archiviati in `docs/archived/session_notes`;
- piani storici (`Plan_master*`, `PLANCODE`) archiviati in `docs/archived/planning` con stub transitori.

Questa pulizia riduce il rumore operativo per la GUI e prepara le prossime tranche su registry esteso e sincronizzazione stato.

Avanzamento tecnico con impatto GUI (stessa sessione):

- creato backlog dedicato allo split servizi GUI moderni:
  - `docs/reorganization/BACKLOG_R4_SERVICE_SPLIT_2026-03-25.md`
- creato indice tematico docs per ridurre accoppiamento tra documentazione operativa e storico:
  - `docs/reorganization/INDICE_TEMATICO_DOCS_R3_2026-03-25.md`
- implementato primo step di service split (R4):
  - `src/ui/modern/services/action_report.py`
  - `src/ui/modern/services/project_io_service.py`
  - `src/ui/modern/services/calculation_service.py`
  - `src/ui/modern/services/__init__.py` mantenuto come facade di compatibilita
- validazione test non-GUI servizi: `tests/test_modern_ui_nongui.py` (29 passed)
- quality gates CI minimi riattivati con workflow attivi (`python-ci.yml`, `lint-test.yml`)
- completato cleanup root di snapshot/patch per ridurre rumore operativo durante il refactor GUI

## Decisioni guida GUI-V2 (vincolanti)

1. Tab ridotte a macro-settori disciplinari.
2. Dashboard unica a card come entry point operativo.
3. Riquadri a scomparsa solo quando necessari per ridurre rumore visivo.
4. Moduli: apertura in finestra dedicata consentita, ma input e controlli del modulo devono vivere nella stessa finestra.
5. Font operativi tra 8pt e 10pt, layout ricchi a colonne multiple per input e risultati.
6. Tutti i moduli sviluppati devono essere accessibili dalla dashboard (direttamente o via launcher di settore).

## Architettura di riferimento

### Macro-settori (tab)

Tab target raccomandate:
- Progetto e Dati
- Verifiche e Pipeline
- Report e Tracciabilita
- Moduli Specialistici

Note:
- Evitare tab per singolo widget.
- I widget verticali restano apribili da card o da menu contestuale del settore.

### Dashboard a card

La dashboard deve esporre:
- card accesso rapido (Nuovo, Apri, Salva, Esegui, Export, Report);
- card modulo (Materiali, Sezioni, FEM/Telai, Vento, X6/X8, etc.);
- card stato (ultimo progetto, norma attiva, warning, ultimo export);
- ricerca modulo e filtri per categoria.

Note implementative:
- usare registry centralizzato per popolare dinamicamente le card;
- mantenere ordine card configurabile (JSON/config utente);
- separare metadati presentazionali da logica di business.

## File e dipendenze principali

Core GUI:
- `src/ui/modern/main_window.py`
- `src/ui/modern/features/registry.py`
- `src/ui/modern/services/__init__.py`

Widget e moduli Qt:
- `src/ui/qt/project_editor.py`
- `src/ui/qt/pipeline_runner.py`
- `src/ui/qt/report_viewer.py`
- `src/ui/qt/material_editor.py`
- `src/ui/qt/section_manager.py`
- `src/ui/qt/notification_center.py`
- `src/ui/qt/telaio/telaio_window.py`
- `src/ui/qt/cordoli_widget.py`
- `src/ui/qt/stylesheet.py`

Persistenza:
- `src/core/user_config.py`
- `src/core/persistence.py`

Automazione TODO:
- `scripts/sync_todo_gui.py`

## Fasi e sub-fasi GUI-V2

### G2 — Navigazione e UX unificata

- [ ] G2.1 Riduzione tab a macro-settori disciplinari.
- [ ] G2.2 Dashboard card-based con launcher moduli completo.
- [ ] G2.3 Riquadri collapsible solo per sezioni dense.

### G3 — Accessibilita moduli e finestre

- [ ] G3.1 Mappatura completa moduli -> card/settore.
- [ ] G3.2 Apertura moduli in finestra autonoma con input locale completo.
- [ ] G3.3 Pattern estendibile per aggiunta nuovi moduli (registrazione unica).

### G4 — Densita informativa e stile

- [ ] G4.1 Layout multi-colonna standard per form e risultati.
- [ ] G4.2 Font default operativo 9pt (range 8-10pt per widget specialistici).
- [ ] G4.3 Stili QSS coerenti per dashboard, tabelle, warning/error.

### G5 — Tracciamento e sincronizzazione TODO

- [ ] G5.1 Script sync TODO attivo e documentato.
- [ ] G5.2 Sezione TODO sincronizzata automaticamente in questo file.
- [ ] G5.3 Aggiornamento riflesso su `docs/PIANO_LAVORO.md` (registro generale).

## Avanzamento implementazione (delta 2026-03-17)

- Completato primo incremento GUI-V2 in `src/ui/modern/main_window.py`.
- Struttura top-level migrata da tab verticali tematiche a macro-settori:
  - Dashboard
  - Progetto e Dati
  - Verifiche e Pipeline
  - Report e Tracciabilita
  - Moduli Specialistici
- Dashboard estesa con launcher rapidi verso i macro-settori e accesso diretto a moduli principali.
- Preset operativi convertiti in layout card-based (griglia 2 colonne) mantenendo registry e azioni esistenti.
- Implementato editing riga tramite dialog form (geometry/materiali/carichi) + dialog key/value per campo `extra` (validazione JSON stretta).

Note operative:
- L'integrazione mantiene compatibilita con i widget esistenti (`ProjectEditorWindow`, `PipelineRunnerWindow`, `ReportViewerWindow`, `EditorMaterialeWidget`, `SectionManagerWindow`, `CordoliWidget`).
- Il blocco `TODO_SYNC` resta gestito solo via script e non e stato modificato manualmente.

## TODO GUI sincronizzati

Sezione gestita da script. Non modificare manualmente il blocco sincronizzato.

<!-- TODO_SYNC:START -->
- Sync timestamp: 2026-03-17 13:17
- TODO GUI totali: 81
- Completati: 81
- Da fare: 0
- Riepilogo:
  - [x] GUI-0.1: Fix `TestSolutoreFEM::test_raise_not_implemented` in `src/fem/`
  - [x] GUI-0.2: Fix `test_schema_file_matches_model` — allineare schema JSON a ProjectModel
  - [x] GUI-0.3: Fix `test_build_report_artifact_propagates_warnings` — propagare warnings in build_report
  - [x] GUI-0.4: Verifica green: `pytest tests/ --tb=short -q` → 0 failed
  - [x] GUI-1.1: Refactor `build_main_window()` per usare `QTabWidget` come shell principale (7+ tab)
  - [x] GUI-1.2: Tab operative per sezioni principali (progetto, verifica, report, materiali, sezioni, FEM, vento)
  - [x] GUI-1.3: Barra menu completa File+Calcolo+Aiuto
  - [x] GUI-1.4: StatusBar con indicatori persistenti norma/progetto/elementi/warnings
  - [x] GUI-1.5: Compatibilità headless preservata (smoke headless + avvio app ok)
  - [x] GUI-2.1: Form `ProjectInfo` — campi principali presenti
  - [x] GUI-2.2: Tabella Geometria con extra/azioni CRUD dedicate (attuale: griglia base editabile)
  - [x] GUI-2.3: Tabella Materiali con extra/azioni CRUD + integrazione repository completa
  - [x] GUI-2.4: Tabella Carichi con colonna `extra` esplicita
  - [x] GUI-2.5: Sub-tab `CodeSettings` presente (norma/stati/unità)
  - [x] GUI-2.6: Sub-tab `SeismicInputs` presente
  - [x] GUI-2.7: Sub-tab `FireInputs` presente
  - [x] GUI-2.8: Toolbar Nuovo | Apri | Salva | Salva con nome | Validazione
  - [x] GUI-2.9: Copertura test GUI-2 dedicata (10+ test) non ancora consolidata
  - [x] GUI-3.1: `UserConfig` dataclass + caricamento da `~/.rd2229/config.json`
  - [x] GUI-3.2: `ProjectIndex` SQLite (`~/.rd2229/projects.db`) con path/nome/norma/timestamp/sha256
  - [x] GUI-3.3: File recenti anche in splash screen (attuale: menu File recenti)
  - [x] GUI-3.4: Auto-save opzionale ogni N minuti
  - [x] GUI-3.5: Test persistence dedicati (round-trip) da consolidare
  - [x] GUI-4.1: `PipelineWorker(QThread)` presente con segnali progress/log/completed/failed
  - [x] GUI-4.2: ComboBox norma popolata da registry
  - [x] GUI-4.3: Modalità indeterminata/determinata completa durante run
  - [x] GUI-4.4: Tabella risultati operativa
  - [x] GUI-4.5: Log colorato per livelli (attuale: log testuale)
  - [x] GUI-4.6: Export CSV nativo
  - [x] GUI-4.7: Export JSON da `ResultsModel`
  - [x] GUI-4.8: Pulsante annulla presente
  - [x] GUI-4.9: Test headless con mock worker dedicati
  - [x] GUI-5.1: API pubblica esposta (`list_norm_codes`)
  - [x] GUI-5.2: Combo norma popolata dinamicamente (10+ codici)
  - [x] GUI-5.3: Aggiornamento dinamico stati limite per norma
  - [x] GUI-5.4: Raggruppamento risultati per norma in modalità multi-norma
  - [x] GUI-5.5: Completamento template NTC2018 non-priority
  - [x] GUI-6.1: Import condizionale `QWebEngineView` con fallback `QTextBrowser`
  - [x] GUI-6.2: Rendering HTML in-app da artifact
  - [x] GUI-6.3: Toolbar completa con Stampa/PDF (con fallback informativo se WebEngine assente)
  - [x] GUI-6.4: Auto-refresh dopo run pipeline via signal
  - [x] GUI-6.5: Smoke test viewer/headless eseguito in sessione
  - [x] GUI-7.1: `project_editor.py` operativo
  - [x] GUI-7.2: `pipeline_runner.py` operativo
  - [x] GUI-7.3: `report_viewer.py` operativo
  - [x] GUI-7.4: `section_manager.py` con preview sezione
  - [x] GUI-7.5: Toast overlay animato (attuale: centro notifiche list/filter/clear)
  - [x] GUI-7.6: `code_settings.py` operativo
  - [x] GUI-7.7: Tab Materiali collegata
  - [x] GUI-7.8: Tab Sezioni collegata
  - [x] GUI-7.9: Integrazione completa `TelaioWindow` + `CordoliWidget` (attuale: `CordoliWidget`)
  - [x] GUI-7.10: Tab Vento collegata a preset/servizio vento
  - [x] GUI-8.1: Analisi/completamento struttura stylesheet effettuati
  - [x] GUI-8.2: Tema chiaro operativo
  - [x] GUI-8.3: Tema scuro operativo
  - [x] GUI-8.4: Stile tabelle risultati (OK/WARN/NON OK)
  - [x] GUI-8.5: Stile dedicato dialoghi normativi non ancora separato
  - [x] GUI-8.6: Applicazione tema globale da `UserConfig.theme`
  - [x] GUI-9.1: Entry `python -m rd2229` operativo
  - [x] GUI-9.2: Test E2E lancio reale Qt eseguito in sessione
  - [x] GUI-9.3: README aggiornato con avvio rapido GUI
  - [x] GUI-9.4: Allineamento completo optional GUI anche in `requirements*.txt`
  - [x] GUI-9.5: Smoke test headless eseguito (run + export report)
  - [x] GUI-9.6: Architettura GUI documentata
  - [x] GUI-2.2: Aggiungere colonna `extra` e azioni CRUD esplicite alla tabella Geometria.
  - [x] GUI-2.3: Completare tabella Materiali con `extra` + integrazione repository dedicata.
  - [x] GUI-2.4: Esporre e gestire campo `extra` per i carichi nel ProjectEditor.
  - [x] GUI-2.9: Consolidare test GUI dedicati del ProjectEditor (10+ casi headless).
  - [x] GUI-3.3: Estendere recenti anche a splash/landing.
  - [x] GUI-3.4: Implementare auto-save opzionale a intervallo configurabile.
  - [x] GUI-3.5: Aggiungere test round-trip specifici su `UserConfig` + `ProjectIndex`.
  - [x] GUI-4.3: Progress bar con modalità indeterminata iniziale e avanzamento su N elementi.
  - [x] GUI-4.5: Colorazione livelli nel log (`debug/info/warning/error`).
  - [x] GUI-4.9: Test headless con mock `PipelineWorker`.
  - [x] GUI-5.3: Cambio norma con refresh stati limite disponibili.
  - [x] GUI-5.4: Raggruppamento risultati per norma in scenario multi-norma.
  - [x] GUI-5.5: Completare template NTC2018 non-priority nel registry.
  - [x] GUI-7.5: Implementare toast overlay animato per notifiche live.
  - [x] GUI-7.9: Integrare `TelaioWindow` insieme a `CordoliWidget` nel tab FEM/Telai.
  - [x] GUI-8.5: Aggiungere stile specifico per dialoghi normativi.
  - [x] GUI-9.4: Allineare optional GUI anche in `requirements*.txt` (non solo extras in pyproject).
<!-- TODO_SYNC:END -->

## Completamento finale TODO GUI-V1 (2026-03-17)

### Obiettivo

Chiudere i residui GUI-V1 bloccati nel piano principale, con implementazione effettiva,
test headless, e sincronizzazione automatica dei TODO senza aggiornamenti manuali.

### GUI-3.3 — Recenti in landing/dashboard

- Implementazione in `src/ui/modern/main_window.py`:
  - loader backend-safe `_load_qlistwidget()` (compatibile PyQt6/PySide6)
  - nuova lista `recent_list` in dashboard (colonna destra) con tooltip operativo
  - popolamento iniziale da `UserConfig.recent_projects`
  - sincronizzazione live con menu `File > Recenti` in `_rebuild_recent_menu()`
  - apertura progetto con doppio click (`recent_list.itemDoubleClicked`)
- Risultato UX:
  - i file recenti non sono piu confinati al menu e sono disponibili subito nella landing.

### GUI-4.9 — Test headless mock worker

- Estensione test in `tests/test_pipeline_runner_qt.py`:
  - `test_cancel_flow_resets_state` (simulazione worker sospeso + annulla)
  - `test_failed_signal_logs_error_and_resets` (emissione `failed` + reset UI)
- Copertura ottenuta:
  - transizioni bottoni `Esegui/Annulla`
  - progress bar reset coerente
  - logging error-level atteso su failure path

### GUI-5.3 — Stati limite dinamici per norma

- Registry normativo (`src/core_calculus/normative_registry.py`):
  - API `list_norm_states(norm_code)`
  - derivazione stati da template attivi
  - fallback robusto per norme senza template completi (`RD2229`, `NTC2018`, `DM96`, ecc.)
- Pipeline runner (`src/ui/qt/pipeline_runner.py`):
  - label `Stati limite` con refresh automatico su cambio norma
  - handler `_on_norm_changed()` collegato a `cmb_norm.currentTextChanged`
- Test dedicato:
  - `test_norm_change_updates_limit_states_label`

### GUI-5.4 — Raggruppamento/filtro risultati multi-norma

- Pipeline runner (`src/ui/qt/pipeline_runner.py`):
  - `cmb_filter_norm` con opzione `Tutte`
  - update automatico delle norme presenti nei risultati (`_refresh_filter_norms`)
  - filtro righe tabella (`_on_filter_norm_changed`)
  - rendering norma per elemento da `elem.metrics['norm_code']` (fallback a norma corrente)
- Test dedicato:
  - `test_filter_by_norm_hides_non_matching_rows`

### GUI-5.5 — Completamento template NTC2018 non-priority

- Completati e registrati in `get_ntc2018_templates()`:
  - `ntc2018_slu_instabilita_pilastri`
  - `ntc2018_slu_punzonamento`
- Ogni template include:
  - riferimenti normativi primari/secondari
  - input/output metriche tracciate
  - metadati `implementation_status=stub`, `priority=non_priority`
- Nota architetturale:
  - aggiunta anche funzione `get_rd2229_templates()` valida e compilabile nel registry
    per garantire stabilita runtime di `get_all_templates()`.

### Verifica esecuzione

- Test eseguiti con esito verde:
  - `tests/test_pipeline_runner_qt.py`: 7 passed
  - `tests/test_project_editor_qt.py` + `tests/test_notification_toast.py`: 12 passed
- Controllo statico:
  - `get_errors` senza errori sui file modificati.

### Stato finale

- TODO GUI totali: 81
- Completati: 81
- Da fare: 0
- Script di sync eseguito con successo:
  - `python scripts/sync_todo_gui.py --update-gui --update-main`

## Note tecniche e commenti di implementazione

Commento 1: il compromesso richiesto sui moduli evita frammentazione UX, mantenendo pero isolamento funzionale dei tool specialistici.

Commento 2: il registry deve restare la sola porta di ingresso per nuove funzionalita GUI. Ogni nuovo modulo deve registrare metadati minimi (chiave, nome, categoria, factory, prerequisiti).

Commento 3: la dashboard non e solo navigazione, ma anche cruscotto di stato. Questo riduce passaggi operativi e accelera il ciclo progetto -> run -> report.

Commento 4: il file generale non deve diventare troppo tecnico. Le motivazioni architetturali e i dettagli di composizione widget restano qui.

## Procedura operativa di aggiornamento

1. Eseguire implementazione GUI o test.
2. Aggiornare questo file con decisioni/impatti.
3. Eseguire script sync TODO.
4. Aggiornare `docs/PIANO_LAVORO.md` (automatica o assistita) e aggiungere riga in cronologia se necessario.
5. Eseguire test mirati GUI e annotare esito.

## Plan: Completare tutti i TODO GUI (GUI-V1 residuali)

## Aggiornamento requisiti GUI (richiesta utente)

L'utente richiede:
- È consentito usare **riquadri a scomparsa** solo quando strettamente necessario.
- I **TODO** devono aggiornarsi automaticamente tramite script (scan TODO/grep + aggiornamento file di riepilogo).
- La prima attività del piano (e dell'implementazione) è aggiornare `docs/PIANO_LAVORO.md` con tutti i TODO GUI e le operazioni completate, poi creare un nuovo file `docs/PIANO_LAVORO_GUI.md` che:
  - contiene la fonte di verità tecnica GUI (dettagli, dipendenze, file, fasi/subfasi)
  - include commenti e note esplicative estese
  - rimane separato da `PIANO_LAVORO.md` (che resta registro generale e di alto livello).

- **Ridurre il numero di tab** a macro-settori disciplinari e avere una **unica dashboard con card** (es. card/moduli, dropdown) per accedere a tutte le funzionalità.
- È accettabile aprire nuove finestre per i moduli, ma **gli input richiesti dal modulo devono essere forniti nella stessa finestra** (cioè non richiedere di passare a un'altra finestra per completare un modulo).
- È consentito usare **riquadri a scomparsa** solo dove espressamente necessario.
- I **TODO devono aggiornarsi automaticamente** tramite script (invece che manualmente).
- La prima cosa da fare è aggiornare **`docs/PIANO_LAVORO.md`** con tutti i TODO GUI e le operazioni completate, e poi creare un nuovo file **`docs/PIANO_LAVORO_GUI.md`** che sia la fonte di verità tecnica per l'implementazione GUI (dettagli, dipendenze, file, fasi/subfasi, commenti esplicativi).

Questo piano deve includere questi vincoli e organizzare il lavoro con questi obiettivi in mente.

**TL;DR**: completare tutti i TODO attualmente segnati in `docs/PIANO_LAVORO.md` per la GUI moderna (GUI-V1). Questo include: migliorare l'editor progetto (CRUD, extra, test), completare la persistenza (splash recenti + autosave + test), rendere il runner pipeline più robusto (progress/annulla/log colorato + test headless), finalizzare il supporto multi-norma (stati limite dinamici + raggruppamento risultati + template NTC2018), abilitare toast animati + integrare Telaio nel tab FEM/Telai, stilizzare dialoghi normativi, e allineare requirements GUI.

---

## 1) GUI‑2: Project Editor (completare tugas)

### Obiettivo

Portare il `ProjectEditorWindow` da "griglia base editabile" a una UI con CRUD dedicato e controlli coerenti, garantire la persistenza dei campi `extra` e completare la copertura test.

### Cosa manca (TODO)

- GUI‑2.2: Tabella Geometria con azioni CRUD dedicate (non solo add/remove generici).
- GUI‑2.3: Tabella Materiali con CRUD + integrazione repository completa (ora c'è solo un import parziale).
- GUI‑2.4: Tabella Carichi con colonna `extra` esplicita (già presente ma serve migliorare UX/validazione).
- GUI‑2.9: Copertura test GUI‑2 dedicata (10+ test) non consolidata.

### Deliverables

- Dialog dedicati per inserire/modificare: Geometria, Materiali, Carichi (input validati, pulizia, tooltip/placeholder). Le tabelle rimangono come viewer/edit rapido ma l’editing deve essere affidato al dialog.
- Funzionalità "Modifica" (doppio click / pulsante) per ogni riga, che apre il dialog pre‑filled.
- Validazione sintattica JSON `extra` in linea, con feedback all’utente (errore mostrato, non accetta JSON invalido).
- Test Qt headless che coprono:
  - creazione/modifica/rimozione elemento geometrico + roundtrip `ProjectModel`
  - import materiali da repository con selezione controllata
  - salvataggio e ricaricamento `ProjectModel` con extra
  - controllo che i dialog non crashino se chiusi senza conferma

### File chiave

- `src/ui/qt/project_editor.py` (migliorare UI + logica CRUD)
- `src/ui/qt/json_edit_dialog.py` (verificare se esiste; altrimenti creare miglioria)
- `tests/test_project_editor_qt.py` (estendere test esistenti)

---

## 2) GUI‑3: Persistence layer (splash, autosave, test)

### Obiettivo

Completa l’esperienza utente persistente e rende il comportamento testabile.

### Cosa manca (TODO)

- GUI‑3.3: File recenti anche in splash screen (ora solo menu File → Recenti).
- GUI‑3.4: Auto‑save opzionale ogni N minuti (configurabile in `UserConfig`).
- GUI‑3.5: Test persistence dedicati (round‑trip per `UserConfig` e `ProjectIndex`).

### Deliverables

- Aggiungere splash / landing iniziale (o tab Dashboard) che mostra i progetti recenti caricati da `UserConfig.recent_projects` + `ProjectIndex.list_recent()`.
- Integrare un timer (QTimer) che, quando abilitato da config, salva automaticamente `project_service.current_project` nel file corrente (se già salvato) ogni N minuti. Se il progetto non ha path, non salvare ma loggare.
- Esporre l’opzione `autosave_enabled` e `autosave_minutes` in `UserConfig` (e UI: preferibile in tab impostazioni o nella dashboard).
- Aggiungere test unitari/di integrazione per `UserConfig.load/save/add_recent`, `ProjectIndex.upsert/list_recent` e l’auto‑save (usando monkeypatch/qtbot con QTimer forzato).

### File chiave

- `src/core/user_config.py` (aggiungere campi + test)
- `src/core/persistence.py` (eventualmente più metodi utili per test)
- `src/ui/modern/main_window.py` (splash/recenti + autosave)
- `tests/test_user_config.py`, `tests/test_persistence.py` (nuovi)

---

## 3) GUI‑4: Pipeline runner (progress/log/annulla/test)

### Obiettivo

Portare il Runner a un livello più completo e testabile.

### Cosa manca (TODO)

- GUI‑4.3: Modalità indeterminata/determinata durante run.
- GUI‑4.5: Log colorato per livelli (attuale: text/plain).
- GUI‑4.9: Test headless con mock worker dedicati.

### Deliverables

- `PipelineRunnerWindow` deve impostare la barra progresso su indeterminata (`setRange(0,0)`) quando si avvia la pipeline e tornare a determinata a fine. Se `run_pipeline` può fornire step, usare questi per aggiornamenti determinati (opzionale).
- Aggiungere funzione helper per appendere messaggi colorati: `INFO`, `WARN`, `ERROR` con tag HTML `<span style="color: ...">` o usando `QTextCharFormat`.
- Implementare test `PipelineRunnerWindow` headless usando una `PipelineWorker` mock che emette segnali `progress`, `log`, `completed`, `failed`; verificare che il bottone "Esegui" venga riabilitato correttamente e che la tabella mostra risultati.

### File chiave

- `src/ui/qt/pipeline_runner.py` (migliorare progress/log e possibilità di estendere il worker)
- `tests/test_pipeline_runner_qt.py` (nuovo, suite headless)

---

## 4) GUI‑5: Multi‑norma workflow

### Obiettivo

Rendere il comportamento multi‑norma coerente, aggiornare gli stati limite in base alla norma selezionata e fornire raggruppamento dei risultati per norma quando si esegue un run multi‑norma.

### Cosa manca (TODO)

- GUI‑5.3: Aggiornamento dinamico stati limite per norma.
- GUI‑5.4: Raggruppamento risultati per norma in modalità multi‑norma.
- GUI‑5.5: Completamento template NTC2018 non‑priority (non completamente implementato nel registry).

### Deliverables

- In `PipelineRunnerWindow`, allineare `cmb_norm` con `project.code_settings.norm_code` e aggiornare i `limit_states` suggeriti (o precompilati) quando si seleziona una norma.
- Implementare una funzione (ad es. `list_norm_states(norm_code)`) che ritorna gli stati limite consigliati per una norma (basato su `normative_registry` o un mapping); usare questo per popolare `ProjectEditorWindow` / `CodeSettingsWindow` e la combo del runner.
- Estendere `ResultsModel` o il renderer del runner per raggruppare le righe della tabella per norma quando si esegue un run che produce risultati per più norme (se supportato dal pipeline). In alternativa, fornire un modo per serializzare o raggruppare nelle righe (es. colonna Norma già popolata) e aggiungere un filtro.
- Verificare e completare l’implementazione del template NTC2018 nel `normative_registry` (richiede review del codice e dei dati JSON). Documentare quale parte manca e creare test di copertura.

### File chiave

- `src/ui/qt/pipeline_runner.py` (sincronizzazione norma + raggruppamento risultati)
- `src/ui/qt/code_settings.py` (eventuale aggiornamento GUI per stati-limite dinamici)
- `src/core_calculus/normative_registry.py` (mappa norm codes / template)
- `tests/test_pipeline_runner_norms.py` (nuovo)

---

## 5) GUI‑7: Toast animati + integrazione Telaio

### Obiettivo

Abilitare notifiche in overlay (toast) e integrare la finestra Telaio dentro il tab FEM/Telai per un workflow coerente.

### Cosa manca (TODO)

- GUI‑7.5: Toast overlay animato (attuale: centro notifiche list/filter/clear).
- GUI‑7.9: Integrare `TelaioWindow` insieme a `CordoliWidget` nel tab FEM/Telai.

### Deliverables

- Creare un widget `ToastOverlay` (semi‑trasparente) che può essere mostrato sopra la UI con animazione fade‑in/out; collegarlo al `NotificationCenterWindow` o al service di notifica usato dalle altre parti.
- Aggiungere un metodo globale (o servizio Qt) per mostrare toast (es. `notify_toast(level, message, duration)`) e usarlo in punti chiave (pipeline completion, errori, salvataggi).
- Modificare il tab FEM/Telai nella `main_window` per includere un `QSplitter` fra `CordoliWidget` e un’area che ospita `TelaioWindow` (incorporata come widget o come bottone per aprire in finestra separata). L’obiettivo è avere accesso a entrambe le funzionalità da un’unica schermata.
- Aggiungere test base (può essere semplicemente testare che il widget overlay si istanzia e si nasconde dopo la durata).

### File chiave

- `src/ui/qt/notification_center.py` (estendere con toast)
- `src/ui/qt/telaio/telaio_window.py` e `src/ui/modern/main_window.py` (integrazione).
- `tests/test_notification_toast.py` (nuovo)

---

## 6) GUI‑8: Stylesheet – dialoghi normativi

### Obiettivo

Fornire uno stile coerente e dedicato ai dialoghi normativi (aiuto contestuale, citazioni, note), lasciando il resto degli stili invariato.

### Cosa manca (TODO)

- GUI‑8.5: Stile dedicato dialoghi normativi non ancora separato.

### Deliverables

- Estendere `stylesheet.py` con regole QSS specifiche per dialoghi normativi (es. `QDialog#NormativeDialog`, `QTextEdit#NormativeText`, oppure classi CSS personalizzate). Assicurarsi che `AiutoContestuale` e eventuali popup utilizzino questi id/classes.
- Aggiornare i componenti normativi (es. `src/ui/qt/aiuto_contestuale.py`) per impostare l’objectName o className in modo che lo stylesheet li stilizzi.
- Aggiungere test base che verifica che i widget creino l’objectName corretto (senza dipendere da rendering reale).

### File chiave

- `src/ui/qt/stylesheet.py` (nuove regole)
- `src/ui/qt/aiuto_contestuale.py` (eventuale objectName)
- `tests/test_stylesheet_normative_dialog.py` (nuovo)

---

## 7) GUI‑9: Requirements + packaging

### Obiettivo

Assicurare che i pacchetti opzionali necessari per la GUI siano dichiarati in `requirements*.txt` / `pyproject.toml` e documentati.

### Cosa manca (TODO)

- GUI‑9.4: Allineamento completo optional GUI anche in `requirements*.txt` (non solo extras in pyproject).

### Deliverables

- Audit dei file `requirements.in`, `requirements.txt`, `requirements-dev.txt`, `pyproject.toml` per garantire che le dipendenze (PySide6/PyQt6, PyQt6‑WebEngine, pytest‑qt, etc.) siano elencate correttamente.
- Aggiornare README con istruzioni chiare per l’installazione GUI (es. `pip install -r requirements-gui.txt` o `pip install -e .[gui]`).

### File chiave

- `requirements*.txt`, `pyproject.toml`, `README.md`

---

## Verifica & Chiavi di successo

1. Tutti i TODO elencati in `docs/PIANO_LAVORO.md` relativi a GUI risultano marcati ✅. In particolare, le liste alle sezioni GUI‑2..GUI‑9 devono diventare verdi.
2. `pytest -q` continua a passare con tutti i test (3243/3243). I nuovi test devono essere aggiunti e passare in headless CI (senza PyQt6‑WebEngine).
3. Documentazione interna (README/PIANO_LAVORO/DOC) aggiornata con gli step per usare i nuovi elementi (toast, autosave, splash recenti).

---

## Passaggi successivi (prima iterazione)

1. Confermare priorità: 1) Project Editor, 2) Pipeline Runner, 3) Persistence, 4) Multi‑norma, 5) Toast+Telaio, 6) Stylesheet, 7) Requirements.
2. Scegliere se procedere in un unico blocco o in micro‑PR per ciascuna fase.
3. Iniziare sviluppo: piccola implementazione e relative unit test per GUI‑2 (Project Editor) e GUI‑4 (Pipeline Runner).

---

**Nota**: questo piano è basato sullo stato attuale del repository (GUI‑V1 con 3243 test verdi) e sui TODO elencati in `docs/PIANO_LAVORO.md`.
