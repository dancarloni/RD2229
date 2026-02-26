
KB_NTC2018_CA – Calcestruzzo Armato (SLU / SLE)
Status: NORMA VIGENTE – KB DI SECONDO LIVELLO (NTC2018)
Ruolo nella Knowledge Base: definisce in modo vincolante le regole di progettazione e verifica delle strutture in calcestruzzo armato secondo le NTC 2018, con riferimento agli Stati Limite Ultimi (SLU) e agli Stati Limite di Esercizio (SLE).
Questo file è subordinato a:

KB_NTC2018.md (impianto generale);
KB_NTC2018_AZIONI.md (azioni e combinazioni);
KB_NTC2018_ANALISI.md (tipi di analisi).


1. Riferimenti normativi

Norma principale: D.M. 17/01/2018 – NTC 2018
Capitoli di riferimento:§4.1 – Calcestruzzo
§4.1.2 – Materiali
§4.1.3 – Azioni di progetto e resistenze
§4.1.4 – Verifiche agli stati limite
Circolare applicativa: Circ. 21/01/2019 n. 7
Ogni verifica implementata deve essere citabile a livello di paragrafo.


2. Campo di applicazione
Le presenti regole si applicano a:

strutture in calcestruzzo armato ordinario;
strutture in calcestruzzo armato precompresso (solo se esplicitamente previsto);
elementi strutturali quali:travi;
pilastri;
setti;
solai;
fondazioni.
Sono escluse da questo file:

muratura;
acciaio;
materiali compositi (trattati in KB dedicate).


3. Materiali
3.1 Calcestruzzo
Caratteristiche fondamentali:

resistenza caratteristica fck;
resistenza di progetto fcd;
modulo elastico;
deformazioni limite.
Principi vincolanti:

i valori di progetto derivano da coefficienti parziali γC;
i parametri devono essere KB‑driven;
nessun valore può essere hardcoded.


3.2 Acciaio per armature
Caratteristiche fondamentali:

resistenza caratteristica fyk;
resistenza di progetto fyd;
duttilità (classi di acciaio).
Principi vincolanti:

uso di γS;
verifica della duttilità ove richiesta;
tracciabilità dei parametri.


4. Ipotesi di calcolo
Le verifiche in c.a. secondo NTC 2018 si basano su:

ipotesi di Bernoulli;
legame costitutivo non lineare dei materiali;
sezioni piane che restano piane;
comportamento differenziato trazione/compressione.
Nel software:

le ipotesi devono essere esplicitate;
il metodo di analisi (Cross, FEM, ecc.) fornisce gli effetti interni;
la norma consuma tali effetti.


5. Stati Limite Ultimi (SLU)
5.1 Tipologie di verifica SLU
Devono essere considerate, ove applicabili:

flessione retta;
pressoflessione;
taglio;
torsione;
instabilità locale degli elementi compressi.
Ogni verifica SLU deve indicare:

combinazione di carico;
stato limite;
riferimento normativo.


5.2 Resistenza delle sezioni
Principi generali:

confronto tra domanda (effetti interni di progetto) e capacità;
uso di resistenze di progetto;
verifica separata per ciascun meccanismo resistente.
Il software deve:

restituire esito OK / NOT_OK / NOT_APPLICABLE;
consentire il dettaglio dei passaggi di calcolo;
garantire tracciabilità completa.


6. Stati Limite di Esercizio (SLE)
6.1 Tipologie di verifica SLE
Devono essere considerate:

limitazione delle tensioni;
controllo della fessurazione;
verifica delle deformazioni;
durabilità.
Le verifiche SLE utilizzano:

combinazioni SLE (rara, frequente, quasi‑permanente);
analisi generalmente lineare elastica.


6.2 Fessurazione e deformazioni
Principi:

controllo dell’ampiezza delle fessure;
limiti di deformazione funzione dell’uso;
eventuale dipendenza dalle condizioni ambientali.
Nel software:

i limiti devono essere parametrici;
ogni valore deve essere citabile;
i risultati devono essere riportabili in relazione.


7. Gerarchia delle resistenze (rinvio)
La progettazione in capacità e la gerarchia delle resistenze:

sono rilevanti soprattutto in ambito sismico;
non sono sviluppate in questo file;
rimandano a KB_NTC2018_SISMICA.md.


8. Relazione di calcolo
La relazione deve riportare:

dati dei materiali;
combinazioni utilizzate;
verifiche SLU e SLE eseguite;
esiti;
riferimenti normativi puntuali.
Ogni verifica deve essere ricostruibile a posteriori.


9. Regole di utilizzo nel software
Nel framework:

le verifiche in c.a. sono moduli separati;
nessuna formula normativa è duplicata fuori dalla KB;
Copilot deve:rifiutare verifiche prive di base normativa;
segnalare TODO in caso di lacune.


10. Confronto con normative precedenti (TA)
Il confronto con DM96 / DM92 / RD2229:

è ammesso solo a fini comparativi;
richiede stesso modello e stessa analisi;
deve essere dichiarato esplicitamente in relazione.
È vietato qualsiasi uso ibrido.


11. Criteri di accettazione
Questa KB è conforme se:

copre tutte le verifiche fondamentali in c.a.;
ogni parametro è tracciabile;
non esistono hard‑coding normativi;
la relazione di calcolo è integralmente difendibile.


Questo file fa parte integrante e vincolante della Knowledge Base NTC2018.
