Piano Architetturale RD2229 v0.1.0
Canvas 1: Obiettivi e Scope
Obiettivo:
Rendere RD2229 una piattaforma modulare, estendibile e utilizzabile sia da CLI che da GUI, in grado di gestire progetti strutturali completi (elementi, materiali, codici, pipeline, report) secondo le convenzioni e l’architettura esistente.

Deliverable v0.1.0:

Input strutturato per elementi, materiali, sezioni, verifiche, codici
Esecuzione pipeline + report MD/HTML
Tre plugin di esempio (info progetto, esecuzione, export)
Registry/GUI che mostri e lanci le funzionalità
Entry point CLI e GUI funzionanti
Canvas 2: Architettura e Flusso Dati
Componenti principali:

ProjectModel (src/project/)
Engine di verifica (src/core_calculus/core/, calculations/)
Registry plugin (src/ui/modern/registry.py)
Pipeline orchestrator (src/core/pipeline.py)
Loader/configurazione (config/, data/)
Report builder (src/reporting/)
Interfacce: CLI (rd2229), GUI (rd2229-gui)
Flusso dati:

Caricamento progetto: YAML/JSON → validazione schema → ProjectModel
Definizione elementi: inserimento/edizione elementi, materiali, sezioni, armature
Selezione codici: scelta codici verifica, parametri contestuali
Esecuzione pipeline: run_pipeline(ProjectModel) → risultati
Report: build_report(ProjectModel, ResultsModel) → MD/HTML
Estensioni/plugin: registry carica e mostra plugin disponibili (info, esecuzione, export)
Canvas 3: Contratti e API Principali
Contratti chiave:

ProjectModel: rappresenta il progetto strutturale, serializzabile
VerificationInput: input per engine di verifica (elemento, azioni, codici)
run_pipeline(ProjectModel) -> ResultsModel: esegue tutte le verifiche richieste
build_report(ProjectModel, ResultsModel) -> ReportArtifact: genera report
Plugin: interfaccia base per plugin (nome, descrizione, esegui)
PluginRegistry: discovery e gestione plugin
API CLI:

rd2229 new <file>: crea nuovo progetto
rd2229 load <file>: carica progetto esistente
rd2229 run <file>: esegue pipeline e stampa report
rd2229 export <file> [--format md|html]: esporta report
API GUI:

Sidebar/toolbar generata da registry
Form per inserimento/edizione elementi, materiali, codici
Pulsanti per esecuzione pipeline, export, info progetto
Canvas 4: Estensioni e Punti di Integrazione
Punti di estensione:

Plugin (src/ui/modern/registry.py, src/plugins/)
Configurazione codici/materiali (config/calculation_codes/, config/historical_materials/)
Report builder (src/reporting/export.py)
Pipeline steps (calculations/<element>/<topic>.py)
Plugin di esempio:

Info progetto (visualizza metadati)
Esecuzione pipeline (run)
Export report (MD/HTML)
Pattern plugin:
Ogni plugin implementa un’interfaccia standard, è registrato nel registry e può essere lanciato da CLI/GUI.

Canvas 5: File/Namspace da Modificare o Aggiungere
Da modificare:

src/project/project_model.py: assicurare serializzazione/validazione
src/core/pipeline.py: orchestrazione pipeline
src/ui/modern/registry.py: discovery/registrazione plugin
src/reporting/report_builder.py: generazione report
config/calculation_codes_loader.py: caricamento codici
Da aggiungere:

src/plugins/info_plugin.py
src/plugins/run_plugin.py
src/plugins/export_plugin.py
src/ui/modern/sidebar.py: generazione dinamica da registry
src/cli/entrypoint.py: CLI entry point
src/gui/entrypoint.py: GUI entry point
Canvas 6: Roadmap Attività v0.1.0
Analisi e refactor ProjectModel
Validazione schema, serializzazione, metodi CRUD
Definizione contratti plugin e registry
Interfaccia base, discovery, registrazione
Implementazione plugin esempio
Info, run, export
Refactor pipeline e reporting
Orchestrazione, output MD/HTML
Configurazione CLI/GUI entry point
Comandi base, integrazione registry
GUI: sidebar/toolbar dinamica
Generazione da registry, binding azioni
Test end-to-end
Caricamento progetto, esecuzione pipeline, export report
Documentazione e convenzioni
Aggiornamento README, specifiche API, esempi d’uso
Canvas 7: Criteri di Accettazione
Tutte le operazioni principali disponibili sia da CLI che da GUI
Plugin di esempio funzionanti e visibili in registry
Pipeline e report funzionanti su dati di esempio
Nessun coupling diretto tra GUI, engine e storage: tutto passa tramite contratti/services
Logging e gestione errori presenti nei punti critici
Documentazione aggiornata e chiara
Canvas 8: Note e Convenzioni
Usare solo moduli e pattern già presenti dove possibile
Seguire schema versioning e pattern plugin esistenti
Validare sempre input/output (schema, tipi, parametri)
Isolare codice legacy, non introdurre accoppiamenti
Ogni nuovo modulo/plugin deve essere testato e documentato
Fine del file piano.



