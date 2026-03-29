
KB_DM_1992_TA – D.M. 14 febbraio 1992 (Tensioni Ammissibili)
Status: NORMA STORICA – UTILIZZO CONSENTITO COME NORMA PRIMARIA O DI CONFRONTO
Ruolo nella Knowledge Base: fonte normativa autonoma per verifiche strutturali secondo il criterio delle tensioni ammissibili, in continuità ed evoluzione rispetto al R.D. 2229/1939.

1. Identità normativa

Titolo ufficiale: Decreto Ministeriale 14 febbraio 1992 – Norme tecniche per il calcolo, l’esecuzione ed il collaudo delle strutture in cemento armato, normale e precompresso
Pubblicazione: Gazzetta Ufficiale della Repubblica Italiana, 1992
Stato giuridico: norma superata da DM 1996 e successive, ma ancora rilevante:per edifici esistenti progettati negli anni ’90;
per verifiche a tensioni ammissibili;
per confronti normativi e consulenze tecniche.

1. Campo di applicazione
Il DM 14/02/1992 si applica a:

strutture in cemento armato ordinario;
strutture in cemento armato precompresso;
edifici civili e industriali ordinari;
elementi soggetti a:flessione;
pressoflessione;
compressione;
taglio.
Ambito tipico di utilizzo nel software:

verifiche di edifici esistenti progettati secondo DM92;
confronto RD2229 ↔ DM92 ↔ DM96;
base normativa per studi di vulnerabilità storica.

1. Ipotesi fondamentali
Il DM 1992 si fonda sulle seguenti ipotesi:

comportamento elastico lineare dei materiali;
criterio di sicurezza basato su tensioni ammissibili;
coefficienti di sicurezza incorporati nei valori limite;
distinzione più chiara tra:calcestruzzo;
acciaio;
precompressione.
Non sono presenti:

stati limite ultimi;
stati limite di esercizio;
concetti di duttilità o gerarchia delle resistenze.

1. Prescrizioni di calcolo
Il DM 1992 prescrive che:

l’analisi strutturale sia di tipo elastico;
le sollecitazioni derivino da un modello globale coerente;
le tensioni calcolate non superino i valori ammissibili;
le verifiche siano condotte separatamente per:calcestruzzo;
acciaio ordinario;
acciaio da precompressione.
Nel software:

il metodo di analisi (es. Metodo di Cross) è esterno alla norma;
la norma consuma tensioni ed effetti interni;
il risultato è espresso come OK / NOT_OK / NOT_APPLICABLE.

1. Limiti normativi
Il DM 1992 introduce:

valori ammissibili aggiornati rispetto al RD2229;
differenziazione più esplicita dei materiali;
prescrizioni geometriche e costruttive più dettagliate;
limiti specifici per il c.a.p.
Nel contesto software:

tutti i limiti devono essere modellati come valori normativi KB‑driven;
ogni valore deve essere citabile;
l’assenza di una prescrizione deve generare NOT_APPLICABLE.

1. Rinvii e integrazioni
Il DM 1992:

non rinvia agli Eurocodici;
costituisce un’evoluzione diretta del RD2229;
è sostituito concettualmente dal DM 1996 (TA evolute).
Il confronto è ammesso con:

RD 2229/1939;
DM 1996;
NTC2018 (solo a fini comparativi e dichiarati).

1. Citazioni puntuali
Ogni riferimento al DM 14/02/1992 nella relazione di calcolo deve indicare:

Norma: D.M. 14/02/1992
Capitolo / Paragrafo applicato
Eventuale comma o tabella
Formato concettuale consigliato:

“Verifica eseguita secondo D.M. 14/02/1992, criterio delle tensioni ammissibili, § …”

1. Uso nella relazione di calcolo
Quando il DM 1992 è utilizzato:

deve essere dichiarato come norma primaria;
devono essere dichiarate le ipotesi elastiche;
non devono essere mescolati criteri SLU/SLE;
il confronto con DM96 o NTC2018 deve essere separato e motivato.

1. Integrazione con il software
Nel framework:

DM 1992 è esposto come CodeModule TA;
utilizza input comuni e metodi comuni;
produce output conformi a PLAN_OUTPUT_COMUNE;
consente confronti normativi diretti.
GitHub Copilot deve:

usare questo file come unica fonte normativa DM92;
non introdurre coefficienti moderni;
segnalare TODO se una prescrizione non è presente.

1. Limiti di responsabilità
Il DM 1992 non è idoneo per:

progettazione di nuove strutture secondo normative vigenti;
verifiche sismiche moderne;
valutazioni di duttilità e capacità dissipativa.
Il software deve segnalare tali casi come OUT_OF_SCOPE.

1. Criteri di accettazione
Questa KB è conforme se:

ogni verifica DM92 richiama questo file;
ogni limite è tracciabile;
la relazione di calcolo è ricostruibile;
non esistono contaminazioni con SLU/SLE.

Questo file fa parte integrante e vincolante della Knowledge Base normativa del progetto.
