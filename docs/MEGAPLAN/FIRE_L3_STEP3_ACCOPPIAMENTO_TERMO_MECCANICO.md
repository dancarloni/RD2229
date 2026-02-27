
FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO – Step 3 implementazione reale solver FEM L3
Status: IN IMPLEMENTAZIONE
Ruolo: Terzo step dell’implementazione reale del solver FEM L3 – accoppiamento completo termo‑meccanico e gestione instabilità


1. Scopo dello Step 3
Questo documento sviluppa lo STEP 3 dell’implementazione reale del solver FEM L3, completando l’accoppiamento termo‑meccanico nel tempo e introducendo:

loop temporale completo
gestione della non convergenza
primo trattamento degli effetti del II ordine
definizione robusta del tempo di collasso
Con questo step il solver L3 diventa operativo end‑to‑end (pur restando prototipale).


2. Dipendenze obbligatorie
Lo Step 3 può essere implementato solo se:

FIRE_L3_STEP1_ANALISI_TERMICA.md è completato
FIRE_L3_STEP2_ANALISI_MECCANICA.md è completato
le interfacce ThermalSolverL3 e MechanicalSolverL3 sono stabili
i test minimi degli Step 1 e 2 sono superati


3. Concetto di accoppiamento termo‑meccanico
L’accoppiamento adottato è di tipo weak coupling incrementale:

calcolo termico allo step \\(t_i\\)
aggiornamento proprietà meccaniche
calcolo capacità resistente
verifica collasso
avanzamento temporale
Questo schema è ammesso dagli Eurocodici per analisi avanzate semplificate ed è numericamente stabile per prototipi.


4. Loop temporale completo
Il solver L3 gestisce il tempo in modo esplicito:
\\[ t_{i+1} = t_i + \\Delta t \\]
con:

\\(\\Delta t\\) scelto dall’utente (parametro FEM)
controllo di stabilità su \\(\\Delta t\\)


5. Flusso algoritmico dettagliato
Per ogni incremento temporale:
thermal_solver.step(t)6. Gestione della non convergenza
La non convergenza può derivare da:

degradazione estrema dei materiali
perdita di rigidezza
oscillazioni numericheRegola di progetto:
prima non convergenza → collasso numerico
il collasso numerico è accettato come collasso strutturale conservativo


7. Effetti del II ordine (livello prototipale)
In questo step si introduce una gestione semplificata degli effetti del II ordine:

amplificazione del momento agente:\\[ M_{Ed,fi}^{(2)} = M_{Ed,fi} \\cdot (1 + \\alpha) \\]
con \\(\\alpha\\) parametro di snellezza (input)⚠️ Questo non è un modello completo di instabilità, ma:
è coerente con l’obiettivo prototipale
prepara l’estensione futura


8. Criterio finale di collasso
Il collasso è dichiarato quando si verifica almeno una delle condizioni:

\\(M_{Rd,fi}(t) < M_{Ed,fi}^{(2)}\\)
non convergenza numerica
superamento soglie di deformazione (se implementate)Il tempo di collasso è:
\\[ t_{coll} = t_i \\]


9. Interfaccia del solver L3 completo

class SolverL3FEM:
    def run(self, fire_time_target, M_Ed_fi) -> VerificationResultItem:
        ...


Il solver:

incapsula termica + meccanica
gestisce il tempo
restituisce un solo risultato finale


10. Scheletro di implementazione (codice reale)

class SolverL3FEM:
    def __init__(self, thermal_solver, mechanical_solver, dt, alpha):
        self.thermal = thermal_solver
        self.mechanical = mechanical_solver
        self.dt = dt
        self.alpha = alpha
        self.time = 0.0

    def run(self, fire_time_target, M_Ed_fi):
        while self.time <= fire_time_target * 60:
            self.thermal.step(self.time)
            temps = self.thermal.get_fiber_temperatures()

            M_Rd = self.mechanical.compute_capacity(temps)
            M_Ed_2 = M_Ed_fi * (1 + self.alpha)

            if M_Rd < M_Ed_2:
                return {
                    "fire_method": "L3",
                    "fire_time_achieved": self.time / 60,
                    "esito": "NOT_OK",
                    "warning_note": "Collasso termo-meccanico L3",
                }

            self.time += self.dt

        return {
            "fire_method": "L3",
            "fire_time_achieved": fire_time_target,
            "esito": "OK",
            "warning_note": None,
        }


⚠️ Codice prototipale, ma:

completo
coerente con Step 1 e 2
pronto per test automatici


11. Test minimi obbligatori
Prima di considerare lo Step 3 completato:

☐ test L3 end‑to‑end su caso semplice
☐ confronto L2 vs L3 (tempo di collasso)
☐ test di stabilità al variare di \\(\\Delta t\\)
☐ test con \\(\\alpha = 0\\) (assenza II ordine)


12. Gate di completamento STEP 3
Lo Step 3 è considerato completato solo se:

il solver L3 gira end‑to‑end
produce sempre un esito deterministico
supera i test minimi
è valutato tramite FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md13. Stato del solver dopo STEP 3
Dopo questo step il solver L3 è:

FUNZIONANTE (PROTOTIPO)
integrabile nel CodeModule_INCENDIO14. Collegamenti

FIRE_L3_STEP1_ANALISI_TERMICA.md
FIRE_L3_STEP2_ANALISI_MECCANICA.md
FIRE_SOLVER_L3_FEM_CODICE.md
FIRE_GATE_RILASCIO_L3_FEM.md
PLAN_CALCOLO.md



soggetto al Gate di rilascio L3






temperatures = thermal_solver.get_fiber_temperatures()
M_Rd = mechanical_solver.compute_capacity(temperatures)
confronto con \\(M_{Ed,fi}\\)
verifica convergenza
decisione di collasso / avanzamento