TL;DR
RD2229 diventerà una piattaforma modulare estendibile con interfacce CLI e GUI basate su contratti solidi. Il nucleo è un ProjectModel pydantic validato via JSON‑Schema; la pipeline è configurabile e i risultati riportati in MD/HTML. I plugin, caricati automaticamente da plugins, espongono azioni eseguibili da entrambe le interfacce. Logging completo in logs; test unit, CLI e GUI garantiscono regressioni.

Componenti principali
src/project/project_model.py: pydantic model + generazione schema (schema.json)
pipeline.py: orchestrator configurabile, produce ResultsModel
registry.py: discovery/import automatico dei plugin
report_builder.py: export MD/HTML con TOC/tabelle
CLI (src/cli/entrypoint.py con Typer) e GUI (src/gui/entrypoint.py con PySide6)
logs directory per file di log rotanti
plugins: repository dei plugin, base class con lifecycle
Flusso dati
Caricamento progetto YAML/JSON → validazione via JSON‑Schema → ProjectModel
Pipeline: sequenza passi definita nel progetto → esegue calcoli per elemento → ResultsModel
Report: MD/HTML generati da report_builder
Plugin: configurati nel progetto, eseguiti da CLI/GUI, con lifecycle init/execute/teardown
Tutte le azioni (UI, CLI, I/O) registrate in log dettagliati
API e contratti
ProjectModel serializzabile, validabile, CRUD interno
VerificationInput come oggi, utilizzato dai calcoli
run_pipeline(ProjectModel) → ResultsModel
build_report(ProjectModel, ResultsModel) → ReportArtifact
Plugin interface: nome, descrizione, init, execute, teardown
PluginRegistry: importa ogni modulo in plugins all’avvio e registra le classi
Estensioni
Plugins automatici (import directory); configurabili via ProjectModel
Pipeline order configurabile nel file progetto
Logs su file diario, formato rotante
GUI error dialog oltre al log
Roadmap v0.1.0
Refactor ProjectModel e generazione schema
Implementazione registry / plugin base + esempi (info, run, export)
Costruzione pipeline configurabile e ResultsModel
Report builder MD/HTML semplice
CLI Typer con comandi new, load, run, export
GUI PySide6: sidebar dinamica, form elementi, pulsanti esecuzione
Logging esteso e file in logs
Tests: unit (modelli/registry/plugins), integrazione CLI, GUI con pytest-qt
Aggiornamento README + documentazione d’uso
Validazione cross-platform Linux/macOS/Windows
Verifica
Eseguire pipeline con progetto demo → generare report
Verificare visibilità dei plugin appena creati importando nuovi moduli
Controllare file schema e validazione JSON/YAML
Lanciare GUI e osservare log/dialog di errore
Eseguire suite test (pytest -q) inclusivi di GUI
Decisioni chiave
pydantic + JSON‑Schema per modelli
Typer per CLI, PySide6 per GUI
Plugins import directory (automatico)
Pipeline order configurabile
Logging file con livello DEBUG
Progetti in JSON/YAML

PROMPT PER AGENTE DI PROGETTAZIONE E INTEGRAZIONE RD2229 v0.1.0
Obiettivo generale
Progetta, integra e verifica una piattaforma software modulare, estendibile e robusta per la gestione di progetti strutturali secondo normative storiche e moderne (TA, SLU, DM96, ecc.), con interfacce CLI e GUI, supporto plugin, pipeline configurabile, logging avanzato e reporting automatico. Il risultato deve essere garantito, testabile e documentato.

1. Architettura e componenti principali
ProjectModel:

Definito tramite pydantic.BaseModel in src/project/project_model.py
Serializzazione/validazione automatica via JSON-Schema (schema.json)
Supporto sia per file JSON che YAML (auto-detect tramite estensione)
CRUD completo e validazione schema in CLI/GUI
Motore di verifica e calcolo:

verification_engine.py (funzione create_verification_engine)
Moduli di calcolo per elemento in calculations e logica storica in verifications
Registry normative in normative_registry.py
Input tramite VerificationInput, output dettagliato (OK/NON OK + steps intermedi)
Pipeline:

Orchestrazione in pipeline.py
Pipeline configurabile: ordine passi definito nel file progetto
Adattatori step in step5_adapter.py
Output: ResultsModel con risultati per elemento e riepilogo
Materiali e elementi:

Repository materiali in materials, loader storici in historical_materials_loader.py
Modelli elementi in elements
Azioni specialistiche:

Verifiche incendio in fire
Azioni vento in wind
Reportistica:

Costruzione report in report_builder.py
Esportazione MD/HTML in export.py
Report con TOC, tabelle, dettagli intermedi (steps) su richiesta
Plugin/Estensioni:

