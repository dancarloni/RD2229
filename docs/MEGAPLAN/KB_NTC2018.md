
KB_NTC2018 – Norme Tecniche per le Costruzioni 2018
Status: NORMA VIGENTE – RIFERIMENTO PRIMARIO
Ruolo nella Knowledge Base: riferimento normativo principale per la progettazione e la verifica strutturale in Italia secondo il metodo agli Stati Limite, con integrazione della sicurezza sismica e della progettazione in capacità.


1. Identità normativa

Titolo ufficiale: Decreto Ministeriale 17 gennaio 2018 – Aggiornamento delle Norme Tecniche per le Costruzioni
Pubblicazione: Gazzetta Ufficiale della Repubblica Italiana n. 42 del 20/02/2018
Circolare applicativa: Circolare n. 7 del 21/01/2019
Stato giuridico: norma vigente per la progettazione, verifica e collaudo delle strutture


2. Campo di applicazione generale
Le NTC 2018 si applicano a:

opere civili e industriali;
nuove costruzioni;
costruzioni esistenti (verifica, miglioramento, adeguamento);
interventi locali;
strutture soggette ad azioni statiche e sismiche.
Materiali strutturali disciplinati:

calcestruzzo armato e precompresso;
acciaio;
muratura;
legno;
materiali compositi (FRP/FRCM – ove richiamati).


3. Impianto concettuale della norma
Le NTC 2018 adottano:

il metodo agli Stati Limite;
il principio di sicurezza probabilistica;
l’uso di coefficienti parziali sui materiali e sulle azioni;
la distinzione tra:Stati Limite Ultimi (SLU);
Stati Limite di Esercizio (SLE).
In ambito sismico introducono:

progettazione in capacità;
gerarchia delle resistenze;
classificazione della duttilità;
livelli di conoscenza e fattori di confidenza (costruzioni esistenti).


4. Struttura generale delle NTC 2018
Ai fini della Knowledge Base, la norma è organizzata per macro‑aree:

Principi generali e sicurezza
Azioni sulle costruzioni e combinazioni
Analisi strutturale
Progettazione e verifica per materiale
Costruzioni esistenti
Sicurezza sismica
Collaudo e controlli
Ogni macro‑area sarà sviluppata in KB di secondo livello.


5. Analisi strutturale (concetti generali)
Le NTC 2018 ammettono:

analisi lineare elastica;
analisi lineare con ridistribuzioni;
analisi non lineare (pushover, time‑history);
analisi statica equivalente e dinamica modale.
Nel framework software:

i metodi di calcolo (Cross, FEM, ecc.) sono esterni alla norma;
la norma consuma spostamenti ed effetti interni;
la scelta del tipo di analisi deve essere:esplicita;
tracciata;
riportata in relazione.


6. Stati Limite
6.1 Stati Limite Ultimi (SLU)
Verificano:

sicurezza strutturale;
stabilità globale e locale;
collasso e perdita di equilibrio.
6.2 Stati Limite di Esercizio (SLE)
Verificano:

deformazioni;
fessurazione;
vibrazioni;
durabilità e funzionalità.
Ogni verifica deve indicare:

stato limite;
combinazione di carico;
riferimento normativo puntuale.


7. Costruzioni esistenti
Le NTC 2018 introducono:

livelli di conoscenza (LC1, LC2, LC3);
fattori di confidenza (FC);
verifiche in termini di sicurezza globale (ζE);
distinzione tra:interventi locali;
miglioramento;
adeguamento.
Questo ambito richiede KB dedicate di secondo livello.


8. Rapporto con norme precedenti (TA)
Le NTC 2018:

non sono direttamente compatibili con il metodo a tensioni ammissibili;
consentono confronti solo:a parità di modello di analisi;
come valutazione tecnica;
con esplicita dichiarazione in relazione.
Il software deve:

impedire verifiche ibride TA / SLU;
consentire confronti solo in modalità comparativa.


9. Relazione di calcolo
Quando si applicano le NTC 2018, la relazione deve:

dichiarare:metodo di analisi;
stati limite verificati;
combinazioni utilizzate;
citare:capitolo;
paragrafo;
circolare applicativa se usata;
distinguere chiaramente:analisi;
verifica;
confronto normativo (se presente).


10. Integrazione con il software
Nel framework:

NTC 2018 è esposta come CodeModule SLU/SLE;
utilizza la Knowledge Base come fonte unica;
dialoga con i metodi di calcolo tramite interfacce standard;
produce output conformi a PLAN_OUTPUT_COMUNE.
GitHub Copilot deve:

usare questo file come riferimento primario NTC;
non introdurre regole non presenti in KB;
segnalare TODO in caso di lacune normative.


11. Estensioni previste (KB di secondo livello)
Saranno sviluppate separatamente:

KB_NTC2018_AZIONI.md
KB_NTC2018_ANALISI.md
KB_NTC2018_CA.md
KB_NTC2018_ACCIAIO.md
KB_NTC2018_MURATURA.md
KB_NTC2018_ESISTENTI.md
KB_NTC2018_SISMICA.md


12. Criteri di accettazione
Questa KB è conforme se:

costituisce riferimento primario per NTC2018;
ogni verifica SLU/SLE richiama una sezione dedicata;
la relazione di calcolo è integralmente ricostruibile;
non esistono contaminazioni con criteri TA.


Questo file fa parte integrante e vincolante della Knowledge Base normativa del progetto.
