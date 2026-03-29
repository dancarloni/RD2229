
KB_NTC2018_ESISTENTI – Costruzioni esistenti (ζE, LC, FC)
Status: NORMA VIGENTE – KB DI SECONDO LIVELLO (NTC2018)
Ruolo nella Knowledge Base: definisce in modo vincolante le regole di valutazione della sicurezza delle costruzioni esistenti secondo le NTC 2018, includendo livelli di conoscenza (LC), fattori di confidenza (FC), indice di sicurezza ζE e tipologie di intervento (locali, miglioramento, adeguamento).
Questo file è subordinato a:

KB_NTC2018.md (impianto generale);
KB_NTC2018_AZIONI.md (azioni e combinazioni);
KB_NTC2018_ANALISI.md (tipi di analisi);
KB_NTC2018_CA.md (verifiche di resistenza per c.a.).

1. Riferimenti normativi

Norma principale: D.M. 17/01/2018 – NTC 2018
Capitoli di riferimento:§8 – Costruzioni esistenti
§2 – Sicurezza e prestazioni attese (richiami)
§7 – Progettazione per azioni sismiche (per ζE)
Circolare applicativa: Circ. 21/01/2019 n. 7
Ogni valutazione deve essere citabile a livello di capitolo/paragrafo.

1. Ambito di applicazione
Le presenti disposizioni si applicano a:

edifici e opere esistenti;
strutture progettate con normative precedenti (RD2229, DM92, DM96, NTC precedenti);
verifiche di sicurezza in condizioni statiche e sismiche;
interventi su strutture in esercizio.
Sono incluse:

strutture in calcestruzzo armato;
strutture in acciaio;
muratura (per quanto di competenza, con rinvio a KB dedicate).

1. Obiettivi della valutazione
La valutazione della sicurezza mira a:

stimare il livello di sicurezza dell’opera;
confrontare la capacità con le azioni previste;
supportare la scelta del tipo di intervento;
produrre un esito tecnico‑legalmente difendibile.
L’esito non coincide necessariamente con il rispetto integrale delle NTC per nuove costruzioni.

1. Livelli di conoscenza (LC)
Le NTC 2018 definiscono tre livelli di conoscenza:
4.1 LC1 – Conoscenza limitata

documentazione scarsa o incompleta;
indagini limitate;
elevata incertezza sui parametri meccanici.
4.2 LC2 – Conoscenza adeguata

documentazione parziale ma significativa;
indagini mirate;
buona definizione del modello strutturale.
4.3 LC3 – Conoscenza accurata

documentazione completa;
indagini estese;
alta affidabilità dei parametri.
Il livello di conoscenza deve essere dichiarato esplicitamente.

1. Fattori di confidenza (FC)
A ciascun livello di conoscenza è associato un fattore di confidenza FC che:

riduce le resistenze di progetto;
tiene conto dell’incertezza residua;
è applicato alle capacità, non alle azioni.
Principi vincolanti:

FC è funzione esclusiva del LC;
non può essere scelto arbitrariamente;
deve essere tracciabile in relazione.

1. Indice di sicurezza ζE
6.1 Definizione
L’indice di sicurezza ζE esprime il rapporto tra:

capacità della struttura;
domanda derivante dalle azioni previste dalle NTC.
6.2 Interpretazione

ζE < 1.0 → sicurezza inferiore a quella richiesta per nuove costruzioni;
ζE ≈ 1.0 → sicurezza paragonabile a nuova costruzione;
ζE > 1.0 → margine di sicurezza superiore.
Il valore di ζE deve essere:

calcolato;
motivato;
riportato in relazione.

1. Tipologie di intervento
7.1 Interventi locali

non modificano il comportamento globale;
mirano a eliminare carenze locali;
non richiedono il raggiungimento di ζE = 1.0.
7.2 Miglioramento sismico

aumenta la sicurezza globale;
non è obbligatorio raggiungere ζE = 1.0;
deve dimostrare un incremento significativo.
7.3 Adeguamento sismico

rende la struttura conforme ai livelli di sicurezza delle nuove costruzioni;
richiede ζE ≥ 1.0;
è obbligatorio nei casi previsti dalla norma.

1. Analisi strutturale per edifici esistenti
Le analisi possono essere:

lineari elastiche;
non lineari;
statiche o dinamiche (in ambito sismico).
La scelta dipende da:

livello di conoscenza;
tipologia strutturale;
obiettivo dell’intervento.
Il tipo di analisi deve essere coerente con KB_NTC2018_ANALISI.md.

1. Uso di normative precedenti (TA)
È ammesso:

utilizzare verifiche TA come supporto conoscitivo;
confrontare risultati TA vs NTC solo in modo comparativo.
Non è ammesso:

sostituire la verifica NTC con TA;
mescolare criteri TA e SLU/SLE.

1. Relazione di calcolo
La relazione deve includere:

descrizione dell’opera e dello stato di fatto;
livello di conoscenza adottato;
fattore di confidenza;
valore di ζE;
tipo di intervento;
riferimenti normativi puntuali.
Ogni scelta deve essere motivata e tracciabile.

1. Regole di utilizzo nel software
Nel framework:

LC, FC e ζE sono parametri espliciti;
il software deve impedire:omissioni del LC;
uso di FC incoerenti;
Copilot deve:rifiutare verifiche prive di ζE;
segnalare TODO in caso di dati insufficienti.

1. Criteri di accettazione
Questa KB è conforme se:

consente valutazioni complete degli edifici esistenti;
distingue chiaramente tra interventi locali, miglioramento e adeguamento;
ogni parametro è tracciabile;
la relazione di calcolo è difendibile in sede tecnica e legale.

Questo file fa parte integrante e vincolante della Knowledge Base NTC2018.
