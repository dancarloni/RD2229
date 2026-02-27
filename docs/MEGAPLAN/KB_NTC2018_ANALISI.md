
KB_NTC2018_ANALISI – Analisi strutturale secondo NTC 2018
Status: NORMA VIGENTE – KB DI SECONDO LIVELLO (NTC2018)
Ruolo nella Knowledge Base: definisce in modo vincolante i tipi di analisi strutturale ammessi, i criteri di scelta, le ipotesi di validità e le relazioni tra analisi, metodo di calcolo e verifiche secondo le NTC 2018.
Questo file è subordinato a KB_NTC2018.md e opera in coordinamento con KB_NTC2018_AZIONI.md e KB_NTC2018_SISMICA.md.


1. Riferimenti normativi

Norma principale: D.M. 17/01/2018 – NTC 2018
Capitoli di riferimento:§2 – Sicurezza e prestazioni attese
§4 – Costruzioni civili e industriali (analisi strutturale)
§7 – Progettazione per azioni sismiche
Circolare applicativa: Circ. 21/01/2019 n. 7
Ogni scelta di analisi deve essere citabile a livello di paragrafo normativo.


2. Principi generali dell’analisi strutturale
Le NTC 2018 richiedono che l’analisi strutturale:

rappresenti in modo adeguato il comportamento reale della struttura;
sia coerente con:tipologia strutturale;
materiali;
azioni considerate;
stato limite da verificare;
produca spostamenti e/o effetti interni utilizzabili dalle verifiche.
Nel software:

l’analisi è sempre distinta dalla verifica;
i metodi di calcolo sono norma‑agnostici;
la norma consuma i risultati dell’analisi.


3. Tipi di analisi ammessi
Le NTC 2018 ammettono le seguenti categorie di analisi:
3.1 Analisi lineare elastica
Caratteristiche:

comportamento elastico dei materiali;
legame costitutivo lineare;
validità per:SLU (con opportuni coefficienti);
SLE;
molte verifiche sismiche semplificate.
È l’analisi di riferimento per:

telai in c.a. ordinari;
strutture regolari;
uso del Metodo di Cross o FEM lineare.


3.2 Analisi lineare con ridistribuzione
Caratteristiche:

analisi elastica globale;
ridistribuzione locale degli sforzi;
ammessa solo entro limiti normativi espliciti.
Nel software:

la ridistribuzione deve essere:dichiarata;
parametrizzata;
tracciata in relazione.


3.3 Analisi non lineare
Comprende:

analisi pushover;
analisi time‑history;
analisi con legami costitutivi non lineari.
Caratteristiche:

rappresentazione avanzata del comportamento;
richiesta per:valutazioni di capacità;
analisi sismiche avanzate;
livelli di conoscenza elevati.
Queste analisi sono fuori dallo scope immediato del Metodo di Cross.


4. Analisi in funzione dello Stato Limite
4.1 SLU
Per gli Stati Limite Ultimi:

è ammessa analisi lineare elastica con coefficienti di sicurezza;
è ammessa analisi non lineare;
l’analisi deve essere coerente con:combinazioni SLU;
ipotesi di duttilità (in sismica).


4.2 SLE
Per gli Stati Limite di Esercizio:

l’analisi è generalmente lineare elastica;
si utilizzano combinazioni SLE (rara, frequente, quasi‑permanente);
non si applicano coefficienti γ sulle azioni.


5. Analisi sismica (rinvio)
Le analisi sismiche possono essere:

statica equivalente;
dinamica modale;
non lineare.
Questo file non entra nel dettaglio delle analisi sismiche, che sono trattate in KB_NTC2018_SISMICA.md.


6. Metodo di Cross nell’ambito NTC 2018
Il Metodo di Cross può essere utilizzato nelle NTC 2018 se:

l’analisi è lineare elastica;
la struttura è schematizzabile come telaio piano;
non sono richieste analisi non lineari;
la scelta del metodo è dichiarata in relazione.
Nel framework:

Cross è un metodo di analisi, non una norma;
produce effetti interni;
è consumato dai moduli di verifica SLU/SLE.


7. Coerenza modello – analisi – verifica
Principi vincolanti:

il modello strutturale usato per l’analisi deve essere:coerente con quello di verifica;
documentato;
serializzabile;
non è ammesso:cambiare modello tra SLU e SLE senza dichiarazione;
usare analisi diverse per confronti normativi non espliciti.


8. Relazione di calcolo
La relazione deve sempre indicare:

tipo di analisi utilizzata;
metodo di calcolo;
ipotesi principali;
riferimento normativo (capitolo/paragrafo);
limiti di validità dell’analisi.
L’assenza di tali informazioni rende la verifica non difendibile.


9. Regole di utilizzo nel software
Nel software:

il tipo di analisi è una scelta esplicita dell’utente;
ogni analisi è un oggetto tracciabile;
le verifiche rifiutano risultati incompatibili con l’analisi scelta;
Copilot non può:cambiare tipo di analisi automaticamente;
introdurre assunzioni non dichiarate.


10. Confronto con normative a TA
Il confronto con analisi a tensioni ammissibili:

è ammesso solo in modalità comparativa;
richiede stesso modello strutturale;
deve essere dichiarato esplicitamente in relazione.
È vietato qualsiasi uso ibrido.


11. Criteri di accettazione
Questa KB è conforme se:

ogni analisi è coerente con NTC2018;
il Metodo di Cross è correttamente inquadrato;
non esistono ambiguità tra analisi e verifica;
la relazione di calcolo è integralmente ricostruibile.


Questo file fa parte integrante e vincolante della Knowledge Base NTC2018.
