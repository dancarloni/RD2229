
KB_NTC2018_SISMICA – Sicurezza sismica, spettro, capacità
Status: NORMA VIGENTE – KB DI SECONDO LIVELLO (NTC2018)
Ruolo nella Knowledge Base: definisce in modo vincolante le regole di progettazione e verifica sismica secondo le NTC 2018, includendo azione sismica, spettro di risposta, fattore di comportamento q, gerarchia delle resistenze, progettazione in capacità e verifiche per costruzioni nuove ed esistenti.
Questo file è subordinato a:

KB_NTC2018.md (impianto generale);
KB_NTC2018_AZIONI.md (azioni e combinazioni);
KB_NTC2018_ANALISI.md (tipi di analisi);
KB_NTC2018_CA.md (verifiche di resistenza);
KB_NTC2018_ESISTENTI.md (ζE, LC, FC).


1. Riferimenti normativi

Norma principale: D.M. 17/01/2018 – NTC 2018
Capitoli di riferimento:§3.2 – Azione sismica
§7 – Progettazione per azioni sismiche
§8 – Costruzioni esistenti (richiami sismici)
Circolare applicativa: Circ. 21/01/2019 n. 7
Ogni prescrizione sismica implementata deve essere citabile a livello di capitolo/paragrafo.


2. Azione sismica di progetto
L’azione sismica è definita in funzione di:

pericolosità sismica del sito;
vita nominale dell’opera;
classe d’uso;
categoria di sottosuolo;
condizioni topografiche.
Nel software:

i parametri sismici sono input o derivati da basi dati ufficiali;
ogni parametro deve essere tracciabile;
non è ammesso hard‑coding dei valori.


3. Spettro di risposta elastico
Lo spettro elastico è definito da:

accelerazione massima al suolo ag;
fattori di amplificazione F0;
periodi caratteristici TB, TC, TD;
smorzamento di riferimento.
Principi vincolanti:

lo spettro deve essere costruito secondo la categoria di sottosuolo;
eventuali modifiche (smorzamento diverso) devono essere dichiarate;
lo spettro è base comune per analisi lineari e non lineari.


4. Fattore di comportamento (q)
Il fattore q rappresenta:

la capacità dissipativa della struttura;
la riduzione delle forze elastiche;
il comportamento duttile atteso.
Il valore di q dipende da:

tipologia strutturale;
regolarità in pianta e in altezza;
materiale;
dettagli costruttivi.
Nel software:

q è parametro esplicito;
la sua scelta deve essere motivata;
l’uso di q implica il rispetto delle regole di duttilità.


5. Analisi sismica
Le NTC 2018 ammettono:
5.1 Analisi statica equivalente

per strutture regolari;
con limiti dimensionali e di altezza;
uso dello spettro di progetto.
5.2 Analisi dinamica modale

per strutture irregolari;
combinazione degli effetti modali;
uso dello spettro di progetto.
5.3 Analisi non lineare

pushover;
time‑history;
valutazione diretta della capacità.
La scelta del tipo di analisi deve essere coerente con KB_NTC2018_ANALISI.md.


6. Progettazione in capacità
La progettazione in capacità richiede:

gerarchia delle resistenze;
meccanismi duttili prevalenti;
prevenzione di collassi fragili.
Principi vincolanti:

elementi dissipativi e non dissipativi devono essere distinti;
le verifiche di capacità sono obbligatorie quando si usa q;
la gerarchia deve essere verificata esplicitamente.


7. Gerarchia delle resistenze
Devono essere garantiti:

meccanismi duttili (cerniere plastiche in posizioni controllate);
resistenza adeguata degli elementi non dissipativi;
continuità del percorso resistente.
Nel software:

la gerarchia è una verifica dedicata;
l’esito deve essere esplicito;
l’assenza di verifica genera NOT_APPLICABLE o NOT_OK.


8. Costruzioni esistenti e sismica
Per le costruzioni esistenti:

la sicurezza sismica è espressa tramite ζE;
il tipo di intervento (locale, miglioramento, adeguamento) guida il livello di verifica;
è ammesso l’uso di analisi semplificate o avanzate in funzione del LC.
Il collegamento con KB_NTC2018_ESISTENTI.md è obbligatorio.


9. Relazione di calcolo
La relazione deve riportare:

parametri sismici del sito;
spettro utilizzato;
tipo di analisi sismica;
valore di q;
verifiche di capacità e gerarchia;
valore di ζE (per esistenti);
riferimenti normativi puntuali.
Ogni scelta deve essere motivata e tracciabile.


10. Regole di utilizzo nel software
Nel framework:

la sismica è un modulo esplicito;
non è ammesso l’uso automatico di q senza verifiche di capacità;
Copilot deve:rifiutare analisi sismiche incoerenti;
segnalare TODO se mancano dati essenziali.


11. Confronto con normative precedenti
Il confronto con normative precedenti (TA o NTC passate):

è ammesso solo in modalità comparativa;
richiede stesso modello strutturale;
deve essere dichiarato esplicitamente.
È vietato qualsiasi uso sostitutivo.


12. Criteri di accettazione
Questa KB è conforme se:

copre l’intero impianto sismico NTC2018;
integra correttamente analisi, capacità e ζE;
ogni parametro è tracciabile;
la relazione di calcolo è difendibile in sede tecnica e legale.


Questo file fa parte integrante e vincolante della Knowledge Base NTC2018.
