
professionale assistito – relazione tecnica di supporto al progetto
Ruolo: Modello standard di relazione di calcolo per verifiche al fuoco L3 2D (pareti portanti in c.a.)


0. Premessa e avvertenze
La presente relazione di calcolo tipo costituisce un modello standard per la documentazione delle verifiche di resistenza al fuoco di pareti portanti in calcestruzzo armato, eseguite mediante analisi avanzata L3 2D.
La relazione:

non sostituisce il giudizio del progettista
deve essere adattata al caso reale
è valida solo se accompagnata da checklist e gate di rilascio
⚠️ L’analisi L3 ha carattere prestazionale e richiede competenza specialistica.


1. Oggetto della relazione
Oggetto della presente relazione è la verifica della resistenza al fuoco di una parete portante in c.a., mediante:

verifica semplificata L2 (per confronto)
verifica avanzata L3 2D (analisi FEM termo‑meccanica)
Classe di resistenza richiesta: R__ (es. R90 / R120).


2. Riferimenti normativi

EN 1991‑1‑2 – Azioni sulle strutture – Azioni in caso di incendio
EN 1992‑1‑2 – Progettazione delle strutture di calcestruzzo – Progettazione strutturale contro l’incendio
NTC vigenti (per quanto applicabile)


3. Descrizione dell’opera e dell’elemento strutturale

Tipologia strutturale: parete portante in c.a.
Funzione: elemento verticale portante
Posizione nell’opera: ____
3.1 Geometria

Spessore parete: ____ cm
Larghezza di calcolo: ____ m
Altezza considerata: ____
Copriferro nominale: ____ cm
Lati esposti al fuoco: ____


3.2 Materiali

Calcestruzzo: 
Acciaio di armatura: 
Le proprietà a caldo sono assunte secondo EN 1992‑1‑2.


4. Azioni e combinazioni in incendio
Le azioni sono valutate in situazione di incendio secondo EN 1991‑1‑2.

Sforzo normale di progetto in incendio: \\(N_{Ed,fi}\\)
Azioni orizzontali: 


5. Verifica con metodo L2 (per confronto)
5.1 Metodo adottato
Il metodo L2 prevede:

determinazione della profondità di calcestruzzo danneggiato
definizione della sezione efficace residua
verifica a presso‑compressione su sezione ridotta
Schema di verifica:
\\[ N_{Ed,fi} \\le N_{Rd,fi,R} \\]


5.2 Esito della verifica L2

Esito: OK / NOT_OK
Commento sintetico: ____


6. Verifica con metodo L3 2D (analisi avanzata)
6.1 Motivazione dell’uso del metodo L3
Il metodo L3 è adottato in quanto:

il metodo L2 risulta non rappresentativo / non sufficiente
sono presenti gradienti termici significativi
si vuole valutare il tempo reale di collasso


6.2 Modello di calcolo

Tipo di analisi: FEM 2D termo‑meccanica
Stato di sforzo: piano‑sforzi / piano‑deformazioni
Solver utilizzato: L3 2D interno


6.3 Analisi termica

Incendio di riferimento: ISO 834
Campo termico: \\(T(x,y,t)\\)
Metodo: analisi 2D per strati


6.4 Analisi meccanica

Leggi costitutive: non lineari termo‑dipendenti
Metodo risolutivo: Newton‑Raphson incrementale
Passo temporale: \\(\\Delta t = ____\\)


7. Risultati dell’analisi L3

Tempo di collasso individuato: \\(t_{coll,2D} = ____\\)
Meccanismo di collasso: ____
Esito verifica L3: OK / NOT_OK


8. Confronto L2 vs L3
Il confronto tra i due metodi evidenzia:

differenze di approccio (semplificato vs prestazionale)
eventuali meccanismi locali non intercettati dal metodo L2
Il metodo L3 non sostituisce automaticamente il metodo L2.


9. Valutazione ingegneristica
Il progettista, alla luce dei risultati:

valuta la coerenza dei risultati
assume le decisioni progettuali conseguenti
definisce eventuali misure correttive


10. Limiti di validità
La presente verifica è valida solo per:

i dati geometrici e meccanici assunti
il modello di incendio considerato
le ipotesi dichiarate


11. Checklist e gate di rilascio
La presente relazione è valida solo se accompagnata da:
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md12. Conclusioni
La verifica al fuoco della parete è:

soddisfatta / non soddisfattaIl progettista assume la piena responsabilità delle scelte progettuali.


13. Allegati

Output del solver L3 2D
Log di calcolo
Benchmark automatico


Firma del progettista
Data: 




FIRE_GATE_RILASCIO_L3_FEM.md
