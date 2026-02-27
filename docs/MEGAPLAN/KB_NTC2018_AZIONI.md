
KB_NTC2018_AZIONI – Azioni sulle costruzioni e combinazioni
Status: NORMA VIGENTE – KB DI SECONDO LIVELLO (NTC2018)
Ruolo nella Knowledge Base: definisce in modo vincolante le azioni sulle costruzioni, i valori caratteristici, i coefficienti parziali e le combinazioni di carico da utilizzare nelle verifiche agli Stati Limite Ultimi (SLU) e agli Stati Limite di Esercizio (SLE) secondo le NTC 2018.
Questo file è subordinato a KB_NTC2018.md e ne costituisce una specializzazione operativa.


1. Riferimenti normativi

Norma principale: D.M. 17/01/2018 – NTC 2018
Capitoli di riferimento:§2 – Sicurezza e prestazioni attese
§3 – Azioni sulle costruzioni
§7 – Progettazione per azioni sismiche (per la parte combinazioni sismiche)
Circolare applicativa: Circ. 21/01/2019 n. 7
Ogni prescrizione implementata deve essere citabile a livello di paragrafo.


2. Classificazione delle azioni
Le NTC 2018 classificano le azioni in:
2.1 Azioni permanenti (G)

G1 – permanenti strutturali (peso proprio degli elementi strutturali)
G2 – permanenti non strutturali (tamponamenti, finiture, impianti)
Caratteristiche:

agiscono per tutta la vita dell’opera;
sono generalmente valutate tramite valori nominali o caratteristici;
sono soggette a coefficienti parziali γG.


2.2 Azioni variabili (Q)
Comprendono, a titolo esemplificativo:

carichi di esercizio;
neve;
vento;
temperatura;
azioni eccezionali di esercizio.
Caratteristiche:

sono definite tramite valori caratteristici Qk;
sono associate a coefficienti di combinazione ψ0, ψ1, ψ2;
sono soggette a coefficienti parziali γQ.


2.3 Azioni sismiche (E)

definite in termini di accelerazione di riferimento;
dipendono da:pericolosità sismica del sito;
categoria di sottosuolo;
classe d’uso;
vita nominale.
Le azioni sismiche non sono trattate in dettaglio in questo file e rimandano a KB_NTC2018_SISMICA.md.


3. Valori delle azioni
Per ogni azione devono essere distinti:

valore caratteristico (Gk, Qk);
valori di combinazione;
valori di progetto.
Nel software:

i valori caratteristici sono input o derivati;
i valori di progetto sono calcolati applicando coefficienti KB‑driven;
nessun coefficiente può essere hardcoded.


4. Coefficienti parziali di sicurezza
Le NTC 2018 introducono coefficienti parziali:

γG per azioni permanenti;
γQ per azioni variabili;
coefficienti specifici per combinazioni sismiche.
Principi vincolanti:

i coefficienti dipendono dal tipo di verifica (SLU / SLE);
i valori devono essere esplicitamente richiamati dalla KB;
eventuali differenze tra Circ. 2019 e testo NTC devono essere tracciate.


5. Combinazioni di carico
5.1 Combinazioni agli Stati Limite Ultimi (SLU)
Le combinazioni SLU sono del tipo:

combinazioni fondamentali;
combinazioni sismiche;
combinazioni eccezionali.
Caratteristiche:

uso di valori caratteristici e coefficienti γ;
presenza di una azione principale e azioni concomitanti ridotte con ψ0;
obbligo di dichiarazione della combinazione utilizzata in relazione.


5.2 Combinazioni agli Stati Limite di Esercizio (SLE)
Le NTC 2018 distinguono:

SLE rara;
SLE frequente;
SLE quasi‑permanente.
Caratteristiche:

uso dei coefficienti ψ1 e ψ2;
assenza di coefficienti γ sulle azioni (salvo casi specifici);
finalità legate a deformazioni, fessurazioni e comfort.


6. Regole di utilizzo nel software
Nel framework di calcolo:

le combinazioni sono generate da un motore combinazioni dedicato;
ogni combinazione è un oggetto tracciabile;
l’utente deve poter:selezionare lo stato limite;
visualizzare la formula della combinazione;
risalire al riferimento normativo.
È vietato:

mescolare azioni TA con combinazioni SLU/SLE;
applicare coefficienti non presenti in KB;
usare combinazioni implicite non dichiarate.


7. Relazione di calcolo
La relazione deve riportare:

elenco delle azioni considerate;
valori caratteristici;
combinazioni applicate;
stato limite di riferimento;
citazione puntuale dei paragrafi NTC.
Ogni risultato numerico deve essere ricostruibile a posteriori.


8. Confronto con normative precedenti (TA)
Il confronto con norme a tensioni ammissibili:

è ammesso solo a parità di modello di analisi;
ha valore esclusivamente comparativo;
deve essere dichiarato esplicitamente in relazione.
Il software deve impedire qualsiasi uso ibrido.


9. Criteri di accettazione
Questa KB è conforme se:

tutte le azioni e combinazioni derivano da questo file;
nessun coefficiente è hardcoded;
ogni combinazione è tracciabile e citabile;
la relazione di calcolo è completamente ricostruibile.


Questo file fa parte integrante e vincolante della Knowledge Base NTC2018.
