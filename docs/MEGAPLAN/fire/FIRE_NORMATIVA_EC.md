
FIRE_NORMATIVA_EC – Quadro normativo europeo (Eurocodici)
Status: STABILE
Ruolo: Riferimento tecnico‑normativo per il calcolo strutturale in caso di incendio

1. Inquadramento generale
Nel sistema europeo la progettazione strutturale in caso di incendio è disciplinata dai cosiddetti Eurocodici “hot”, ossia le parti ‑1‑2 degli Eurocodici strutturali.
Per le strutture in calcestruzzo armato, il riferimento principale è:

EN 1992‑1‑2 – Eurocodice 2 – Progettazione delle strutture di calcestruzzo – Parte 1‑2: Progettazione strutturale in caso di incendio
Gli Eurocodici forniscono:

i principi di verifica
le proprietà dei materiali a temperatura elevata
i metodi di calcolo (da semplificati ad avanzati)
👉 Gli Eurocodici stabiliscono il “come si calcola” la resistenza al fuoco.

1. Sistema degli Eurocodici per l’incendio
2.1 Eurocodici coinvolti
La verifica strutturale in incendio richiede l’uso combinato di:

EN 1990 – Principi generali di progettazione
EN 1991‑1‑2 – Azioni sulle strutture esposte al fuoco
EN 1992‑1‑2 – Calcestruzzo armato in incendio
Altri materiali (per estensioni future):

EN 1993‑1‑2 – Acciaio
EN 1994‑1‑2 – Strutture composte
EN 1995‑1‑2 – Legno

1. EN 1991‑1‑2 – Azioni in caso di incendio
3.1 Modelli di incendio
La norma definisce diversi modelli di incendio, tra cui:

Curva standard ISO 834 (curva nominale)
Curve parametriche di incendio naturale
Curve specifiche (idrocarburi, tunnel – fuori ambito ordinario)
La curva standard ISO 834 è la base per:

classificazione R30, R60, R90, R120
confronti normativi
3.2 Combinazioni di carico in incendio
Le azioni meccaniche in incendio sono definite come:
\\[ E_{d,fi} = \\eta_{fi} \\cdot E_d \\]
con riduzione delle azioni variabili mediante coefficienti \\(\\psi_{fi}\\).

1. EN 1992‑1‑2 – Calcestruzzo armato in incendio
4.1 Campo di applicazione
La norma si applica a:

strutture in calcestruzzo normale
calcestruzzo armato e precompresso
fino alle classi di resistenza ammesse dalla norma
Sono esclusi:

comportamenti anomali non modellabili
effetti non strutturali

4.2 Obiettivo della verifica
La verifica fondamentale è:
\\[ E_{d,fi} \\le R_{d,fi,t} \\]
Dove:

\\(E_{d,fi}\\) = azione di progetto in incendio
\\(R_{d,fi,t}\\) = resistenza residua della sezione al tempo \\(t\\)

1. Metodi di verifica previsti
5.1 Metodo tabellare (Livello 1)
Caratteristiche:

uso di tabelle normative
dimensioni minime della sezione
copriferro minimo
tempo di resistenza prefissato
✅ Vantaggi:

rapido
robusto
❌ Limiti:

conservativo
poco flessibile

5.2 Metodo semplificato (Livello 2)
Caratteristiche:

sezione ridotta ("effective section")
profilo termico semplificato
riduzione delle proprietà dei materiali
✅ Buon compromesso tra accuratezza e semplicità

5.3 Metodo avanzato (Livello 3)
Caratteristiche:

analisi termica + meccanica
possibile uso FEM
modellazione esplicita del tempo
✅ Massima accuratezza ❌ Elevata complessità

1. Proprietà dei materiali a temperatura elevata
La EN 1992‑1‑2 fornisce:

curve di riduzione della resistenza del calcestruzzo
curve di riduzione della resistenza dell’acciaio
variazione del modulo elastico
Tali curve sono vincolanti per il calcolo.

1. Versioni e aggiornamenti

EN 1992‑1‑2:2004 + A1:2019 – Prima generazione
EN 1992‑1‑2:2023 – Seconda generazione
Nel software:

la versione deve essere esplicitamente selezionabile
i risultati devono riportare la versione normativa

1. Ruolo degli Eurocodici nel software
Nel sistema software:
Gli Eurocodici determinano:

modelli di calcolo
formule
coefficienti di riduzione
limiti di applicabilità
Gli Eurocodici non determinano:

la classe R richiesta
il livello di prestazione
gli obblighi di verifica (definiti da NTC / VVF)

1. Collegamento con gli altri documenti

FIRE_MASTER.md → coordinamento generale
FIRE_NORMATIVA_NTC.md → obblighi e prestazioni
FIRE_TEORIA_CALCOLO.md → formule dettagliate ed esempi
FIRE_INTEGRAZIONE_SOFTWARE.md → input, output, GUI

1. Criteri di accettazione

Tutti i modelli fanno riferimento a EN 1991‑1‑2 e EN 1992‑1‑2
Metodo di verifica esplicitamente dichiarato
Versione normativa sempre tracciata
Coerenza con la distinzione NTC (prestazioni) / EC (calcolo)
