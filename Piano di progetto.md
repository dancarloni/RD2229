You are GitHub Copilot Agent. Execute the entire task in ONE pass, without asking follow‑up questions and without splitting into multiple requests. If information is missing, make the smallest safe assumptions and proceed.

GOAL
Refactor and implement the requested feature in my Python/Tkinter engineering app, keeping strict separation between GUI and calculation modules.

SCOPE

- Language: Python 3.x
- GUI: Tkinter (with necessary external dependencies, to be imported in .venv)
- Domain: civil/structural engineering utilities (sections, materials, checks)
- Style: professional, cautious, transparent logs of every calculation step

INPUTS (replace placeholders)

- Target module(s): <path/to/module.py>, <path/to/gui.py>
- Feature/spec: <paste concise requirements here, including I/O>
- Constraints:
  - Keep lines ≤ 100 chars
  - Black/Ruff compliant
  - No network calls
  - Immutable public APIs unless specified
  - Avoid breaking existing tests
  - Logging with rotation (size‑based), DEBUG togglable
- Data persistence: JSON/CSV only (UTF‑8), no DB

DELIVERABLES

1) Complete code edits for all affected files (show unified diffs).
2) New/updated unit tests (pytest), covering edge cases.
3) Docstrings (Google style) + inline comments for tricky logic.
4) CHANGELOG entry (concise) + brief migration notes if needed.
5) A single final recap: what changed, assumptions made, and how to revert.

RULES

- Do not ask me anything back. Do not start a second task.
- Minimize file churn; change only what is necessary.
- Prefer pure functions; isolate side effects.
- For UI: responsive layout, keyboard navigation (Tab/Enter/Arrows), tooltips where useful.
- For plots/exports: label axes/units; keep terminology in Italian when user‑facing.
- For calculations: show safety factors, normative coefficients, and intermediate steps in logs.
- massima modularità del codice, delle gui, delle funzioni, dei database
- limita al massimo le modifiche del codice, non modificare gui, funzioni già funzionanti
- non inventare. se c

CHECKLIST BEFORE OUTPUT

- [ ] All changes compile and run
- [ ] Tests pass locally (explain new tests)
- [ ] No line > 100 chars; no trailing whitespace
- [ ] Sorting/filtering in tables preserved
- [ ] No additional prompts required from user

"Context",
      "- Linguaggio: Python 3.x",
      "- GUI: Tkinter",
      "- Repository: ${1:descrizione sintetica (app/gui, app/core, tests, requirements)}",
      "- Norme/Metodi: RD 2229/39, Santarella/Giangreco, TA/SLU/SLE",
      "- Vincoli UX: suggerimenti, tastiera, tooltips, adattività, wrapping, errori chiari, logging, help formule, stato persistente.",
      "",
      "Initial Tasks",
      "1) Mappa del codice (ruoli/entry points). Ignora venv/.cache.",
      "2) Identifica GUI input, logica calcolo, utilità comuni.",
      "3) Piano di rifattorizzazione leggero per contratti (CalcInput/CalcOutput + Protocol), controller GUI e spostamento servizi in app/core/services.",
      "4) Implementa collegamento end-to-end (wiring bottone, threading, validazioni, update view).",
      "",
      "Acceptance Criteria",
      "- Avvio: `python -m app.main` apre la GUI.",
      "- Dati di esempio → ‘Calcola’ produce CalcOutput.ok e popola risultati senza freeze.",
      "- `pytest -q` passa test core + 1 integrazione.",
      "- Lint/format ok (ruff/flake8/black o tool repo).",
      "",
      "Guardrails & Constraints",
      "- Non rompere API pubbliche senza motivo; documenta cambi se necessari.",
      "- Commits chiari; preserva selettore metodo (TA/SLU/SLE/Santarella) e tracciabilità fonti.",
      "- Test e doc minimi inclusi.",
      "",
      "Deliverables",
      "- `app/core/contracts.py`, un service in `app/core/services/`, `app/gui/controller.py` + wiring, tests core+integrazione, README aggiornato.",
      "",
      "Execution Notes",
      "- Procedi per batch: (1) mappa+piano, (2) contratti+service, (3) controller+wiring, (4) test+lint+doc.",
      "- Se ambiguità su campi input/output: usa placeholder ragionevoli, documenta TODO.",

