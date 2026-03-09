
FIRE_L3_COSTITUTIVE_NONLINEARI – Raffinamento delle leggi costitutive a caldo
Status: STABILE
Ruolo: Definizione e integrazione di leggi costitutive non lineari per il solver FEM L3

1. Scopo del documento
Questo documento raffina le leggi costitutive a caldo utilizzate nel solver L3 FEM, passando dal modello lineare degradato prototipale a modelli non lineari dipendenti dalla temperatura, coerenti con i principi della EN 1992‑1‑2.
L’obiettivo è:

migliorare la rappresentazione fisica del comportamento dei materiali
aumentare l’affidabilità del tempo di collasso
mantenere stabilità numerica e controllabilità

1. Principi generali di modellazione
Le leggi costitutive L3 devono rispettare i seguenti principi:

dipendenza esplicita dalla temperatura \\(T\\)
degradazione di resistenza e rigidezza
comportamento monotono e dissipativo
assenza di parametri normativi hardcoded nel codice
separazione netta tra legge materiale e solver

1. Acciaio di armatura – modello non lineare a caldo
3.1 Descrizione del modello
Per l’acciaio di armatura si adotta un modello bilineare elastico‑plastico a caldo:

ramo elastico con modulo ridotto
plateau plastico con tensione di snervamento ridotta
Formulazione:
\\[ \\sigma_s = \\begin{cases} E_{s,\ heta} \\varepsilon_s & |\\varepsilon_s| \\le \\varepsilon_{y,\ heta} \\\\ f_{y,\ heta} \\cdot \\mathrm{sign}(\\varepsilon_s) & |\\varepsilon_s| > \\varepsilon_{y,\ heta} \\end{cases} \\]
con:

\\(E_{s,\ heta} = k_{E,s}(T) E_s\\)
\\(f_{y,\ heta} = k_{y,s}(T) f_y\\)
\\(\\varepsilon_{y,\ heta} = f_{y,\ heta} / E_{s,\ heta}\\)

3.2 Scheletro di implementazione

class SteelLawL3:
    def __init__(self, Es, fy, kE_func, ky_func):
        self.Es = Es
        self.fy = fy
        self.kE = kE_func
        self.ky = ky_func

    def stress(self, strain, T):
        EsT = self.Es * self.kE(T)
        fyT = self.fy * self.ky(T)
        eps_y = fyT / EsT
        if abs(strain) <= eps_y:
            return EsT * strain
        return fyT * (1 if strain >= 0 else -1)

4. Calcestruzzo – modello non lineare compressivo a caldo
4.1 Descrizione del modello
Per il calcestruzzo si adotta un modello non lineare solo in compressione, con:

ramo parabolico degradato
annullamento della resistenza a grandi deformazioni
contributo a trazione trascurato
Formulazione normalizzata:
\\[ \\sigma_c = f_{c,\ heta} \\cdot g(\\varepsilon_c) \\]
con:

\\(f_{c,\ heta} = k_c(T) f_c\\)
\\(g(\\varepsilon)\\) funzione parabolica normalizzata

4.2 Scheletro di implementazione

class ConcreteLawL3:
    def __init__(self, fc, kc_func, eps_cu_func):
        self.fc = fc
        self.kc = kc_func
        self.eps_cu = eps_cu_func

    def stress(self, strain, T):
        # calcestruzzo teso trascurato
        if strain >= 0:
            return 0.0
        fcT = self.fc * self.kc(T)
        eps_cu_T = self.eps_cu(T)
        if strain >= eps_cu_T:
            x = strain / eps_cu_T
            return fcT * (2 * x - x * x)
        return 0.0

5. Integrazione nel MechanicalSolverL3
Il MechanicalSolverL3 deve:
usare le classi SteelLawL3 e ConcreteLawL36. Impatto numerico e stabilità
L’introduzione delle non linearità comporta:

maggiore sensibilità al passo temporale \\(\\Delta t\\)
possibile necessità di riduzione di \\(\\Delta t\\)
importanza dei test di convergenzaRegola pratica:

le leggi non lineari non devono introdurre oscillazioni numeriche spurie.

1. Test dedicati obbligatori
Prima dell’attivazione delle leggi non lineari:

☐ test monotonicità \\(\\sigma(\\varepsilon)\\)
☐ test a freddo (coerenza con L2)
☐ test a caldo per temperature chiave (20°C, 400°C, 600°C)
☐ test L3 end‑to‑end aggiornati

1. Gate di attivazione
Le leggi costitutive non lineari possono essere attivate nel solver L3 solo se:

i test FIRE_L3_TESTS_PYTEST_END_TO_END.md sono tutti verdi
la checklist FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md è soddisfatta
il Gate di rilascio L3 lo consente

1. Stato del solver dopo questo step
Con questo documento il solver L3 passa a:

PROTOTIPO AVANZATO
comportamento meccanico più realistico
maggiore affidabilità del tempo di collasso

1. Collegamenti

FIRE_L3_STEP2_ANALISI_MECCANICA.md
FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md
FIRE_L3_TESTS_PYTEST_END_TO_END.md
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
FIRE_GATE_RILASCIO_L3_FEM.md

valutare la tensione fibra‑per‑fibra
gestire il passaggio elastico → plastico
restituire una capacità resistente coerente e monotona
