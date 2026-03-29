
FIRE_INTEGRAZIONE_L3_IN_CODEMODULE – Integrazione del solver L3 FEM
Status: STABILE
Ruolo: Specifica di integrazione del solver L3 FEM nel CodeModule_INCENDIO

1. Scopo del documento
Questo documento definisce come integrare formalmente il solver L3 FEM all’interno del CodeModule_INCENDIO, mantenendo:

coerenza architetturale con i PLAN
separazione netta L1 / L2 / L3
controllo tramite gate di rilascio
tracciabilità tecnico‑legale
L’integrazione rende L3 invocabile dal sistema, ma non automaticamente abilitato.

1. Architettura aggiornata del CodeModule_INCENDIO

CodeModule_INCENDIO
 ├─ Solver_L1          (tabellare)
 ├─ Solver_L2          (sezione efficace)
 ├─ Solver_L3_FEM      (beam‑fiber / FEM)
 └─ FireSolverRouter   (selezione metodo)

Principio fondamentale:

L3 è sempre una scelta consapevole, mai automatica.

1. FireSolverRouter – Selezione del metodo
3.1 Regola generale
Il router seleziona il solver in base a:

fire_method (input esplicito)
validità del metodo per il caso specifico
superamento del gate di rilascio L3

3.2 Pseudocodice di routing

if fire_method == "L1":
    solver = Solver_L1()
elif fire_method == "L2":
    solver = Solver_L2()
elif fire_method == "L3":
    if not gate_L3_passed:
        raise RuntimeError("L3 non rilasciabile secondo FIRE_GATE_RILASCIO_L3_FEM")
    solver = Solver_L3_FEM()
else:
    raise ValueError("Metodo incendio non riconosciuto")

1. Interfaccia unificata dei solver
Tutti i solver incendio devono esporre la stessa interfaccia logica:

class FireSolver:
    def run(self, fire_input) -> VerificationResultItem:
        ...

Questo garantisce:

intercambiabilità
testabilità
routing pulito

1. Integrazione del solver L3 FEM
5.1 Inizializzazione
Il Solver_L3_FEM viene inizializzato con:

dati geometrici
dati dei materiali
parametri FEM (mesh, Δt, criteri di convergenza)
Tutti i parametri FEM:

non sono normativi
devono essere versionati

5.2 Esecuzione
Flusso interno:

costruzione modello FEM
loop termo‑meccanico nel tempo
individuazione del tempo di collasso
costruzione VerificationResultItem

1. Output e tracciabilità
L’output del solver L3:

deve essere un VerificationResultItem
deve indicare:fire_method = L3
fire_time_achieved
esito
warning_note
In aggiunta:

log FEM archiviato
riferimento alla versione del solver

1. Controllo tramite Gate di rilascio
7.1 Punto di aggancio
Il controllo del gate avviene:

prima dell’invocazione di Solver_L3_FEM
dentro il FireSolverRouter

7.2 Documenti vincolanti
Il router deve verificare la presenza di:

FIRE_GATE_RILASCIO_L3_FEM.md
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
In assenza:

L3 non è invocabile

1. Integrazione con test automatici

i test pytest L3 usano il router
mock del gate per test positivi/negativi
test separati per:routing
solver

1. Comportamento in caso di errore

gate non superato → RuntimeError controllato
instabilità numerica → NOT_APPLICABLE
collasso prima di R → NOT_OK

1. Stato del solver L3 nel sistema
Il solver L3 può avere stato:

DISABLED (default)
ENABLED_INTERNAL
VALIDATED
Lo stato deve essere:

esplicito
tracciabile

1. Collegamenti

FIRE_SOLVER_L3_FEM_CODICE.md
FIRE_GATE_RILASCIO_L3_FEM.md
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
FIRE_CODEMODULE_INCENDIO.md
PLAN_CALCOLO.md