##

voglio un prompt per richiedere il ripristino delle funzionalità dello workspace, visto che dopo un refactoring e un linting il software non si avvia più.
Una volta ricreato il verification module, voglio che tutto sia funzionante come già previsto.
senza eseguire modifiche al codice se non necessarie, verifica che i collegamenti funzionino, che i campi di selezione facciano riferimento ai repository e ai sistemi di selezione dei dati.
di seguito riporto il funzionamento di alcuni moduli.

##################################
geometry module:
il geometry module non deve essere modificato, se non per i necessari collegamenti e per mantenere il massimo livello di modularità e separazione.

material module
il material module è già funzionante in modo corretto.
senza modificare le funzionalità esistenti, senza riscivere completamente il codice è necessario aggiungere una nuova funzione per i materiali esistenti inseriti ai sensi dell'NTC2008, dell'NTC2018, dell' Eurocodice EC2.
di seguito alcuni riferimenti normativi relativi all'Eurocodice 2:

1. Eurocodice 2 – EN 1992‑1‑1 (seconda generazione, 2023) – Annex I: Assessment of existing structures
La versione aggiornata dell’Eurocodice 2 (BS EN 1992‑1‑1:2023) introduce l’Allegato I, interamente dedicato alla valutazione delle strutture esistenti in c.a., comprensivo di:

caratterizzazione dei materiali sulla base di prove in situ;
gestione dell’incertezza e della variabilità dei parametri meccanici;
criteri per la valutazione della resistenza residua;
indicazioni per elementi con dettagli costruttivi storici.

Queste informazioni sono confermate dalle fonti tecniche consultate, che precisano che Annex I è informativo e pensato per la valutazione di strutture esistenti in c.a. [scispace.com]

1. Eurocodice 0 – prEN 1990‑2 (in fase di introduzione) – Basis of assessment and retrofitting of existing structures
La nuova versione dell’Eurocodice 0 include una nuova parte dedicata esclusivamente alla valutazione e al rinforzo delle strutture esistenti, che definisce:

principi generali di valutazione;
criteri di analisi e verifiche specifiche per l’esistente;
approcci per interventi e retrofitting.

È indicato come documento complementare all’EC2 per l’esistente. [scispace.com]

1. Quadro generale europeo in evoluzione
Il JRC conferma che sono in sviluppo nuove regole europee specifiche per le strutture esistenti, pensate per integrare gli Eurocodici esistenti e armonizzare le metodologie nazionali. [eurocodes.....europa.eu]

In sintesi
Se la domanda è “in quale Eurocodice si parla di calcestruzzo armato esistente?”, la risposta corretta è:
👉 Eurocodice 2 – EN 1992‑1‑1 (2023), Annex I – Assessment of existing structures
👉 Eurocodice 0 – prEN 1990‑2, che definisce la base di valutazione per tutte le strutture esistenti.

RIFERIMENTI EUROCODICI E STRUTTURE ESISTENTI

1. Assessment of Existing Concrete Structures Under Second‑Generation Eurocode 2
<https://structurescentre.com/assessment-of-existing-concrete-structures-under-second-generation-eurocode-2/>

2. New technical rules on existing structures – Eurocodes: Building the future (JRC)
<https://eurocodes.jrc.ec.europa.eu/2nd-generation-evolution/new-technical-rules-existing-structures>

3. 2nd Generation Eurocode 2 – Concrete Centre
<https://www.concretecentre.com/Structural-design/Eurocode-2-concrete/2nd-Generation-Eurocode-2.aspx>

4. Contributions of the Future Eurocode 2 for Assessment of Existing Concrete Structures (Hormigón y Acero)
<https://scispace.com/pdf/contributions-of-the-future-eurocode-for-the-assessment-of-ekbcbedi.pdf>

5. Provisions for assessment of existing structures in the second‑generation concrete Eurocode (IStructE)
<https://www.istructe.org/journal/volumes/volume-102-%282024%29/issue-4/ec2-assessment-of-existing-structures/>

6. Contributions of the Future Eurocode for the Assessment of Existing Concrete Structures (Academia.edu)
<https://www.academia.edu/128798578/Contributions_of_the_Future_Eurocode_for_the_Assessment_of_Existing_Concrete_Structures>

---
CONFRONTO CON NTC 2008 E NTC 2018

