
FIRE_ESTENSIONE_R90_R120 – Estensione del modulo incendio
Status: STABILE
Ruolo: Specifica tecnica e normativa per l’estensione delle verifiche a R90 e R120


1. Scopo del documento
Questo documento definisce come estendere il modulo INCENDIO dalle verifiche R60 alle classi R90 e R120, in piena coerenza con:

FIRE_CODEMODULE_INCENDIO.mdL’estensione è incrementale, senza refactor dell’architettura esistente.


2. Principio generale dell’estensione
L’estensione a R90/R120 non introduce nuovi modelli, ma:

generalizza il tempo di esposizione
rafforza i controlli di validità
richiede verifiche di stabilità numerica del solverLa condizione fondamentale resta:
\\[ E_{d,fi}(t) \\le R_{d,fi,t} \\]
con \\(t = 90\\) o \\(120\\) minuti.


3. Impatto sugli INPUT
3.1 Campi già esistenti (nessuna modifica)
fire_class_required3.2 Regole di coerenza aggiuntive
fire_class_required = R90 → fire_time_target = 904. Estensione del CALCOLO – Metodo L2 (sezione efficace)
4.1 Profilo termico

Calcolo della profondità danneggiata a t = 90 / 120 min
Verifica che la sezione efficace residua sia non nullaSe la sezione efficace è nulla:
interrompere il calcolo
restituire NOT_OK


4.2 Degradazione dei materiali

Applicazione delle curve \\(k_{c,\	heta}(T)\\), \\(k_{s,\	heta}(T)\\) fino a temperature più elevate
Controllo di:riduzione eccessiva del modulo elastico
perdita di stabilità numericaIn caso di instabilità numerica:
risultato marcato NOT_APPLICABLE
warning esplicito


5. Controlli aggiuntivi obbligatori
5.1 Stabilità e snellezza (pilastri)
Per R90/R120 è obbligatorio:

controllo della snellezza
verifica semplificata degli effetti del II ordineSe gli effetti del II ordine non sono trascurabili:
L2 non ammesso
suggerire L3


5.2 Spalling (avvertenza)

Per tempi lunghi (≥ 90 min) segnalare rischio spalling
Non modellato → warning obbligatorio in output


6. Estensione del Metodo L1 (tabellare)

Verifica disponibilità di tabelle normative per R90/R120
Se tabelle non applicabili:restituire NOT_APPLICABLE


7. Output – Estensioni
Il VerificationResultItem deve riportare:
fire_class_required = R90 / R1208. Test automatici da aggiungere
8.1 Test R90
Caso conforme → esito = OK8.2 Test R120

Caso conforme → OKTutti i test devono derivare da:
FIRE_TESTS_AUTOMATICI_R60.md9. Aggiornamento roadmap
Dopo l’implementazione R90/R120, aggiornare:
FIRE_NEXT_STEPS_ROADMAP.md10. Criteri di accettazione
L’estensione R90/R120 è considerata completa quando:

nessun nuovo campo input è introdotto
R60 continua a funzionare (non‑regressione)
test R90 e R120 passano
output è coerente con checklist tecnico‑legale


11. Collegamenti

FIRE_CODEMODULE_INCENDIO.md
FIRE_TEORIA_CALCOLO.md
FIRE_TESTS_AUTOMATICI_R60.md
FIRE_NEXT_STEPS_ROADMAP.md



stato modulo: L2 completo R30–R120



Sezione collassata prima → NOT_OK

Caso limite → NOT_OK



fire_time_target = 90 / 120
fire_time_achieved
esito (OK / NOT_OK / NOT_APPLICABLE)
warning specifici (snellezza, spalling, metodo)



fire_class_required = R120 → fire_time_target = 120
incoerenze → ERROR_INPUT

fire_time_target
fire_curve
fire_exposure_sides
fire_method

FIRE_TEORIA_CALCOLO.md
FIRE_INTEGRAZIONE_SOFTWARE.md
PLAN_CALCOLO.md
