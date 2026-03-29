
FIRE_INTEGRAZIONE_SOFTWARE – Integrazione nel sistema di calcolo
Status: STABILE
Ruolo: Specifica di integrazione software per le verifiche di resistenza al fuoco

1. Scopo del documento
Questo documento definisce come la teoria e la normativa incendio vengono integrate nel sistema software, in coerenza con:

PLAN_MASTER.md
PLAN_CALCOLO.md
PLAN_INPUT_COMUNE.md
PLAN_OUTPUT_COMUNE.md
PLAN_GUI.md
Il documento è vincolante per:

architettura dei moduli incendio
schema dati
output di verifica
GUI e report

1. Architettura dei moduli incendio
2.1 CodeModule_INCENDIO
Il calcolo incendio è implementato come CodeModule dedicato, separato dal calcolo a temperatura ordinaria.
Responsabilità:

selezione normativa (NTC / EC)
selezione metodo (Livello 1 / 2 / 3)
gestione del tempo di esposizione
orchestrazione calcolo termico‑meccanico
Dipendenze ammesse:

FIRE_NORMATIVA_EC.md
FIRE_TEORIA_CALCOLO.md
Dipendenze vietate:

GUI
moduli di calcolo SLU/SLE ordinari

1. Integrazione con l’INPUT COMUNE
3.1 Estensioni dati incendio
Allo schema BaseElementSpec si aggiungono campi incendio, esclusivamente in forma additiva:

fire_required (bool)
fire_class_required (R30, R60, R90, R120, …)
fire_exposure_sides (1 / 2 / 3 / 4 lati)
fire_curve (ISO_834 / parametrica)
fire_protection_type (nessuna / intonaco / pannello / altro)
fire_method (L1 / L2 / L3)
fire_time_target (min)
Regole:

nessun campo incendio è obbligatorio se fire_required = false
la validazione avviene prima del calcolo

1. Integrazione con il CALCOLO
4.1 Flusso di calcolo incendio

Validazione input incendio
Costruzione combinazioni di carico in incendio
Calcolo termico (esplicito o semplificato)
Calcolo meccanico della sezione
Valutazione al tempo richiesto
4.2 Selezione del metodo

L1 → nessun solver meccanico, solo confronto tabellare
L2 → solver di sezione con sezione ridotta
L3 → solver termo‑meccanico avanzato
Il metodo deve essere sempre dichiarato nell’output.

1. Integrazione con l’OUTPUT COMUNE
5.1 VerificationResultItem – Estensioni incendio
Per ogni verifica incendio viene prodotto un VerificationResultItem con:

check_id = FIRE_*
stato_limite = INCENDIO
fire_class_required
fire_time_achieved
fire_method
norma (NTC + EC)
esito (OK / NOT_OK / NOT_APPLICABLE)
utilisation
norm_references
warning_note
⚠️ Nessun dato interno del solver deve essere esposto direttamente.

1. Integrazione con la GUI
6.1 GUI di input incendio

selezione obbligatorietà verifica incendio
scelta classe R
scelta metodo di calcolo
indicazione protezioni passive
6.2 GUI di output incendio

esito verifica R
tempo di collasso stimato
confronto R richiesta / R raggiunta
evidenza dei limiti di validità
La GUI non deve:

eseguire calcoli
interpretare formule

1. Database e file di configurazione
7.1 Database materiali
Devono essere disponibili:

curve di degrado calcestruzzo k_c,θ(T)
curve di degrado acciaio k_s,θ(T)
versionamento per norma
7.2 File di configurazione

curve di incendio standard
parametri di default (configurabili)
mapping norma → solver
Nessun parametro normativo deve essere hardcoded.

1. Logging, tracciabilità e test

log completo del flusso incendio
tracciabilità di:input
norma
metodo
versione solver
Devono essere previsti:

test unitari per L1/L2
test di benchmark per casi noti

1. Limiti di utilizzo
Il modulo incendio:

non sostituisce la progettazione antincendio globale
non valuta la compartimentazione
non valuta la sicurezza delle vie di esodo

1. Collegamenti

FIRE_MASTER.md
FIRE_NORMATIVA_NTC.md
FIRE_NORMATIVA_EC.md
FIRE_TEORIA_CALCOLO.md
PLAN_* (architettura)

1. Criteri di accettazione

Tutti i dati incendio sono opzionali e versionati
Output conforme a VerificationResultItem
Nessuna logica normativa in GUI
Separazione netta input / calcolo / output