NTC 2008:

- Impostazione tradizionale basata su livelli di conoscenza (LC1-2-3) e fattori di confidenza.
- Approccio globale senza capitoli specifici dedicati esclusivamente alle strutture esistenti in c.a., ma con criteri generali per edifici esistenti.
- Metodologia fortemente orientata al miglioramento sismico minimo richiesto.

NTC 2018:

- Aggiornamento e razionalizzazione dei livelli di conoscenza.
- Maggiore attenzione alla caratterizzazione meccanica dei materiali esistenti tramite prove in-situ.
- Processo valutativo più coerente con gli Eurocodici, pur mantenendo struttura normativa nazionale.
- Introduzione di criteri più dettagliati per le verifiche locali e globali.

Confronto sintetico:

- Eurocodice 2 (Annex I) e prEN1990-2 introducono un approccio europeo specifico per l’esistente, più avanzato nella gestione dell’incertezza.
- NTC 2018 mantiene l’impianto nazionale ma risulta più allineata alle logiche europee rispetto alla NTC 2008.
- Eurocodici pongono forte enfasi sulla caratterizzazione dei materiali esistenti in opere in c.a. mediante prove dirette.
- NTC 2008 e NTC 2018 introducono invece livelli di conoscenza e fattori di confidenza, assenti nell’EC2.

le funzionalità di selezione e applicazione dei livelli di conoscenza  e fattori di confidenza deve essere disponibile per materiali esistenti.
i materiali classificati come nuovi non devono consentire l'inserimento di livelli di conoscenza e fattori di confidenza.

di seguito alcune informazioni utili e collegamenti che devi utilizzare

# Tabella comparativa – Strutture esistenti (EC2, prEN 1990-2, NTC 2008/2018)

| Codice | Parte / Sezione | Stato | Vincolatività | Ambito esistente | Punti chiave | LC/FC | Classificazione interventi |
|---|---|---|---|---|---|---|---|
| EN 1992-1-1 | Annex I | pubblicato (2023) | Informativo | Sì | Materiali in-situ, incertezza/dispersione, test ed estrapolazione motivata | n.d. | n.d. (rinvio a EN 1990-2 / norme nazionali) |
| prEN 1990-2 | Parte 2 | **bozza** (2024→) | Normativo (quando adottato) | Sì | Principi generali per valutazione e azioni; non copre progetto di nuovi elementi; sisma in EN 1998-3 | n.d. | Principi generali (non categorie nazionali) |
| NTC 2008 | Cap. 8 | sostituito | Normativo | Sì | Valutazione sicurezza; prime definizioni LC/FC; schema interventi | LC1–LC3 + FC | Locale / Miglioramento / Adeguamento |
| NTC 2018 | Cap. 8 (+ Circ. 2019) | vigente | Normativo | Sì | Razionalizzazione LC/FC; centralità interventi locali; criteri dettagliati | LC1–LC3 + FC=1.35/1.20/1.00 | Locale / Miglioramento / Adeguamento |

> **Note d’uso**: utilizzare il JSON per l’integrazione software; il CSV per import rapidi; la presente tabella per la consultazione.

tabella comparativa avanzata pronta per l’integrazione in un software sviluppato in Visual Studio Code (Python/Tkinter, web o CLI). Ti consegno tre formati:

JSON (machine‑readable, consigliato per l’app): comparativa_norme_esistente.json
CSV (import rapido in fogli di calcolo o librerie pandas): comparativa_norme_esistente.csv
Markdown (anteprima umana/README): comparativa_norme_esistente.md

Contenuto tecnico (fonti verificate)
La tabella copre:

