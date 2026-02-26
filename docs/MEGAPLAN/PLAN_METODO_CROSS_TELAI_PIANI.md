
PLAN METODO DI CROSS PER TELAI PIANI
Status: VINCOLO DURO
1. Scopo del documento
Questo PLAN definisce l’architettura vincolante del Metodo di Cross per telai piani, inteso come:

metodo di calcolo strutturale generale;
indipendente dalle singole norme;
riutilizzabile da più contesti normativi (NTC2018, DM96, Eurocodici);
utilizzabile sia in modalità professionale sia didattica.
Il documento non contiene formule e non sostituisce la teoria del metodo.


2. Collocazione architetturale
Il Metodo di Cross appartiene al livello:
Metodi di calcolo strutturale
Non appartiene a:

NTC2018;
DM92 / DM96;
Eurocodici.
Le norme:

forniscono azioni, combinazioni, limiti di verifica;
consumano gli effetti interni prodotti dal metodo.


3. Campo di applicazione
Il Metodo di Cross è applicabile a:

telai piani in calcestruzzo armato e acciaio;
schemi iperstatici a nodi rigidi;
analisi elastica lineare.
Fuori campo (in questa fase):

comportamento non lineare;
plasticizzazione diffusa;
instabilità globale avanzata;
analisi dinamiche modali (predisposizione futura).


4. Responsabilità del metodo
Il Metodo di Cross deve:

ricevere un modello strutturale astratto;
calcolare:momenti agli estremi delle aste;
distribuzioni di rigidezza;
riequilibrio iterativo dei nodi;
produrre effetti interni finali utilizzabili dalle norme;
produrre output intermedi tracciabili.
Il Metodo di Cross non deve:

applicare coefficienti normativi;
verificare resistenze;
decidere stati limite;
conoscere la norma applicata.


5. Modello strutturale concettuale
Il metodo opera su un modello composto da:

nodi;
aste;
vincoli;
rigidezze flessionali;
condizioni di carico.
Il modello è:

norma‑agnostico;
indipendente dalla GUI;
serializzabile e persistente;
riutilizzabile da più analisi normative.


6. Output del metodo
Output obbligatori

momenti finali agli estremi delle aste;
momenti nodali equilibrati;
numero di iterazioni;
criteri di convergenza raggiunti.
Output opzionali (modalità didattica)

storia iterativa completa;
fattori di distribuzione;
fattori di trasporto;
riepilogo passo‑passo delle iterazioni.
Tutti gli output devono essere:

numerici;
tracciabili;
archiviabili;
richiamabili nella relazione di calcolo.


7. Integrazione con le norme
Le norme:

richiedono al Metodo di Cross gli effetti interni;
applicano le proprie regole di verifica (SLU, SLE, TA);
citano il Metodo di Cross come procedura di analisi strutturale.
Il Metodo di Cross:

non conosce stati limite;
non conosce coefficienti γ;
non genera combinazioni di carico.


8. Integrazione con la GUI
La GUI:

costruisce il modello strutturale;
invoca il Metodo di Cross;
visualizza risultati finali e intermedi.
La GUI non può:

modificare il metodo;
introdurre logica numerica;
alterare il flusso iterativo;
introdurre coefficienti normativi.


9. Relazione di calcolo
La relazione di calcolo deve:

dichiarare esplicitamente l’uso del Metodo di Cross;
indicare le ipotesi adottate (elasticità, linearità);
distinguere chiaramente:analisi strutturale;
verifiche normative;
citare la norma che ammette l’uso del metodo.


10. Estensioni future consentite
Sono ammesse solo previa estensione formale del PLAN:

estensione a telai spaziali;
integrazione con analisi FEM;
interazione con analisi sismica globale;
applicazione a muratura (solo se compatibile con le ipotesi del metodo).


11. Criteri di accettazione
Il Metodo di Cross è conforme a questo PLAN se:

è invocabile indipendentemente dalla norma;
produce output completi e tracciabili;
non contiene logica normativa;
può essere utilizzato da più norme senza duplicazioni;
supporta modalità professionale e didattica.


Questo PLAN è vincolante per tutte le implementazioni del Metodo di Cross per telai piani.
