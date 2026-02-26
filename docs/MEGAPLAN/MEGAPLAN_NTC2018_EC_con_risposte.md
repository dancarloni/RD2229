ser: cambio contesto
User: Sei un assistente di sviluppo per un ingegnere strutturista che lavora con Python e Tkinter su verifiche secondo la normativa NTC2018.

🎯 OBIETTIVO
Nel repository corrente sono già presenti molti file, inclusi file relativi a NTC2018 e parti di interfaccia Tkinter. Voglio che tu:
- analizzi in modo leggero la struttura del repository
- proponga una architettura modulare chiara
- organizzi e/o produca:
  - codice Python per la logica NTC2018
  - GUI in Tkinter
  - file di configurazione
  - file di archivio / salvataggio dati
- mantenendo tutto ben separato e riutilizzabile.

Non devi riscrivere tutto da zero: è importante **riusare il più possibile il codice esistente** quando ha senso.

---

📂 PASSO 1 – Analisi leggera del repository (Python + Tkinter)
Esegui una ricognizione **non esaustiva** del repository, limitandoti a:

- individuare:
  - moduli Python che riguardano le verifiche NTC2018
  - file Python che contengono GUI Tkinter (es. uso di `tkinter`, `ttk`, finestre, widget)
  - file di configurazione (es. `.ini`, `.json`, `.yaml`, `.cfg`, ecc.)
  - file o moduli che gestiscono salvataggio/caricamento dati (es. CSV, pickle, SQLite, ecc.)

- dedurre:
  - come è organizzata oggi la logica di calcolo NTC2018 (funzioni sparse? classi? script monolitici?)
  - come è strutturata la GUI Tkinter (finestre principali, dialog, moduli separati?)
  - se esiste già una qualche separazione tra:
    - logica di calcolo
    - interfaccia utente
    - configurazione
    - archivio dati

⚠️ Importante per ridurre il carico e l’uso di risorse:
- Non analizzare tutti i file in dettaglio.
- Basati principalmente su:
  - nomi delle cartelle
  - nomi dei file
  - alcuni file chiave che ritieni più rilevanti
- Se ritieni necessario aprire molti file, **fermati e chiedimi prima quali file puoi analizzare**.

📤 Output atteso del PASSO 1:
- Breve riassunto del progetto (solo le parti rilevanti per NTC2018 + Tkinter).
- Elenco raggruppato dei file in quattro aree:
  1. logica NTC2018
  2. GUI Tkinter
  3. configurazione
  4. archivio / dati

Non generare ancora codice: solo analisi e classificazione.

---

🏗️ PASSO 2 – Proposta di architettura modulare (Python + Tkinter)
In base a quanto hai trovato, proponi una **architettura modulare** in Python con Tkinter in cui siano nettamente separati:

1. **Core NTC2018 (logica di calcolo)**
   - Moduli/classi/funzioni che implementano:
     - combinazioni di carico
     - verifiche allo SLU, SLE, azioni sismiche
     - parametri normativi principali
   - Nessun codice GUI in questi moduli (no import di Tkinter).

2. **GUI Tkinter**
   - Moduli dedicati alle finestre (root, toplevel, dialog, ecc.)
   - Gestione dei widget, layout, binding dei comandi
   - Le funzioni di callback devono delegare la logica alla parte di calcolo, senza contenere formule o logica NTC complessa.

3. **Configurazione**
   - Uno o più file per parametri di configurazione:
     - parametri generali
     - impostazioni predefinite per le verifiche NTC2018
     - percorsi di cartelle, ecc.
   - Un modulo Python che gestisce lettura/scrittura di questi file (es. `config.py`).

4. **Archivio / Dati**
   - Un modulo (o package) che si occupa di:
     - salvataggio di progetti, casi di carico, risultati
     - caricamento da file (es. JSON, CSV, SQLite, altro formato già usato)
   - Nessun riferimento diretto a Tkinter in questi moduli.

Proponi:
- una struttura di cartelle (esempio: `core_ntc/`, `gui/`, `config/`, `storage/`)
- i nomi dei moduli Python (ad es. `core_ntc/combinazioni.py`, `gui/main_window.py`, `config/settings.py`, `storage/project_repo.py`)
- le responsabilità principali di ogni modulo.

📤 Output atteso del PASSO 2:
- alberatura delle cartelle proposta
- elenco dei moduli con una breve descrizione (1–2 righe) per ognuno
- suggerimenti su quali file esistenti spostare o rifattorizzare nei nuovi moduli.

Non scrivere ancora il codice completo, solo la progettazione.

---

⚙️ PASSO 3 – Implementazione incrementale dei moduli
Dopo aver mostrato l’architettura proposta, chiedimi esplicitamente con quale blocco iniziare, tipicamente tra:

- `core_ntc` (logica principale NTC2018)
- `config` (gestione configurazioni)
- `storage` (archiviazione progetti/dati)
- `gui` (finestra principale Tkinter e moduli collegati)

Quando inizi l’implementazione:

1. Lavora **su un solo modulo o piccolo gruppo di moduli per volta**.
2. Genera solo il codice essenziale per:
   - definire le classi/funzioni pubbliche
   - impostare le firme delle funzioni e le interfacce
   - aggiungere docstring chiare su cosa fa ogni elemento

3. Mantieni il codice:
   - indipendente dalla GUI per tutto ciò che riguarda calcoli NTC2018
   - senza logica NTC dentro i callback Tkinter (i callback devono solo chiamare il core)

4. Se la quantità di codice da scrivere per un modulo è grande:
   - suddividi la risposta in più blocchi
   - fermati a fine blocco e chiedimi se puoi proseguire.

---

🔒 VINCOLI GENERALI (per un uso più “leggero” e controllato)
- Non generare l’intero progetto in un’unica risposta.
- Non introdurre nuove librerie pesanti se non strettamente necessario, e solo dopo avermelo proposto (ad es. per logging, config avanzata, ecc.).
- Limita la lettura del repository ai file realmente necessari e, se possibile, chiedimi prima quali cartelle/file esplorare in dettaglio.
- Se rilevi che il contesto sta diventando troppo ampio, fermati e proponi di:
  - riassumere
  - ripulire le informazioni
  - oppure spezzare il lavoro in ulteriori passi.

---

Ora esegui il PASSO 1:
analizza in modo leggero il repository e restituisci:
- il riassunto del progetto
- la classificazione dei file nelle quattro aree: NTC2018, GUI Tkinter, configurazione, archivio/dati.

GitHub Copilot: Espressione regolare `NTC2018|NTC|sism|sisma|seismic|verif|verifiche|SLU|SLE|FRC|verification_engine|core_calculus` (`**/*.{py,md,txt,json}`) ricercata, 200 risultati

Ricerca di file corrispondenti `**/src/**/verification_engine.py`, 2 corrispondenze

Leggere [](file:///c%3A/workspaces/RD2229/RD2229/src/core_calculus/core/verification_engine.py#1-1), righe da 1 a 300

Espressione regolare `NTC2018|params/NTC2018|clauses/NTC2018|calculation_codes_loader|historical_materials_loader|config/` (`**/*.{py,yml,yaml,json,md,txt}`) ricercata, 200 risultati

Ricerca di file corrispondenti `**/src/methods/checks_ntc2018.py`, 1 corrispondenza

Leggere [](file:///c%3A/workspaces/RD2229/RD2229/src/methods/checks_ntc2018.py#1-1), righe da 1 a 400

## PASSO 1 — Ricognizione leggera (NTC2018 + Tkinter) 🔎

Breve sintesi del progetto (solo parti rilevanti)
- Questo repository è un framework di verifiche strutturali con:
  - un **core di calcolo** ben separato (core_calculus, methods) che contiene motore di verifica, formule e controlli (tra cui supporto per **NTC2018**);
  - una **UI Tkinter** (package sections + vecchie copie in app_module) per input, gestione materiali/sezioni e esecuzione rapide delle verifiche;
  - un sistema di **config/jsoncode** per parametri normativi (materiali, coefficienti di sicurezza, NTC2018 ecc.);
  - moduli di **storage / import‑export** (CSV/JSON) e un repository dati per sezioni/materiali.
- Buone pratiche già presenti: core senza dipendenze GUI, loader di configurazione, demo/tests che documentano l’uso (es. demo_verification_engine.py, test_*).

Classificazione (file/percorsi chiave — non esaustiva)

1) Logica NTC2018 (core di calcolo, controlli normativi)
- checks_ntc2018.py — implementazioni (parziali/placeholder) delle verifiche SLU/SLE/TA per NTC2018.  
- verification_engine.py — engine che orchestri calcoli (TA / SLU / SLE) e carica configurazioni.  
- verification_core.py — primitive/strutture dati per verifiche (NeutralAxis, StressState, ecc.).  
- section_calculations.py — calcoli sezionali (aree, centroidi, inerzie, core, ellissi).  
- material_sources.py & `config/historical_materials/*` — mapping proprietà materiali (NTC2018 incluso).  
- Script di esempio: demo_verification_engine.py.

2) GUI Tkinter (finestre, dialog, controller)
- main_window.py, module_selector.py — finestra principale / launcher.  
- frc_verification_window.py, frc_manager.py, historical_main_window.py — dialog per verifiche/materiali.  
- section_graphics.py — renderer / trasformazioni per canvas (usato dai test/demo).  
- Legacy / compat: `libs/app_module/ui/*` (versioni storiche della GUI, usate per compatibilità/tests).

3) Configurazione (parametri normativi e loader)
- calculation_codes_loader.py — loader per TA/SLU/SLE (`.jsoncode`).  
- historical_materials_loader.py — loader per fonti materiali (RD2229, NTC2008, **NTC2018**).  
- `config/calculation_codes/*.jsoncode`, `config/historical_materials/*.jsoncode` — dati normativi/materiali.  
- Documentazione/demo: README.md, demo_config_system.py.

4) Archivio / salvataggio dati
- storage.py — import/export CSV (SectionGeometry ↔ CSV).  
- sec_repository, sections.json, materials.json, historical_materials.json — repository dati / file persistenti.  
- Test e helper: test_storage.py, utility in `softw_components/*` (alcuni duplicati già rimossi/shimmati).

Osservazioni sull’organizzazione attuale (ricognizione leggera)
- Separazione logica vs GUI: buona — il core non importa Tkinter; la GUI chiama il core/engine.  
- Configurazione: esiste un sistema JSON/YAML‑like (`.jsoncode`) e loader dedicati — integrabile con NTC2018.  
- Archiviazione: moduli per CSV/JSON già presenti e testati.  
- Duplicità/compatibilità: esistono copie legacy (libs, softw_components) ma sono in fase di consolidamento (shims/deletion già applicati per alcuni file).  
- NTC2018: presente sia come dati (config/`material_sources`) sia come funzioni di verifica (checks_ntc2018.py) — molte routine sono parziali ma ben collocate.

---

Vuoi che proceda ora con il PASSO 2 (proposta architettura modulare) oppure preferisci che prima apra/mostri specifici file chiave (es. checks_ntc2018.py o verification_engine.py) per approfondire qualche punto?

User: IMPORTANTE: rimani sempre e solo in "modalità Plan". Non generare codice. Non proporre implementazioni. Limita la tua attività esclusivamente alla pianificazione, alla definizione di fasi, dipendenze, attività e roadmap tecnica.
Agisci come:

- architetto software per applicazioni di calcolo strutturale;
- ingegnere strutturista esperto di NTC2018;
- sviluppatore Python con esperienza in architetture modulari e UI Tkinter.

CONTESTO PROGETTO (riassunto):

- Il repository è un framework di verifiche strutturali con:
  - un core di calcolo separato dalla GUI (moduli come core_calculus, methods, verification_engine, verification_core);
  - una UI Tkinter (package sections + vecchie copie in app_module) per input, gestione materiali/sezioni ed esecuzione delle verifiche;
  - un sistema di configurazione basato su file .jsoncode per parametri normativi e materiali (NTC2018 inclusa);
  - storage/import-export CSV/JSON e repository dati per sezioni/materiali (sections.json, materials.json, historical_materials.json);
  - alcune funzioni NTC2018 già presenti (es. checks_ntc2018.py) soprattutto per il calcestruzzo armato, ma ancora parziali.

VINCOLI ATTUALI:

- Tutte le nuove funzionalità devono:
  - riutilizzare i materiali e le sezioni già presenti nel repository;
  - appoggiarsi alle GUI e ai sistemi di calcolo sezionale già implementati;
  - essere progettate in modo modulare, ossia facilmente estendibili a futuri materiali, norme e moduli di verifica.

OBIETTIVO DI QUESTA SESSIONE:

- Definire un PIANO COMPLETO E STRUTTURATO (roadmap tecnica) di tutte le pianificazioni possibili e immaginabili relative all’implementazione di NTC2018 nel software, in modo modulare ed espandibile.
- Il piano deve essere il più dettagliato possibile, ma eseguibile all’interno di UNA SOLA SESSIONE di chat, massimizzando il valore che ottengo dal premium.

LISTA DI MACRO-AREE DA COPRIRE (roadmap):

A. Architettura software modulare:
   - definizione di un’interfaccia generale per moduli normativi (CodeModule, con funzioni tipo check_slu, check_sle, check_seismic, ecc.);
   - riorganizzazione del codice NTC2018 (es. checks_ntc2018.py) in un package dedicato (codes/ntc2018/…);
   - design di un sistema di configurazione estensibile per parametri normativi NTC2018 (γ, ψ, combinazioni, parametri di materiale, ecc.);
   - previsione di hook e interfacce per futuri moduli di norma (NTC2008, Eurocodici, ecc.).

B. Azioni e combinazioni:
   - catalogo delle azioni permanenti, variabili, sismiche e accidentali secondo NTC2018;
   - generazione di combinazioni di carico per SLU e SLE (rare, frequenti, quasi permanenti), configurabili via .jsoncode;
   - API chiare per la produzione di combinazioni da passare al motore di verifica (verification_engine).

C. Materiali e modelli costitutivi:
   - riuso e razionalizzazione del sistema attuale (material_sources, config/historical_materials);
   - estensione strutturata per:
     - calcestruzzo armato (classi, parametri f_ck, f_cd, f_ctm, ecc.);
     - acciaio per c.a. e per carpenteria;
     - muratura, legno, geotecnica, ecc. come livelli successivi (anche solo pianificati);
   - mantenimento del vincolo: per ora si usano solo materiali e sezioni già presenti nel repository, predisponendo però i punti di estensione.

D. Verifiche per elementi in calcestruzzo armato:
   - travi (SLU: flessione, taglio, torsione, interazione N-M; SLE: fessurazione, deformazioni, tensioni limite);
   - pilastri (SLU: dominio N–M, instabilità/secondo ordine; SLE: tensioni e deformazioni);
   - solai/piastra e fondazioni a piastra (flessione e punzonamento, SLE di freccia e fessurazione);
   - fondazioni (plinti, travi rovesce) con richiamo al modulo geotecnico.

E. Verifiche per elementi in acciaio:
   - classificazione delle sezioni;
   - verifiche di resistenza di sezione (trazione, compressione, flessione, taglio, presso-flessione);
   - instabilità (buckling, instabilità latero-torsionale);
   - pianificazione dei moduli per i collegamenti (anche solo come stub iniziali).

F. Strutture in legno:
   - pianificazione di verifiche per flessione, trazione, compressione, instabilità;
   - gestione dei parametri k_mod, k_def, classi di servizio;
   - verifiche dei collegamenti (chiodi, bulloni, viti) come estensione futura.

G. Strutture in muratura:
   - muratura nuova: resistenza a compressione, taglio nel piano, flessione fuori piano, meccanismi locali;
   - muratura esistente: livelli di conoscenza, fattori di confidenza, meccanismi locali e globali, safety index.

H. Geotecnica:
   - fondazioni superficiali: capacità portante, scorrimento, ribaltamento, cedimenti;
   - fondazioni profonde (pali): portanza e cedimenti, anche solo come pianificazione modulare;
   - interfaccia tra modulo strutturale e modulo geotecnico.

I. Sismica globale:
   - parametri sismici NTC2018 (spettri, categoria di sottosuolo e topografica);
   - analisi statica equivalente e, in prospettiva, modale;
   - verifiche globali: drift, elementi non strutturali, gerarchia delle resistenze.

L. Edifici esistenti:
   - obiettivi (miglioramento, adeguamento);
   - definizione di indici di sicurezza (ζ_E) e modalità di calcolo domanda/capacità;
   - pianificazione dell’integrazione con moduli muratura e c.a. esistente.

M. UI Tkinter e workflow:
   - schermate per selezione norma, tipo di verifica, materiale, sezione;
   - riutilizzo delle GUI esistenti per definizione di sezioni e materiali;
   - flusso utente: definizione sezioni/materiali → definizione azioni/combinazioni → scelta verifica → risultati.

N. Validazione, test, demo e documentazione:
   - strategia di test (unit, integrazione) per ogni modulo di verifica;
   - demo di utilizzo dell’engine NTC2018;
   - aggiornamento documentazione (README, esempi).

COSA VOGLIO DA TE ORA:

1. Proponi un PIANO dettagliato, strutturato per fasi (Fase 1, Fase 2, …), che copra tutte le macro-aree sopra, indicando per ciascuna:
   - sotto-attività specifiche,
   - priorità (alta/media/bassa),
   - dipendenze (cosa deve esserci prima),
   - cosa è realistico implementare subito usando solo i materiali/sezioni esistenti.

2. Nel proporre il piano, tieni conto che:
   - voglio massimizzare il valore di QUESTA SINGOLA SESSIONE: quindi dammi subito una roadmap completa e coerente;
   - nelle fasi iniziali è preferibile consolidare bene il modulo NTC2018 per c.a. (RC), poi estendere agli altri materiali;
   - qualsiasi suggerimento architetturale deve rispettare la separazione core/GUI già esistente.

3. Alla fine, fornisci:
   - una versione “compatta” del piano (solo titoli e priorità) da usare come checklist;
   - una versione “estesa” con un po’ di dettagli per ogni task (ma senza scrivere codice per ora).

Inizia presentando la struttura del piano (indice delle fasi) e poi vai in dettaglio.


GitHub Copilot: ## Indice del piano (strutturato per fasi) 📋
1. Fase 0 — Preparazione e consolidamento (scoping, test‑hygiene)  
2. Fase 1 — API normativa & packaging NTC2018 (CodeModule)  
3. Fase 2 — Azioni e combinazioni (motore combinazioni configurabile)  
4. Fase 3 — Materiali e modelli costitutivi (focus CA / NTC2018)  
5. Fase 4 — Verifiche elementi in calcestruzzo armato (priorità: travi → pilastri → solette/fondazioni)  
6. Fase 5 — Sismica globale (NTC2018: spettri + statica equivalente)  
7. Fase 6 — Acciaio / Legno / Muratura (moduli estendibili)  
8. Fase 7 — Geotecnica & interfacce (stub → integrazione)  
9. Fase 8 — Edifici esistenti (procedure di adeguamento)  
10. Fase 9 — UI Tkinter e workflow utente (incrementale, riuso)  
11. Fase 10 — Validazione, test, demo e documentazione  
12. Fase 11 — Release, CI e governance

---

## Panoramica rapida (TL;DR) 💡
- Primo obiettivo: consolidare un package `codes/ntc2018` + interfaccia `CodeModule` che espone check SLU/SLE/sismici; riusare checks_ntc2018.py e `VerificationEngine`.  
- Priorità iniziale: completare verifiche CA (flessione, taglio, N–M) e generatore combinazioni configurabile; aggiornare configurazione `config/*` per NTC2018.  
- UI: estendere selettore norma + pannello combinazioni; mantenere separazione core/GUI.  
- Validazione: test unitari normativi + esempi demo (numeri di riferimento).

---

## Fase 0 — Preparazione e consolidamento (High)
Obiettivo: ridurre rumore e definire punto di partenza pulito.

- Sotto‑attività
  1. Verificare copertura test corrente; aggiungere smoke tests per `VerificationEngine` e checks_ntc2018.py.  
  2. Consolidare riferimenti canonici (già fatto in larga parte: core_calculus, sections).  
  3. Documentare “contract” per CalcInput/VerificationTemplate (rif. `src/core_calculus/contracts`).
- Dipendenze: nessuna
- Deliverable: test baseline verde, checklist file da rifattorizzare (checks_ntc2018.py segnalato)
- Realizzabile subito con i file esistenti: sì

---

## Fase 1 — API normativa & packaging NTC2018 (CodeModule) (High)
Obiettivo: definire interfaccia comune per tutti i moduli normativi.

- Sotto‑attività
  1. Definire `CodeModule` (API/contract): metodi es.: `available_checks()`, `run_check(id, CalcInput)`, `load_templates()`, `get_parameters()`.  
  2. Creare package `src/codes/ntc2018/` (namespace) e mappare checks_ntc2018.py come implementazione iniziale.  
  3. Implementare registry loader che `VerificationEngine` può interrogare per la norma selezionata.  
  4. Stendere SPEC delle `VerificationTemplate` per NTC2018 (SLU/SLE/sismico).
- Dipendenze: Fase 0
- Deliverable: design API + schematic file mapping (no refactor invasivo iniziale)
- Cosa usare subito: checks_ntc2018.py, verification_engine.py
- Acceptance: engine può invocare check tramite `CodeModule` senza import diretti a checks_ntc2018.py.

---

## Fase 2 — Azioni & combinazioni (High)
Obiettivo: motore combinazioni conforme NTC2018, configurabile via `.jsoncode`.

- Sotto‑attività
  1. Catalogo azioni NTC2018: permanente (G1,G2), variabile (Qk con categorie), neve, vento, sisma, accidentale.  
  2. Design `combinations` engine: regole configurabili (ψ-factors, γ-factors), template per SLU/SLE (rare/frequent/quasi‑permanent).  
  3. Inserire default NTC2018 in `config/calculation_codes/NTC2018.jsoncode` (combinazioni, ψ, elenco azioni).  
  4. API: `generate_combinations(loads, scenario)` → lista `LoadCase` compatibili con `VerificationEngine`.
- Dipendenze: Fase 1 (per template)  
- Deliverable: modulo `core/combinations` + config example
- Realizzabile subito: generator base usando regole standard e dati in config

---

## Fase 3 — Materiali e modelli costitutivi (High)
Obiettivo: stabilire registry e adapter materiali NTC2018.

- Sotto‑attività
  1. Consolidare `MaterialProperties` e registry in `src/core_calculus/materials` (adapter verso `config/historical_materials_loader` e material_sources.py).  
  2. Implementare funzioni NTC2018 per ricavare f_cd, f_ctm, fattori LC/FC (riuso `VerificationEngine.get_allowable_stresses`).  
  3. Test: mapping materiale → proprietà (C25/30, B450C, ecc.) con casi di riferimento.  
- Dipendenze: Fase 1, Fase 2  
- Deliverable: material adapter + test suite per NTC2018 materials
- Realizzabile subito: sì (usa material_sources.py e historical_materials)

---

## Fase 4 — Verifiche per calcestruzzo armato (RC) — PRIORITÀ MASSIMA
Obiettivo: implementare controlli NTC2018 per elementi CA (progressivo, test-driven).

- Sotto‑attività per travi (prima iterazione)
  1. Flessione semplice (SLU) — completare/validare `check_flessione_slu_rett` in checks_ntc2018.py.  
  2. Minimi armatura (SLE) — `check_minimi_armatura_flessione_slu`.  
  3. Taglio (SLU) — implementare `check_taglio_slu` con shear‑capacity e verif armatura trasversale.  
  4. Interaction N–M (piastra semplice e travi composte).  
  5. Unit tests + normative references (`NormReference`).
- Sotto‑attività per pilastri
  1. Verifica N–M (SLU, instabilità secondo ordine), fascio di test.  
  2. Controlli snellezza, buckling, duttilità.  
- Sotto‑attività per solette/fondazioni
  1. Punzonamento (solette piane), controllo flessione, fessurazione (SLE).  
  2. Fondazioni superficiali: verifica capacità portante (collegamento a modulo geotecnico in Fase 7).
- Dipendenze: Fasi 1–3
- Deliverable: set di `check_*` per CA, integrati in `CodeModule` NTC2018, test numerici comparativi
- Realizzabile subito: flessione semplice e minimi armatura (già parziali nel repo)

---

## Fase 5 — Sismica globale (NTC2018) (High)
Obiettivo: implementare parametri sismici NTC2018 e analisi statica equivalente.