EN 1992‑1‑1:2023 (EC2) – Annex I: introduce un allegato informativo per la valutazione delle strutture in c.a. esistenti, focalizzato su caratterizzazione materiali in‑situ, gestione dell’incertezza/dispersione e uso di prove con estrapolazione ragionata quando l’accessibilità è limitata. [eu-prod.as...rosoft.com], [eu-prod.as...rosoft.com], [eu-prod.as...rosoft.com]
prEN 1990‑2 (bozza): parte dedicata alla valutazione delle strutture esistenti con principi generali e regole per le azioni in fase di assessment (complemento a EN 1991); non copre la progettazione di nuovi elementi e rimanda a EN 1998‑3 per il sismico. Stato: draft (conversione della CEN/TS 17440). [en-standard.eu], [scispace.com], [structurescentre.com]
NTC 2008 – Cap. 8: introduce in modo sistematico Livelli di Conoscenza (LC1–LC3) e Fattori di Confidenza (FC) e la classificazione degli interventi (locale, miglioramento, adeguamento). [cdn.standa...ds.iteh.ai], [austrian-s...andards.at], [eurocodes.....europa.eu]
NTC 2018 – Cap. 8 + Circolare 2019 (Cap. C8): conferma e razionalizza LC/FC (valori tipici 1.35/1.20/1.00), dà rilievo agli interventi locali e struttura con maggiore dettaglio il processo di valutazione e gli interventi. [online.scu...ichelli.it], [Decreto de...azione ...], [ediltecnico.it]

Nota: nel JSON ogni voce include anche gli URL ufficiali/tecnici utili per la tracciabilità.

Schema dati (JSON) — pronto per l’app
Ogni record ha i seguenti campi (pensati per filtri, mapping UI e logiche di verifica):
JSON{  "code": "EN 1992-1-1",  "part": "Annex I",  "title": "Eurocode 2 – Design of concrete structures: Annex I – Assessment of existing structures",  "jurisdiction": "EU",  "status": "published | draft | current | replaced",  "publication_date": "YYYY-MM-DD",  "binding": "informative | normative (when adopted) | normative",  "scope_existing": true,  "core_topics": ["..."],  "lc_fc_applicability": "descrizione sintetica",  "interventions_classification": "descrizione sintetica",  "notes": "contesto e limiti applicativi",  "evidence_links": ["url1", "url2", "..."]}``Mostra più linee
File: comparativa_norme_esistente.json

Esempi d’uso (drop‑in in Visual Studio Code)

