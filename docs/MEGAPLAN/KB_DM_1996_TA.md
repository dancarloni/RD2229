
KB_DM_1996_TA – D.M. 9 gennaio 1996 (Tensioni Ammissibili)
Status: NORMA STORICA AVANZATA – UTILIZZO CONSENTITO COME NORMA PRIMARIA O DI CONFRONTO
Ruolo nella Knowledge Base: ultima e più evoluta normativa italiana basata sul criterio delle tensioni ammissibili per strutture in cemento armato, immediatamente precedente al passaggio concettuale agli stati limite.


1. Identità normativa

Titolo ufficiale: Decreto Ministeriale 9 gennaio 1996 – Norme tecniche per il calcolo, l’esecuzione ed il collaudo delle strutture in cemento armato, normale e precompresso
Pubblicazione: Gazzetta Ufficiale della Repubblica Italiana, 1996
Stato giuridico: norma superata dalle NTC successive, ma di riferimento essenziale:per edifici esistenti progettati tra 1996 e primi anni 2000;
per verifiche a tensioni ammissibili evolute;
per confronti tecnico‑normativi con NTC2018;
in ambito di consulenza tecnica e valutazioni di sicurezza.


2. Campo di applicazione
Il DM 09/01/1996 si applica a:

strutture in cemento armato ordinario;
strutture in cemento armato precompresso;
edifici civili e industriali;
opere ordinarie non speciali.
Elementi strutturali considerati:

travi;
pilastri;
setti;
solai;
fondazioni (in forma semplificata).
Ambito tipico di utilizzo nel software:

verifiche di edifici esistenti progettati secondo DM96;
confronto DM92 ↔ DM96 ↔ NTC2018;
analisi di sicurezza con approccio storico coerente.


3. Ipotesi fondamentali
Il DM 1996 si fonda sulle seguenti ipotesi:

comportamento elastico lineare dei materiali;
criterio di sicurezza basato su tensioni ammissibili;
maggiore formalizzazione delle ipotesi di calcolo;
coefficienti di sicurezza incorporati nei valori ammissibili;
separazione più chiara tra analisi e verifica.
Non introduce:

stati limite ultimi;
stati limite di esercizio;
progettazione in capacità;
criteri di duttilità.


4. Prescrizioni di calcolo
Il DM 1996 prescrive che:

l’analisi strutturale sia elastica lineare;
il modello globale sia coerente e dichiarato;
le sollecitazioni derivino da un’analisi strutturale esplicita;
le tensioni nei materiali non superino i valori ammissibili;
siano effettuate verifiche distinte per:calcestruzzo;
acciaio ordinario;
acciaio da precompressione.
Nel software:

il metodo di analisi (Cross, elastico, FEM lineare) è esterno alla norma;
la norma consuma tensioni ed effetti interni;
l’esito è espresso come OK / NOT_OK / NOT_APPLICABLE.


5. Limiti normativi
Il DM 1996 introduce:

valori ammissibili ulteriormente aggiornati rispetto al DM92;
maggiore articolazione dei limiti per materiali e stati di sollecitazione;
prescrizioni costruttive più strutturate;
controlli più espliciti sugli schemi statici.
Nel contesto software:

ogni limite è modellato come entità normativa KB‑driven;
ogni valore deve essere citabile (capitolo/paragrafo);
la mancanza di una prescrizione genera NOT_APPLICABLE.


6. Rinvii e integrazioni
Il DM 1996:

non rinvia formalmente agli Eurocodici;
rappresenta il culmine del metodo TA in Italia;
è concettualmente superato dalle NTC (stati limite).
Il confronto è ammesso con:

RD 2229/1939;
DM 1992;
NTC2018 (solo a fini comparativi e dichiarati);
Eurocodici (solo come supporto tecnico esplicito, non automatico).


7. Citazioni puntuali
Ogni riferimento al DM 09/01/1996 nella relazione di calcolo deve indicare:

Norma: D.M. 09/01/1996
Capitolo / Paragrafo applicato
Eventuale comma o tabella
Formato concettuale consigliato:


“Verifica eseguita secondo D.M. 09/01/1996, criterio delle tensioni ammissibili, § …”




8. Uso nella relazione di calcolo
Quando il DM 1996 è utilizzato:

deve essere dichiarato come norma primaria;
devono essere esplicitate le ipotesi elastiche;
non devono essere introdotti criteri SLU/SLE;
ogni confronto con NTC2018 deve essere separato, motivato e dichiarato.


9. Integrazione con il software
Nel framework:

DM 1996 è esposto come CodeModule TA avanzato;
utilizza input comuni e metodi comuni;
produce output conformi a PLAN_OUTPUT_COMUNE;
è compatibile con confronti multi‑norma.
GitHub Copilot deve:

usare esclusivamente questo file come fonte normativa DM96;
non introdurre coefficienti agli stati limite;
segnalare TODO in caso di prescrizioni non presenti.


10. Limiti di responsabilità
Il DM 1996 non è idoneo per:

progettazione di nuove strutture secondo normativa vigente;
verifiche sismiche moderne;
progettazione in capacità;
valutazioni di duttilità e comportamento post‑elastico.
Il software deve segnalare tali casi come OUT_OF_SCOPE.


11. Criteri di accettazione
Questa KB è conforme se:

ogni verifica DM96 richiama questo file;
ogni limite è tracciabile a un riferimento normativo;
la relazione di calcolo è ricostruibile a posteriori;
non esistono contaminazioni con criteri agli stati limite.


Questo file fa parte integrante e vincolante della Knowledge Base normativa del progetto.
