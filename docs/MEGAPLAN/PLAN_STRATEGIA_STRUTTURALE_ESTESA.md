
PLAN STRATEGIA STRUTTURALE ESTESA
Status: VINCOLO DURO (estendibile solo previa richiesta esplicita dell’utente)

1. Scopo del documento
Questo PLAN definisce la strategia complessiva e vincolante per lo sviluppo del software di calcolo strutturale in Python + Tkinter, da realizzare in VS Code con GitHub Copilot Pro, garantendo:

coerenza architetturale;
tracciabilità tecnico‑normativa;
separazione rigorosa tra metodi di calcolo, norme, GUI e output;
possibilità di estensione futura controllata (muratura, edifici esistenti, FEM, ecc.).
Il documento recepisce e cristallizza le decisioni strategiche fornite dall’utente (Q1–Q5).

1. Priorità di sviluppo (vincolanti)
Ordine di priorità obbligatorio per tutte le roadmap e i sottopiani:

Calcestruzzo armato – NTC2018 (elementi singoli e telai piani)
Metodo di Cross per telai piani
Muratura (solo pianificazione architetturale iniziale)
Edifici esistenti (ζE, miglioramento/adeguamento – pianificazione successiva)
Nessun modulo di priorità inferiore può introdurre dipendenze che ostacolino o ritardino quelli superiori.

1. Ruolo del Metodo di Cross
Il Metodo di Cross è definito come:

Metodo di calcolo strutturale autonomo (engine interno) ✅
Metodo applicabile in ambito normativo (NTC2018, DM96, EC come fallback) ✅
Strumento didattico e professionale ✅
Conseguenze architetturali:

il metodo non appartiene a una norma;
le norme consumano i risultati del metodo;
il metodo deve produrre output intermedi tracciabili (momenti, rotazioni, iterazioni);
la GUI può opzionalmente visualizzare i passaggi (modalità “didattica”).

1. Muratura – Stato attuale
La muratura è fuori dallo scope implementativo immediato.
In questa fase:

è ammessa solo pianificazione architetturale;
devono essere predisposti:modelli concettuali;
workflow;
interfacce con sismica e metodi di calcolo.
Le verifiche dei meccanismi locali (ribaltamento, flessione fuori piano, cinematismi) sono esplicitamente rimandate a fasi future.

1. Relazione di calcolo e difendibilità legale
Requisito obbligatorio:
Il software deve poter produrre una relazione di calcolo difendibile, che:

citi automaticamente:norma applicata;
capitolo;
paragrafo;
distingua chiaramente:NTC2018;
DM92 / DM96;
Eurocodici (fallback dichiarato);
consenta, quando tecnicamente sensato:confronto tra norme sullo stesso elemento.
Questo requisito impatta direttamente:

PLAN_OUTPUT_COMUNE;
struttura dei VerificationResultItem;
knowledge base normative.

1. Regime dei PLAN (vincoli duri)
Tutti i PLAN del progetto sono:

vincoli architetturali duri;
non violabili da Copilot;
non derogabili automaticamente.
È ammesso:

estendere un PLAN;
integrare nuovi moduli;
solo previa richiesta esplicita dell’utente, con aggiornamento formale del PLAN interessato.

1. Suddivisione concettuale del sistema
Struttura logica obbligatoria:

Metodi di calcolo (Cross, elastico, FEM futuro)
Norme (RD2229, DM92, DM96, NTC2018, EC)
Engine di verifica (norma‑agnostico)
GUI (thin)
Output (unica fonte per report e confronti)
Nessun layer può inglobare responsabilità di un altro.

1. Collegamento con gli altri PLAN
Questo documento è gerarchicamente coordinato con:

PLAN_MASTER.md
PLAN_CALCOLO.md
PLAN_GUI.md
PLAN_INPUT_COMUNE.md
PLAN_OUTPUT_COMUNE.md
In caso di conflitto:

PLAN_MASTER
PLAN_STRATEGIA_STRUTTURALE_ESTESA
altri PLAN di dominio

1. Criteri di accettazione
Il sistema è conforme a questo PLAN se:

il Metodo di Cross è implementato come metodo indipendente dalla norma;
le norme non contengono logica di calcolo globale;
ogni risultato è tracciabile e citabile in relazione;
l’estensione futura non richiede refactor distruttivi.

Questo PLAN è vincolante per tutto lo sviluppo futuro.
