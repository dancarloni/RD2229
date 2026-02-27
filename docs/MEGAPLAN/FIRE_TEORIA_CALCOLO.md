
FIRE_TEORIA_CALCOLO – Teoria e modelli di verifica
Status: STABILE
Ruolo: Base teorica e di calcolo per le verifiche di resistenza al fuoco


1. Scopo del documento
Questo documento raccoglie la teoria di calcolo, i modelli matematici, le formulazioni operative e gli schemi di verifica per la resistenza al fuoco delle sezioni strutturali, in particolare in calcestruzzo armato.
È destinato a:

motori di calcolo incendio
Copilot / agenti di supporto allo sviluppo
documentazione tecnica di riferimento
⚠️ Non contiene obblighi normativi (vedi FIRE_NORMATIVA_NTC.md) né scelte architetturali (PLAN).


2. Impostazione generale della verifica
La verifica strutturale in incendio si svolge nello stato limite ultimo in situazione eccezionale.
La disuguaglianza fondamentale è:
\\[ E_{d,fi} \\le R_{d,fi,t} \\]
Dove:

\\(E_{d,fi}\\) = azione di progetto in incendio
\\(R_{d,fi,t}\\) = resistenza residua della sezione al tempo \\(t\\)
Il tempo \\(t\\) è funzione della classe di resistenza richiesta (R30, R60, R90, …).


3. Azioni di progetto in incendio
3.1 Riduzione delle azioni
L’azione di progetto in incendio deriva da quella a temperatura ordinaria:
\\[ E_{d,fi} = \\eta_{fi} \\cdot E_d \\]
con:
\\[ \\eta_{fi} = \\frac{G_k + \\psi_{fi} Q_k}{\\gamma_G G_k + \\gamma_Q Q_k} \\]
Dove:

\\(G_k\\) = azioni permanenti
\\(Q_k\\) = azioni variabili
\\(\\psi_{fi}\\) = coefficiente di combinazione in incendio


4. Modelli termici (richiamo concettuale)
Il calcolo meccanico richiede come input:

distribuzione della temperatura nella sezione
in funzione del tempo di esposizione
Nel metodo semplificato si assumono:

curve nominali (ISO 834)
profili termici unidimensionali
Nel metodo avanzato:

analisi termica dedicata (FEM o equivalente)


5. Degradazione dei materiali
5.1 Calcestruzzo
Al crescere della temperatura si ha:

riduzione della resistenza a compressione \\(f_{c,\	heta}\\)
riduzione del modulo elastico \\(E_{c,\	heta}\\)
Le proprietà sono espresse come:
\\[ f_{c,\	heta} = k_{c,\	heta} \\cdot f_{ck} \\]
con \\(k_{c,\	heta}\\) funzione della temperatura.
⚠️ Fenomeni non modellabili direttamente:

spalling esplosivo


5.2 Acciaio di armatura
La resistenza dell’acciaio decresce rapidamente:
\\[ f_{y,\	heta} = k_{s,\	heta} \\cdot f_{yk} \\]
con:

forti riduzioni oltre 500–600 °C


6. Metodi di calcolo della resistenza
6.1 Metodo tabellare (Livello 1)

nessun calcolo analitico
verifica per confronto con tabelle
basato su:dimensioni sezione
copriferro
carico relativo
Uso consigliato:

verifiche preliminari
casi standard


6.2 Metodo semplificato – Sezione efficace (Livello 2)
Principio:

eliminazione delle zone di calcestruzzo con temperatura eccessiva
definizione di una sezione resistente ridotta
Passaggi concettuali:

determinazione profondità danneggiata
riduzione geometria
applicazione delle proprietà ridotte dei materiali
La verifica avviene come a temperatura ordinaria, ma su:

sezione ridotta
materiali degradati


6.3 Metodo avanzato (Livello 3)

analisi termo‑meccanica accoppiata
integrazione nel tempo
valutazione esplicita del collasso
Richiede:

modellazione FEM
leggi costitutive dipendenti dalla temperatura


7. Verifica di sezione in c.a.
7.1 Flessione semplice

calcolo asse neutro sulla sezione ridotta
equilibrio delle forze:compressione nel calcestruzzo
trazione nell’acciaio residuo
7.2 Presso‑flessione

interazione N–M a caldo
dominio di resistenza ridotto nel tempo
7.3 Stabilità (cenni)

effetti del secondo ordine amplificati
particolarmente rilevanti per pilastri snelli


8. Output del calcolo
Il motore di calcolo deve restituire almeno:

tempo di resistenza raggiunto
classe R soddisfatta / non soddisfatta
utilisation in incendio
metodo adottato (L1 / L2 / L3)
avvertenze di validità


9. Limiti di validità
La teoria esposta è valida se:

incendio conforme al modello adottato
comportamento della sezione regolare
assenza di meccanismi fragili non modellati
In caso contrario:

il risultato deve essere marcato come NOT_APPLICABLE


10. Collegamenti

FIRE_NORMATIVA_EC.md → quadro normativo
FIRE_INTEGRAZIONE_SOFTWARE.md → implementazione pratica
PLAN_CALCOLO.md → architettura del solver


11. Criteri di accettazione

Formule esplicite ma generiche
Nessun valore numerico hardcoded
Metodo sempre dichiarato
Coerenza con Eurocodici
