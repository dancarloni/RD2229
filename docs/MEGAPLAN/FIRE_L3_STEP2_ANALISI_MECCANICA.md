
FIRE_L3_STEP2_ANALISI_MECCANICA – Step 2 implementazione reale solver FEM L3
Status: IN IMPLEMENTAZIONE
Ruolo: Secondo step concreto dell’implementazione reale del solver FEM L3 (analisi meccanica beam‑fiber)


1. Scopo dello Step 2
Questo documento sviluppa lo STEP 2 dell’implementazione reale del solver FEM L3, introducendo l’analisi meccanica a caldo basata su modello beam‑fiber, utilizzando direttamente l’output dello STEP 1 – Analisi termica.
Lo Step 2 consente di:

calcolare la capacità resistente nel tempo
integrare il contributo delle fibre di calcestruzzo e acciaio
individuare il collasso meccanico


2. Dipendenze obbligatorie
Lo Step 2 può essere implementato solo se:

FIRE_L3_STEP1_ANALISI_TERMICA.md è completato e testato
l’interfaccia ThermalSolverL3 è stabile
i test termici minimi sono superati


3. Ambito dello Step 2 (controllato)
In questo step si implementa solo:

modello beam‑fiber 1D
comportamento flessionale (trave/pilastro)
materiali:calcestruzzo
acciaio di armatura
leggi costitutive semplificate ma dipendenti dalla temperatura
Sono esclusi:

instabilità globale di telaio
modelli 2D / 3D
accoppiamento non lineare avanzato


4. Ipotesi meccaniche di base

sezioni piane restano piane
contributo del calcestruzzo teso trascurato
armatura concentrata in fibre equivalenti
equilibrio interno forze‑momenti
Queste ipotesi sono coerenti con EN 1992‑1‑2 per analisi avanzate semplificate.


5. Leggi costitutive a caldo (livello prototipale)
5.1 Acciaio di armatura
Per ciascuna fibra di acciaio:

tensione:
\\[ \\sigma_s = k_{s,\	heta} \\cdot E_s \\cdot \\varepsilon_s \\]

con:\\(k_{s,\	heta}\\) da curva normativa
\\(E_s\\) modulo elastico a freddo
5.2 Calcestruzzo
Per ciascuna fibra di calcestruzzo compressa:

tensione:
\\[ \\sigma_c = k_{c,\	heta} \\cdot E_c \\cdot \\varepsilon_c \\]
Il modello è volutamente lineare degradato (step successivi potranno introdurre non linearità).


6. Integrazione delle fibre
Per una curvatura imposta \\(\\chi\\):

calcolo deformazione fibra:
\\[ \\varepsilon_i = \\chi \\cdot y_i \\]

calcolo tensione fibra \\(\\sigma_i\\)
calcolo forza fibra:
\\[ F_i = \\sigma_i \\cdot A_i \\]

integrazione:risultante assiale
momento resistente


7. Calcolo della capacità resistente nel tempo
Per ogni istante \\(t\\):
acquisizione temperature da ThermalSolverL38. Criterio di collasso meccanico
Il collasso meccanico è assunto quando:

\\(M_{Rd,fi}(t) < M_{Ed,fi}\\)oppure quando:
la soluzione di equilibrio non convergeIl tempo di collasso meccanico è:
\\[ t_{coll} = \\min(t) \\; | \\; M_{Rd,fi}(t) < M_{Ed,fi} \\]


9. Interfaccia del modulo meccanico

class MechanicalSolverL3:
    def __init__(self, section, materials):
        ...

    def compute_capacity(self, temperatures) -> float:
        """Restituisce M_Rd,fi(t)"""
        ...


Il modulo meccanico non gestisce il tempo, ma lavora su uno stato termico assegnato.


10. Scheletro di implementazione (codice reale)

class MechanicalSolverL3:
    def __init__(self, fibers, materials):
        self.fibers = fibers
        self.materials = materials

    def compute_capacity(self, temperatures):
        M = 0.0
        for fiber, T in zip(self.fibers, temperatures):
            k_theta = self.materials[fiber.material].reduction_factor(T)
            sigma = k_theta * fiber.E * fiber.strain
            M += sigma * fiber.area * fiber.y
        return M


⚠️ Codice intenzionalmente semplificato, ma:

coerente
testabile
estendibile


11. Test minimi obbligatori
Prima di procedere allo Step 3 devono essere superati:

☐ test a freddo (confronto con L2)
☐ test a caldo a tempi noti
☐ test di monotonicità di \\(M_{Rd,fi}(t)\\)


12. Gate di avanzamento allo Step 3
È consentito procedere allo Step 3 – Accoppiamento completo termo‑meccanico solo se:

la capacità resistente è calcolata correttamente
il criterio di collasso è robusto
i test minimi sono superati


13. Prossimo step (NON ancora implementato)
STEP 3 – Accoppiamento completo e gestione II ordine:

loop termico‑meccanico
instabilità
raffinamento del criterio di collasso


14. Collegamenti

FIRE_L3_STEP1_ANALISI_TERMICA.md
FIRE_PROTOTIPO_L3_MINIMALE.md
FIRE_SOLVER_L3_FEM_CODICE.md
FIRE_GATE_RILASCIO_L3_FEM.md
PLAN_CALCOLO.md



aggiornamento \\(k_{s,\	heta}\\), \\(k_{c,\	heta}\\)
calcolo del momento resistente \\(M_{Rd,fi}(t)\\)
