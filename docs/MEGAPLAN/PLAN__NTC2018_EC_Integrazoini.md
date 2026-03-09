Sei un assistente di sviluppo per un ingegnere strutturista che lavora con Python e Tkinter su verifiche secondo la normativa NTC2018.

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

IMPORTANTE: rimani sempre e solo in "modalità Plan". Non generare codice. Non proporre implementazioni. Limita la tua attività esclusivamente alla pianificazione, alla definizione di fasi, dipendenze, attività e roadmap tecnica.
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

PROMPT INCREMENTALE SUL PIANO PRECEDENTE (NON GENERARE CODICE)

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
  <https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=18A0071600100010110001&dgu=2018-02-20&art.dataPubblicazioneGazzetta=2018-02-20&art.codiceRedazionale=18A00716&art.num=1&art.tiposerie=SG>  [1](https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?cdimg=18A0071600100010110001&dgu=2018-02-20&art.dataPubblicazioneGazzetta=2018-02-20&art.codiceRedazionale=18A00716&art.num=1&art.tiposerie=SG)
- Estratto Cap.7 PDF: <https://www.studiopetrillo.com/files/ntc2018/cap7.pdf>  [2](https://www.studiopetrillo.com/files/ntc2018/cap7.pdf)
- Ulteriore estratto NTC2018 Cap.7: <https://www.bertolinoengineering.it/wp-content/uploads/2024/08/NTC2018_cap7.pdf>  [3](https://www.bertolinoengineering.it/wp-content/uploads/2024/08/NTC2018_cap7.pdf)

Approfondimenti sugli elementi non strutturali (NTC):

- “Elementi non strutturali in zona sismica, NTC 2008 vs NTC 2018”:  
  <https://www.ingenio-web.it/articoli/elementi-costruttivi-non-strutturali-negli-edifici-in-c-a-in-zona-sismica-cosa-cambia-con-le-ntc-2018/>  [4](https://www.ingenio-web.it/articoli/elementi-costruttivi-non-strutturali-negli-edifici-in-c-a-in-zona-sismica-cosa-cambia-con-le-ntc-2018/)
- “Verifiche elementi non strutturali – quadro completo”:  
  <https://ediltecnico.it/verifiche-elementi-non-strutturali/>  [5](https://ediltecnico.it/verifiche-elementi-non-strutturali/)
- “Dettagli tecnici elementi non strutturali (NTC 2018)”:  
  <https://www.bmigroup.com/it/intervenire-sul-tetto/progettare-il-tetto/sismico/verifica-vulnerabilita-sismica-ntc/>  [6](https://www.bmigroup.com/it/intervenire-sul-tetto/progettare-il-tetto/sismico/verifica-vulnerabilita-sismica-ntc/)

EUROCODICE 8 — ELEMENTI NON STRUTTURALI:

- Testo completo EN 1998‑1 (PDF):  
  <https://www.phd.eng.br/wp-content/uploads/2015/02/en.1998.1.2004.pdf>  [7](https://www.phd.eng.br/wp-content/uploads/2015/02/en.1998.1.2004.pdf)
- Guida Prota “Seismic forces on non-structural members (EC8 4.3.5)”:  
  <https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members>  [8](https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members)
- White paper: “Non-Structural Member Forces EC8”:  
  <https://protasoftware.com/white-paper/non-structural-member-forces-ec8/>  [9](https://protasoftware.com/white-paper/non-structural-member-forces-ec8/)
- JRC Worked Examples – EC8:  
  <https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EC8_Seismic_Design_of_Buildings-worked_examples-main_only.pdf>  [10](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EC8_Seismic_Design_of_Buildings-Worked_examples-main_only.pdf)

ESEMPI NUMERICI PER TEST DI VALIDAZIONE:

- Verifica tamponature con spettri di piano (NTC2018 + Circ. 2019):  
  <https://biblus.acca.it/la-verifica-delle-tamponature-secondo-le-nuove-ntc-2018-e-la-circolare-2019/>  [11](https://biblus.acca.it/la-verifica-delle-tamponature-secondo-le-nuove-ntc-2018-e-la-circolare-2019/)
- Esempio EC8 di calcolo forze su elementi non strutturali (Prota):  
  <https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members>  [8](https://support.protasoftware.com/portal/en/kb/articles/seismic-forces-on-non-structural-members)
- EC8 worked examples – drift e componenti fragili:  
  <https://www.slideshare.net/slideshow/ec8-seismic-designofbuildingsworkedexamples/48158324>  [12](https://www.slideshare.net/slideshow/ec8-seismic-designofbuildingsworkedexamples/48158324)

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