Tutti i moduli in plugins sono caricati automaticamente all’avvio tramite import dinamico
Ogni plugin implementa una base class con ciclo di vita completo (init, execute, teardown)
Configurazione plugin tramite sezione dedicata nel ProjectModel
Supporto a plugin di esempio: info progetto, esecuzione pipeline, export report
Registry e collegamento dinamico:

Registry centrale delle feature in registry.py
Auto-discovery tramite decoratore standard (es. @gui_feature) o funzione di registrazione
Menu/toolbar dinamici popolati interrogando il registry
Supporto a plugin/estensioni senza modificare la GUI principale
Interfacce:

CLI in src/cli/entrypoint.py (framework Typer), comandi: new, load, run, export
GUI in src/gui/entrypoint.py (PySide6, MVVM), sidebar aggiornata dinamicamente, dialog di configurazione per ogni feature, visualizzazione steps su richiesta, supporto batch per pipeline/progetti
Logging e gestione errori:

Logging dettagliato (livello DEBUG) di tutte le azioni utente (UI, CLI, I/O, modifiche file)
Log persistenti in logs con rotazione giornaliera
Errori mostrati sia in log che tramite dialog GUI
Aggiornamento registry delle feature in tempo reale (watch su filesystem)
2. Flusso dati e operazioni
Definizione progetto:
L’utente crea/carica un progetto strutturale, inserisce elementi, materiali, carichi, seleziona la normativa
Validazione:
Il progetto viene validato tramite JSON-Schema generato da pydantic
Esecuzione pipeline:
run_pipeline(ProjectModel) richiama il motore di verifica e i moduli di calcolo secondo la normativa selezionata
Ogni verifica produce risultati dettagliati e steps intermedi
Generazione report:
build_report(ProjectModel, ResultsModel) esporta MD/HTML con TOC, tabelle, dettagli intermedi su richiesta
Visualizzazione/esportazione:
La GUI mostra sidebar aggiornata, dialog di configurazione per feature/plugin, risultati in tabella, albero, dashboard e report testuale
Supporto batch per esecuzione multipla di pipeline/progetti
Logging:
Tutte le azioni e operazioni sono registrate in log dettagliati
Plugin/estensioni:
Nuove funzionalità sono rese disponibili automaticamente tramite registry e auto-discovery
3. Dettagli implementativi e scelte progettuali
Registrazione feature GUI:
Usa decoratore @gui_feature o funzione register_feature() per auto-registrazione
Registry centrale interrogato dalla GUI per popolare sidebar e toolbar
Visualizzazione dinamica:
Sidebar aggiornata in tempo reale con nuove feature scoperte
Dialog di configurazione per ogni feature/plugin
Steps intermedi di calcolo visibili su richiesta dell’utente
Categorie attivabili/disattivabili:
Calcolo/verifica, pipeline, materiali, elementi strutturali, azioni specialistiche, reportistica
Gestione registry:
Aggiornamento in tempo reale tramite watch su filesystem
Risultati verifiche:
Visualizzazione multipla: tabella per elemento, vista ad albero, dashboard grafica, report testuale (tutte le modalità disponibili)
Esecuzione batch:
Supporto a selezione multipla di pipeline/progetti dalla GUI
Configurazione plugin/feature:
Dialog dedicato per ogni feature, con possibilità di wizard guidato
Test e verifica:
Test unitari per modelli, registry, plugin
Test di integrazione CLI e GUI (pytest-qt)
Test funzionali GUI per tutte le categorie attivabili
Documentazione:
Aggiornamento README con istruzioni CLI/GUI/plugin
Esempi d’uso e specifiche API
Criteri di accettazione:
Tutte le operazioni principali disponibili sia da CLI che da GUI
Plugin di esempio funzionanti e visibili in registry
Pipeline e report funzionanti su dati di esempio
Nessun coupling diretto tra GUI, engine e storage: tutto passa tramite contratti/services
Logging e gestione errori presenti nei punti critici
Documentazione aggiornata e chiara
4. Roadmap operativa
Refactor ProjectModel e generazione schema
Implementazione registry / plugin base + esempi (info, run, export)
Costruzione pipeline configurabile e ResultsModel
Report builder MD/HTML semplice
CLI Typer con comandi new, load, run, export
GUI PySide6: sidebar dinamica, form elementi, pulsanti esecuzione, dialog configurazione feature
Logging esteso e file in logs
Tests: unit (modelli/registry/plugins), integrazione CLI, GUI con pytest-qt
Aggiornamento README + documentazione d’uso
Validazione cross-platform Linux/macOS/Windows
5. Garanzie e qualità
Ogni nuova feature/modulo/plugin deve essere auto-registrato e visibile nella GUI senza modifiche manuali
Tutte le azioni utente e di sistema sono tracciate in log persistenti
Validazione schema e gestione errori robuste
Test automatici e manuali per tutte le funzionalità principali
Documentazione aggiornata e chiara per ogni componente
ESEGUI QUESTO PIANO senza omissioni, garantendo modularità, estendibilità, logging, testabilità e usabilità sia da CLI che da GUI. Ogni decisione architetturale e di dettaglio deve essere rispettata e documentata.