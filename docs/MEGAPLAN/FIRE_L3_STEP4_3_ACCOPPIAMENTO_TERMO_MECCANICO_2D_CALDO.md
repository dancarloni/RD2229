
FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO – Analisi L3 2D a caldo
Status: IN IMPLEMENTAZIONE
Ruolo: STEP 4.3 – Accoppiamento termo‑meccanico 2D a caldo per pareti portanti in c.a.


1. Scopo dello STEP 4.3
Questo documento sviluppa lo STEP 4.3 della linea 2D, completando l’accoppiamento termo‑meccanico 2D a caldo per pareti portanti in calcestruzzo armato.
Con questo step il solver L3 2D diventa operativo end‑to‑end, includendo:

campo termico 2D dipendente dal tempo
degradazione termo‑dipendente dei materiali
equilibrio meccanico 2D non lineare
individuazione del tempo di collasso della parete


2. Dipendenze obbligatorie
Lo STEP 4.3 è ammesso solo se:

FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md è completato
FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO.md è validato
le leggi costitutive non lineari (FIRE_L3_COSTITUTIVE_NONLINEARI.md) sono operative
i test FEM 2D a freddo sono superati


3. Concetto di accoppiamento 2D a caldo
L’accoppiamento adottato è di tipo weak coupling incrementale nel tempo, coerente con la strategia L3 già usata per il modello 1D:

aggiornamento del campo termico 2D
aggiornamento locale delle proprietà dei materiali
risoluzione del problema meccanico 2D
verifica dei criteri di collasso
avanzamento temporale


4. Loop temporale dell’analisi 2D
Il tempo è discretizzato come:
\\[ t_{n+1} = t_n + \\Delta t \\]
con:

\\(\\Delta t\\) parametro FEM controllabile
verifica di stabilità al variare di \\(\\Delta t\\)


5. Analisi termica 2D a caldo
Per ogni incremento temporale:

esecuzione di ThermalSolverL3_2D.step(t)Il campo termico è non uniforme e dipende dalla distanza dalle superfici esposte.


6. Aggiornamento delle proprietà dei materiali
Per ciascun elemento FEM:

valutazione della temperatura media dell’elemento
aggiornamento dei parametri:\\(E_{c,\	heta}, f_{c,\	heta}\\)
\\(E_{s,\	heta}, f_{y,\	heta}\\)secondo le leggi definite in FIRE_L3_COSTITUTIVE_NONLINEARI.md.


7. Analisi meccanica 2D a caldo
Il problema meccanico risolto è:
\\[ \\mathbf{K(u,T)}\\, \\mathbf{u} = \\mathbf{F}_{fi} \\]
con:

matrice di rigidezza dipendente da temperatura
comportamento non lineare dei materiali
carichi di incendio \\(\\mathbf{F}_{fi}\\)La risoluzione avviene tramite Newton‑Raphson incrementale.


8. Criteri di collasso della parete
La parete è considerata collassata quando si verifica almeno una delle condizioni:

mancata convergenza dell’equilibrio
schiacciamento diffuso del calcestruzzo
formazione di meccanismo fragile localizzato
perdita di capacità portante globaleIl tempo di collasso 2D è:
\\[ t_{coll,2D} \\]


9. Interfaccia del solver L3 2D completo

class SolverL3FEM_2D:
    def run(self, fire_time_target, loads, bc) -> dict:
        """
        Esegue analisi termo-meccanica 2D a caldo
        Restituisce tempo di collasso e campi di risultato
        """
        ...




10. Scheletro di implementazione (codice prototipale)

class SolverL3FEM_2D:
    def __init__(self, thermal_solver, mechanical_solver, dt):
        self.thermal = thermal_solver
        self.mechanical = mechanical_solver
        self.dt = dt
        self.time = 0.0

    def run(self, fire_time_target, loads, bc):
        while self.time <= fire_time_target * 60:
            self.thermal.step(self.time)
            T_field = self.thermal.get_temperature_field()

            result = self.mechanical.solve(loads, bc, T_field)

            if result.get("collapsed", False):
                return {
                    "fire_method": "L3",
                    "fire_time_achieved": self.time / 60,
                    "esito": "NOT_OK",
                    "warning_note": "Collasso termo-meccanico 2D"
                }

            self.time += self.dt

        return {
            "fire_method": "L3",
            "fire_time_achieved": fire_time_target,
            "esito": "OK",
            "warning_note": None
        }




11. Test minimi obbligatori
Prima di considerare completato lo STEP 4.3:

☐ test termo‑meccanico 2D elementare
☐ confronto qualitativo con modello 1D (stessa sezione)
☐ test di stabilità al variare di \\(\\Delta t\\)
☐ verifica riproducibilità dei risultati


12. Gate di completamento STEP 4.3
Lo STEP 4.3 è considerato completato solo se:

l’analisi 2D a caldo è stabile
il tempo di collasso è deterministico
i test minimi sono superati
la checklist L3 è soddisfatta


13. Stato del solver dopo STEP 4.3
Dopo questo step il solver L3 supporta:

✅ analisi 2D a caldo su pareti
✅ meccanismi locali
✅ confronto 1D vs 2Ded è pronto per il primo caso studio 2D (parete R90).


14. Collegamenti

FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md
FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO.md
FIRE_L3_COSTITUTIVE_NONLINEARI.md
FIRE_L3_ANALISI_COMPLETE_E_CONFRONTO_L2_L3.md
FIRE_GATE_RILASCIO_L3_FEM.md

ottenimento del campo \\(T(x,y,t)\\)
associazione della temperatura a ciascun elemento FEM