1) Python (Tkinter o backend di calcolo)
Carica, filtra e usa i dati in un’app Tkinter o CLI:
Pythonimport jsonfrom pathlib import PathDATA = json.loads(Path("comparativa_norme_esistente.json").read_text(encoding="utf-8"))# Filtri tipiciec2_annex = [r for r in DATA if r["code"] == "EN 1992-1-1" and r["part"] == "Annex I"]ntc_correnti = [r for r in DATA if r["code"].startswith("NTC") and r["status"] in {"current"}]# Esempio: ottieni valori LC/FC (NTC 2018)ntc2018 = next(r for r in DATA if r["code"] == "NTC 2018")print(ntc2018["lc_fc_applicability"])  # "Confermati LC1–LC3; FC tipici 1.35 / 1.20 / 1.00 ..."Mostra più linee
(Motivazione tecnica: LC/FC e classificazioni interventi derivano da Cap. 8 NTC 2018 e relativa Circolare; i valori tipici 1.35/1.20/1.00 sono riportati nel § C8.5.4.) [online.scu...ichelli.it], [ediltecnico.it]
2) TypeScript (web UI con tabella)
TypeScriptexport interface NormRecord {  code: string;  part: string;  title: string;  jurisdiction: "EU" | "IT";  status: "published" | "draft" | "current" | "replaced";  publication_date: string; // ISO yyyy-mm-dd  binding: string;  scope_existing: boolean;  core_topics: string[];  lc_fc_applicability: string;  interventions_classification: string;  notes: string;  evidence_links: string[];}``Mostra più linee

Anteprima umana (Markdown)
Per portali/README: comparativa_norme_esistente.md
La tabella evidenzia, tra l’altro, che EC2:2023 – Annex I è informativo e mirato all’assessment su c.a. esistente, da usare con i principi generali di EN 1990(-2) e l’Annex Nazionale; mentre prEN 1990‑2 fornisce il quadro generale per l’assessment e le azioni, con esclusione del progetto di nuovi elementi (il sismico resta in EN 1998‑3). [eu-prod.as...rosoft.com], [eu-prod.as...rosoft.com], [en-standard.eu], [scispace.com]

Come estendere “riferimenti futuri”

Aggiungi nuovi record allo stesso schema (es. EN 1998‑3 per l’esistente in ambito sismico, quando necessario), impostando status e publication_date.
Integra eventuali National Annex o Linee Guida interne aggiungendo campi come national_annex_ref o local_policy_ref (string o array).
Mantieni i link di evidenza per la tracciabilità tecnica e normativa (URL a GU, JRC, BSI, ecc.). (Il JRC anticipa da anni le regole europee per l’esistente e ne documenta la progressione: utile per tracking degli aggiornamenti.) [structurescentre.com]

Verifiche di coerenza normativa (pillole utili per il software)

EC2:2023 – Annex I: assessment su c.a. esistente → caratterizzazione materiali in‑situ, incertezza/dispersione, prove con estrapolazione ragionata (informativo, non introduce LC/FC). [eu-prod.as...rosoft.com], [eu-prod.as...rosoft.com], [eu-prod.as...rosoft.com]
prEN 1990‑2: quadro normativo generale per l’assessment (azioni, principi, interventi), senza specifiche di materiale; seismicità demandata a EN 1998‑3; non copre il progetto di nuovi elementi. [en-standard.eu], [scispace.com]
NTC 2008/2018: Cap. 8 regola l’esistente in Italia con LC/FC e classificazione degli interventi; in NTC 2018 i FC tipici sono 1.35/1.20/1.00 (Circ. § C8.5.4) e cresce l’attenzione agli interventi locali. [cdn.standa...ds.iteh.ai], [online.scu...ichelli.it], [ediltecnico.it]

devo scrivere un software per il calcolo strutturale.

In questa fase devo descrivere un modulo del software che consente di definire i parametri i coefficienti, tutte le impostazioni e coefficienti da definire a cura del progettista relative ai materiali, alle azioni, alle verifiche di calcolo previste dalle seguenti normative:

- RD2229/39
- DM92
- DM96
- NTC2008
- NTC2018
- EC2
- prevedere di poter implementare ulteriori normative future mediante appositi moduli

per poter eseguire verifiche a:

- flessione semplice
- flessione deviata
- Presso/tenso flessione semplice
- presso/tenso flessione deviata
- compressione/trazione
- taglio
- torsione
- taglio torsione
- minimi di armatura a flessione
- minimi di armatura a taglio
- tensioni di esercizio
- verifiche alle tensioni ammissibili
- verifiche allo stato limite ultimo
- verifiche allo stato limite di collasso
- apertura delle fessure
- fessurazione
- stato limite di operativita
- deformazioni ammissibili

L'interfaccia deve consentire di inserire in modo semplice e veloce, sfruttando automatismi, autocompletamento, completamento previsionale, menu a tendina, filtri di selezione o inserimento diretto:

- nome dell'elemento soggetto a verifica (inserimento diretto)
- le caratteristiche delle sezioni (da repository sezioni)
- le caratteristiche dei materiali (da repository materiali)
- normativa da applicare (da archivio normative, questo da creare)
- la normativa applicata.
- Azioni N, Tx ,Ty, Mx, My, Mz (inserimento diretto)
- Area delle Armature As, As', (inserimento diretto o calcolo automatico con helper già definito nel workspace)
- Altezze utili dal lembo superiore della sezione (d, d') (inserimento diretto, con controllo di compatibilità geometrica rispetto la sezione scelta)
- diametro delle staffe (inserimento diretto)
- numero di bracci delle staffe (inserimento diretto)
- passo delle staffe (inserimento diretto)
- Area dei ferri piegati (con helper o inserimento diretto) (vedi limitazioni RD2229 e altre normative)

Una volta definiti tutti questi parametri, necessari per la descrizione completa degli elementi da sottoporre a verifica, il software deve ricavare tutte le caratteristiche geometriche, meccaniche, dei materiali selezionati da inserire nel codice di calcolo.

per ogni elemento così inizializzato, deve essere eseguito il calcolo secondo la normativa selezionata e di seguito ai dati inseriti dall'utente il software deve calcolare: posizione dell'asse neutro rispetto il bordo superiore della sezione, coefficienti di sicurezza e tassi di utilizzo ai sensi della normativa selezionata e delle verifiche condotte (vedi sopra le verifiche).

le verifiche di ciascun elemento strutturale inserito devono essere eseguite appena terminato l'inserimento dei dati per quell'elemento strutturale.

ottimizza le funzioni di calcolo, di verifica per evitare calcoli in eccesso.
Fai in modo che tutto sia modulare, i dati recuperati dinamicamente.

NON INVENTARE MAI. in caso di dubbi chiedi a me.