- Sotto‑attività
  1. Configurare parametri sismici in `config/calculation_codes/NTC2018.jsoncode` (ag, Tc, S, site class, behaviour factor q).  
  2. Implementare generator spettri elastic/response spectrum utility (funzioni in `src/sismo/`).  
  3. Implementare analisi statica equivalente (NTC2018 §) e collegare a verifica globale drift e forze di progetto.  
  4. Prevedere hook per analisi modale successiva.
- Dipendenze: Fase 1–3
- Deliverable: spettro generator + API che fornisce azioni sismiche a `VerificationEngine`
- Realizzabile subito: parametri + generator spettro e test comparativi.

---

## Fase 6 — Acciaio, Legno, Muratura (Medium)
Obiettivo: design modulare + primi check per acciaio.

- Sotto‑attività (acc. prima)
  1. Definire data model per acciaio (classi sezione, yield, buckling).  
  2. Implementare check flessione/pressione/base per sections classificate (starter).  
- Legno/muratura: solo API & stubs (plan + template tests)
- Dipendenze: Fase 1, Fase 3 (materials)
- Deliverable: `codes/steel` stub + 1–2 check implementati

---

## Fase 7 — Geotecnica (Medium)
Obiettivo: definire interfaccia tra strutturale e geotecnico.

- Sotto‑attività
  1. Disegnare `GeotechAdapter` API (capienza portante, cedimenti stimati).  
  2. Implementare check plinti (capacity + settlement heuristic) come esempio.
- Dipendenze: Fase 3, Fase 4
- Deliverable: adapter/contract + demo integration

---

## Fase 8 — Edifici esistenti (Medium)
Obiettivo: procedure di adeguamento / indici (ζ_E).

- Sotto‑attività
  1. Definire workflow per valutazione domanda/capacità (sisma) e strumenti di input (livello conoscenza).  
  2. Implementare calcolo indice di sicurezza e report sintetico.
- Dipendenze: Fase 4, Fase 5
- Deliverable: `codes/ntc2018/existing_buildings` (stubs + checks)

---

## Fase 9 — UI Tkinter e workflow (High, incrementale)
Obiettivo: integrare scelta norma, combinazioni e risultati.

- Sotto‑attività (iteration 1 → MVP)
  1. Aggiungere selettore **Norma** in main_window.py.  
  2. Pannello Combinazioni: editor + presets NTC2018 (reuse UI widgets esistenti).  
  3. Dialog risultati: mostra `VerificationResult` step‑by‑step + normativa/riferimenti.  
- Iteration 2: visualizzazioni sismiche (spettri), reporting PDF/Markdown.
- Dipendenze: Fasi 1–5
- Deliverable: UI estesa che chiama `VerificationEngine` con `CodeModule` selezionato
- Realizzabile subito: aggiunta selector + hooking `VerificationEngine` (usa esistenti frc_verification_window.py come pattern)

---

## Fase 10 — Validazione, test, demo, documentazione (High)
Obiettivo: garantire correttezza normativa e facilità d’uso.

- Sotto‑attività
  1. Unit tests per ogni check (numerical invariants + edge cases).  
  2. Integration tests: scenari di riferimento (es. manuali NTC2018 examples).  
  3. Demo scripts (demo_verification_engine.py) aggiornati per NTC2018.  
  4. Documentazione: `docs/NTC2018.md`, aggiornare README.md e CHANGELOG.  
- Metriche di qualità: >90% unit test coverage per nuovi moduli; test numerici con tolleranze documentate.
- Dipendenze: tutte le fasi precedenti
- Deliverable: suite test, demo scenari, documentazione

---

## Fase 11 — Release & CI (Medium)
- Aggiornare CI per includere: matrix (python versions), test coverage, warnings-as-errors optional.  
- Tag/release note e guida migrazione per utenti (shim deprecations).

---

## Priorità sintetica (alta → bassa)
- Alta: Fase 1, 2, 3, 4, 9, 10, 5  
- Media: Fase 6, 7, 8, 11  
- Bassa: estensioni aggiuntive materiale/collegamenti

---

## Dipendenze chiave (riassunto)
- `CodeModule API` (Fase 1) → requisito per tutte le verifiche modulari.  
- calculation_codes aggiornato → necessario per combinazioni e sismica.  
- `material registry` (Fase 3) → usato da engine e checks.  
- `VerificationEngine` estensibile → deve chiamare `CodeModule` senza knowledge diretta.

---

## Cosa è realistico implementare SUBITO in questa sessione (valore massimo)
- Disegno dettagliato `CodeModule` + mapping file/funzioni da refattorizzare (documento + TODO list).  
- Specifica `config/calculation_codes/NTC2018.jsoncode` (skeleton) e lista parametri obbligatori.  
- Lista di check prioritari per CA con riferimenti normativi e test‑cases numerici da aggiungere.  
- Wireframe UI minimali (lista di widget da aggiornare in ui).  
(Tutto quanto sopra come piano e artefatti di progetto — non viene scritto codice.)

---

## Acceptance criteria (per ogni fase)
- API pulita e documentata (`CodeModule`); engine può usare moduli normativi tramite registry.  
- Ogni nuova verifica ha unit test con riferimenti normativi e benchmark numerico.  
- Nessun codice normativo dentro i callback GUI; GUI chiama solo API pubbliche del core.  
- Configurazione NTC2018 disponibile via `config/*` e non hard‑coded.  
- Full test‑suite verde prima del merge.

---

## Rischi & mitigazioni
- Rischio: regressioni numeriche dovute a refactor → mitigate con test numerici di riferimento.  
- Rischio: duplicazione logica tra `methods/` e core_calculus → mitigare consolidando in Core e usando shims temporanei.  
- Rischio: aspettative normative incomplete → usare step incrementali e documentare TODO normativi.

---

## Consegne e milestones (suggerite)
- Milestone 1 (2–3 sprint): Fase 0–4 + UI minimo per SLU flessione/travi + tests.  
- Milestone 2 (2 sprint): Sismica (Fase 5) + combinazioni complete + demo.  
- Milestone 3 (2–3 sprint): Estensioni materiali e moduli secondari + documentazione completa.

---

## Checklist compatta (usa come TODO rapido)
- [ ] Fase 0 — test baseline verde  
- [ ] Fase 1 — definire `CodeModule` + packaging `src/codes/ntc2018`  
- [ ] Fase 2 — motore combinazioni + config NTC2018  
- [ ] Fase 3 — material registry aggiornato (NTC2018)  
- [ ] Fase 4 — flessione/taglio/N–M per CA (unit tests)  
- [ ] Fase 5 — spettro + statica equivalente  
- [ ] Fase 9 — UI: selettore norma + editor combinazioni  
- [ ] Fase 10 — test, demo, docs

---

## Versione estesa (task-by-task — riepilogo per esecuzione)
Per ogni fase ho predisposto: obiettivo, sotto‑task, file esistenti da riusare, criteri di accettazione e test da scrivere. (Posso consegnare il dettaglio file‑per‑file e il set di test‑case se vuoi che proceda alla fase successiva del piano.)

---

Prossimo passo raccomandato (da eseguire subito): formalizzare l’API `CodeModule` e mappare i file/calls esistenti (checks_ntc2018.py → `src/codes/ntc2018/*`), generare la checklist dettagliata per la Fase 1.  
Vuoi che prepari ora la SPEC dettagliata di `CodeModule` + la lista di refactor file‑by‑file per la Fase 1?

User: PROMPT INCREMENTALE SUL PIANO PRECEDENTE (NON GENERARE CODICE)

IMPORTANTE (promemoria): rimani sempre e solo in "modalità Plan". Non generare codice. Non proporre implementazioni operative. Limita la tua attività esclusivamente alla pianificazione (fasi, sotto-task, dipendenze, criteri di accettazione).

A partire dal piano che hai già prodotto (con Fasi 0–11, in particolare la Fase 4 sulle verifiche per calcestruzzo armato), voglio che tu lo ESTENDA includendo in modo esplicito e strutturato le verifiche per elementi strutturali privi di specifica armatura a taglio, come previsto dal Capitolo 4 delle NTC2018.

Obiettivo dell’incremento:
- Estendere la Fase 4 (Verifiche RC) per coprire non solo il taglio con armatura trasversale, ma anche:
  - la verifica V_Rd,c per elementi SENZA armatura a taglio;
  - tutte le condizioni di applicabilità previste dal Cap. 4 NTC2018 (limiti geometrici, percentuali di armatura longitudinale, effetti di N, ecc.);
  - i controlli associati di tipo SLE (fessurazione) quando non sono presenti staffe specifiche.

Aggiornamenti richiesti alla Fase 4:
1. Mantieni quanto già previsto (flessione, minimi di armatura, taglio CON armatura, interazione N–M, ecc.), ma aggiungi un nuovo blocco di sotto-attività per:

   "Taglio SENZA armatura trasversale (V_Rd,c) per elementi RC secondo Cap. 4 NTC2018"

   Il nuovo blocco di sotto-attività deve includere almeno:
   - Modellazione della resistenza a taglio V_Rd,c in funzione di:
     - bw, d, f_ck, ρ_l, σ_cp e altri parametri richiesti dalla norma;
   - Condizioni di applicabilità:
     - limiti geometrici (larghezza minima, altezza utile, rapporti di snellezza, ecc.);
     - limiti sull’armatura longitudinale (ρ_l min e max);
     - influenza di uno sforzo normale N (σ_cp favorevole/sfavorevole);
   - Eventuali riduzioni o integrazioni previste dal Cap. 4:
     - presenza di torsione T,
     - elevato livello di fessurazione,
     - domini combinati V–M in campi non fessurati.
   - Collegamento con verifiche SLE:
     - controllo di fessurazione in assenza di staffe specifiche;
     - coerenza con i limiti di apertura fessure e con il comportamento fessurato.

2. Prevedi una sezione specifica per i TEST relativi al taglio SENZA armatura:
   - casi di riferimento numerici (esempi tipo):
     - trave con sola armatura longitudinale, senza staffe;
     - trave con sforzo normale di compressione;
     - casi ai limiti di applicabilità (deve “fallire” la verifica se fuori campo).
   - criteri di accettazione:
     - conformità ai vantaggi/svantaggi rispetto a V_Rd,s;
     - chiarezza dei messaggi di verifica (campo di validità, eventuali warning).

3. Aggiorna la sezione “Deliverable” della Fase 4:
   - includi la presenza di uno o più check concettuali per:
     - “RC_SLU_VRDc_NoStirrups” (o nome equivalente a tua scelta);
   - specifica che questi check devono essere esposti tramite il CodeModule NTC2018 come nuove voci in available_checks() (ma senza generare il codice, solo come pianificazione).

4. Aggiorna la checklist compatta:
   - aggiungi una voce esplicita, ad es.:
     - "Fase 4 — Taglio SENZA armatura trasversale (V_Rd,c) — verifiche e test"

5. Mantieni esplicitamente la priorità ALTA per questa estensione della Fase 4, indicando che:
   - le verifiche a taglio senza armatura fanno parte del “core” RC secondo NTC2018, quindi devono essere considerate entro le prime milestone.

Formato di output richiesto:
- NON riscrivere l’intero piano da zero.
- Fornisci:
  1) un breve riepilogo di come si modifica la Fase 4 (paragrafi aggiornati);
  2) le nuove sotto-attività puntuali da aggiungere alla Fase 4;
  3) la riga aggiuntiva da mettere nella checklist compatta;
  4) eventuali aggiornamenti ai criteri di accettazione legati alla Fase 4.

Ricorda ancora: non generare codice, non proporre implementazioni in Python; rimani esclusivamente in ambito di pianificazione (Plan).

PROMPT INCREMENTALE SUL PIANO PRECEDENTE (MODULO ELEMENTI STRUTTURALI SECONDARI — SOLO PLAN)

IMPORTANTE (promemoria): rimani sempre e solo in "modalità Plan". 
Non generare codice. 
Non proporre implementazioni operative (funzioni Python, classi, Tkinter code, ecc.). 
Limita la tua attività esclusivamente alla pianificazione: fasi, sotto-task, architettura, API, GUI da progettare, file di config/registro, dipendenze e criteri di accettazione.

CONTESTO DI PARTENZA:

Hai già prodotto un piano strutturato per fasi (Fase 0–11) per l’implementazione NTC2018 nel framework, con:
- CodeModule NTC2018,
- combinazioni,
- materiali,
- verifiche RC, sismica, moduli futuri, UI, test, ecc.

Ora voglio ESTENDERE quel piano introducendo un **modulo separato** per la gestione delle **verifiche di elementi strutturali secondari** secondo NTC2018, Cap. 7.2, integrato, dove necessario, con le formulazioni degli Eurocodici (quando NTC2018 non fornisce formule applicabili o complete).

OBIETTIVO DI QUESTO INCREMENTO:

1. Definire una nuova sezione del piano (ad es. una sotto-fase dedicata o una nuova Fase tipo “Fase X — Elementi strutturali secondari”) che progetti:
   - un modulo separato per le verifiche di elementi strutturali secondari in codes/ntc2018 (es. codes/ntc2018/secondary_elements);
   - il relativo supporto nell’engine, nella configurazione e nella UI.

2. Considerare esplicitamente diversi tipi di elementi secondari, ad esempio:
   - tramezzi/partizioni (anche non portanti, soggetti ad azioni sismiche/accidentali),
   - insegne, pannelli pubblicitari, elementi sospesi,
   - camini, comignoli, parapetti, elementi fuori piano,
   - elementi che lavorano a mensola (appoggiati/incastrati in un solo punto),
   - elementi incastrati a entrambe le estremità (travi iperstatiche),
   - elementi incernierati alle due estremità (travi isostatiche),
   - altri elementi secondari che possono essere presenti nel Cap. 7.2 o nella prassi progettuale.

3. Per ognuna di queste categorie:
   - impostare il SISTEMA DI CALCOLO (modello statico, schema, combinazioni rilevanti, si/no sisma, ipotesi semplificative);
   - specificare quali parti derivano direttamente da NTC2018 e quali invece richiedono il ricorso agli EUROCODICI (es. EC2, EC3, EC8) per la definizione delle formule di verifica, in quanto NTC2018 non fornisce espressioni esplicite.

4. Estendere questo approccio anche ad **altre verifiche previste da NTC2018** per le quali:
   - la norma indica che il tecnico può/dover usare formule disponibili altrove,
   - non è riportata una formulazione chiusa,
   - le modalità di calcolo sono “rinviate” alla letteratura o ad altre norme (es. Eurocodici).
   In questi casi, voglio che il piano:
   - segnali esplicitamente che si attinge alle formulazioni degli Eurocodici;
   - identifichi il tipo di modello di calcolo da implementare (senza scrivere le formule, ma descrivendo che tipo di relazione e parametri servono).

RICHIESTA DETTAGLIATA DI PIANIFICAZIONE:

A. Architettura del modulo “elementi strutturali secondari”
   - Progetta a livello di piano un nuovo modulo (es. codes/ntc2018/secondary_elements) che:
     - definisce tipi di elementi secondari (enum, classi concettuali);
     - espone nuove verifiche tramite CodeModule NTC2018 (es. check_secondary_*).
   - Indica:
     - quali API devono essere aggiunte a CodeModule per questi elementi;
     - come il VerificationEngine deve orchestrare questi check (solo a livello di design, non codice).

B. Sistemi di calcolo per ciascun tipo di elemento secondario
   Per ognuna delle seguenti categorie, definisci i sotto-task di pianificazione:
   1) Tramezzi / partizioni interne:
      - criteri di modellazione sotto azione sismica (forze equivalenti, drift, ecc.);
      - campi di validità delle verifiche;
      - origine delle formule (NTC2018 vs Eurocodici).
   2) Insegne, pannelli, elementi sospesi:
      - modelli a mensola / a trave;
      - combinazioni di carico (vento, sisma, peso proprio, neve se applicabile);
      - richiami agli Eurocodici per le formule mancanti.
   3) Camini, comignoli, parapetti:
      - modello a mensola / elemento in elevazione;
      - verifiche a flessione, instabilità, connessione alla struttura;
      - uso di EC8/EC2/EC3 dove NTC2018 è qualitativa.
   4) Elementi tipo mensola:
      - schema di calcolo: incastro alla base, carichi distribuiti/puntuali;
      - verifiche SLU/SLE rilevanti;
      - richiesta esplicita di integrazione Eurocodici se NTC2018 è carente.
   5) Elementi incastrati alle estremità:
      - travi continue o incastrate-inincastrate;
      - momenti e tagli di progetto (solo a livello di metodo);
      - verifiche associate nelle combinazioni.
   6) Elementi incernierati alle estremità:
      - travi semplicemente appoggiate;
      - schema statico, carichi, modalità di verifica.

   Per ogni categoria, il piano deve:
   - definire le verifiche da coprire (flessione, taglio, instabilità, deformabilità, ecc.);
   - indicare se la fonte principale è NTC2018 o Eurocodice;
   - indicare eventuali “limiti di responsabilità” del modulo (es. avvisi se fuori campo di applicazione).

C. Integrazione con Eurocodici
   - Pianifica come integrare sistematicamente gli Eurocodici per:
     - le verifiche degli elementi strutturali secondari;
     - tutte le altre parti NTC2018 dove la norma rinvia a “formule disponibili altrove”.
   - Il piano deve specificare:
     - per quali tipologie di verifica si attinge a EC2/EC3/EC8 (senza riportare formule, ma solo a livello concettuale);
     - come documentare, all’interno del software, la fonte normativa (es. codici di riferimento, note nei report di verifica).

D. Sistemi di calcolo, GUI e file di registro/archivio (SEMPRE SOLO PIANIFICAZIONE)
   - Sistemi di calcolo:
     - definisci, a livello di design, quali nuovi “CalculationTemplate”/“VerificationTemplate” servono per gli elementi secondari;
     - specifica quali dati di input sono necessari (geometria, fissità, carichi, parametri normativi);
     - come questi template si integrano con l’engine esistente.
   - GUI (Tkinter):
     - progetta nuovi pannelli/finestre per:
       - la definizione degli elementi secondari (tipo elemento, schema statico, fissità);
       - l’assegnazione dei carichi e delle combinazioni;
       - la visualizzazione dei risultati e dei messaggi normativi (NTC2018 + Eurocodice).
     - riuso di pattern UI esistenti (menu norma, editor sezioni e materiali, ecc.).
   - File di registro, archivio e configurazione:
     - pianifica la struttura dei nuovi file di config/registro (es. config/codes/ntc2018/secondary_elements.jsoncode);
     - definisci le voci minime da salvare:
       - tipo elemento secondario;
       - schema di vincolo;
       - sorgente normativa (NTC/EC);
       - parametri di calcolo specifici;
       - risultati sintetici per reporting.
     - prevedi come archiviare/salvare:
       - set di elementi secondari associati ad un progetto;
       - eventuali librerie di “tipi standard” (es. tramezzo tipo, insegna tipo, camino tipo).

E. Inserimento nel piano esistente (Fasi 0–11)
   - Indica chiaramente:
     - se questo modulo va inserito come:
       - una nuova Fase (es. “Fase 6bis — Elementi strutturali secondari”), oppure
       - una sotto-sezione di una Fase esistente (es. estensione di Fase 6 o Fase 4/5).
   - Aggiorna:
     - dipendenze (richiede CodeModule NTC2018, combinazioni, materiali, ecc.);
     - priorità (es. media/alta a seconda della combinazione con la sismica e l’uso pratico);
     - impatto su UI e sulle pipeline di verifica.

F. Checklist compatta e criteri di accettazione
   - Aggiungi voci esplicite nella checklist compatta, ad es.:
     - “Modulo elementi strutturali secondari (Cap. 7.2 NTC2018 + Eurocodici) — design completato”
     - “GUI per definizione/verifica elementi secondari — design completato”
     - “Config/registry per elementi secondari — schema definito”
   - Aggiorna i criteri di accettazione:
     - ogni tipo di elemento secondario ha:
       - un sistema di calcolo definito;
       - le fonti normative (NTC vs EC) chiaramente indicate;
       - il flusso di input/output previsto (core + GUI + storage) descritto.

FORMATO DI OUTPUT RICHIESTO:

1. NON riscrivere tutto il piano da zero.
2. Fornisci:
   - una breve descrizione di dove si inserisce il “Modulo elementi strutturali secondari” nel piano esistente (nuova fase o sotto-fase);
   - l’elenco strutturato dei sotto-task per questo modulo, raggruppato per:
     - Architettura;
     - Sistemi di calcolo per tipo di elemento;
     - Integrazione Eurocodici;
     - GUI e storage;
     - Dipendenze e priorità;
   - le nuove voci da aggiungere alla checklist compatta;
   - eventuali estensioni dei criteri di accettazione generali, legate a questo modulo.

Ribadisco: non generare codice, non proporre implementazioni Python/Tkinter; resta in modalità Plan, limitandoti alla definizione del piano tecnico, dei task, delle dipendenze e dei criteri di successo.

PROMPT INCREMENTALE SUL PIANO PRECEDENTE (MIGLIORAMENTO GUI + CALCOLO + REGISTRY + STORAGE — SOLO PLAN)

IMPORTANTE (promemoria): rimani sempre e solo in "modalità Plan".
Non generare codice. 
Non proporre implementazioni operative (Python, classi, Tkinter, file JSON).
Limita l’attività alla pianificazione: fasi, sotto-task, architettura, API, GUI, registry, storage, dipendenze, criteri di accettazione.

CONTESTO DI PARTENZA:
Abbiamo già stabilito un piano completo per NTC2018, con moduli incrementali (RC, combinazioni, CodeModule, elementi secondari, ecc.).
Il repository contiene già strumenti di calcolo per normative precedenti (RD2229, Tensioni Ammissibili DM ’92 e DM ’96).
Sono già presenti:
- GUI Tkinter parziali (sections, frc_verification_window, storico materiali),
- sistemi di storage (JSON, CSV),
- sistemi di calcolo “storici” integrati tramite loader,
- collegamenti tra GUI → Engine → Moduli normativi.

Obiettivo dell’incremento:
Voglio che venga esteso il piano precedente includendo un’analisi dettagliata e una pianificazione completa per:

1. **migliorare, armonizzare e modernizzare TUTTE le GUI esistenti**, mantenendo compatibilità retroattiva;
2. **migliorare e ottimizzare i file di calcolo, registry, storage**, senza riscrivere completamente i moduli delle normative precedenti (RD2229, DM ’92, DM ’96);
3. **analizzare il repository per capire dove intervenire nelle dipendenze**, nei collegamenti e negli hook tra:
   - GUI → VerificationEngine,
   - Engine → CodeModule,
   - CodeModule → sistemi di calcolo specifici,
   - sistemi di calcolo → materiali / sezioni / combinazioni;
4. **produrre un piano strutturato** in cui:
   - vengono elencati gli aggiornamenti per ogni GUI esistente;
   - vengono indicate tutte le modifiche necessarie ai file di registry e storage (senza generare i file);
   - vengono identificate ottimizzazioni dei collegamenti e dei parametri tra normative diverse;
   - viene indicato come integrare senza traumi i nuovi moduli (NTC2018) con le norme storiche.

RICHIESTE DI PIANIFICAZIONE:

A. ANALISI DEL REPOSITORY E MAPPATURA DEI PUNTI DI INTERVENTO
   - Effettua a livello concettuale una “mappa di dipendenze”:
     - moduli GUI esistenti;
     - moduli di calcolo esistenti (NTC, RD2229, DM ’92, DM ’96);
     - storage esistenti (materials.json, sections.json, historical_materials.json, .jsoncode);
     - registry loader (calculation_codes_loader, historical_materials_loader).
   - Identifica:
     - duplicazioni da consolidare,
     - moduli che necessitano unificazioni o refactor non invasivi,
     - collegamenti fragili/rigidi da sostituire con API più pulite.

B. MIGLIORAMENTO E INTEGRAZIONE DELLE GUI
   - Analizza TUTTE le GUI presenti nel repository:
     - section GUI,
     - materials GUI,
     - frc_verification_window,
     - historical GUIs,
     - selettori vari.
   - Pianifica:
     - un’estensione coerente del selettore di norma (in tutte le GUI rilevanti),
     - standardizzazione del flusso input → engine → result,
     - UI per editor parametri normativi (quando ammesso),
     - miglioramento del form per combinazioni,
     - miglioramento dei flussi per:
       - sezioni,
       - materiali,
       - carichi,
       - assegnazione verifiche,
       - visualizzazione risultati.
   - Proponi (solo a livello di design):
     - dove aggiungere pannelli,
     - quali controlli unificare,
     - come migliorare l’esperienza dell’utente,
     - come evitare duplicazioni tra vecchie e nuove GUI.

