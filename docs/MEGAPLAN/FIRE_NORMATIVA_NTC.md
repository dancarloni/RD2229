
FIRE_NORMATIVA_NTC – Quadro normativo italiano
Status: STABILE
Ruolo: Riferimento normativo nazionale per le verifiche di resistenza al fuoco


1. Inquadramento generale
Nel sistema normativo italiano l’incendio è qualificato come azione eccezionale.
Le verifiche strutturali in caso di incendio hanno come obiettivo principale il mantenimento della capacità portante (R) per un tempo prefissato, in funzione del livello di prestazione richiesto.
La normativa italiana:

definisce le prestazioni richieste (classe R)
non fornisce metodi analitici completi di calcolo
ammette esplicitamente il ricorso a metodi di calcolo riconosciuti (Eurocodici)


2. NTC 2018 – Norme Tecniche per le Costruzioni
2.1 Riferimenti normativi

§2.4.3 – Sicurezza antincendio
Introduce la sicurezza antincendio tra i requisiti fondamentali delle opere strutturali.

§3.2.1 – Azioni eccezionali
L’incendio è classificato come azione eccezionale, con combinazioni di carico dedicate.

§4.1.4 – Verifiche in situazioni eccezionali
Stabilisce che le verifiche devono essere condotte considerando la riduzione delle proprietà meccaniche dei materiali.

2.2 Impostazione concettuale delle NTC
Le NTC 2018:

non prescrivono formule di calcolo a caldo per sezioni in c.a.
richiedono che la struttura mantenga:stabilità globale
capacità portante degli elementi
demandano il calcolo a:metodi tabellari
norme tecniche di comprovata validità (Eurocodici)
👉 In pratica, le NTC stabiliscono il “cosa”, non il “come”.


3. Normativa di Prevenzione Incendi
3.1 DM 9 marzo 2007 – Prestazioni di resistenza al fuoco

Definisce i criteri per determinare le prestazioni di resistenza al fuoco delle costruzioni
Introduce il concetto di:classe R = tempo (in minuti) di mantenimento della capacità portante
Collega le prestazioni richieste:alla destinazione d’uso
al carico di incendio
3.2 DM 16 febbraio 2007 – Classificazione di resistenza al fuoco

Fornisce la classificazione ufficiale degli elementi costruttivi
Simboli principali:R – capacità portante
E – tenuta
I – isolamento
La classificazione è espressa in minuti (R30, R60, R90, R120, …)
⚠️ Il DM 16/02/2007 non fornisce modelli di calcolo, ma solo criteri di classificazione.


4. Codice di Prevenzione Incendi
DM 3 agosto 2015 e s.m.i.

Capitolo S.2 – Resistenza al fuoco
Introduce i livelli di prestazione (da I a V)
Consente:soluzioni conformi
soluzioni alternative basate su calcolo
Quando si applica il Codice:

non si applicano DM 9/3/2007 e DM 16/2/2007
resta valido l’uso di modelli di calcolo avanzati


5. Ruolo della normativa italiana nel software
Nel sistema software:
Le NTC e i DM determinano:

obbligatorietà della verifica incendio
classe R richiesta
contesto normativo (prevenzione incendi)
Le NTC non determinano:

il modello di calcolo
le formule
il metodo analitico
👉 Il calcolo numerico deve essere affidato ai modelli:

Eurocodice (EN 1991‑1‑2, EN 1992‑1‑2)
altri metodi riconosciuti


6. Collegamento con gli altri documenti

FIRE_MASTER.md → coordinamento generale
FIRE_NORMATIVA_EC.md → modelli di calcolo
FIRE_TEORIA_CALCOLO.md → formule, esempi, verifiche
FIRE_INTEGRAZIONE_SOFTWARE.md → input, output, GUI


7. Criteri di accettazione

Nessuna formula di calcolo inserita in questo file
Tutti i riferimenti normativi espliciti
Coerenza con NTC 2018 e normativa VVF
Ruolo chiaramente distinto da Eurocodici e teoria
