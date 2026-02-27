
PLAN INTEGRAZIONE METODI – NORME
Status: VINCOLO DURO (estendibile solo previa richiesta esplicita dell’utente)
1. Scopo del documento
Questo PLAN definisce in modo vincolante le regole di integrazione tra metodi di calcolo strutturale (es. Metodo di Cross) e le norme tecniche (RD2229/39, DM92, DM96, NTC2018, Eurocodici), stabilendo:

ruoli e responsabilità di ciascun livello;
modalità corrette di utilizzo dei metodi all’interno delle verifiche normative;
criteri di priorità e fallback normativo;
regole di tracciabilità per la relazione di calcolo.
Il documento non contiene formule e non sostituisce la teoria normativa o dei metodi.


2. Principio fondamentale (non negoziabile)

I metodi di calcolo producono effetti interni e risultati di analisi strutturale.
Le norme consumano tali risultati per effettuare verifiche.
Nessuna norma può contenere o duplicare la logica interna di un metodo.
Nessun metodo può contenere coefficienti, limiti o decisioni normative.
Questo principio è gerarchicamente subordinato solo a PLAN_MASTER e PLAN_STRATEGIA_STRUTTURALE_ESTESA.


3. Livelli del sistema e responsabilità
3.1 Metodi di calcolo strutturale
Esempi:

Metodo di Cross (telai piani)
Analisi elastica semplificata
Metodi iterativi (predisposizione)
Responsabilità:

ricevere un modello strutturale astratto;
calcolare spostamenti e/o effetti interni;
produrre output numerici tracciabili.
Divieti:

applicare coefficienti normativi;
conoscere stati limite;
generare combinazioni di carico normative.


3.2 Motore di verifica (norma‑agnostico)
Responsabilità:

orchestrare l’interazione metodo ↔ norma;
passare ai metodi i carichi/combinazioni;
raccogliere risultati di verifica.
Il motore di verifica:

non contiene formule normative;
non contiene logica di metodo;
opera solo tramite interfacce formali.


3.3 Norme tecniche
Norme supportate:

RD2229/1939 (tensioni ammissibili)
DM 1992 (tensioni ammissibili)
DM 1996 (tensioni ammissibili)
NTC2018
Eurocodici (EC2, EC3, EC8 – solo fallback dichiarato)
Responsabilità delle norme:

definire azioni e combinazioni;
definire limiti di verifica;
interpretare gli effetti interni;
produrre esiti di verifica (OK / NOT_OK / NOT_APPLICABLE).
Divieti:

risolvere il modello strutturale;
modificare i risultati del metodo;
introdurre semplificazioni non dichiarate.


4. Mappatura metodi ↔ norme
4.1 Metodo di Cross
Il Metodo di Cross può essere utilizzato da:

NTC2018 → analisi elastica dei telai piani
DM96 / DM92 → analisi iperstatica in regime elastico
Eurocodici → analisi elastica lineare (fallback)
Condizioni obbligatorie:

dichiarazione esplicita del metodo in relazione;
coerenza con le ipotesi di linearità ed elasticità;
assenza di riduzioni o amplificazioni normative interne al metodo.


4.2 Altri metodi (predisposizione)

Analisi FEM → consumabile da NTC2018 ed Eurocodici
Metodi semplificati → solo se ammessi esplicitamente dalla norma
Ogni nuovo metodo richiede:

estensione formale del PLAN;
dichiarazione del campo di applicabilità.


5. Priorità e fallback normativo
Ordine di priorità vincolante:

Norma primaria selezionata dall’utente
Eventuali chiarimenti/circolari ufficiali
Eurocodici solo se:la norma primaria rinvia esplicitamente;
oppure è tecnicamente carente
Il fallback deve essere:

esplicito;
tracciato;
riportato in relazione.


6. Tracciabilità e relazione di calcolo
Ogni verifica deve consentire:

identificazione del metodo di analisi utilizzato;
identificazione della norma applicata;
citazione di capitolo e paragrafo;
distinzione netta tra:analisi strutturale;
verifica normativa.
Il confronto tra norme è ammesso solo se:

gli effetti interni sono identici;
le ipotesi di analisi sono compatibili.


7. Integrazione con GUI
La GUI:

consente la selezione del metodo;
consente la selezione della norma;
mostra chiaramente l’accoppiamento metodo ↔ norma.
La GUI non può:

nascondere il metodo utilizzato;
cambiare automaticamente norma o metodo;
applicare logiche di fallback implicite.


8. Estensioni future consentite
Sono ammesse solo previa estensione formale del PLAN:

integrazione di nuovi metodi di analisi;
supporto avanzato muratura;
analisi non lineari;
integrazione completa FEM.


9. Criteri di accettazione
Il sistema è conforme a questo PLAN se:

ogni metodo è indipendente dalla norma;
ogni norma consuma solo risultati di analisi;
il fallback Eurocodice è sempre dichiarato;
la relazione di calcolo è ricostruibile a posteriori;
non esistono scorciatoie implicite metodo ↔ norma.


Questo PLAN è vincolante per tutte le integrazioni tra metodi di calcolo e norme tecniche.