C. MIGLIORAMENTO DEI FILE DI CALCOLO, REGISTRY E STORAGE
   - Prevedi per ogni tipo di file:
     - historical_materials.json → come integrarlo con materiali NTC2018, senza romperlo;
     - calculation_codes/*.jsoncode → come estenderli per:
       - collegamenti con Eurocodice,
       - moduli secondari,
       - moduli NTC2018 RC e non-RC;
     - storage sezioni → estendere senza perdere retrocompatibilità.
   - Pianifica aggiornamenti senza riscrittura delle normative storiche:
     - RD2229,
     - tensioni ammissibili DM ’92 / DM ’96,
     - mantenere i vecchi loader ma aggiungere nuove chiavi/config di espansione.
   - Pianifica un “registry unificato” dei moduli normativi:
     - uno strato neutro sopra RD2229/DM’92/DM’96/NTC2018.

D. INTEGRAZIONE E ARMONIZZAZIONE TRA LE NORME
   - Pianifica l’aggiornamento dell’Engine per:
     - lavorare via CodeModule anche con RD2229, DM ’92, DM ’96;
     - definire template comuni per:
       - input,
       - output,
       - parametri,
       - formati di verifica.
   - Pianifica cosa va fatto per:
     - non riscrivere i calcoli storici,
     - ma esporli tramite API più coerenti,
     - riorganizzando solo i collegamenti.

E. ORGANIZZAZIONE DELLE DIPENDENZE E GESTIONE DEI CAMBIAMENTI
   - Se un miglioramento richiede modifiche a:
     - loader,
     - registry,
     - collegamenti GUI → Engine,
     - dipendenze tra moduli,
     pianifica queste modifiche in modo:
       - funzionale,
       - non distruttivo,
       - incrementale,
       - atomico per fase.
   - Specifica una matrice:
     - “rischio vs impatto vs priorità” dei cambiamenti.

F. OUTPUT DELLA PIANIFICAZIONE
   Fornisci:
   1. una nuova sezione da inserire nel piano principale (es. “Fase 12 — Modernizzazione GUI + Registry + Storage” oppure sotto-fase della Fase 9 o Fase 1, a tua scelta motivata);
   2. l’elenco completo dei sotto-task raggruppati in:
      - Analisi del repository,
      - GUI,
      - File di calcolo / Registry / Storage,
      - Integrazione norme storiche / moderne,
      - Dipendenze e refactor non invasivi;
   3. nuove righe nella checklist compatta;
   4. estensione dei criteri di accettazione.

Ricorda: non generare codice, non proporre implementazioni in Python/Tkinter; resta esclusivamente in modalità Plan.

GitHub Copilot: ## Dove si inserisce l’incremento
- Inserimento principale: **estensione della Fase 4** (Verifiche RC) per includere esplicitamente il controllo del taglio *senza armatura trasversale* (V_Rd,c) — **priorità: ALTA**.  
- Nuovo modulo per elementi secondari: aggiungere **“Fase 6bis — Elementi strutturali secondari”** (modulo separato sotto `codes/ntc2018/secondary_elements`) — **priorità: MEDIA‑ALTA** (importante per implicazioni sismiche e pratiche di progetto).  
- Modernizzazione GUI / registry / storage: inserirla come **Fase 12 — Modernizzazione GUI + Registry + Storage** (collegamento diretto a Fasi 1–4 & 6bis) — **priorità: ALTA** per usabilità e integrazione.

---

## Sintesi: cosa cambia nella Fase 4 (breve)
- Mantieni tutte le sotto‑attività già pianificate (flessione, minimi armatura, taglio *con* staffe, N–M, SLE).  
- Aggiungi un nuovo blocco organizzato e prioritario: **Taglio SENZA armatura trasversale (V_Rd,c)** con modellazione, criteri di applicabilità, controlli SLE associati (fessurazione) e test dedicati.  
- Esporre nuovi check nel CodeModule NTC2018 (es.: `RC_SLU_VRDc_NoStirrups`, `RC_SLE_Cracking_NoStirrups`).

---

## Dettaglio: nuove sotto‑attività da aggiungere a Fase 4 (Taglio SENZA staffe) — tutte PRIORITÀ: ALTA

1. Specifica normativa e mapping
   - Identificare e citare i paragrafi NTC2018 §4.* che disciplinano V_Rd,c e limiti di applicabilità.  
   - Mappare punti mancanti verso EC2/EC8 se NTC rinvia a formule esterne.

2. Modellazione della resistenza V_Rd,c (concept, senza formule)
   - Definire i parametri di input richiesti: `b_w`, `d` (altezza utile), `f_ck`, `ρ_l` (armatura longitudinale efficace), `σ_cp` (pressione assiale), condizioni di bordo, lunghezza utile.  
   - Design dell’algoritmo decisionale:
     - calcolo di V_Rd,c (norma) → confronto con V_Ed;  
     - applicare fattori riduttivi per torsione, fessurazione elevata, effetti N negativi/positivi.  
   - Output del check: {OK | NOT_OK | NOT_APPLICABLE} + `utilisation` + `norm_references` + `messages/warnings`.

3. Condizioni di applicabilità (validation rules)
   - Definire regole che emettono `NOT_APPLICABLE` o `WARNING`:
     - limiti geometrici (es. rapporto h/b, profondità utile minima, ecc.);  
     - limiti ρ_l (armatura longitudinale min/max per poter usare V_Rd,c);  
     - effetti di sforzo normale (`σ_cp` favorevole aumenta V_Rd,c; sfavorevole riduce o richiede verifica alternativa);  
     - esclusione se presenza di torsione significativa o se dominio di applicabilità (es. elementi corti/strani).
   - Definire messaggi espliciti per ogni condizione di esclusione.

4. Integrazione con verifiche SLE (fessurazione)
   - Check SLE che valuta comportamento fessurato in assenza di staffe:
     - calcolo indicatori di fessurazione (armatura longitudinale, spazi fessurativi attesi, apertura fessure rispetto a w_max normativo);  
     - generazione di azioni correttive (warning “considerare inserimento staffe” o `FAIL` per serviceability).
   - Collegamento tra SLU (calcolo V_Rd,c) e SLE (fessurazione): condizioni di coerenza e messaggi combinati.

5. Controlli addizionali / combinazioni V–M, torsione
   - Definire come combinare V_Rd,c con momenti e/o torsione (regole conservative, condizioni di warning).  
   - Prevedere test per casi combinati (V + M).

6. Documentazione & normative
   - Aggiornare section-calculations.md e `docs/NTC2018.md` con riferimenti, limiti di validità e decision flowchart per V_Rd,c.

7. Tests (unit + integration)
   - Caso base PASS, caso base FAIL, casi ai limiti di applicabilità (NOT_APPLICABLE), casi con N favorevole/sfavorevole, SLE crack check.
   - Definire `golden` examples e tolleranze numeriche.

---

## Test cases proposti per V_Rd,c (descrizioni — **numerici di input solo come esempi di test**, outcome atteso)
- Test A — PASS (within capacity)
  - Beam rect.: b=300 mm, d=450 mm, f_ck=30 MPa, ρ_l=0.015, σ_cp=0 MPa, V_Ed=60 kN → EXPECT: OK (V_Ed ≤ V_Rd,c)
- Test B — FAIL (overload)
  - Same geom, V_Ed=200 kN → EXPECT: NOT_OK (V_Ed > V_Rd,c)
- Test C — APPLICABILITY WARNING / NOT_APPLICABLE
  - ρ_l < normative_min OR d < normative_min → EXPECT: NOT_APPLICABLE (check must return explanatory warning)
- Test D — EFFECT OF AXIAL COMPRESSION
  - As A but σ_cp = +3 MPa (compressive) → EXPECT: V_Rd,c increased → re-evaluate PASS/FAIL accordingly
- Test E — SLE Crack control (no stirrups)
  - Low longitudinal reinforcement → EXPECT: SLE check FAIL or WARNING for excessive crack width

(Ciascun test dovrà includere un “expected behaviour” e il riferimento normativo; i valori numerici servono a definire i fixture di unit‑test — risultati attesi comparabili con formule NTC/EC.)

---

## Deliverable (Fase 4 — aggiornato)
- Nuovi checks esposti tramite CodeModule NTC2018:
  - `RC_SLU_VRDc_NoStirrups` (SLU shear capacity without stirrups)
  - `RC_SLE_Cracking_NoStirrups` (SLE crack serviceability when no stirrups)
  - `RC_SHEAR_Applicability_Check` (validazione campo applicativo)
- Test suite con i casi A–E + boundary tests
- Documentazione normativa + flowchart di decisione
- Messaggi di output standardizzati per `NOT_APPLICABLE`, `WARNING`, `OK`, `FAIL`

---

## Aggiornamento checklist compatta (riga da aggiungere)
- [ ] **Fase 4 — Taglio SENZA armatura trasversale (V_Rd,c) — verifiche, SLE fessurazione e test** (PRIORITÀ: ALTA)

---

## Estensioni ai criteri di accettazione (Fase 4)
- `RC_SLU_VRDc_NoStirrups` deve:
  - restituire chiaramente OK/NOT_OK/NOT_APPLICABLE con messaggi normativi e riferimenti;  
  - coprire tutte le condizioni di applicabilità indicate in NTC2018 (limiti geometrici, ρ_l, σ_cp);  
  - emettere `WARNING` se la verifica è **limite** o se assunzioni conservative sono applicate;  
  - essere coperto da unit test che includono casi limite e scenari di compressione/traction;  
  - includere almeno 3 `golden` numeric examples comparabili con calcoli di riferimento.
- SLE crack check deve:
  - fornire una stima qualitativa/quantitativa dello stato di fessurazione e indicare se supera il limite di servizio definito (w_max);  
  - essere eseguito automaticamente se non sono presenti staffe o se la geometria rientra in criteri previsti.

---

## Nuova sezione: Fase 6bis — “Elementi strutturali secondari” (overview)
- Posizionamento: **Fase 6bis** (dopo Fase 6 — Acciaio), integrate con Fasi 1–5 per dipendenze normative e sismiche.  
- Priorità: **MEDIA‑ALTA** (importante per valutazioni sismiche e pratica progettuale; non blocca core RC ma rilevante per consegne clienti).

### Architettura del modulo (alto livello)
- Package: `src/codes/ntc2018/secondary_elements` (implementazione `CodeModule` per secondary elements).  
- Componenti chiave (plan only):
  - `SecondaryElementType` (enum concettuale: PARTITION, SIGNAGE, CANTILEVER, CHIMNEY, PARAPET, etc.)  
  - `SecondaryElementSpec` (template dati: geometry, fixity, mass, wind/other loads, attachment details)  
  - `check_secondary_<type>` functions esposte tramite `CodeModule.available_checks()`  
  - Registry per “tipi standard” (salvabili in storage come librerie).

### API (da aggiungere a `CodeModule`)
- `available_secondary_types() -> list[str]`  
- `run_secondary_check(check_id: str, spec: SecondaryElementSpec, CalcInput) -> SingleCheckResult`  
- `list_secondary_templates()` (per UI presets)

### Orchestrazione (VerificationEngine — design)
- Engine consulta `CodeModule` per `available_checks()`; per elementi secondari usa `run_secondary_check` passando spec + combinazioni generate; engine include i risultati in `VerificationResult` con tag `secondary_element`.

---

## Sistemi di calcolo per ciascun tipo di elemento secondario (sotto‑task per ciascuna categoria)

Nota: per ogni voce sotto riportare — (A) modello statico, (B) verifiche da coprire, (C) fonte normativa (NTC2018 o EC*)

1) Tramezzi / partizioni interne
   - A: pannello non‑portante o pannello in semplice appoggio; modellazione come parete sottile o carico concentrato su struttura primaria.  
   - B: verifica resistenza a forze fuori‑piano (sisma), controllo ancoraggi e interazione con struttura portante, SLE (deformazioni).  
   - C: **NTC2018** per criteri sismici generali; per formule dettagliate attingere a **EC8 / linee guida tecniche**.  
   - Deliverable: `check_secondary_partition_sismo`, UI preset “partition”.

2) Insegne, pannelli, elementi sospesi
   - A: modello a mensola o a trave, carichi vento + peso proprio + sisma (se rilevante).  
   - B: controllo resistenza a taglio e momento, ancoraggi, stabilità globale (capovolgimento), verifica fatica se applicabile.  
   - C: NTC2018 indica criteri generali; formule per ancoraggi e dettagliatE → **EC3/EN anchors standards / Eurocodes**.  
   - Deliverable: `check_secondary_signage_shear_anchor`, UI per mensola/pannello.

3) Camini, comignoli, parapetti
   - A: elementi in elevazione; modellazione come trave verticale/torretta.  
   - B: verifica flessione, instabilità (wind + seismic), connessione alla struttura portante.  
   - C: parzialmente NTC2018 (criteri), dettagli tecnici → **EC2/EC8** per instabilità e comportamento sismico.  
   - Deliverable: `check_secondary_chimney_buckling`, warnings per esposizione sismica.

4) Elementi a mensola
   - A: incastro alla base; carichi puntuali/distribuiti; modellazione cantilever beam.  
   - B: SLU flessione/struttura di fissaggio, SLE deformabilità/deflessione.  
   - C: NTC2018 per criteri; calcoli dettagliati → **EC2/EC3** se necessario.  
   - Deliverable: `check_secondary_cantilever_moment`.

5) Elementi incastrati/continue
   - A: modello travi continue/incastro-incastro; considerare sovrapposizione momenti e condizioni di carico.  
   - B: verifiche momenti, tagli, serviceability; controllo di ripartizione delle azioni.  
   - C: fondamento NTC + utilizzo di teorie classiche (EC2/EC3) per parti non esplicitate.  
   - Deliverable: `check_secondary_continuous_beam`.

6) Elementi semplicemente appoggiati
   - A: travi isostatiche; calcolo momenti massimi; combinazioni di carico.  
   - B: SLU flessione, SLE deflessione, verifiche di appoggio e ancoraggi.  
   - C: principalmente formule standard (NTC applicabile), integrare EC dove NTC non specifica dettagli.

Per ogni categoria:
- definire `CalculationTemplate` (input fields), `VerificationTemplate` (check ids), e `storage schema` per salvataggio.

---

## Integrazione con Eurocodici (policy di progetto)
- Regola generale: **usare NTC2018 se espressa**; dove NTC rinvia o non fornisce espressioni numeriche implementare la soluzione **documentando chiaramente** la fonte EC (EC2, EC3, EC8) o standard di supporto (anchor codes, fatigue standards).  
- Piano operativo (non‑codice):
  - mappare per ogni check la fonte normativa (campo `norm_reference` nell’output);  
  - creare una tabella di “fallback normative” (es. per chimneys → EC1/EC8 per azioni wind/sismiche, per ancoraggi → EN anchors).  
  - documentare nel report di verifica quale norma è stata applicata e perché (NTC vs EC).

---

## GUI & storage per elementi secondari (pianificazione)
### GUI (Tkinter) — pannelli previsti
- `SecondaryElement Editor` (in ui):
  - selezione `element_type`, definizione geometria minima, fissità, carichi assegnati, attach points;  
  - presets/libreria elementi standard;  
  - pulsante “Generate combinations (NTC2018)” e “Run secondary checks”.
- `SecondaryResults` panel:
  - riepilogo esito (OK/FAIL/NOT_APPLICABLE), messaggi normativi e link a `norm_references`.
- Riuso: integrare i nuovi pannelli nel flusso esistente (menu norma, project manager, storage).

### Storage / registry (schema plan)
- `config/codes/ntc2018/secondary_elements.jsoncode` — registrare templates, limiti di validità e parametri standard.  
- Project storage entries:
  - `secondary_elements` array per progetto con item fields: `id`, `type`, `spec`, `norm_source`, `results` (summary), `created_from_template`.  
- Librerie: permettere salvataggio di “element types” riutilizzabili (`library/secondary_elements/*.json`).

---

## Inserimento nel piano esistente & dipendenze
- Posizionamento: aggiungere **Fase 6bis** subito dopo Fase 6 (Acciaio).  
- Dipendenze:
  - obbligatorie: Fase 1 (CodeModule API), Fase 2 (Combinazioni), Fase 3 (Materials), Fase 5 (Sismica) per elementi sensibili a sisma.  
  - GUI/storage: richiede Fase 12 (Modernizzazione GUI + Registry + Storage) o parallelo coordinato.
- Priorità: **media‑alta** (dipende dalle esigenze pratiche; per build sismiche è alta).

---

## Checklist compatta — nuove righe da aggiungere
- [ ] **Fase 4 — Taglio SENZA armatura trasversale (V_Rd,c) — verifiche e test** (ALTA)  
- [ ] **Fase 6bis — Modulo elementi strutturali secondari (Cap. 7.2 NTC2018 + EC fallback)** (MEDIA‑ALTA)  
- [ ] **Fase 12 — Modernizzazione GUI + Registry + Storage** (ALTA)

---

## Criteri di accettazione (aggiunte / estensioni)
- Per tutti i nuovi checks (V_Rd,c e secondary elements):
  - API: disponibili in `CodeModule.available_checks()` e invocabili tramite `VerificationEngine` (contract documentato).  
  - Output: struttura `SingleCheckResult` completa di `norm_references`, `messages_it`, `utilisation`, `details`.  
  - Validazione: unit/integration test che coprono OK/NOT_OK/NOT_APPLICABLE e boundary cases.  
  - Documentazione: per ogni check la fonte normativa è esplicitata (NTC o EC) e documentata nel report.  
  - UI: pannelli per input e risultati devono esistere come prototipo GUI (MVP) e non contenere formule normative (solo delega al core).

---

## Rischi specifici e mitigazioni (sintesi)
- Rischio: ambiguità normativa NTC sulle formule → mitigazione: usare EC come “fallback” con rinvio esplicito nel report.  
- Rischio: aumento complessità UI → mitigazione: design modulare, riuso componenti UI esistenti, feature‑toggles.  
- Rischio: comportamenti out‑of‑scope → mitigazione: `NOT_APPLICABLE` + warning ben documentati.

---

## Prossimi passi raccomandati (plan‑only)
1. Redigere SPEC formale per `RC_SLU_VRDc_NoStirrups` e `RC_SLE_Cracking_NoStirrups` (inputs, outputs, norme di riferimento, casi test).  
2. Definire `SecondaryElementSpec` schema e mappare 3‑4 tipi prioritari (mensola, insegna, tramezzo, camino) con i relativi `VerificationTemplate`.  
3. Aggiornare la documentazione del `CodeModule` per includere i nuovi check e i fallback EC.  
4. Progettare wireframe UI per `SecondaryElement Editor` e `SecondaryResults` (MVP).

---

Se vuoi procedo con il passo successivo di pianificazione: preparo (Plan only) la SPEC dettagliata per il check `RC_SLU_VRDc_NoStirrups` (input/output/casi di test e normative di riferimento) oppure la SPEC del `SecondaryElementSpec` per gli elementi prioritari — indicami quale preferisci che formalizzi adesso (solo plan).

AGISCI COME:
- ingegnere strutturista con esperienza in NTC2018 e Eurocodici (EC2, EC3, EC8);
- architetto software Python;
- assistente di pianificazione (PLAN-ONLY), NON generatore di codice.

CONTESTO (REPO LOCALE):
Sto lavorando su un framework di calcolo strutturale in Python con:
- motore di verifica separato dalla GUI (core_calculus, verification_engine, verification_core, methods);
- moduli normativi esistenti (NTC2018, RD2229, DM ’92, DM ’96) integrati tramite loader e file .jsoncode;
- GUI Tkinter per definizione sezioni, materiali e avvio verifiche (es. main_window, frc_verification_window, historical_main_window, ecc.);
- sistemi di storage (JSON/CSV) per sezioni, materiali, historical_materials, calculation_codes.

In precedenti passaggi di pianificazione ho già:
- introdotto il concetto di CodeModule per ciascuna norma;
- pianificato un modulo per NTC2018 (RC + combinazioni + elementi secondari);
- impostato l’idea di avere moduli separati per NTC2018, ma riusando materiali/sezioni esistenti e rispettando la separazione core/GUI.

OBIETTIVO SPECIFICO DI QUESTO PROMPT:
Voglio che tu, come GitHub Copilot Chat in VS Code:

1. Analizzi il **repository locale** (codice, GUI, config, storage) per capire dove e come:
   - integrare un modulo dedicato agli **elementi strutturali secondari**,
   - collegarlo in modo pulito a VerificationEngine, CodeModule NTC2018 e alla GUI.

2. Usi anche il **web** (documentazione online, testi normativi, articoli tecnici) per:
   - individuare riferimenti affidabili al **Capitolo 7.2 delle NTC2018** (“elementi non strutturali/secondari” e simili),
   - identificare le parti in cui NTC2018 NON fornisce formule esplicite,
   - trovare, in questi casi, le **formulazioni pertinenti negli Eurocodici** (es. EC8 per elementi non strutturali, EC2/EC3 per elementi a mensola o travi secondarie).

3. Resti **esclusivamente in modalità PIANIFICAZIONE**:
   - niente codice Python/Tkinter,
   - niente riscritture di file,
   - solo analisi + proposte di struttura, API, file di config, GUI da creare/estendere.

TIPI DI ELEMENTI SECONDARI DA CONSIDERARE:
Analizza e pianifica verifiche e modelli di calcolo per le seguenti categorie di elementi secondari, dove applicabile:

- tramezzi / partizioni non portanti;
- insegne, pannelli, elementi sospesi;
- camini, comignoli, parapetti, elementi fuori piano;
- elementi che operano come mensole (incastro a una estremità);
- elementi incastrati a entrambe le estremità;
- elementi incernierati alle due estremità (travi appoggiate);
- qualsiasi altro elemento secondario citato o implicito nel Cap. 7.2 NTC2018 o nella prassi corrente.

Per ciascuna categoria voglio che tu definisca, a livello di PIANO:

1) SISTEMA DI CALCOLO (MODELLO STRUTTURALE)
   - schema statico (mensola, trave isostatica, trave iperstatica, elemento snello ecc.);
   - azioni rilevanti (peso proprio, carichi variabili, vento, azione sismica, altre);
   - combinazioni di carico tipiche (SLU/SLE, con riferimenti a NTC2018 e, se serve, EC8);
   - limiti di applicabilità (snellezza, massa, collegamento alla struttura principale).

2) FONTE NORMATIVA
   - cosa deriva direttamente da **NTC2018 §7.2** (o altri paragrafi collegati);
   - dove NTC2018 è generica/qualitativa, indica:
     - quali **Eurocodici** useresti (EC2, EC3, EC8…),
     - a che tipo di formulazione si fa riferimento (resistenza a flessione, taglio, drift ammissibile, ecc.),
     - come dichiarare esplicitamente nel software che quella verifica si basa su ECx + NTC2018.

3) PIANIFICAZIONE DEL MODULO DI CALCOLO
   - progetta, SOLO A PAROLE, un sottopackage del tipo:
     - `codes/ntc2018/secondary_elements/`
   - descrivi:
     - quali tipi/logiche di “VerificationTemplate” servono per ciascun tipo di elemento;
     - quali input minimi saranno richiesti (geometria, fissità, massa, accelerazione sismica, parametri del sito, ecc.);
     - quali output serviranno (esito SLU/SLE, drift, forze di ancoraggio, note normative).

4) INTEGRAZIONE CON LA GUI ESISTENTE
   Analizza le GUI nel repository e:
   - individua quali finestre/dialog devono essere estese o affiancate (es. main_window, selettore norme, finestra combinazioni);
   - pianifica:
     - una GUI per la definizione degli elementi secondari (tipo elemento, schema statico, fissità, input geometrici e materiali);
     - una GUI per la definizione delle azioni (peso proprio, vento, sisma, altre azioni specifiche per elementi secondari);
     - una GUI/report per la visualizzazione dei risultati di verifica, con:
       - richiamo a NTC2018 §7.2,
       - richiamo alle parti degli Eurocodici utilizzate.

5) FILE DI CONFIGURAZIONE, REGISTRO E STORAGE
   - pianifica nuovi file o estensioni di file esistenti (solo come design), ad es.:
     - `config/codes/ntc2018/secondary_elements.jsoncode` per parametri specifici;
     - estensioni a `calculation_codes_loader` per includere template di verifica di elementi secondari;
     - eventuali adattamenti a `historical_materials` e `sections` per supportare questi elementi (solo se necessario).
   - pianifica anche:
     - come archiviare in storage JSON/CSV le istanze di elementi secondari (tipo, parametri, risultati);
     - come mantenere compatibilità con i sistemi storici (RD2229, DM ’92, DM ’96) senza riscriverli.

MODALITÀ DI RISPOSTA (PLAN INCREMENTALE):
- NON voglio codice.
- NON voglio che tu modifichi o riscriva concettualmente RD2229 / DM ’92 / DM ’96.
- Voglio invece:
  1) Una breve sezione iniziale che spiega dove collocheresti il “modulo elementi secondari” all’interno del piano globale già esistente (nuova fase o sotto-fase).
  2) Una lista strutturata di sotto-task, raggruppata in:
     - Analisi normativa (NTC2018 §7.2 + Eurocodici da usare),
     - Sistemi di calcolo per ciascun tipo di elemento secondario,
     - Architettura software (modulo, API, integrazione con CodeModule/VerificationEngine),
     - GUI da creare/integrare,
     - Config/registry/storage.
  3) Una mini-checklist “operativa” (in stile TODO) con i punti chiave per iniziare a lavorare nel codice in una fase successiva (ma senza scriverlo ora).
  4) Eventuali avvertenze/limitazioni (ad es. campi di applicabilità degli schemi semplificati) da tenere presenti nel progetto del modulo.

Ribadisco: resta in modalità di ANALISI & PIANIFICAZIONE, senza produrre codice, ma sfrutta sia:
- il repository locale aperto in VS Code,
- sia le risorse disponibili su Internet (testi NTC2018, parti rilevanti degli Eurocodici, articoli tecnici affidabili),
per proporre un piano robusto e coerente.


Tip: You can undo Copilot's changes to any point by clicking Restore Checkpoint.

AGISCI COME:
- ingegnere strutturista con esperienza in NTC2018 e Eurocodici (EC2, EC3, EC8);
- architetto software Python;
- assistente di pianificazione (PLAN-ONLY), NON generatore di codice.

CONTESTO (REPO LOCALE):
Sto lavorando su un framework di calcolo strutturale in Python con:
- motore di verifica separato dalla GUI (core_calculus, verification_engine, verification_core, methods);
- moduli normativi esistenti (NTC2018, RD2229, DM ’92, DM ’96) integrati tramite loader e file .jsoncode;
- GUI Tkinter per definizione sezioni, materiali e avvio verifiche (es. main_window, frc_verification_window, historical_main_window, ecc.);
- sistemi di storage (JSON/CSV) per sezioni, materiali, historical_materials, calculation_codes.

In precedenti passaggi di pianificazione ho già:
- introdotto il concetto di CodeModule per ciascuna norma;
- pianificato un modulo per NTC2018 (RC + combinazioni + elementi secondari);
- impostato l’idea di avere moduli separati per NTC2018, ma riusando materiali/sezioni esistenti e rispettando la separazione core/GUI.

OBIETTIVO SPECIFICO DI QUESTO PROMPT:
Voglio che tu, come GitHub Copilot Chat in VS Code:

1. Analizzi il **repository locale** (codice, GUI, config, storage) per capire dove e come:
   - integrare un modulo dedicato agli **elementi strutturali secondari**,
   - collegarlo in modo pulito a VerificationEngine, CodeModule NTC2018 e alla GUI.

2. Usi anche il **web** (documentazione online, testi normativi, articoli tecnici) per:
   - individuare riferimenti affidabili al **Capitolo 7.2 delle NTC2018** (“elementi non strutturali/secondari” e simili),
   - identificare le parti in cui NTC2018 NON fornisce formule esplicite,
   - trovare, in questi casi, le **formulazioni pertinenti negli Eurocodici** (es. EC8 per elementi non strutturali, EC2/EC3 per elementi a mensola o travi secondarie).

3. Resti **esclusivamente in modalità PIANIFICAZIONE**:
   - niente codice Python/Tkinter,
   - niente riscritture di file,
   - solo analisi + proposte di struttura, API, file di config, GUI da creare/estendere.

TIPI DI ELEMENTI SECONDARI DA CONSIDERARE:
Analizza e pianifica verifiche e modelli di calcolo per le seguenti categorie di elementi secondari, dove applicabile:

- tramezzi / partizioni non portanti;
- insegne, pannelli, elementi sospesi;
- camini, comignoli, parapetti, elementi fuori piano;
- elementi che operano come mensole (incastro a una estremità);
- elementi incastrati a entrambe le estremità;
- elementi incernierati alle due estremità (travi appoggiate);
- qualsiasi altro elemento secondario citato o implicito nel Cap. 7.2 NTC2018 o nella prassi corrente.

Per ciascuna categoria voglio che tu definisca, a livello di PIANO:

1) SISTEMA DI CALCOLO (MODELLO STRUTTURALE)
   - schema statico (mensola, trave isostatica, trave iperstatica, elemento snello ecc.);
   - azioni rilevanti (peso proprio, carichi variabili, vento, azione sismica, altre);
   - combinazioni di carico tipiche (SLU/SLE, con riferimenti a NTC2018 e, se serve, EC8);
   - limiti di applicabilità (snellezza, massa, collegamento alla struttura principale).

2) FONTE NORMATIVA
   - cosa deriva direttamente da **NTC2018 §7.2** (o altri paragrafi collegati);
   - dove NTC2018 è generica/qualitativa, indica:
     - quali **Eurocodici** useresti (EC2, EC3, EC8…),
     - a che tipo di formulazione si fa riferimento (resistenza a flessione, taglio, drift ammissibile, ecc.),
     - come dichiarare esplicitamente nel software che quella verifica si basa su ECx + NTC2018.

3) PIANIFICAZIONE DEL MODULO DI CALCOLO
   - progetta, SOLO A PAROLE, un sottopackage del tipo:
     - `codes/ntc2018/secondary_elements/`
   - descrivi:
     - quali tipi/logiche di “VerificationTemplate” servono per ciascun tipo di elemento;
     - quali input minimi saranno richiesti (geometria, fissità, massa, accelerazione sismica, parametri del sito, ecc.);
     - quali output serviranno (esito SLU/SLE, drift, forze di ancoraggio, note normative).

4) INTEGRAZIONE CON LA GUI ESISTENTE
   Analizza le GUI nel repository e:
   - individua quali finestre/dialog devono essere estese o affiancate (es. main_window, selettore norme, finestra combinazioni);
   - pianifica:
     - una GUI per la definizione degli elementi secondari (tipo elemento, schema statico, fissità, input geometrici e materiali);
     - una GUI per la definizione delle azioni (peso proprio, vento, sisma, altre azioni specifiche per elementi secondari);
     - una GUI/report per la visualizzazione dei risultati di verifica, con:
       - richiamo a NTC2018 §7.2,
       - richiamo alle parti degli Eurocodici utilizzate.

5) FILE DI CONFIGURAZIONE, REGISTRO E STORAGE
   - pianifica nuovi file o estensioni di file esistenti (solo come design), ad es.:
     - `config/codes/ntc2018/secondary_elements.jsoncode` per parametri specifici;
     - estensioni a `calculation_codes_loader` per includere template di verifica di elementi secondari;
     - eventuali adattamenti a `historical_materials` e `sections` per supportare questi elementi (solo se necessario).
   - pianifica anche:
     - come archiviare in storage JSON/CSV le istanze di elementi secondari (tipo, parametri, risultati);
     - come mantenere compatibilità con i sistemi storici (RD2229, DM ’92, DM ’96) senza riscriverli.

MODALITÀ DI RISPOSTA (PLAN INCREMENTALE):
- NON voglio codice.
- NON voglio che tu modifichi o riscriva concettualmente RD2229 / DM ’92 / DM ’96.
- Voglio invece:
  1) Una breve sezione iniziale che spiega dove collocheresti il “modulo elementi secondari” all’interno del piano globale già esistente (nuova fase o sotto-fase).
  2) Una lista strutturata di sotto-task, raggruppata in:
     - Analisi normativa (NTC2018 §7.2 + Eurocodici da usare),
     - Sistemi di calcolo per ciascun tipo di elemento secondario,
     - Architettura software (modulo, API, integrazione con CodeModule/VerificationEngine),
     - GUI da creare/integrare,
     - Config/registry/storage.
  3) Una mini-checklist “operativa” (in stile TODO) con i punti chiave per iniziare a lavorare nel codice in una fase successiva (ma senza scriverlo ora).
  4) Eventuali avvertenze/limitazioni (ad es. campi di applicabilità degli schemi semplificati) da tenere presenti nel progetto del modulo.

Ribadisco: resta in modalità di ANALISI & PIANIFICAZIONE, senza produrre codice, ma sfrutta sia:
- il repository locale aperto in VS Code,
- sia le risorse disponibili su Internet (testi NTC2018, parti rilevanti degli Eurocodici, articoli tecnici affidabili),
per proporre un piano robusto e coerente.

AGISCI COME:
- ingegnere strutturista esperto NTC2018 §7.2 e EN 1998‑1 (Eurocodice 8),
- architetto software Python,
- assistente di pianificazione (PLAN ONLY).

IMPORTANTE:
Rimani SEMPRE e SOLO in modalità PLAN.
NON generare codice Python.
NON creare file.
NON proporre implementazioni operative.
Fornisci solo: analisi, piano tecnico, task, dipendenze, criteri di validazione.

OBIETTIVO DI QUESTA SESSIONE:
Voglio sviluppare un modulo completo per la verifica degli ELEMENTI NON STRUTTURALI SISMICI secondo NTC 2018 §7.2 con integrazione delle formulazioni mancanti tratte da EUROCODICE 8 (EN 1998‑1).

Il modulo deve:
- definire modelli di calcolo per ogni categoria di elemento non strutturale,
- individuare le parti di NTC2018 applicabili e dove ricorrere all’EC8,
- definire input richiesti (massa, quota, rigidezza, ancoraggi, schema statico),
- definire output (domanda sismica, drift, forze orizzontali, vincoli),
- integrare il tutto in VerificationEngine + CodeModule,
- prevedere GUI dedicate (solo pianificazione),
- definire file di config/registry/storage,
- costruire test di validazione basati su esempi ufficiali o affidabili.

CONTESTO (REPOSITORY):
Lavoro in un framework di calcolo strutturale Python con:
- core_calculus, verification_engine, verification_core,
- file norms .jsoncode (calculation_codes),
- GUI Tkinter (materiali, sezioni, verifiche),
- norme storiche RD2229, DM92, DM96,
- modulo NTC2018 già in sviluppo (RC + secondari).

FONTE NORMATIVA — DA ANALIZZARE (LINK):
Usa queste fonti online per estrarre indicazioni normative e modelli di calcolo applicabili agli elementi non strutturali:

NTC 2018 — Capitolo 7:
- Testo Gazzetta Ufficiale (cap. 7, §7.2 elementi non strutturali):  
  https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=18A0071600100010110001&dgu=2018-02-20&art.dataPubblicazioneGazzetta=2018-02-20&art.codiceRedazionale=18A00716&art.num=1&art.tiposerie=SG  [1](https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=18A0071600100010110001&dgu=2018-02-20&art.dataPubblicazioneGazzetta=2018-02-20&art.codiceRedazionale=18A00716&art.num=1&art.tiposerie=SG)
- Estratto Cap.7 PDF: https://www.studiopetrillo.com/files/ntc2018/cap7.pdf  [2](https://www.studiopetrillo.com/files/ntc2018/cap7.pdf)
- Ulteriore estratto NTC2018 Cap.7: https://www.bertolinoengineering.it/wp-content/uploads/2024/08/NTC2018_cap7.pdf  [3](https://www.bertolinoengineering.it/wp-content/uploads/2024/08/NTC2018_cap7.pdf)

Approfondimenti sugli elementi non strutturali (NTC):
- “Elementi non strutturali in zona sismica, NTC 2008 vs NTC 2018”:  
  https://www.ingenio-web.it/articoli/elementi-costruttivi-non-strutturali-negli-edifici-in-c-a-in-zona-sismica-cosa-cambia-con-le-ntc-2018/  [4](https://www.ingenio-web.it/articoli/elementi-costruttivi-non-strutturali-negli-edifici-in-c-a-in-zona-sismica-cosa-cambia-con-le-ntc-2018/)
- “Verifiche elementi non strutturali – quadro completo”:  
  https://ediltecnico.it/verifiche-elementi-non-strutturali/  [5](https://ediltecnico.it/verifiche-elementi-non-strutturali/)
- “Dettagli tecnici elementi non strutturali (NTC 2018)”:  
  https://www.bmigroup.com/it/intervenire-sul-tetto/progettare-il-tetto/sismico/verifica-vulnerabilita-sismica-ntc/  [6](https://www.bmigroup.com/it/intervenire-sul-tetto/progettare-il-tetto/sismico/verifica-vulnerabilita-sismica-ntc/)

EUROCODICE 8 — ELEMENTI NON STRUTTURALI:
- Testo completo EN 1998‑1 (PDF):  
  https://www.phd.eng.br/wp-content/uploads/2015/02/en.1998.1.2004.pdf  [7](https://www.phd.eng.br/wp-content/uploads/2015/02/en.1998.1.2004.pdf)
- Guida Prota “Seismic forces on non-structural members (EC8 4.3.5)”:  
  https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members  [8](https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members)
- White paper: “Non-Structural Member Forces EC8”:  
  https://protasoftware.com/white-paper/non-structural-member-forces-ec8/  [9](https://protasoftware.com/white-paper/non-structural-member-forces-ec8/)
- JRC Worked Examples – EC8:  
  https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EC8_Seismic_Design_of_Buildings-worked_examples-main_only.pdf  [10](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EC8_Seismic_Design_of_Buildings-Worked_examples-main_only.pdf)

ESEMPI NUMERICI PER TEST DI VALIDAZIONE:
- Verifica tamponature con spettri di piano (NTC2018 + Circ. 2019):  
  https://biblus.acca.it/la-verifica-delle-tamponature-secondo-le-nuove-ntc-2018-e-la-circolare-2019/  [11](https://biblus.acca.it/la-verifica-delle-tamponature-secondo-le-nuove-ntc-2018-e-la-circolare-2019/)
- Esempio EC8 di calcolo forze su elementi non strutturali (Prota):  
  https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members  [8](https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members)
- EC8 worked examples – drift e componenti fragili:  
  https://www.slideshare.net/slideshow/ec8-seismic-designofbuildingsworkedexamples/48158324  [12](https://www.slideshare.net/slideshow/ec8-seismic-designofbuildingsworkedexamples/48158324)

CATEGORIE DI ELEMENTI NON STRUTTURALI DA INCLUDERE:
- tramezzi e tamponature (fragili/semirigide),
- parapetti, comignoli, camini,
- elementi a mensola, insegne, pannelli,
- componenti sospesi,
- elementi incernierati / incastrati,
- elementi non strutturali in facciata,
- apparecchiature, ancoraggi, sistemi di facciata.

CHE COSA VOGLIO DA TE (SOLO PLAN):

1. Analisi normativa:
   - estrai per ciascun tipo di elemento cosa dice NTC §7.2,
   - identifica lacune normative e quando usare EC8 (con riferimento a §4.3.5, drift limits ecc.).

2. Modelli strutturali da implementare:
   - mensola,
   - trave incastrata‑incastrata,
   - trave appoggiata,
   - pannello verticale,
   - sistemi sospesi,
   - elementi fuori piano.

3. Input/Output del modulo:
   - dati geometrici, massa, quota z, rigidezza,
   - spettri di piano / accelerazioni locali,
   - domanda sismica (forza Fp o drift),
   - verifiche di sicurezza e ancoraggi.

4. Integrazione software:
   - come collegare il modulo a CodeModule NTC2018,
   - come estendere l’engine senza rompere RD2229/DM92/DM96,
   - come organizzare templates di calcolo e config .jsoncode.

5. GUI:
   - piani le nuove finestre/dialog,
   - campi input essenziali,
   - visualizzazione risultati + note normative NTC/EC8.

6. Storage/Registry:
   - struttura dei file da integrare (solo pianificazione),
   - schema per salvare elementi non strutturali.

7. Test di validazione:
   - definisci una lista strutturata di test case basati sui link forniti (es. drift tamponature, forza Fp su insegna, parapetto in sommità),
   - per ogni test indica: input reali da estrarre, output atteso, riferimento alla fonte.

FORMATO DI RISPOSTA
- Non riscrivere il codice.
- Produci un output ordinato in sezioni:
  1) architettura modulo,
  2) analisi normativa,
  3) sistemi di calcolo per elemento,
  4) integrazione engine,
  5) pianificazione GUI,
  6) storage/config,
  7) test plan,
  8) checklist conclusiva.

Rimani SEMPRE in modalità PLAN.

AGISCI COME:
- ingegnere strutturista con esperienza in NTC2018 e Eurocodici (EC2, EC3, EC8);
- architetto software Python;
- assistente di pianificazione (PLAN ONLY), NON generatore di codice.

IMPORTANTE:
Rimani SEMPRE e SOLO in modalità PLAN.
NON generare codice Python.
NON creare file.
NON proporre implementazioni operative.
Fornisci solo: analisi, piano tecnico, task, dipendenze, criteri di validazione.

CONTESTO (REPO LOCALE / FRAMEWORK):
Sto lavorando su un framework di calcolo strutturale in Python con:
- motore di verifica separato dalla GUI (core_calculus, verification_engine, verification_core, methods);
- moduli normativi esistenti (NTC2018, RD2229, DM ’92, DM ’96) integrati tramite loader e file .jsoncode;
- GUI Tkinter per definizione sezioni, materiali e avvio verifiche (es. main_window, frc_verification_window, historical_main_window, ecc.);
- sistemi di storage (JSON/CSV) per sezioni, materiali, historical_materials, calculation_codes.

In precedenti passaggi di pianificazione ho già:
- introdotto il concetto di CodeModule per ciascuna norma;
- pianificato un modulo per NTC2018 (RC + combinazioni + elementi secondari);
- impostato l’idea di avere moduli separati per NTC2018, riusando materiali/sezioni esistenti e rispettando la separazione core/GUI.

OBIETTIVO DI QUESTA SESSIONE:
Voglio sviluppare un modulo completo per la verifica degli ELEMENTI NON STRUTTURALI / SECONDARI in zona sismica secondo NTC 2018 §7.2, con integrazione delle formulazioni mancanti tratte da EUROCODICE 8 (EN 1998‑1).

Il modulo deve:
- definire modelli di calcolo per ogni categoria di elemento non strutturale;
- individuare le parti di NTC2018 applicabili e dove ricorrere a EC8;
- definire input richiesti (massa, quota, rigidezza, ancoraggi, schema statico);
- definire output (domanda sismica, drift, forze orizzontali, vincoli);
- integrare il tutto in VerificationEngine + CodeModule NTC2018;
- prevedere GUI dedicate (solo pianificazione, nessun codice);
- definire file di config/registry/storage;
- costruire test di validazione basati su esempi ufficiali o affidabili.

FONTE NORMATIVA — LINK DA ANALIZZARE:

NTC 2018 — Capitolo 7 (azioni sismiche, §7.2 elementi non strutturali/secondari):
- Testo Gazzetta Ufficiale (cap. 7, §7.2):
  https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=18A0071600100010110001&dgu=2018-02-20&art.dataPubblicazioneGazzetta=2018-02-20&art.codiceRedazionale=18A00716&art.num=1&art.tiposerie=SG
- Estratto Cap.7 PDF (Studio Petrillo):
  https://www.studiopetrillo.com/files/ntc2018/cap7.pdf
- Ulteriore estratto NTC2018 Cap.7 (Bertolino Engineering):
  https://www.bertolinoengineering.it/wp-content/uploads/2024/08/NTC2018_cap7.pdf

Approfondimenti NTC su elementi non strutturali:
- “Elementi non strutturali in zona sismica, NTC 2008 vs NTC 2018”:
  https://www.ingenio-web.it/articoli/elementi-costruttivi-non-strutturali-negli-edifici-in-c-a-in-zona-sismica-cosa-cambia-con-le-ntc-2018/
- “Verifiche elementi non strutturali – quadro completo”:
  https://ediltecnico.it/verifiche-elementi-non-strutturali/
- “Dettagli tecnici elementi non strutturali (NTC 2018)”:
  https://www.bmigroup.com/it/intervenire-sul-tetto/progettare-il-tetto/sismico/verifica-vulnerabilita-sismica-ntc/

EUROCODICE 8 — ELEMENTI NON STRUTTURALI:
- Testo completo EN 1998‑1 (PDF):
  https://www.phd.eng.br/wp-content/uploads/2015/02/en.1998.1.2004.pdf
- Guida Prota “Seismic forces on non-structural members (EC8 4.3.5)”:
  https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members
- White paper: “Non-Structural Member Forces EC8”:
  https://protasoftware.com/white-paper/non-structural-member-forces-ec8/
- JRC Worked Examples – EC8 (drift, spostamenti, componenti non strutturali fragili):
  https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EC8_Seismic_Design_of_Buildings-worked_examples-main_only.pdf

ESEMPI NUMERICI PER TEST DI VALIDAZIONE:
- Verifica tamponature con spettri di piano (NTC2018 + Circolare 2019):
  https://biblus.acca.it/la-verifica-delle-tamponature-secondo-le-nuove-ntc-2018-e-la-circolare-2019/
- Esempio EC8 di calcolo forze su elementi non strutturali (Prota):
  https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members
- EC8 worked examples – drift e componenti fragili (slide):
  https://www.slideshare.net/slideshow/ec8-seismic-designofbuildingsworkedexamples/48158324

CATEGORIE DI ELEMENTI NON STRUTTURALI / SECONDARI DA CONSIDERARE:
- tramezzi / tamponature (fragili o semirigide);
- parapetti, camini, comignoli, elementi fuori piano;
- elementi a mensola (insegne, pannelli, parapetti a sbalzo);
- componenti sospesi;
- elementi incastrati a entrambe le estremità;
- elementi incernierati alle due estremità (travi appoggiate);
- elementi non strutturali in facciata;
- apparecchiature, sistemi di facciata, ancoraggi.

CHE COSA VOGLIO DA TE (SOLO PIANIFICAZIONE):

1) Analisi normativa
   - per ogni tipo di elemento:
     - estrai cosa dice NTC2018 §7.2 (e paragrafi collegati);
     - individua le lacune (assenza di formule, prescrizioni qualitative);
     - indica quando e come ricorrere a EN 1998‑1 (es. §4.3.5 forze sui componenti, limiti di drift).
   - specifica quali parti del modulo saranno “NTC-based” e quali “EC8-based”, esplicitando i riferimenti.

2) Sistemi di calcolo (modelli strutturali)
   Per ciascuna categoria di elemento (tramezzi, parapetti, mensole, sospesi, ecc.):
   - definisci lo schema statico (mensola, trave appoggiata, incastro-incastro, pannello, sistema sospeso);
   - individua le azioni rilevanti (peso proprio, sovraccarico, vento, azione sismica, altre);
   - specifica le combinazioni SLU/SLE importanti (NTC2018 + EC8 se necessario);
   - definisci limiti di applicabilità (snellezza, altezza, massa, collegamento alla struttura principale).

3) Pianificazione del modulo di calcolo
   - progetta SOLO A PAROLE un sottopackage del tipo:
     - `codes/ntc2018/secondary_elements/`
   - descrivi:
     - quali tipi/logiche di “VerificationTemplate” servono per ciascun tipo di elemento;
     - input minimi richiesti (geometria, fissità, massa, quota z, accelerazione sismica, parametri sito, tipo di collegamento);
     - output necessari (esito SLU/SLE, drift, forze di ancoraggio, eventuali warning su campo di applicabilità).

4) Integrazione con VerificationEngine e CodeModule
   - spiega come collegare il modulo “secondary_elements” al CodeModule NTC2018:
     - nuove voci in available_checks();
     - nuove tipologie di CalculationTemplate.
   - indica come estendere l’engine:
     - senza rompere RD2229 / DM ’92 / DM ’96;
     - usando un registry/modello unificato per le norme.

5) GUI (Tkinter) – solo design, nessun codice
   - individua quali GUI esistenti devono essere estese (main_window, selettore norme, pannello combinazioni, ecc.);
   - pianifica:
     - una GUI per definire gli elementi non strutturali/secondari (tipo elemento, schema statico, fissità, parametri principali);
     - una GUI per le azioni (peso proprio, vento, sisma, altre azioni specifiche);
     - una GUI/report per la visualizzazione dei risultati con:
       - indicazione NTC2018 §7.2;
       - indicazione delle parti EC8 utilizzate.

6) Config / Registry / Storage
   - definisci la struttura (solo concettuale) di nuovi file o estensioni, ad es.:
     - `config/codes/ntc2018/secondary_elements.jsoncode`;
   - pianifica:
     - come estendere calculation_codes_loader per includere i template degli elementi non strutturali;
     - se e come adattare historical_materials/sections per supportare questi elementi;
     - come archiviare in JSON/CSV:
       - tipo elemento,
       - parametri geometrici,
       - parametri normativi,
       - risultati di verifica.

7) Test di validazione (da esempi reali)
   - definisci una lista di test case da implementare in seguito, basati sui link forniti:
     - es. drift tamponature secondo NTC2018 + Circ. 2019 e esempi EC8;
     - es. forza Fp su insegna/pannello esterno secondo EC8 4.3.5;
     - es. parapetto/camino in sommità soggetto a sisma.
   - per ogni test case:
     - indica quali input vanno estratti dai documenti (geometria, massa, z/H, parametri sismici);
     - indica quale output atteso confrontare (forza, drift, esito OK/KO).

MODALITÀ DI RISPOSTA:
- NON riscrivere o proporre codice.
- NON modificare concettualmente RD2229 / DM ’92 / DM ’96 (puoi solo pianificare l’integrazione).
- Produci un output ordinato in sezioni:
  1) Architettura modulo;
  2) Analisi normativa;
  3) Sistemi di calcolo per elemento;
  4) Integrazione con engine e CodeModule;
  5) Pianificazione GUI;
  6) Storage / Config / Registry;
  7) Piano dei test di validazione;
  8) Checklist conclusiva (TODO sintetico).

Rimani SEMPRE in modalità PLAN (analisi + pianificazione), senza generare codice.

PROMPT INCREMENTALE DI APPROFONDIMENTO (PLAN-ONLY)

AGGIUNTA AI REQUISITI:  
Oltre a quanto già richiesto, voglio che tu, Copilot, sviluppi una comprensione teorica e strutturale più profonda delle necessità del modulo NTC 7.2 + EC8, affinché la pianificazione sia realmente completa e organica.

1) TEORIA DI BASE (DA ANALIZZARE E ASSUMERE NEL PIANO)
Integra nella pianificazione i principi fondamentali di:
- risposta degli elementi non strutturali alla domanda sismica (massa, quota, amplificazione locale);
- verifica tramite spettri di piano secondo NTC2018 + Circolare e EC8;
- criteri di danno, drift ammissibile, stato limite di sicurezza e funzionalità;
- gerarchia tra struttura portante ed elementi non strutturali;
- modelli base dell’ingegneria sismica per mensole, appendici, parapetti, tamponature, elementi sospesi.

Assicurati che la pianificazione software tenga conto di queste basi concettuali in modo coerente con:
NTC 2018 (Capitolo 7.2)  
https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=18A0071600100010110001&dgu=2018-02-20&art.dataPubblicazioneGazzetta=2018-02-20&art.codiceRedazionale=18A00716&art.num=1&art.tiposerie=SG

EC8 (EN 1998-1, forze su componenti non strutturali, §4.3.5 e drift)  
https://www.phd.eng.br/wp-content/uploads/2015/02/en.1998.1.2004.pdf

Esempi applicativi EC8:  
https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members  
https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EC8_Seismic_Design_of_Buildings-worked_examples-main_only.pdf

2) SISTEMA DI INPUT COMUNE — FATTORI CHIAVE
Nel piano devi definire un **sistema unificato di input**, condiviso da tutti i moduli (NTC2018, RC, elementi secondari, elementi non strutturali, DM ’92, DM ’96).  
Questo sistema deve includere:

- parametri geometrici standardizzati (base, altezza, profondità, spessore, area d’influenza);
- parametri meccanici/materiali unificati (provenienti da historical_materials o NTC2018 matériaux);
- parametri sismici comuni (accelerazioni di piano, spettro del sito, categoria suolo);
- parametri di vincolo/fissità scelti da un insieme coerente;
- metadati normativi condivisi (norma, categoria elemento, stato limite);
- parametri di massa, posizione (quota z), rigidezza, comportamento fuori piano.

Richiedo che il piano illustri come:
- questi input vengono centralizzati,
- come alimentano TUTTI i moduli,
- come evitare duplicazioni,
- come condividere i dati tra GUI diverse e tra moduli diversi.

3) SISTEMA DI OUTPUT COMUNE
Definisci in pianificazione un sistema unico di output per TUTTE le verifiche, con:
- esito (OK/KO),
- margine di sicurezza,
- combinazione critica,
- parametri di domanda e capacità,
- riferimento normativo (NTC2018, EC8, DM, ecc.),
- eventuali warning su condizioni di applicabilità.

4) GUI INTERCONNESSE
Nel piano stabilisci che tutte le GUI devono:
- utilizzare lo stesso sistema di input centralizzato (nessun duplicato per sezioni, materiali, azioni sismiche);
- condividere archivi comuni (materials.json, sections.json, calculation_codes);
- usare la stessa logica di validazione (input obbligatori, warning normativi);
- rispettare la modularità: ogni nuovo modulo (secondari, non strutturali, RC, geotecnica) deve estendere ma NON duplicare i widget e le finestre esistenti;
- prevedere un sistema di navigazione coerente (selettore norma → selettore modulo → definizione elementi → lanci verifica).

Chiedo inoltre che tu pianifichi:
- quali GUI devono essere “centralizzate” (es. editor materiali, editor sezioni),
- quali GUI vanno estese (pannello combinazioni),
- quali GUI devono essere nuove ma basate su pattern esistenti.

5) MODULARITÀ ESTREMA + RIUTILIZZO
Nel piano devi esplicitare:
- la struttura modulare ideale (es. codes/ntc2018/secondary_elements, codes/ntc2018/nonstructural, ecc.);
- come i template di calcolo e i registry si integrano in modo plug‑in;
- come mantenere retro‑compatibilità con DM92, DM96, RD2229 senza duplicare logiche;
- come i nuovi moduli erediteranno input e output standard senza customizzazioni ridondanti.

6) ARCHIVI E STORAGE COMUNI
Richiedo di pianificare:
- un archivio unificato per definire elementi (anche secondari e non strutturali), con un unico schema dati;
- un sistema di serializzazione coerente (JSON/CSV),
- mapping stabile tra GUI → input comune → engine → output comune → storage.

7) COSTRUZIONE DELLA TEORIA “SOFTWARE-READY”
Voglio che tu espliciti, nella pianificazione:
- quali blocchi teorici sono necessari per ricostruire gli algoritmi (non il codice!),
- quali parametri devono essere esplicitamente richiesti dall’utente,
- quali parametri devono essere inferiti dall’engine,
- quali limiti normativi devono essere controllati all’ingresso (campo di validità delle formule NTC/EC8),
- quali vincoli devono essere verificati prima del calcolo (massa minima, spessore minimo, tipo di ancoraggio, regole di drift).

8) RISULTATO ATTESO
Come output di questo prompt incrementale, voglio che tu produca:
- un approfondimento del piano esistente,
- una sezione dedicata alla teoria e agli input comuni,
- un elenco di adattamenti necessari per rendere le GUI integrate e riutilizzabili,
- linee guida progettuali per modularità, componentizzazione e riuso,
- una mini‑checklist per il “core input framework” comune a tutti i moduli.

Ribadisco: SOLO pianificazione, nessun codice, nessun file.

Sintesi esecutiva
Posizionamento: integrare il modulo NTC §7.2 + EC8 (non‑strutturali/secondari) come componente di Fase 6bis (dipende da Fase 1/2/3/5).
Obiettivo tecnico: fornire spec, API e file di configurazione per calcolare Fa/Ta, valutare SLU/SLE/SLV per non‑structural/secondary elements e integrare i risultati nel VerificationEngine usando CodeModule (documentato e testato).
Questo documento è esclusivamente PLAN — nessun codice, solo specifiche, input/output, GUI, storage, test e criteri di accettazione.
1) Teoria di base — principi da codificare nel progetto
Risposta sismica: la domanda su un elemento non‑strutturale è funzione primaria di massa (Wa), quota z (amplificazione), periodo proprio Ta e spettro di piano Se(Ta,z).
Formula operativa (policy): Fa ≈ Sa(Ta,z) * Wa / qa — Sa ricavato da spettro di piano (NTC circolare §C7.2 / EC8 §4.3.5). qa e γa da tabelle normative.
Periodo equivalente Ta: stimatore semplificato (mensola, pannello, trave) oppure input opzionale; Ta influisce fortemente su Sa.
Stato limite e danno:
SLV → verifica stabilità/espulsione (Fa vs resistenza di ancoraggio/azione di ribaltamento).
SLE/SLD → deformazioni, apertura fessure, perdita di servizio.
Gerarchia: struttura portante definisce azioni di input (spettri/modi); se l’elemento influenza la risposta globale → escalation a modello globale.
Modelli statici base da implementare concettualmente: cantilever (mensola), trave appoggiata, trave continua, pannello (fuori‑piano), corpo sospeso/appendice, elemento slen­der (chimney/parapet).
Regola progettuale: applicare NTC dove prescrittivo; usare EC8 (EN1998‑1 §4.3.5) per formule esplicite e dettaglio (documentare sempre la fonte).
2) Sistema di INPUT comune (standardizzato)
Campi geometrici standard: id, type, length L, height h, depth d, thickness s, area A, projected area Ap.
Campi meccanici/materiali: material_id, density ρ, E (opz.), fk/fck o f_masonry (se presente), damping ξ (default).
Parametri sismici: site_ag, soil_category (S), topographic_factor, building_T1, building_H, z (elevazione), Sa_spetro locale, Ta (opz.).
Vincoli / ancoraggi: support_type (incastro, appoggio, suspension), anchor_type, anchor_capacity_ref.
Metadati normativi: norm_code (e.g. NTC2018), fallback_norm (e.g. EC8), importance γa, behavior qa, class_of_use.
Parametri operativi: influence_on_global_model (bool), library_preset, notes.
Centralizzazione e condivisione:
Un unico SecondaryElementSpec JSON nel progetto (salvato in project.secondary_elements[]).
GUI legge/scrive tramite lo stesso schema; VerificationEngine consuma lo stesso oggetto senza mappature locali.
Evitare duplicazione definendo i campi canonici in schemas.py (SecondaryElementSpec) e in config/codes/ntc2018/secondary_elements.jsoncode (defaults/presets).
Validazione input (prima dell’esecuzione): range check (Wa>0, 0<z<H), mandatory fields, applicability flags (se influenza la global‑model → warn/escalate).
3) Sistema di OUTPUT comune (standardizzato)
Oggetto risultato (unico schema per tutte le verifiche):
check_id, element_id, esito {OK | NOT_OK | NOT_APPLICABLE}, utilisation (demand/capacity), critical_combination_id, demand_parameters (Fa, M, V, Ta), capacity_parameters (anchorage_capacity, MRd, VRd), norm_references (list), messages (warnings/errors), metadata (timestamp, solver_version).
Requisiti:
ogni SingleCheckResult deve includere riferimento normativo (es. NTC2018 §7.3.6.2, EN1998‑1 §4.3.5) e codice di fallback se EC8 utilizzato.
formato JSON lineare per aggregazione e storage (project.secondary_elements[].results).
4) Architettura software — package & API (design)
Package (plan): src/codes/ntc2018/secondary_elements/
files concettuali: specs.md, templates.py (identificatori), registry.json (presets), checks/ (per category), docs.
API CodeModule estese (design only):
available_secondary_checks() -> list[str]
run_secondary_check(check_id, SecondaryElementSpec, CalcContext) -> SingleCheckResult
estimate_secondary_Ta(spec) -> float
Engine orchestration (flow):
GUI → crea SecondaryElementSpec → salva in project → VerificationEngine.perform_secondary_checks(project, selected_ids) → per ogni spec chiama CodeModule.run_secondary_check → result inserito in VerificationResult.secondary.
Config loader:
estendere calculation_codes_loader.py per leggere secondary_elements node (qa tables, presets).
Backward compatibility:
mantenere RD2229/DM loaders inalterati; esporre i checks storici attraverso lo stesso CodeModule registry (shim).
5) Sistemi di calcolo per ciascun tipo — (concetti e IO richiesti)
Per ogni categoria: modello statico, input minimi, output chiave, norma di riferimento.

Tamponature / tramezzi
Modello: pannello verticale; Ta ~ function(h, s, E, A); Sa(Ta,z) → Fa distribuito o concentrato.
Input: L, h, s, E (o fk), mass Wa, z, boundary (appoggiata/incastro).
Output: Fa, M_out_of_plane, MRd, verification SLV/SLD/SLE.
Fonte: NTC2018 §7.2 + Circolare (spettri di piano); per dettagli EC8.
Insegne / pannelli sospesi
Modello: cantilever / suspended mass; considerare wind + Fa (sisma).
Input: projection area, anchor positions, Wa, z, anchor_type.
Output: anchorage shear/moment demand, overturning moments, OK/NOT_OK.
Fonte: EC8 §4.3.5 (Fa), EN anchors standards for capacity.
Camini / parapetti
Modello: slender cantilever (buckling/overturning).
Input: H, cross-section, mass distribution, Wind coeff.
Output: stability check, overturning moment, buckling index, SLV pass/fail.
Fonte: NTC qualitative + EC8/EC2 for slenderness.
Mensole (cantilever)
Modello: beam cantilever; compute Mmax, V, anchorage forces.
Input: L, load distribution, anchor geometry, material.
Output: M/Rd, shear/anchorage demand, SLE deflection.
Fonte: EC2/EC3 for material capacities, EC8 for seismic action.
Travi incastrate/incernierate
Modello: continuous / simply supported; standard beam checks.
Input: span, loads, fixity, section ref.
Output: MEd/MRd, VEd/VRd, deflection, code refs.
Elementi sospesi (equipment)
Model: point mass tied to support; dynamic amplification via Ta; potential impact on building.
Input: mount type, Wa, eccentricity, damping.
Output: Fa, anchorage demand, special classification (γa).
6) GUI: quali schermate centralizzare ed estendere
Centralizzare (riuso obbligatorio)
Editor materiali (frc_manager.py / historical_material_window) → aggiungere voci per materiale secondari (massa, E, fk).
Editor sezioni → estendere per component geometry presets (pannello, parapetto).
Pannello combinazioni → aggiungere opzione “Generate combinations for secondary elements (NTC/EC8)”.
Nuove/Estese GUI
SecondaryElementEditor (nuovo Toplevel, riusa pattern frc_manager): input canonici + presets.
SecondaryResultsPanel (estende VerificationResult view): normativa + dettaglio domanda/capacità.
Project Manager (estende) → lista secondary_elements[], import/export preset.
UX rules
Validazione unica (shared validator utility in core/validation.py)
Single source of truth: inputs salvati in project JSON; GUI sincronizza su save/load.
7) Storage / registry / config (schemi plan)
New config node: config/codes/ntc2018/secondary_elements.jsoncode
contiene qa_table, presets, Ta_estimators, default_damping.
Project storage:
project.json add secondary_elements: [ SecondaryElementSpec + results ].
Registry:
registry/secondary_presets.json per libreria elementi.
Serialization:
JSON canonical schema; CSV export supported for list summary.
Backward compatibility:
Unknown keys tolerated by old loaders; new loader reads secondary_elements if present.
8) Test & validazione (estratto operativo)
Unit tests:
Ta estimator, Sa(Ta,z) approximation, Fa computation, applicability gating, anchorage demand.
Integration tests:
end‑to‑end: GUI → project save → VerificationEngine.run_secondary_checks → result saved.
Golden cases (sources):
Tamponature (BibLus / NTC Circolare) — verify Fa, MRd (example numeric).
EC8 worked example (JRC / Prota) — verify Fa and Sa(Ta).
Signage cantilever (anchor demand) — compare to EC anchor guidance.
Acceptance:
All golden examples within documented tolerance; NOT_APPLICABLE cases return informative messages.
9) “Software‑ready” — blocchi teorici da includere nel design
Period estimator (Ta) per: plate/panel, cantilever, simply supported beam.
Spettro di piano locale Se(Ta,z): via modal contribution (SRSS) o semplificata (C7.2.3).
Fa computation: Fa = Sa(Ta,z) * Wa / qa (with γa handling).
Applicability guardrail: geometric limits, ρ_l ranges, anchor presence, influence_on_global_model rule.
Anchorage demand calculator: shear & moment envelopes at anchor positions.
SLE indicators: crack width estimator, drift fraction, deflection limits.
Decision flow: APPLY_NTC? → ELSE APPLY_EC8 → ELSE NOT_APPLICABLE/WARNING.
10) Checklist sintetica per avvio (operativa)
 Definire SecondaryElementSpec schema e VerificationTemplate IDs
 Aggiungere secondary_elements skeleton in config/codes/ntc2018.jsoncode
 Redigere docs/NTC2018_secondary_elements.md (norme + fallback EC8)
 Wireframe SecondaryElementEditor + SecondaryResultsPanel
 Implementare test fixtures per 3 golden examples (BibLus, EC8 worked example, signage)
 Documentare CodeModule API extension (design only)
 Progettare storage schema e presets registry
Avvertenze, limiti e rischi
Modelli semplificati sono validi solo quando influence_on_global_model == false; in caso contrario richiedere analisi globale.
Quando la norma è evasiva, usare EC8 ma sempre documentare la scelta e la versione della norma.
Accuratezza ancoraggi: attenzione — il core fornisce domanda, la verifica di capacità può richiedere dati produttore/standard di ancoraggio.
Se vuoi, formalizzo subito (PLAN‑ONLY):

A) lo SPEC del SecondaryElementSpec (campo‑by‑campo + validazioni), oppure
B) il SPEC per RC_SLU_SecondaryElement (input/output dettagliati + codici di esito e messaggi normativi).
Scegli A o B per il prossimo deliverable di pianificazione.

PROMPT INCREMENTALE – SPEC SecondaryElementSpec (SOLO PLAN, NESSUN CODICE)

CONTESTO:
Hai già prodotto un piano per il modulo NTC2018 §7.2 + EC8 relativo agli elementi non strutturali/secondari, con:
- modelli di calcolo per tramezzi, tamponature, parapetti, mensole, insegne, elementi sospesi, ecc.;
- integrazione con VerificationEngine e CodeModule NTC2018;
- GUI dedicate e storage JSON/CSV;
- uso combinato NTC2018 + EC8 (formule e limiti).

ORA voglio che ti concentri ESCLUSIVAMENTE su:
👉 definire in modo formale e dettagliato lo SPEC di un oggetto di input comune chiamato **SecondaryElementSpec**, che rappresenta un ELEMENTO NON STRUTTURALE/SECONDARIO nel software.

IMPORTANTE:
- Rimani SEMPRE in modalità PLAN.
- NON generare codice (nessuna classe Python, nessuno snippet Tkinter, nessun JSON effettivo).
- Lavora solo a livello di **specifica**: nomi di campi, tipi, unità di misura, vincoli, mapping verso GUI/Engine/Storage.

OBIETTIVO DEL PROMPT:
Costruire una specifica completa di **SecondaryElementSpec** che:
- sia sufficiente a descrivere tutti i tipi di elementi non strutturali/secondari previsti dal piano (tamponature, parapetti, insegne, mensole, elementi sospesi, ecc.);
- sia riutilizzabile da TUTTI i moduli normativi (NTC2018, EC8, eventualmente DM/RD);
- sia compatibile con:
  - GUI Tkinter esistenti (editor materiali, sezioni, combinazioni),
  - VerificationEngine,
  - CodeModule NTC2018,
  - storage JSON/CSV del progetto.

CHE COSA VOGLIO IN DETTAGLIO:

1) STRUTTURA DI SecondaryElementSpec (campo per campo)
   - Fornisci una tabella o elenco strutturato con, per ogni campo:
     - nome del campo (es. id, element_type, length, height, thickness, z, mass, material_id, ecc.);
     - tipo logico (string, float, enum, bool, lista, ecc.);
     - unità di misura (m, kN, kN/m², kg, ecc.);
     - se è OBBLIGATORIO o OPZIONALE;
     - default (se applicabile);
     - breve descrizione ingegneristica (cosa rappresenta, come si usa);
     - eventuale riferimento normativo (NTC2018/EC8) se il campo è richiesto dalla norma (es. quota z, massa Wa, parametri sismici locali);
     - dipendenze (es. “se element_type = tamponatura, questo campo è obbligatorio”, ecc.).

   In particolare, voglio che la specifica includa gruppi di campi per:
   - Geometria: L, h, s, profondità, area proiettata Ap, area effettiva, ecc.;
   - Materiale: material_id, densità, modulo elastico (se necessario), fk/fck/fm, tipo di materiale;
   - Massa e carichi applicati: massa equivalente Wa, eventuali carichi addizionali;
   - Parametri sismici di riferimento: quota z, H edificio, ag, categoria suolo, Sa di piano (se già noto o calcolabile), Ta opzionale;
   - Vincoli/ancoraggi: schema di vincolo (incastro, appoggio, sospeso), tipo di ancoraggio, riferimento a capacità di ancoraggio;
   - Metadati normativi: norma primaria (NTC2018), norma di supporto (EC8), γa, qa, classe d’uso, influenza sulla risposta globale;
   - Flag operativi: influisce sul modello globale S/N, preset di libreria, note, tag categoria.

2) REGOLA DI VALIDAZIONE E CAMPO DI APPLICABILITÀ
   - Per ciascun blocco di campi definisci:
     - vincoli min/max (es. h > 0, 0 < z ≤ H, Wa > 0, ecc.);
     - combinazioni di campi obbligatorie (es. “se element_type = pannello, serve spessore s e altezza h”);
     - controlli sul campo di applicabilità delle formule NTC/EC8 (es. elementi troppo flessibili, massa molto elevata, z/H fuori range, ecc.).
   - Descrivi a livello concettuale una funzione di validazione:
     - quali errori/warning potrebbe generare,
     - cosa blocca il calcolo,
     - cosa genera solo un warning.

3) RELAZIONE CON ALTRI OGGETTI (materiali, sezioni, combinazioni)
   - Spiega come i campi di SecondaryElementSpec:
     - si collegano alle definizioni di materiali esistenti (via material_id, historical_materials, NTC materials);
     - si collegano a sezioni geometriche (es. se un elemento secondario usa una sezione tipo “pannello 20cm” definita altrove);
     - si integrano con il sistema combinazioni (SLU/SLE) e spettri di piano.
   - Indica esplicitamente quali campi della spec sono “chiavi esterne” verso repository/GUI esistenti.

4) MAPPING VERSO GUI
   - Indica come SecondaryElementSpec dovrebbe riflettersi nelle GUI:
     - quali campi vanno in un editor “generale” (nome elemento, tipo, materiale, geometria base);
     - quali campi in pannelli “avanzati” (parametri normativi, override di qa/γa, ecc.);
     - quali campi possono essere inferiti o precompilati da preset.
   - Proponi, a livello di design, un layout logico (sezioni del form) ma SENZA codice o widget specifici.

5) MAPPING VERSO STORAGE
   - Descrivi:
     - come SecondaryElementSpec dovrebbe essere serializzato in JSON (struttura concettuale, non il file vero);
     - dove andrebbe salvato (es. `project.secondary_elements[]`);
     - come gestire versioning / compatibilità futura (es. presence di field “schema_version”).

6) INTEGRAZIONE CON VerificationEngine / CodeModule
   - Spiega:
     - come SecondaryElementSpec verrà passato a CodeModule NTC2018/EC8 per le verifiche;
     - come può essere riusato da più verifiche (SLU, SLV, SLE) senza modifiche;
     - quali campi sono sempre letti da ogni check e quali sono usati solo da certi modelli (es. pannello vs elemento sospeso).

7) CHECKLIST FINALE
   - Concludi con una checklist sintetica (TODO) tipo:
     - “Definiti tutti i campi di SecondaryElementSpec (nome, tipo, unità, obbligatorietà)”
     - “Definiti i gruppi di campi per geometria/materiali/sisma/vincoli/metadati”
     - “Definite le regole di validazione e campo di applicabilità”
     - “Definito il mapping concettuale verso GUI e storage”
     - “Definita l’interfaccia d’uso con VerificationEngine/CodeModule”

Ribadisco: nessun codice, solo SPEC dettagliato, orientato alla futura implementazione.

PROMPT INCREMENTALE – SPEC Check “NS_SLV_SecondaryElement” (SOLO PLAN, NESSUN CODICE)

CONTESTO:
Hai già:
- un piano per il modulo NTC2018 §7.2 + EC8 per elementi non strutturali/secondari;
- definito (nel prompt precedente) lo SPEC di SecondaryElementSpec, schema di input comune per tutti gli elementi secondari;
- definito un SingleCheckResult/VerificationResult concettuale.

ORA voglio che tu definisca, in modalità PLAN, lo SPEC di UNA verifica specifica:

👉 Check name (di esempio): **NS_SLV_SecondaryElement**  
   Scopo: verificare la sicurezza sismica allo SLV di un elemento non strutturale/secondario (stabilità, espulsione, ancoraggio) utilizzando la domanda Fa derivata da NTC §7.2 + EC8 (EN 1998‑1, §4.3.5 e simili).

IMPORTANTE:
- SOLO pianificazione, nessun codice.
- Niente classi Python, niente funzioni; solo specifiche di:
  - scopo,
  - input,
  - passaggi logici concettuali,
  - output,
  - integrazione con Engine/CodeModule,
  - test da prevedere.

CHE COSA VOGLIO IN DETTAGLIO:

1) IDENTITÀ DEL CHECK
   - Nome simbolico del check (es. `NS_SLV_SecondaryElement`).
   - Descrizione testuale: cosa verifica, in che condizioni si applica (tipi di elementi: tamponature, parapetti, insegne, elementi sospesi, ecc.).
   - Elenco degli stati limite coperti (principalmente SLV; eventuali riferimenti a SLE/SLD se rilevanti).
   - Riferimenti normativi:
     - paragrafi NTC2018 §7.2/§7.3/§7.3.6;
     - clausole EC8 pertinenti (es. EN 1998‑1 §4.3.5 per le forze sui componenti, limiti di drift da tabelle EC8).

2) INPUT DEL CHECK
   - Elenca in modo esplicito:
     - quali campi di SecondaryElementSpec sono necessari (es. mass Wa, z, H, tipo elemento, geometria base, tipo ancoraggio, ⋯);
     - quali parametri aggiuntivi tramite CalcContext/Scenario (es. spettro di piano, combinazione sismica, ag, fattori di comportamento, parametri di piano).
   - Per ogni input:
     - specifica se OBBLIGATORIO o OPZIONALE,
     - come viene usato concettualmente nel calcolo (es. quota z setta il fattore di amplificazione, Wa entra nella formula di Fa, ecc.),
     - eventuali controlli preliminari (range, coerenza).

3) LOGICA DI CALCOLO (CONCETTUALE, NON CODICE)
   - Descrivi i passaggi logici, in forma di “flow” o pseudocodice concettuale, SENZA formule dettagliate, ma:
     - Calcolo del periodo equivalente Ta (da SecondaryElementSpec o da modello semplificato);
     - Individuazione di Sa(Ta,z) da spettro di piano (NTC/EC8);
     - Calcolo della domanda di forza Fa (o forza equivalente in testa/piede);
     - Determinazione di effetti (momenti/tagli/sollecitazioni su ancoraggi o sezione);
     - Confronto con capacità (es. capacità di ancoraggio, resistenza di sezione, stabilità al ribaltamento);
     - Determinazione dell’esito allo SLV (OK / NOT_OK).
   - Indica dove la logica segue NTC e dove segue EC8 (fallback), esplicitando i punti in cui si “sceglie” una norma o l’altra.

4) CONDIZIONI DI APPLICABILITÀ E LIMITI
   - Elenca le condizioni per cui il check è APPLICABILE:
     - tipo di elemento (solo tamponature? solo parapetti? anche appendici leggere?),
     - range di massa/dimensioni,
     - campo di drift considerato, ecc.
   - Definisci:
     - cosa succede se i dati sono fuori campo (es. elemento troppo grande o troppo rigido): il check deve restituire `NOT_APPLICABLE` e un WARNING chiaro.
   - Evidenzia i casi in cui è richiesta analisi globale più dettagliata (influence_on_global_model = true).

5) OUTPUT DEL CHECK
   - Specifica il contenuto di un oggetto tipo SingleCheckResult per questo check:
     - check_id (es. “NS_SLV_SecondaryElement”);
     - element_id;
     - esito (OK / NOT_OK / NOT_APPLICABLE);
     - utilisation ratio (Fa / capacità, oppure MEd/MRd, ecc.);
     - combinazione critica / scenario sismico usato;
     - parametri di domanda (Fa, Ta, Sa(Ta,z), drift, ecc.);
     - parametri di capacità (anchorage_capacity, MRd, ecc. – anche se la capacità è fornita da altri moduli o input);
     - norm_references (lista di riferimenti: NTC §…, EC8 §…);
     - messaggi utente (warning, errori, note su campo di validità).
   - Spiega come questo risultato deve integrarsi nel VerificationResult generale del progetto.

6) INTEGRAZIONE CON VERIFICATIONENGINE / CODEMODULE
   - Descrivi come il check viene:
     - esposto dal CodeModule NTC2018/EC8 (es. `available_checks()` che include “NS_SLV_SecondaryElement”);
     - invocato dal VerificationEngine (es. `run_check(check_id, SecondaryElementSpec, CalcContext)`).
   - Indica in che modo:
     - il check può essere riusato per diverse categorie di elementi (via element_type / parametri della spec),
     - logiche comuni (es. calcolo di Sa, drift) possono stare in funzioni condivise di modulo, e quali parti rimangono specializzate.

7) GUI E UX (SOLO DESIGN)
   - Descrivi:
     - quali informazioni devono essere mostrate all’utente quando esegue questo check (esito, margine di sicurezza, combinazione critica, riferimenti normativi);
     - eventuali warning grafici (es. “Elemento fuori campo di validità delle formule – vedi EC8 nota …”).
   - Indica se è utile:
     - un pannello riepilogativo con la “domanda” Fa e le resistenze,
     - link/note ai riferimenti normativi (solo come testo).

8) TEST DI VALIDAZIONE
   - Definisci una lista di **test case** per validare questo check, utilizzando gli esempi numerici delle fonti:
     - caso tamponatura con spettro di piano (BibLus NTC + Circ.);
     - caso componente non strutturale con Fa da EC8 (Prota “Seismic forces on non-structural members”);
     - eventuale caso parapetto/appendice.
   - Per ogni test case:
     - descrivi quali valori di SecondaryElementSpec e CalcContext andranno impostati;
     - quale output atteso (esito OK/NOT_OK, range di Fa, ecc.);
     - a quale riferimento normativo o esempio è collegato.

9) CHECKLIST FINALE
   - Concludi con una checklist tipo:
     - “Definito lo scopo del check e gli stati limite coperti”
     - “Elencati tutti gli input necessari da SecondaryElementSpec + CalcContext”
     - “Descritta la logica di calcolo a livello concettuale (Fa, Ta, Sa, confronto domanda/capacità)”
     - “Definiti condizioni di applicabilità e messaggi NOT_APPLICABLE”
     - “Definita la struttura dell’output SingleCheckResult per questo check”
     - “Definite linee guida per test di validazione basati su esempi reali”

Ribadisco: nessun codice, solo SPEC dettagliato di questo check, coerente con lo schema di SecondaryElementSpec già definito.

Status: preparo la SPEC formale di SecondaryElementSpec (solo planning — nessun codice). Di seguito trovi la specifica completa, le regole di validazione, i mapping GUI/storage e la checklist operativa.

SecondaryElementSpec — Visione generale
Oggetto di input canonico per rappresentare un ELEMENTO NON STRUTTURALE / SECONDARIO (tamponatura, parapetto, insegna, mensola, elemento sospeso, ecc.).
Scopo: fornire un’unica, completa fonte di verità usabile da GUI, VerificationEngine, CodeModule (NTC2018/EC8) e storage (JSON/CSV).
Unità canoniche interne: SI (lunghezze in m, masse in kg, forze in kN, aree in m², densità in kg/m³, pressione in MPa).

1) Struttura (campo‑by‑campo)
Per leggibilità i campi sono raggruppati; ogni campo indica: Tipo — Unità — Obbl./Opz. — Default — Descrizione — Norm/ref — Dipendenze.

A. Identità & metadati
id — string — (OBBL.) — Unique identifier progetto (UUID-like).
name — string — (OPZ.) — "Nome descrittivo" per UI.
schema_version — string — (OBBL., default "1.0") — Versione schema per migration.
tags — list[string] — (OPZ.) — etichette libere (es. "façade","high-risk").
B. Tipo e classificazione
element_type — enum — (OBBL.) — {PANEL, TAMPONATURA, PARAPET, CANTILEVER, SIGNAGE, SUSPENDED, CHIMNEY, BRACKET, FACADE_PANEL, EQUIPMENT, OTHER} — tipo concettuale (mappa a template di verifica). — Normativa: NTC §7.2 / EC8.
class_of_use — enum — (OPZ., default per progetto) — {1,2,3,4} — classe d’uso per criteri SLV (NTC).
norm_primary — enum — (OBBL., default "NTC2018") — {NTC2018, RD2229, DM92, DM96} — fonte preferenziale.
norm_fallback — enum — (OPZ., default "EC8") — norma di dettaglio se NTC non prescrive (es. EC8).
C. Geometria (base)
length_L — float — m — (condizionale) — lunghezza in pianta (p. es. pannello).
height_h — float — m — (condizionale) — altezza verticale dell’elemento.
thickness_s — float — m — (condizionale) — spessore (pannelli/murature).
depth_d — float — m — (condizionale) — profondità o estensione fuori piano.
area_proj_Ap — float — m² — (OPZ.; calcolabile) — area proiettata usata per carichi vento/sisma.
volume — float — m³ — (OPZ.; calcolabile) — volume dell’elemento.
geometry_profile_ref — string — (OPZ.) — riferimento ad una section predefinita (key su sections.json)
Notes: campi geometrici obbligatori dipendono da element_type (v. validazione).
D. Materiale / proprietà meccaniche
material_id — string — (OPZ., consigliato) — chiave su historical_materials.json / registry.
density_rho — float — kg/m³ — (OPZ.; inferibile da material_id) — densità usata per massa.
E_modulus — float — MPa — (OPZ.; inferibile) — modulo elastico per stima Ta, stiffness.
strength_fk — float — MPa — (OPZ.; inferibile) — resistenza (p. es. fk per muratura).
notes_material — string — (OPZ.) — campo libero.
E. Massa & carichi (input operativi)
mass_Wa — float — kg (OBBL. se non inferibile) — massa totale dell’elemento (Wa). Norm ref: NTC/EC8.
distributed_load_q — float — kN/m (OPZ.) — carico permanente/accidentale aggiuntivo.
imposed_loads — list[ {type, value, unit} ] — (OPZ.) — es. wind pressure, snow.
mass_source — enum — {explicit, density*volume} — (OBBL. logicamente)
F. Parametri sismici / sito
z_elevation — float — m — (OBBL. se check_sismic=true) — quota del baricentro elemento (normale rich.). — Norm: NTC §7.x, EC8.
building_H — float — m — (OPZ.; richiesto se Ta calcolato via T1/H) — altezza edificio.
site_ag — float — g (accel) — (OPZ.; da progetto) — ag per SLV/SLU.
soil_category — enum — {A,B,C,D,E} — (OPZ.) — per spettro.
Ta_input — float — s — (OPZ.; default=NULL) — periodo proprio (se noto/utente).
damping_xi — float — % — (OPZ., default 5%) — smorzamento per spettro.
importance_gamma_a — float — (OPZ., default from config) — γa (EC8 table).
behavior_qa — float — (OPZ., default from config) — qa (EC8/NTC tables).
G. Vincoli / ancoraggi / supporti
support_type — enum — {clamped, pinned, suspended, sliding, supported_edge, embedded} — (OBBL.)
anchor_type — enum — {exp_bolt, chem_anchor, weld, plate, none} — (OPZ.; required if suspended/anchored)
anchor_capacity_ref — string/float — (OPZ.) — riferimento dati produttore o capacità presunta (kN).
anchor_positions — list[{x,y,z}] — (OPZ.; for distributed anchors)
fixation_notes — string — (OPZ.)
H. Operational flags & metadata
influence_on_global_model — bool — (OBBL., default false) — se true → escalation per modellazione globale.
preset_id — string — (OPZ.) — se creato da libreria preset.
allow_ec8_fallback — bool — (OPZ., default true) — se usare EC8 quando NTC manca.
user_notes — string — (OPZ.)
created_by, created_at — metadata runtime.
2) Regole di validazione e campo di applicabilità
Validazioni generali (pre‑calcolo)
tipi & range base:
height_h > 0.01 m; length_L > 0.01 m; thickness_s ≥ 0.005 m; mass_Wa > 0.1 kg; 0 ≤ z_elevation ≤ building_H.
coerenza massa/volume:
se mass_Wa e density_rho+volume presenti → abs(mass_Wa − density_rho*volume) / mass_Wa ≤ 0.05 → OK; altrimenti warning mass_mismatch.
campi obbligatori per tipo:
element_type = PANEL/TAMPONATURA → require height_h, length_L, thickness_s, material_id o density_rho, mass_Wa (o inferibile).
SIGNAGE / CANTILEVER → require length_L, anchor_type, anchor_positions, mass_Wa.
SUSPENDED → require anchor_type, anchor_positions, mass_Wa.
parametri sismici:
se check_sismic richiesto → z_elevation & site_ag & soil_category devono essere presenti (altrimenti errore).
applicability gating (NOT_APPLICABLE conditions):
se influence_on_global_model == true → simplified secondary checks must return NOT_APPLICABLE (escalate).
se mass_Wa / floor_mass_estimate > threshold_config (es. 0.05) → warning may_influence_global_model (consiglia modellazione globale).
se slenderness (H/width) supera valore limite per file type → warning/NOT_APPLICABLE per formule semplificate.
Errori vs Warning (concetto)
Errori (block calc): mancano campi obbligatori; valori impossibili (negative dimensions); parametri sismici mancanti quando richiesti.
Warning (informative): mass mismatch, field outside normative preferred range (es. Ta molto alto), influence_on_global_model recommended.
NOT_APPLICABLE: il check specifico non può essere eseguito (es. elemento influenza la risposta globale, formule semplificate non valide).
3) Relazione con altri oggetti del repo
material_id → chiave esterna verso historical_materials.json / materials.json (loader fornisce density/E_modulus/fk).
geometry_profile_ref → riferimento ad una section salvata in sections.json o SectionGeometry (riuso della libreria sezioni).
preset_id → collegamento a registry/secondary_presets.json.
mass_Wa, z_elevation, Ta_input → usati dal motore combinazioni/spettro (componenti sismici).
Chiavi esterne importanti: material_id, geometry_profile_ref, preset_id. GUI/engine devono validare l’esistenza di queste chiavi prima dell’uso.
4) Mapping verso GUI (design form)
Form logico (sezioni):

Header (id, name, preset) — generale.
Tipo & classificazione (element_type, class_of_use, norm_primary) — scelta template.
Geometria & materiale (length_L, height_h, thickness_s, material_id, geometry_profile_ref) — base.
Massa & carichi (mass_Wa, distributed_load_q, imposed_loads) — operativo.
Sisma & sito (z_elevation, site_ag, soil_category, Ta_input, damping) — sezione sismica (collapsible).
Vincoli & ancoraggi (support_type, anchor_type, anchor_positions) — avanzato.
Flags & metadati (influence_on_global_model, notes) — meta.
Buttons: Estimate Ta, Run secondary checks, Save preset, Validate.
UI rules:

campi inferibili precompilati (preset, material lookup);
campi avanzati nascosti in “Advanced” per non‑esperti;
validazione in linea (immediata) con messaggi normativi (es. “NTC §7.2: z required for seismic checks”).
5) Mapping verso storage / JSON schema (design)
Salvataggio concettuale (project JSON):
project.secondary_elements = [ { schema_version, id, name, element_type, geometry:{...}, material_id, mass_Wa, seismic:{...}, supports:{...}, flags:{...}, results:[...] } ]
Versioning: schema_version obbligatorio; migration strategy: new optional fields tolerated; readers ignore unknown fields.
CSV export: flattened columns (id,name,type,L,h,s,Wa,z,material_id,anchor_type,qa,γa) + results as separate CSV or JSON column.
Persistence rule: update sections.json/materials.json references unchanged.
6) Integrazione con VerificationEngine / CodeModule (design)
Flow (concept):
GUI crea SecondaryElementSpec → project saved.
User requests check → VerificationEngine.perform_secondary_checks([spec_ids], calc_context) calls CodeModule.run_secondary_check(check_id, spec, context).
CodeModule (NTC2018) decides whether to apply NTC formulas or fallback EC8 (based on norm_primary & allow_ec8_fallback).
Engine aggregates SingleCheckResult in VerificationResult.secondary[] and stores in project results.
Fields always read by any check: id, element_type, mass_Wa, z_elevation, site_ag/soil_category, support_type, material_id.
Fields used conditionally: geometry group (per type), anchor details (per anchor checks), Ta_input (if provided), influence_on_global_model (gating).
Derived outputs to push back into spec/results: Ta_estimated, Sa, Fa, utilisation, norm_references, messages.
7) Regole di validazione (funzione concettuale)
Firma concettuale: validateSecondaryElementSpec(spec, projectContext) -> {status: VALID|INVALID, errors:[], warnings:[], applicability:[] }
Error-generating conditions (block):
missing required field for element_type; missing seismic inputs when check requested; inconsistent mass/geometry.
Warning conditions:
mass large vs floor mass; Ta very low/high; anchor_type unspecified for suspended.
Applicability flags:
requires_global_model (true) if element influences global response; fallback_ec8_used (if EC8 applied).
Validation messages include normative refs (e.g. "NTC2018 §7.2.3 — z required for seismic checks").
8) Checklist finale (operativa, prima implementazione)
 Concordare enumerazioni canoniche (element_type, support_type, anchor_type).
 Redigere SecondaryElementSpec schema (documento) e includere schema_version.
 Implementare validator spec‑only (plan) e mapping GUI form sections.
 Aggiornare config/codes/ntc2018.jsoncode con secondary_elements presets/qa defaults.
 Definire 3 golden test fixtures (tamponatura, signage, parapet) e aspettative.
 Disegnare storage mapping e migration policy (schema_version).
 Documentare nel docs norme di riferimento (NTC§7.2, EC8 §4.3.5) e policy di fallback.
Note conclusive — linee guida progettuali
Usare SecondaryElementSpec come single source of truth tra GUI ↔ Engine ↔ Storage.
Canonical units = SI; GUI e import/export eseguono conversioni e mostrano unità locali.
Validazione preventiva obbligatoria (errori bloccanti) per evitare calcoli non sensati; warning espliciti con riferimento normativo.
Documentare sempre la fonte normativa scelta (NTC vs EC8) nell’output dei check.
Mantenere retro‑compatibilità: eventuali campi nuovi devono essere opzionali e versionati.
Se vuoi, preparo ora (plan‑only) il documento SPEC formale pronto per essere trasformato in uno jsonschema o in una dataclass di riferimento — confermi che lo formalizzi come prossimo step?

PROMPT INCREMENTALE – SPEC Check “NS_SLV_SecondaryElement” (SOLO PLAN, NESSUN CODICE)

CONTESTO:
Hai già:

un piano per il modulo NTC2018 §7.2 + EC8 per elementi non strutturali/secondari;
definito (nel prompt precedente) lo SPEC di SecondaryElementSpec, schema di input comune per tutti gli elementi secondari;
definito un SingleCheckResult/VerificationResult concettuale.
ORA voglio che tu definisca, in modalità PLAN, lo SPEC di UNA verifica specifica:

👉 Check name (di esempio): NS_SLV_SecondaryElement
Scopo: verificare la sicurezza sismica allo SLV di un elemento non strutturale/secondario (stabilità, espulsione, ancoraggio) utilizzando la domanda Fa derivata da NTC §7.2 + EC8 (EN 1998‑1, §4.3.5 e simili).

IMPORTANTE:

SOLO pianificazione, nessun codice.
Niente classi Python, niente funzioni; solo specifiche di:
scopo,
input,
passaggi logici concettuali,
output,
integrazione con Engine/CodeModule,
test da prevedere.
CHE COSA VOGLIO IN DETTAGLIO:

IDENTITÀ DEL CHECK

Nome simbolico del check (es. NS_SLV_SecondaryElement).
Descrizione testuale: cosa verifica, in che condizioni si applica (tipi di elementi: tamponature, parapetti, insegne, elementi sospesi, ecc.).
Elenco degli stati limite coperti (principalmente SLV; eventuali riferimenti a SLE/SLD se rilevanti).
Riferimenti normativi:
paragrafi NTC2018 §7.2/§7.3/§7.3.6;
clausole EC8 pertinenti (es. EN 1998‑1 §4.3.5 per le forze sui componenti, limiti di drift da tabelle EC8).
INPUT DEL CHECK

Elenca in modo esplicito:
quali campi di SecondaryElementSpec sono necessari (es. mass Wa, z, H, tipo elemento, geometria base, tipo ancoraggio, ⋯);
quali parametri aggiuntivi tramite CalcContext/Scenario (es. spettro di piano, combinazione sismica, ag, fattori di comportamento, parametri di piano).
Per ogni input:
specifica se OBBLIGATORIO o OPZIONALE,
come viene usato concettualmente nel calcolo (es. quota z setta il fattore di amplificazione, Wa entra nella formula di Fa, ecc.),
eventuali controlli preliminari (range, coerenza).
LOGICA DI CALCOLO (CONCETTUALE, NON CODICE)

Descrivi i passaggi logici, in forma di “flow” o pseudocodice concettuale, SENZA formule dettagliate, ma:
Calcolo del periodo equivalente Ta (da SecondaryElementSpec o da modello semplificato);
Individuazione di Sa(Ta,z) da spettro di piano (NTC/EC8);
Calcolo della domanda di forza Fa (o forza equivalente in testa/piede);
Determinazione di effetti (momenti/tagli/sollecitazioni su ancoraggi o sezione);
Confronto con capacità (es. capacità di ancoraggio, resistenza di sezione, stabilità al ribaltamento);
Determinazione dell’esito allo SLV (OK / NOT_OK).
Indica dove la logica segue NTC e dove segue EC8 (fallback), esplicitando i punti in cui si “sceglie” una norma o l’altra.
CONDIZIONI DI APPLICABILITÀ E LIMITI

Elenca le condizioni per cui il check è APPLICABILE:
tipo di elemento (solo tamponature? solo parapetti? anche appendici leggere?),
range di massa/dimensioni,
campo di drift considerato, ecc.
Definisci:
cosa succede se i dati sono fuori campo (es. elemento troppo grande o troppo rigido): il check deve restituire NOT_APPLICABLE e un WARNING chiaro.
Evidenzia i casi in cui è richiesta analisi globale più dettagliata (influence_on_global_model = true).
OUTPUT DEL CHECK

Specifica il contenuto di un oggetto tipo SingleCheckResult per questo check:
check_id (es. “NS_SLV_SecondaryElement”);
element_id;
esito (OK / NOT_OK / NOT_APPLICABLE);
utilisation ratio (Fa / capacità, oppure MEd/MRd, ecc.);
combinazione critica / scenario sismico usato;
parametri di domanda (Fa, Ta, Sa(Ta,z), drift, ecc.);
parametri di capacità (anchorage_capacity, MRd, ecc. – anche se la capacità è fornita da altri moduli o input);
norm_references (lista di riferimenti: NTC §…, EC8 §…);
messaggi utente (warning, errori, note su campo di validità).
Spiega come questo risultato deve integrarsi nel VerificationResult generale del progetto.
INTEGRAZIONE CON VERIFICATIONENGINE / CODEMODULE

Descrivi come il check viene:
esposto dal CodeModule NTC2018/EC8 (es. available_checks() che include “NS_SLV_SecondaryElement”);
invocato dal VerificationEngine (es. run_check(check_id, SecondaryElementSpec, CalcContext)).
Indica in che modo:
il check può essere riusato per diverse categorie di elementi (via element_type / parametri della spec),
logiche comuni (es. calcolo di Sa, drift) possono stare in funzioni condivise di modulo, e quali parti rimangono specializzate.
GUI E UX (SOLO DESIGN)

Descrivi:
quali informazioni devono essere mostrate all’utente quando esegue questo check (esito, margine di sicurezza, combinazione critica, riferimenti normativi);
eventuali warning grafici (es. “Elemento fuori campo di validità delle formule – vedi EC8 nota …”).
Indica se è utile:
un pannello riepilogativo con la “domanda” Fa e le resistenze,
link/note ai riferimenti normativi (solo come testo).
TEST DI VALIDAZIONE

Definisci una lista di test case per validare questo check, utilizzando gli esempi numerici delle fonti:
caso tamponatura con spettro di piano (BibLus NTC + Circ.);
caso componente non strutturale con Fa da EC8 (Prota “Seismic forces on non-structural members”);
eventuale caso parapetto/appendice.
Per ogni test case:
descrivi quali valori di SecondaryElementSpec e CalcContext andranno impostati;
quale output atteso (esito OK/NOT_OK, range di Fa, ecc.);
a quale riferimento normativo o esempio è collegato.
CHECKLIST FINALE

Concludi con una checklist tipo:
“Definito lo scopo del check e gli stati limite coperti”
“Elencati tutti gli input necessari da SecondaryElementSpec + CalcContext”
“Descritta la logica di calcolo a livello concettuale (Fa, Ta, Sa, confronto domanda/capacità)”
“Definiti condizioni di applicabilità e messaggi NOT_APPLICABLE”
“Definita la struttura dell’output SingleCheckResult per questo check”
“Definite linee guida per test di validazione basati su esempi reali”
Ribadisco: nessun codice, solo SPEC dettagliato di questo check, coerente con lo schema di SecondaryElementSpec già definito.

Status: preparo la SPEC di piano per il check “NS_SLV_SecondaryElement” — nessun codice, solo specifica completa e pronta per implementazione.

1) Identità del check
Nome simbolico: NS_SLV_SecondaryElement
Descrizione: verifica la sicurezza sismica (SLV) di un elemento non‑strutturale/secondario (stabilità, espulsione, capacità ancoraggi, ribaltamento). Applicabile a tamponature, pannelli, parapetti, insegne, mensole, elementi sospesi, camini/comignoli; usa NTC2018 (§7.2 / §7.3.6.2) come riferimento primario e applica EC8 (EN1998‑1 §4.3.5) dove NTC richiede formule o dettagli.
Stati limite coperti: SLV (principalmente); segnala SLE/SLD rilevanti (es. servizio/danno) come check secondari o warning.
Riferimenti normativi essenziali:
D.M. 17/01/2018 (NTC2018) — Capitolo 7 (§7.2, §7.3.6.2 e Circolare esplicativa C7.2/C7.3).
EN 1998‑1 (EC8) — §4.3.5 (forze su non‑structural members), tabelle qa, γa, modalità spettro di piano.
Note: il check documenta esplicitamente quale fonte è stata usata (NTC o EC8).
2) Input del check
(Usare campi di SecondaryElementSpec + CalcContext)

Obbligatori (block‑errors se mancanti)

element_id (spec.id) — identificatore dell’elemento
element_type — definisce il modello da usare (PANEL, SIGNAGE, CANTILEVER, PARAPET, SUSPENDED, CHIMNEY, …)
mass_Wa — kg — massa totale dell’elemento (Wa) → entra direttamente in Fa
z_elevation — m — quota del baricentro (influenza Sa(Ta,z))
support_type — tipo di vincolo (es. anchored/suspended/clamped)
site_ag (CalcContext) — accelerazione di progetto (ag) o spettro disponibile
soil_category (CalcContext) — categoria suolo (per spettro)
building_T1 o building_H (CalcContext) — necessario per calcolo Sa(Ta,z) semplificato
Obbligatori condizionali (dipendono da element_type / support_type)

anchor_type / anchor_positions / anchor_capacity_ref — obbligatori se support_type indica ancoraggio
Geometria minima:
per PANEL/TAMPONATURA: height_h, length_L, thickness_s (o area_proj_Ap)
per CANTILEVER/SIGNAGE: length_L e geometry_profile_ref o area_proj_Ap
Opzionali (usati se presenti; inferibili altrimenti)

Ta_input — s (se noto dall’utente)
E_modulus, density_rho, material_id — per stime Ta o capacità MRd
behavior_qa, importance_gamma_a — se si vogliono override delle tabelle normative
damping_xi — % (default 5%)
influence_on_global_model — bool (gating)
Uso concettuale di ogni input

mass_Wa → Wa nella formula Fa (Fa ∝ Wa)
z_elevation, building_T1, building_H, soil_category, site_ag → determinano Sa(Ta,z) (spettro di piano)
Ta_input o stima Ta → periodo dell’elemento per estrazione Sa(Ta)
behavior_qa, importance_gamma_a → fattori di comportamento/importanza (EC8/NTC) applicati a Fa o alle condizioni di progetto
anchor_capacity_ref → capacità di verifica ancoraggi (se disponibile)
Validazioni preliminari: valori fisici (massa>0, 0<z≤H, geometric dims > 0), consistenza material/geometry.
3) Logica di calcolo (concettuale — flow)
VALIDAZIONE INIZIALE

Verifica obbligatorietà (campi mancanti → ERROR block).
Verifica campo di applicabilità (es. influence_on_global_model == true → return NOT_APPLICABLE / escalate).
STIMA / ACQUISIZIONE DEL PERIODO Ta

Se Ta_input presente → Ta = Ta_input
Else → Ta = stima semplificata basata su geometry + E_modulus/density (tipo dipende da element_type).
OTTENIMENTO dello spettro di piano / Sa(Ta,z)

Se spettro completo disponibile in CalcContext → leggere Sa(Ta,z)
Else → calcolare Sa(Ta,z) tramite formulazione semplificata di NTC Circolare (C7.2.3) oppure EC8 (configurable fallback)
Documentare quale metodo è stato usato (NTC vs EC8).
CALCOLO DELLA DOMANDA SISMICA Fa

Formula base (policy selezionabile):
EC8 default: Fa = Sa(Ta,z) * Wa / qa
Se versione normativa richiede γa: Fa = Sa(Ta,z) * Wa * γa / qa
Applicare comportamento qa e importanza γa (da spec o da config).
TRASDUZIONE DOMANDA IN EFFETTI LOCALI

Convertire Fa in azioni pertinenti al tipo: forze concentrate su ancoraggi, distribuite su pannelli, momento di ribaltamento per parapetti, taglio/forza sugli attacchi per insegne/mensole.
Calcolare M_Ed/V_Ed/anchor_forces come opportuno (flow di mapping per element_type).
VERIFICA DELLA CAPACITÀ

Recuperare capacità da anchor_capacity_ref o stimare MRd/VRd (material + geometry).
Confrontare domanda/capacità → calcolare utilisation = demand / capacity.
DECISIONE SLV

Se utilisation ≤ 1.0 e condizioni di applicabilità rispettate → ESITO = OK
Se utilisation > 1.0 → ESITO = NOT_OK (fornire azioni raccomandate)
Se condizioni non conformi / dati insufficienti → ESITO = NOT_APPLICABLE o ERROR con messaggio (vedi regole di validazione).
OUTPUT & TRACCIA

Preparare SingleCheckResult con parametri domanda/capacità, norme applicate, messaggi e suggerimenti (es. aumentare ancoraggi, riposizionare, modellazione globale).
Norme vs punti decisionali

Preferenza NTC2018 per definizioni e semplificazioni; se NTC non fornisce valore/tabella → usare EC8 §4.3.5 (Sa, qa, γa, procedure spettro di piano). La scelta è registrata nel norm_references dell’output.
4) Condizioni di applicabilità / limiti
APPLICABILE se:
element_type ∈ {PANEL, TAMPONATURA, PARAPET, SIGNAGE, CANTILEVER, SUSPENDED, CHIMNEY, …}
mass_Wa e z_elevation disponibili
influence_on_global_model == false (altrimenti escalation)
NON APPLICABILE (NOT_APPLICABLE) se:
influence_on_global_model == true (consiglia analisi globale)
elemento supera threshold dimensionale/massivo (es. Wa/floor_mass > cfg.threshold)
mancano dati sismici essenziali (site_ag o soil_category) — può essere errore o NOT_APPLICABLE a seconda della policy
WARNINGS:
Ta stimato con scarsa informazione (E_modulus assente) → warning Ta_estimated_low_confidence
anchor_capacity_ref mancante → warning anchor_capacity_missing (calcolo procede ma capacity non verificata)
Regole di escalation:
se elemento “influenza la risposta globale” → suggerire NOT_APPLICABLE e richiedere modellazione completa del fabbricato.
5) Output del check (SingleCheckResult — contenuto previsto)
check_id: "NS_SLV_SecondaryElement"
element_id: spec.id
esito: {OK | NOT_OK | NOT_APPLICABLE | ERROR}
utilisation: numero (es. Fa / capacity_o_overturning) — valore principale di controllo
critical_combination_id: id della combinazione sismica usata (CalcContext)
demand: { Fa (kN), Ta (s), Sa (g o m/s²), drift_estimate (mm o ratio), VEd/MEd }
capacity: { anchor_capacity (kN), MRd (kNm), VRd (kN) } — se disponibile
norm_references: [ "NTC2018 §7.3.6.2", "EN1998‑1 §4.3.5" ] — specificare esatta fonte usata
messages: array di stringhe (warnings/errors/validation notes)
details: campo strutturato per traceability (which method used for Sa, Ta estimation, qa/γa values)
suggested_actions: breve elenco (es. “increase anchors”, “model element in global analysis”, “add ties to structure”)
Integrazione risultato: VerificationEngine inserisce il SingleCheckResult in VerificationResult.secondary e nel project.secondary_elements[].results.

6) Integrazione con VerificationEngine / CodeModule
Esposizione: CodeModule.available_checks() include NS_SLV_SecondaryElement.
Invocazione: VerificationEngine chiama run_secondary_check("NS_SLV_SecondaryElement", SecondaryElementSpec, CalcContext).
Reuse: la funzione è parametrica rispetto a element_type; flusso centrale (Sa/Ta/Fa) è comune, poi branch‑per‑type per mapping domanda→effetto→capacity.
Shared utilities (design): centralizzare calcolo Sa(Ta,z), stima Ta, e validazione; check specifici invocano queste utility via API interne al CodeModule.
7) GUI / UX (design)
Quando l’utente esegue NS_SLV_SecondaryElement mostrare:
Sintesi risultato (OK/NOT_OK/NOT_APPLICABLE) con colore e percentuale utilisation.
Box “Domanda” con Fa, Ta, Sa(Ta,z), combinazione critica.
Box “Capacità” con anchor_capacity / MRd (se not available show warning).
Normative applied (badge): es. NTC2018 §7.3.6.2 / EN1998‑1 §4.3.5.
Trace log (espandibile) con passi calcolo (Ta estimation method, Sa source, qa/γa values).
Suggested mitigations (actionable text).
UX rules: errori bloccanti mostrati come dialog; warnings non bloccanti evidenziati ma consentono proseguire.
8) Test di validazione (casi consigliati)
Per ogni test indicare: spec fields (essenziali), CalcContext, expected outcome (qualitativo/normativo).

Test A — Tamponatura (BibLus / NTC Circolare)
Input (esempio da fonte): element_type=PANEL, L=5.0 m, h=2.5 m, s=0.35 m, fk ≈ 2.0 N/mm², density ≈ 8000 N/m³ → mass_Wa (compute), z=7.5 m, building_H=9.0 m, site_ag/soil=S (use example), Ta computed via panel formula.
CalcContext: usare formula NTC semplificata per Sa(Ta,z) (Circolare C7.2.3).
Expected: Fa calcolato; check di SLV (stability/espulsione) → OK per esempio documentato; norm_references include NTC Circolare.
Verifica: utilisation < 1; details show Ta, Sa, qa used.
Test B — EC8 worked example (Prota / JRC)
Input: element_type=SIGNAGE (cantilever), Wa, z, building_T1 per esempio JRC.
CalcContext: use EC8 method for Sa(Ta,z) and qa table.
Expected: Fa per EC8; check outcome consistent with worked example (utilisation within reported value). norm_references include EN1998‑1 §4.3.5.
Test C — Signage with insufficient anchors (Anchor Failure)
Input: SIGNAGE, mass_Wa moderate, anchor_capacity_ref set to value < demanded anchor force (simulate).
Expected: esito NOT_OK; messages: "anchor capacity insufficient"; suggested actions: increase anchors; check reports required anchor force and provided capacity.
Test D — Elemento out‑of‑scope (influence_on_global_model true)
Input: very large panel (mass_Wa / floor_mass > threshold) or influence_on_global_model=true.
Expected: NOT_APPLICABLE (or ERROR depending policy) with message: "Element influences global response — run global model".
Test E — Missing sismic input
Input: element_type=PARAPET but CalcContext missing site_ag.
Expected: ERROR / validation block with message "site_ag required for SLV checks".
Acceptance tolerances: numerical comparisons to reference examples within ±5–10% (document per test); logic outcomes (OK/NOT_OK/NOT_APPLICABLE) must match source expectations.

9) Checklist finale per il check NS_SLV_SecondaryElement
 Definito check_id e descrizione formale
 Mappati tutti gli input richiesti su SecondaryElementSpec + CalcContext
 Specificata la logica di calcolo (Ta → Sa → Fa → demand→capacity → esito) e i punti di fallback NTC→EC8
 Definite regole di validazione / NOT_APPLICABLE / escalation globale
 Stabilito formato SingleCheckResult e integrazione in VerificationResult.secondary[]
 Disegnata UI di output e messaggistica normativa
 Preparata suite test (casi A–E) con riferimenti normativi e acceptance criteria
Vuoi che formalizzi ora (plan‑only) il documento di test‑fixture per il Test A (Tamponatura — Circolare / BibLus) o preferisci che prepari il template del SingleCheckResult (campi + esempi di contenuto) per questo check?

PROMPT INCREMENTALE MASTER (ESPANSIONE COMPLETA, SOLO PLAN)

IMPORTANTE (RIBADITO):
- Rimani SEMPRE e SOLO in modalità PLAN.
- NON generare codice Python.
- NON creare file.
- NON proporre implementazioni operative.
- Fornisci solo: analisi, specifiche, piano tecnico, task, dipendenze, criteri di validazione.

CONTESTO DI PARTENZA (RIEPILOGO):
Hai già costruito, con i prompt precedenti:

- un piano per l’implementazione di NTC2018 nel framework (Fasi 0–11) con:
  - CodeModule NTC2018,
  - combinazioni (SLU/SLE),
  - materiali (adapter NTC2018),
  - verifiche RC (flessione, taglio, torsione, N–M),
  - sismica globale (spettri + statica equivalente),
  - acciaio/legno/muratura,
  - geotecnica,
  - edifici esistenti,
  - UI Tkinter + workflow,
  - validazione/test/demo/doc,
  - release/CI.

- estensioni incrementali:
  - Fase 4: taglio SENZA armatura (V_Rd,c) + condizioni di applicabilità + SLE fessurazione;
  - Fase 6bis: modulo “elementi strutturali secondari” (NTC 7.2 + Eurocodici);
  - Fase 12: modernizzazione GUI + registry + storage.

- un modulo concettuale NTC 7.2 + EC8 per ELEMENTI NON STRUTTURALI/SECONDARI:
  - teoria di base (Fa ≈ Sa(Ta,z)*Wa/qa, uso spettro di piano, stati limite SLU/SLE/SLV),
  - categorie di elementi (tamponature, parapetti, mensole, insegne, sospesi, camini, ecc.),
  - schema di input comune **SecondaryElementSpec**,
  - schema di output comune (SingleCheckResult),
  - specifica concettuale per un check tipo `NS_SLV_SecondaryElement` (SLV su elementi non strutturali),
  - pianificazione test basata su esempi numerici reali (NTC, Circolare, EC8, Prota, JRC, BibLus, …).

OBIETTIVO DI QUESTO PROMPT:
Voglio che tu PRENDA TUTTO IL PIANO/SPEC CHE HAI GIÀ PRODUtTO e lo ESPANDA ulteriormente, andando più in profondità su:

- teoria,
- requisiti di input/output,
- architettura software,
- GUI interconnesse,
- storage/registry/config,
- coerenza tra norme (NTC, ECx, RD2229, DM92, DM96),
- test e validazione,
- rischi e limiti di applicabilità.

Non devi riscrivere tutto da zero, ma:
- raffinare,
- completare i punti rimasti generici,
- risolvere eventuali ambiguità,
- evidenziare più chiaramente le scelte progettuali.

————————————————————————
1) APPROFONDIMENTO TEORICO (TUTTE LE AREE)
————————————————————————

Per ogni macro‑area già presente nel piano (RC, taglio V_Rd,c, sismica globale, acciaio, legno, muratura, geotecnica, esistenti, elementi secondari, non strutturali NTC 7.2 + EC8), voglio che:

1.1. Espliciti i PRINCIPI TEORICI chiave da integrare nel progetto software:
     - quali relazioni concettuali formano il “cuore” dei calcoli (senza scrivere formule matematiche in dettaglio);
     - quali parametri sono davvero essenziali per tali relazioni;
     - quali sono i principali limiti di validità (domini normativi).

1.2. Indichi, per ogni ambito:
     - quali parti sono chiaramente definite da NTC2018 (capitoli e paragrafi),
     - dove invece è necessario ricorrere ad Eurocodici (EC2, EC3, EC8) o altre fonti per ottenere espressioni pratiche,
     - come documentare questa scelta a livello di software (campi di `norm_references`, note nei report).

1.3. Colleghi la teoria all’input:
     - per ogni concetto teorico chiave (es. drift, Fa, V_Rd,c, ζ_E, capacità geotecnica, ecc.) esplicita quali campi di input deve avere il framework per calcularlo.

————————————————————————
2) SISTEMA DI INPUT COMUNE (NON SOLO SECONDARI)
————————————————————————

Hai già definito `SecondaryElementSpec` e uno schema di input comune per elementi non strutturali/secondari.

Ora voglio che tu estenda e armonizzi il concetto di “input framework” a TUTTI i moduli:

2.1. Descrivi una mappa concettuale degli SCHEMI DI INPUT:
     - per elementi in CA (RC),
     - acciaio,
     - legno,
     - muratura,
     - elementi secondari,
     - elementi non strutturali sismici,
     - verifiche globali,
     - geotecnica.

2.2. Identifica:
     - quali campi possono essere STANDARDIZZATI (es. geometria base, materiale, parametri sismici, metadati normativi);
     - quali campi sono specifici di ciascun dominio, ma possono essere strutturati in modo coerente;
     - come questi schemi si riferiscono a:
       - `historical_materials`,
       - `sections` e `SectionGeometry`,
       - `calculation_codes` e combinazioni.

2.3. Proponi una “gerarchia di schemi”:
     - ad es. “BaseElementSpec” (campi comuni),
       specializzazioni per RC, acciaio, muratura, secondary/nonstructural, ecc.;
     - senza generare codice, descrivi i livelli e le relazioni (ereditarietà concettuale o composizione).

2.4. Aggiorna l’uso di `SecondaryElementSpec`:
     - chiarendo come si inserisce in questa gerarchia,
     - quali parti di `SecondaryElementSpec` possono essere riusate altrove,
     - dove, eventualmente, va raffinato/esteso per essere pienamente coerente con il resto del framework.

————————————————————————
3) SISTEMA DI OUTPUT COMUNE (TUTTE LE VERIFICHE)
————————————————————————

Hai già descritto un SingleCheckResult per elementi secondari/non-strutturali.

3.1. Estendi il concetto a TUTTE le verifiche:
     - RC, acciaio, legno, muratura, geotecnica, globali, esistenti;
     - definisci, a livello di SPEC, un output comune (es. “VerificationResultItem”) con:
       - id check,
       - tipo elemento,
       - esito (OK/NOT_OK/NOT_APPLICABLE/ERROR),
       - utilisation,
       - combinazione critica,
       - parametri di domanda e di capacità (generici estendibili),
       - riferimenti normativi,
       - messaggi/warning,
       - metadati (timestamp, versione, modulo).

3.2. Spiega:
     - come questo output comune si integra con VerificationEngine e con la UI,
     - come viene salvato in storage (project.json, export CSV),
     - come supporta la comparazione tra normative diverse (NTC, RD, DM, EC).

————————————————————————
4) ARCHITETTURA SOFTWARE — CONSOLIDAMENTO GLOBALE
————————————————————————

Hai già definito CodeModule, pacchetti `codes/ntc2018/*`, Fase 6bis, Fase 12.

4.1. Raffina il DISEGNO ARCHITETTURALE:
     - come si presentano, in modo uniforme:
       - moduli normativi (CodeModule NTC2018, RD2229, DM92, DM96, futuri ECx),
       - moduli di verifica (RC, secondari, non strutturali, geotecnica, ecc.),
       - moduli trasversali (combinazioni, materiali, spettro, storage, GUI).

4.2. Esplicita una “mappa dei packages” finale:
     - non solo per NTC2018, ma includendo i moduli storici,
     - senza codice, solo alberatura e responsabilità di ciascun package.

4.3. Approfondisci la compatibilità:
     - come i vecchi sistemi (RD2229/DM) vengono mantenuti e agganciati a CodeModule,
     - quali shims / adaptation layer sono necessari,
     - come evitare duplicazioni di logica (es. combinazioni, materiali, spettri) tra norme diverse.

————————————————————————
5) GUI INTERCONNESSE — VISIONE DI INSIEME
————————————————————————

Hai già pianificato:

- GUI per RC, materiali, sezioni,
- pannello combinazioni,
- editor e risultati per elementi secondari/non-strutturali,
- Fase 9 e Fase 12 per modernizzazione.

5.1. Costruisci una visione globale delle GUI:
     - quali pannelli sono “core” e centralizzati (es. editor sezioni, editor materiali, configurazione norme, combinazioni),
     - quali pannelli sono “di dominio” (RC, secondari, non-strutturali, geotecnica, ecc.),
     - come l’utente naviga tra:
       - scelta norma,
       - scelta modulo di verifica,
       - definizione input (sezioni, materiali, elementi),
       - lancio verifiche,
       - visualizzazione risultati.

5.2. Descrivi come assicurare:
     - massimo riuso di componenti UI (widget, editor condivisi),
     - coerenza di input (stesse etichette, stessi tipi, stessi controlli),
     - coerenza di output (stile uniforme, strutture simili, riferimenti normativi chiari).

5.3. Integra gli elementi non-strutturali:
     - spiega come `SecondaryElementEditor` e `SecondaryResultsPanel` si inseriscono nella UI globale,
     - come condividono archivi e validazioni con gli altri moduli.

————————————————————————
6) STORAGE / REGISTRY / CONFIG — QUADRO UNIFICATO
————————————————————————

Hai già introdotto:

- config/calculation_codes/*.jsoncode,
- historical_materials,
- sections.json,
- secondary_elements.jsoncode (concettuale),
- registry di presets.

6.1. Definisci un quadro unificato di storage:
     - quali file descrivono:
       - norme e parametri normativi,
       - materiali,
       - sezioni,
       - elementi (strutturali/non),
       - progetti,
       - presets/librerie.

6.2. Per ciascun tipo di dato:
     - indica quali chiavi sono obbligatorie per garantire coerenza con gli schemi di input e output (es. id, norm_code, version),
     - come gestire versioning e migrazioni (schema_version).

6.3. Spiega come Fase 12 deve:
     - armonizzare i file esistenti,
     - introdurre nuovi nodi (es. secondary_elements) senza rompere i loader storici,
     - definire un “registry unificato” di moduli normativi e di template di verifica.

————————————————————————
7) TEST, VALIDAZIONE E “GOLDEN CASES” — ESTENSIONE
————————————————————————

Hai già definito test per:

- RC (V_Rd,c con e senza staffe),
- elementi secondari/non-strutturali (BibLus, Prota, JRC, parapetti, ecc.),
- entry level per altri moduli.

7.1. Chiedo di raffinare il PIANO TEST:
     - per OGNI grande modulo (RC, acciaio, muratura, legno, geotecnica, sismica globale, esistenti, secondari, non-strutturali):
       - quali “golden cases” si potrebbero usare,
       - quali parametri chiave misurare (es. V_Rd vs V_Ed, ζ_E, cedimenti, drift, Fa, etc.),
       - quali tolleranze sono accettabili.

7.2. Collegare ciascun gruppo di test:
     - ai riferimenti normativi o a esercizi pubblicati,
     - ai tipi specifici di elementi (travi, pilastri, fondazioni, tamponature, parapetti, ecc.),
     - alle fasi del piano (Fase 4, 5, 6bis, ecc.).

————————————————————————
8) RISCHI, LIMITI E RACCOMANDAZIONI
————————————————————————

Infine, voglio che tu estenda la sezione “Rischi & mitigazioni”:

8.1. Identifica nuovi rischi specifici legati a:
     - uso combinato NTC2018 + ECx nel modulo non-strutturali,
     - errori di input (Ta errato, masse sbagliate, z non coerente),
     - interpretazione eccessivamente semplificata di modelli (mensole, parapetti, elementi sospesi),
     - integrazione di normative storiche (RD/DM) con NTC/EC8 nello stesso ambiente.

8.2. Per ciascun rischio:
     - proporre misure di mitigazione a livello di progettazione software:
       - validazioni aggressive,
       - NOT_APPLICABLE + WARNING,
       - logging esplicito di scelte normative,
       - suggerimenti all’utente per “escalare” a modelli globali quando necessario.

————————————————————————
FORMATO DI RISPOSTA RICHIESTO
————————————————————————

- NON riscrivere tutto il piano da zero.
- Fornisci un **DOCUMENTO DI ESPANSIONE** strutturato in sezioni:

  1) Teoria di base (per macro-area, in forma sintetica ma completa);
  2) Sistema di input comune (schema gerarchico e mappa tra domini);
  3) Sistema di output comune (struttura generica + adattamenti);
  4) Architettura software consolidata (mappa packages, moduli normativi, adapter storici);
  5) GUI interconnesse (visione globale di UX e riuso);
  6) Storage/Registry/Config (schema unificato, versioning, compatibilità);
  7) Test & golden cases (per ogni grande modulo);
  8) Rischi, limiti, raccomandazioni;
  9) Checklist finale aggiornata (TODO sintetico cross‑modulo).

- Mantieni sempre lo stile PLAN, con elenchi di sotto-attività, dipendenze e criteri di accettazione, SENZA mai scendere a livello di codice.

Rimani SEMPRE in modalità PLAN (analisi + pianificazione), senza generare codice.

Documento di espansione (PLAN‑ONLY — NTC2018, ECx, RC, Non‑structural, GUI, Storage, Tests)
Breve nota: questo documento estende e dettaglia il piano già approvato — nessun codice, solo specifiche, regole, task, dipendenze e criteri di accettazione.

1) Teoria di base — principi da codificare nel software
Per ogni area: principio chiave · parametri essenziali · limiti di validità (domini normativi)

Calcestruzzo armato (RC) — core

Principio: equilibrio domanda/capacità (N–M–V interaction). Core: calcolo asse neutro, I1/I2, r_g, M_Rd, V_Rd (con/senza staffe).
Parametri essenziali: area, As, As', d, b_w, f_ck, Ecm, ρ_l, σ_cp, geometria sezionale.
Limiti: formule V_Rd,c valide entro limiti geometrici e ρ_l (NTC §4.x); fuori campo → NOT_APPLICABLE/escalation.
Taglio senza armatura trasversale (V_Rd,c)

Principio: capacità resistente del calcestruzzo non armato modulata da ρ_l e σ_cp; influenza di torsione e fessurazione.
Parametri: b_w, d, f_ck, ρ_l, σ_cp, a_v (arm. longitudinale), presenza di torsione.
Limiti: applicabile solo se ρ_l dentro range normativo; altrimenti uso V_Rd,s o richiesta di staffe.
Sismica globale / elementi non‑strutturali

Principio: domanda = funzione di massa (Wa), Ta, quota z, spettro di piano Sa(Ta,z); Fa ≈ Sa·Wa/qa (EC8/NTC).
Parametri: Wa, z, Ta, soil category, ag, building T1/H, damping ξ, qa, γa.
Limiti: semplificazioni valide se elemento NON influenza risposta globale; altrimenti modellazione globale.
Elementi secondari / non‑structural (NTC §7.2 + EC8)

Principio: valutare stabilità/espulsione (SLV), servizio/danno (SLE), e ancoraggi; usare spettro di piano per domanda sismica.
Parametri: geometria, Wa, z, support/anchor capacity, Ta (stimato o input), qa/γa.
Limiti: NTC fornisce regole semplificate e tabelle; per formule dettagliate usare EC8 §4.3.5.
Geotecnica / fondazioni

Principio: domanda di suolo (q, rimangono cedimenti) vs capacità portante; interfaccia tra carico strutturale e capacità geotecnica.
Parametri: N, M, p_suolo, φ, c, Gs, modulii compressbility.
Limiti: criterio terziario — richiede adattamento a norma geotecnica locale.
Materiali speciali (legno, acciaio, muratura)

Principio: capacità material‑specifica (f_yk, f_tm...), instabilità (buckling), classificazione sezioni.
Parametri: f_yk, f_tm/fm, E, classificazione sezione, slenderness.
Limiti: verifiche normative differenti — usare EC2/EC3 per dettagli ove NTC non specifica.
2) Dove NTC2018 definisce e dove usare Eurocodici
Usare NTC2018 (Cap.7, §7.2/§7.3) per:
criteri generali su elementi non‑strutturali, spettri di piano semplificati, requisiti di prova/controllo, indicazioni su qa e γa (Circolare esplicativa).
Usare EC8 / EC2 / EC3 quando:
NTC è qualitativa o rimanda ad espressioni esterne (es. formula teatro Fa per elementi non‑structural → EC8 §4.3.5),
capacità di ancoraggi e dettagli per connettori → EN / EC3 o standard produttore.
Documentare sempre la fonte in norm_references nel risultato di verifica (es. "NTC2018 §7.3.6.2", "EN1998-1 §4.3.5").
3) Collegamento teoria → INPUT richiesti dal framework
Principali grandezze teoriche e i campi d’input che devono esistere:

Fa (domanda sismica su elemento) ← requires: mass_Wa, Ta (o stimatore), z_elevation, site_ag, soil_category, behavior_qa, importance_gamma_a.
Sa(Ta,z) (spettro di piano) ← requires: CalcContext con spettro o parametri sito (ag, S, T1, H).
V_Rd,c ← requires: bw, d, f_ck, rho_l, sigma_cp (N) — validity checks on rho_l/geometry.
Drift & serviceability thresholds ← requires: geometry, stiffness E, floor system parameters, limit_w (norm).
Anchorage demand ← requires: anchor_positions, anchor_type, anchor_capacity_ref.
Tutti i campi devono essere esposti dal sistema di input comune (vedi sezione 2 successiva).

4) Sistema di input comune — mappa & gerarchia (concept)
4.A Base / gerarchia degli schemi (concettuale)
BaseElementSpec (campi comuni)
id, name, type, material_id, geometry (L,h,s,area), mass_Wa, z_elevation, support_type, influence_on_global_model, schema_version.
Specializzazioni (estensioni semantiche)
RCElementSpec (adds: As, As_prime, bw, d, section_ref, fk, sigma_cp)
SteelElementSpec (adds: section_class, t_profile, Fy, buckling_params)
MasonryElementSpec (adds: fk_m, thickness_s, mortar_props)
SecondaryElementSpec (as defined earlier)
GeotechSpec (adds: soil_params, bearing_capacity, settlement_params)
Principio: composizione (Base + domain extension) — evita duplicazioni.
4.B Campi standardizzabili (da centralizzare)
geometry: {L, h, s, area_proj, volume}
material: {material_id, density, E_modulus, fk}
seismic: {z, site_ag, soil_category, building_T1, H, damping_xi}
metadata/norm: {norm_primary, norm_fallback, class_of_use, schema_version}
support/anchor: {support_type, anchor_type, anchor_capacity_ref}
4.C Uso / mapping
historical_materials.json → material lookup (material_id)
sections.json / SectionGeometry → geometry templates (geometry_profile_ref)
calculation_codes → store qa, γa tables and default parameters per norma
5) Sistema di output comune (VerificationResultItem)
Struttura generica (concept)
check_id, element_id, module (e.g. NTC2018), norm_references, esito, utilisation, critical_combination_id, demand (map), capacity (map), messages, details, timestamp, solver_version.
Adattabilità
demand e capacity sono mappe estensibili (chiavi tipiche: Fa, Ta, Sa, VEd, MEd, anchor_forces, drift_mm).
messages contiene warning/ERROR codes + human text + normative pointer.
Tutti i VerificationResultItem vanno salvati in VerificationResult (aggregato per elemento e per progetto).
6) Architettura software consolidata (package map + responsabilità)
Proposta di package‑map (conceptual)

core_calculus — numeriche di base, SectionGeometry, section_calculations
verification_engine.py — orchestrator, invoca CodeModule
src/codes/ — namespace per normative
src/codes/ntc2018/ — core_checks, secondary_elements, nonstructural, templates
src/codes/ec/ — EC8/EC2/EC3 helpers (fallback implementations)
src/codes/rd2229/, src/codes/dm92/ — legacy adapters (shims)
src/combinations/ — load combination generator (config driven)
src/materials/ — material registry + adapters to historical_materials_loader
src/validation/ — central validators for specs
ui — Tkinter UI (editors, results, secondary editors)
scripts & tests — demos and test suites
config — calculation_codes_loader.py, historical_materials_loader.py, jsoncode files
storage/ or storage.py — import/export, project persistence
Adaptation layer for legacy
src/codes/* includes adapter shims that expose legacy modules (libs/* or softw_components/*) via the CodeModule contract without duplication.
7) GUI interconnesse — visione globale e riuso
Core central panels (single source)
Materials Editor — single canonical editor (used by RC, steel, secondary)
Sections Editor (SectionGeometry) — reuse for element profiles
Norm Selector & Calculation Settings (global)
Combiner / LoadCase Editor (central)
Domain panels (extend core)
RC Verifications Panel (use core inputs + RC-specific fields)
SecondaryElementEditor (extends base editor; presets)
Non‑structural Results Panel (unified results rendering)
Navigation flow (canonical)
Select Norm → Select Project / Element → Edit Inputs (central editors) → Run Verification (engine) → Results (unified panel)
Validation & UX rules
Shared validator service (single place)
Standard field naming and units across all forms
Use presets and library entries to reduce repetitive input
8) Storage / Registry / Config — schema unificato e versioning
Files & responsibilities
config/calculation_codes/*.jsoncode — normative params, qa tables, secondary presets
historical_materials.json — canonical materials; loader returns MaterialProperties
sections.json / sec_repository — SectionGeometry library
project.json (project scope) — includes secondary_elements[], results[], schema_version
registry/presets/*.json — library of element presets
Versioning & migration
every top‑level schema must include schema_version and created_with_version
loader behavior: unknown keys tolerated; migration scripts for schema bumps
Backward compatibility
maintain legacy loaders but expose through CodeModule adapters; deprecate old files with shims and migration path
9) Test strategy & golden cases (refined)
Test pyramid
Unit tests (low‑level functions: Ta estimator, Sa table, Fa calc, V_Rd,c gating)
Integration tests (engine + CodeModule + storage roundtrip)
System/demo tests (UI headless flows, project save/load)
Golden cases (per module) — sources indicated
RC: V_Rd,c examples (NTC §4 examples / handbook cases) — test A/B/C previously listed
Secondary / Non‑structural: BibLus tamponature example (NTC Circolare), EC8 worked examples (JRC, Prota)
Sismica globale: statica equivalente vs modal benchmark (example building)
Anchors: anchor demand vs manufacturer tests (use standards)
Acceptance tolerances
numeric tolerances: ±5% for arithmetic comparisons to worked examples; method alignment (OK/NOT_OK) must match references exactly.
Test data management
store fixtures under tests/fixtures/ntc2018/ with documented reference sources
10) Rischi, limiti, mitigazioni (estesi)
Rischio: interpretazioni diverse NTC vs EC8 → Mitigazione: expose norm_source choice, log normative decisions, show norm_references in output and UI.
Rischio: input quality (Ta, Wa incorrect) → Mitigazione: aggressive validator, default estimators with confidence flags, block SLV if essential fields missing.
Rischio: oversimplification of secondary models → Mitigazione: clear NOT_APPLICABLE gating; recommend “global model required” for flagged cases.
Rischio: duplicate logic across norms → Mitigazione: centralize shared utilities (spectra, Ta_estimators, combinations) and use adapters for norm‑specific rules.
Rischio: user misuses presets as design validation → Mitigazione: display warnings and required assumptions in UI; require confirmation for production outputs.
11) Checklist finale (TODO sintetico, cross‑modulo)
High priority (implementare prima)

 Finalizzare CodeModule contract + registry for checks (NTC2018 + EC fallback)
 Implementare SecondaryElementSpec schema (document + validators)
 Add secondary_elements node in config/calculation_codes/NTC2018.jsoncode (skeleton presets + qa defaults)
 Implement RC_SLU_VRDc_NoStirrups SPEC + golden test cases (unit + integration)
 Centralize spectrum/Ta utilities (shared module) and use in non‑structural checks
 Design & wireframe SecondaryElementEditor + SecondaryResultsPanel (UI MVP)
 Define storage schema versioning & migration plan (include schema_version)
 Create test plan with golden cases (BibLus, EC8 JRC, Prota) and implement fixtures
Medium priority

 Adapter shims for legacy libs and softw_components (if still present)
 Integrate geotechnical adapter interface and basic plinth checks
 Extend documentation (docs/NTC2018_secondary_elements.md, examples)
Acceptance (per milestone)

All new checks exposed via CodeModule.available_checks() and invocable by VerificationEngine
UI uses centralized input schema; project JSON persists secondary elements and results
Test suite green with golden cases and tolerances documented
Fine del piano espanso.
Tutti i punti sopra sono pronti per essere trasformati in specifiche di implementazione (issue/PR/checklist). Vuoi che formalizzi ora (plan‑only) il documento di test‑fixture per il Tamponatura (BibLus / NTC Circolare) o che rediga il Design Doc per CodeModule (contratto di API e mapping dei checks)?

Documento di espansione (PLAN‑ONLY — NTC2018, ECx, RC, Non‑structural, GUI, Storage, Tests)
Breve nota: questo documento estende e dettaglia il piano già approvato — nessun codice, solo specifiche, regole, task, dipendenze e criteri di accettazione.

1) Teoria di base — principi da codificare nel software
Per ogni area: principio chiave · parametri essenziali · limiti di validità (domini normativi)

Calcestruzzo armato (RC) — core

Principio: equilibrio domanda/capacità (N–M–V interaction). Core: calcolo asse neutro, I1/I2, r_g, M_Rd, V_Rd (con/senza staffe).
Parametri essenziali: area, As, As', d, b_w, f_ck, Ecm, ρ_l, σ_cp, geometria sezionale.
Limiti: formule V_Rd,c valide entro limiti geometrici e ρ_l (NTC §4.x); fuori campo → NOT_APPLICABLE/escalation.
Taglio senza armatura trasversale (V_Rd,c)

Principio: capacità resistente del calcestruzzo non armato modulata da ρ_l e σ_cp; influenza di torsione e fessurazione.
Parametri: b_w, d, f_ck, ρ_l, σ_cp, a_v (arm. longitudinale), presenza di torsione.
Limiti: applicabile solo se ρ_l dentro range normativo; altrimenti uso V_Rd,s o richiesta di staffe.
Sismica globale / elementi non‑strutturali

Principio: domanda = funzione di massa (Wa), Ta, quota z, spettro di piano Sa(Ta,z); Fa ≈ Sa·Wa/qa (EC8/NTC).
Parametri: Wa, z, Ta, soil category, ag, building T1/H, damping ξ, qa, γa.
Limiti: semplificazioni valide se elemento NON influenza risposta globale; altrimenti modellazione globale.
Elementi secondari / non‑structural (NTC §7.2 + EC8)

Principio: valutare stabilità/espulsione (SLV), servizio/danno (SLE), e ancoraggi; usare spettro di piano per domanda sismica.
Parametri: geometria, Wa, z, support/anchor capacity, Ta (stimato o input), qa/γa.
Limiti: NTC fornisce regole semplificate e tabelle; per formule dettagliate usare EC8 §4.3.5.
Geotecnica / fondazioni

Principio: domanda di suolo (q, rimangono cedimenti) vs capacità portante; interfaccia tra carico strutturale e capacità geotecnica.
Parametri: N, M, p_suolo, φ, c, Gs, modulii compressbility.
Limiti: criterio terziario — richiede adattamento a norma geotecnica locale.
Materiali speciali (legno, acciaio, muratura)

Principio: capacità material‑specifica (f_yk, f_tm...), instabilità (buckling), classificazione sezioni.
Parametri: f_yk, f_tm/fm, E, classificazione sezione, slenderness.
Limiti: verifiche normative differenti — usare EC2/EC3 per dettagli ove NTC non specifica.
2) Dove NTC2018 definisce e dove usare Eurocodici
Usare NTC2018 (Cap.7, §7.2/§7.3) per:
criteri generali su elementi non‑strutturali, spettri di piano semplificati, requisiti di prova/controllo, indicazioni su qa e γa (Circolare esplicativa).
Usare EC8 / EC2 / EC3 quando:
NTC è qualitativa o rimanda ad espressioni esterne (es. formula teatro Fa per elementi non‑structural → EC8 §4.3.5),
capacità di ancoraggi e dettagli per connettori → EN / EC3 o standard produttore.
Documentare sempre la fonte in norm_references nel risultato di verifica (es. "NTC2018 §7.3.6.2", "EN1998-1 §4.3.5").
3) Collegamento teoria → INPUT richiesti dal framework
Principali grandezze teoriche e i campi d’input che devono esistere:

Fa (domanda sismica su elemento) ← requires: mass_Wa, Ta (o stimatore), z_elevation, site_ag, soil_category, behavior_qa, importance_gamma_a.
Sa(Ta,z) (spettro di piano) ← requires: CalcContext con spettro o parametri sito (ag, S, T1, H).
V_Rd,c ← requires: bw, d, f_ck, rho_l, sigma_cp (N) — validity checks on rho_l/geometry.
Drift & serviceability thresholds ← requires: geometry, stiffness E, floor system parameters, limit_w (norm).
Anchorage demand ← requires: anchor_positions, anchor_type, anchor_capacity_ref.
Tutti i campi devono essere esposti dal sistema di input comune (vedi sezione 2 successiva).

4) Sistema di input comune — mappa & gerarchia (concept)
4.A Base / gerarchia degli schemi (concettuale)
BaseElementSpec (campi comuni)
id, name, type, material_id, geometry (L,h,s,area), mass_Wa, z_elevation, support_type, influence_on_global_model, schema_version.
Specializzazioni (estensioni semantiche)
RCElementSpec (adds: As, As_prime, bw, d, section_ref, fk, sigma_cp)
SteelElementSpec (adds: section_class, t_profile, Fy, buckling_params)
MasonryElementSpec (adds: fk_m, thickness_s, mortar_props)
SecondaryElementSpec (as defined earlier)
GeotechSpec (adds: soil_params, bearing_capacity, settlement_params)
Principio: composizione (Base + domain extension) — evita duplicazioni.
4.B Campi standardizzabili (da centralizzare)
geometry: {L, h, s, area_proj, volume}
material: {material_id, density, E_modulus, fk}
seismic: {z, site_ag, soil_category, building_T1, H, damping_xi}
metadata/norm: {norm_primary, norm_fallback, class_of_use, schema_version}
support/anchor: {support_type, anchor_type, anchor_capacity_ref}
4.C Uso / mapping
historical_materials.json → material lookup (material_id)
sections.json / SectionGeometry → geometry templates (geometry_profile_ref)
calculation_codes → store qa, γa tables and default parameters per norma
5) Sistema di output comune (VerificationResultItem)
Struttura generica (concept)
check_id, element_id, module (e.g. NTC2018), norm_references, esito, utilisation, critical_combination_id, demand (map), capacity (map), messages, details, timestamp, solver_version.
Adattabilità
demand e capacity sono mappe estensibili (chiavi tipiche: Fa, Ta, Sa, VEd, MEd, anchor_forces, drift_mm).
messages contiene warning/ERROR codes + human text + normative pointer.
Tutti i VerificationResultItem vanno salvati in VerificationResult (aggregato per elemento e per progetto).
6) Architettura software consolidata (package map + responsabilità)
Proposta di package‑map (conceptual)

core_calculus — numeriche di base, SectionGeometry, section_calculations
verification_engine.py — orchestrator, invoca CodeModule
src/codes/ — namespace per normative
src/codes/ntc2018/ — core_checks, secondary_elements, nonstructural, templates
src/codes/ec/ — EC8/EC2/EC3 helpers (fallback implementations)
src/codes/rd2229/, src/codes/dm92/ — legacy adapters (shims)
src/combinations/ — load combination generator (config driven)
src/materials/ — material registry + adapters to historical_materials_loader
src/validation/ — central validators for specs
ui — Tkinter UI (editors, results, secondary editors)
scripts & tests — demos and test suites
config — calculation_codes_loader.py, historical_materials_loader.py, jsoncode files
storage/ or storage.py — import/export, project persistence
Adaptation layer for legacy
src/codes/* includes adapter shims that expose legacy modules (libs/* or softw_components/*) via the CodeModule contract without duplication.
7) GUI interconnesse — visione globale e riuso
Core central panels (single source)
Materials Editor — single canonical editor (used by RC, steel, secondary)
Sections Editor (SectionGeometry) — reuse for element profiles
Norm Selector & Calculation Settings (global)
Combiner / LoadCase Editor (central)
Domain panels (extend core)
RC Verifications Panel (use core inputs + RC-specific fields)
SecondaryElementEditor (extends base editor; presets)
Non‑structural Results Panel (unified results rendering)
Navigation flow (canonical)
Select Norm → Select Project / Element → Edit Inputs (central editors) → Run Verification (engine) → Results (unified panel)
Validation & UX rules
Shared validator service (single place)
Standard field naming and units across all forms
Use presets and library entries to reduce repetitive input
8) Storage / Registry / Config — schema unificato e versioning
Files & responsibilities
config/calculation_codes/*.jsoncode — normative params, qa tables, secondary presets
historical_materials.json — canonical materials; loader returns MaterialProperties
sections.json / sec_repository — SectionGeometry library
project.json (project scope) — includes secondary_elements[], results[], schema_version
registry/presets/*.json — library of element presets
Versioning & migration
every top‑level schema must include schema_version and created_with_version
loader behavior: unknown keys tolerated; migration scripts for schema bumps
Backward compatibility
maintain legacy loaders but expose through CodeModule adapters; deprecate old files with shims and migration path
9) Test strategy & golden cases (refined)
Test pyramid
Unit tests (low‑level functions: Ta estimator, Sa table, Fa calc, V_Rd,c gating)
Integration tests (engine + CodeModule + storage roundtrip)
System/demo tests (UI headless flows, project save/load)
Golden cases (per module) — sources indicated
RC: V_Rd,c examples (NTC §4 examples / handbook cases) — test A/B/C previously listed
Secondary / Non‑structural: BibLus tamponature example (NTC Circolare), EC8 worked examples (JRC, Prota)
Sismica globale: statica equivalente vs modal benchmark (example building)
Anchors: anchor demand vs manufacturer tests (use standards)
Acceptance tolerances
numeric tolerances: ±5% for arithmetic comparisons to worked examples; method alignment (OK/NOT_OK) must match references exactly.
Test data management
store fixtures under tests/fixtures/ntc2018/ with documented reference sources
10) Rischi, limiti, mitigazioni (estesi)
Rischio: interpretazioni diverse NTC vs EC8 → Mitigazione: expose norm_source choice, log normative decisions, show norm_references in output and UI.
Rischio: input quality (Ta, Wa incorrect) → Mitigazione: aggressive validator, default estimators with confidence flags, block SLV if essential fields missing.
Rischio: oversimplification of secondary models → Mitigazione: clear NOT_APPLICABLE gating; recommend “global model required” for flagged cases.
Rischio: duplicate logic across norms → Mitigazione: centralize shared utilities (spectra, Ta_estimators, combinations) and use adapters for norm‑specific rules.
Rischio: user misuses presets as design validation → Mitigazione: display warnings and required assumptions in UI; require confirmation for production outputs.
11) Checklist finale (TODO sintetico, cross‑modulo)
High priority (implementare prima)

 Finalizzare CodeModule contract + registry for checks (NTC2018 + EC fallback)
 Implementare SecondaryElementSpec schema (document + validators)
 Add secondary_elements node in config/calculation_codes/NTC2018.jsoncode (skeleton presets + qa defaults)
 Implement RC_SLU_VRDc_NoStirrups SPEC + golden test cases (unit + integration)
 Centralize spectrum/Ta utilities (shared module) and use in non‑structural checks
 Design & wireframe SecondaryElementEditor + SecondaryResultsPanel (UI MVP)
 Define storage schema versioning & migration plan (include schema_version)
 Create test plan with golden cases (BibLus, EC8 JRC, Prota) and implement fixtures
Medium priority

 Adapter shims for legacy libs and softw_components (if still present)
 Integrate geotechnical adapter interface and basic plinth checks
 Extend documentation (docs/NTC2018_secondary_elements.md, examples)
Acceptance (per milestone)

All new checks exposed via CodeModule.available_checks() and invocable by VerificationEngine
UI uses centralized input schema; project JSON persists secondary elements and results
Test suite green with golden cases and tolerances documented
Fine del piano espanso.
Tutti i punti sopra sono pronti per essere trasformati in specifiche di implementazione (issue/PR/checklist). Vuoi che formalizzi ora (plan‑only) il documento di test‑fixture per il Tamponatura (BibLus / NTC Circolare) o che rediga il Design Doc per CodeModule (contratto di API e mapping dei checks)?