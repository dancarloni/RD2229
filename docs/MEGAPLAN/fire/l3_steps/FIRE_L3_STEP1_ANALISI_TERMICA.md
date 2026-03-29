
FIRE_L3_STEP1_ANALISI_TERMICA – Step 1 implementazione reale solver FEM L3
Status: IN IMPLEMENTAZIONE
Ruolo: Primo step concreto dell’implementazione reale del solver FEM L3 (analisi termica)

1. Obiettivo dello step
Questo documento avvia l’implementazione reale, passo‑passo, del solver L3 FEM avanzato, partendo dalla componente termica, che costituisce la base di qualunque analisi termo‑meccanica.
Questo step:

è indipendente dall’analisi meccanica
produce output riutilizzabile negli step successivi
è verificabile autonomamente

1. Perché si parte dall’analisi termica
Motivazioni tecniche:

la temperatura governa la degradazione dei materiali
l’analisi meccanica L3 dipende interamente da \\(T(x,t)\\)
la EN 1991‑1‑2 consente una chiara separazione concettuale termico / meccanico
Regola architetturale:

Nessuna analisi meccanica L3 può essere sviluppata senza un solver termico stabile e testato.

1. Ambito dello Step 1 (volutamente limitato)
In questo step si implementa solo:

incendio ISO 834
modello 1D beam‑fiber
temperatura uniforme per fibra
nessuna diffusione spaziale avanzata
Sono esclusi:

incendi parametrici
modelli 2D / 3D
scambio termico avanzato

1. Interfaccia del modulo termico
Il modulo termico L3 deve esporre un’interfaccia chiara e minimale:

class ThermalSolverL3:
    def step(self, time_s: float) -> None:
        ...

    def get_fiber_temperatures(self) -> list[float]:
        ...

Questa interfaccia sarà usata direttamente dal solver meccanico nello Step 2.

1. Modello termico adottato (ISO 834)
Curva nominale:
\\[ T(t) = 20 + 345 \\log_{10}(8t + 1) \\]
con:

\\(T\\) in °C
\\(t\\) in minuti
Implementazione:

il tempo interno è gestito in secondi
la conversione a minuti è interna al solver

1. Scheletro di implementazione (codice reale)

class ThermalSolverL3:
    def __init__(self, fibers: int):
        self.fibers = fibers
        self.temperatures = [20.0] * fibers

    def iso_834_temperature(self, time_s: float) -> float:
        t_min = time_s / 60.0
        return 20.0 + 345.0 * math.log10(8.0 * t_min + 1.0)

    def step(self, time_s: float) -> None:
        T = self.iso_834_temperature(time_s)
        self.temperatures = [T] * self.fibers

    def get_fiber_temperatures(self) -> list[float]:
        return self.temperatures

⚠️ Questo codice non è definitivo, ma è:

testabile
deterministico
compatibile con il prototipo L3

1. Output dello Step 1
Output garantito:

vettore \\(T_i(t)\\) per ciascuna fibra
andamento temporale monotono
assenza di instabilità numerica
Questo output sarà input diretto dello Step 2.

1. Test minimi obbligatori
Prima di procedere allo Step 2 devono essere superati:

☐ test ISO 834 a tempi noti (0, 30, 60, 120 min)
☐ test di monotonicità della temperatura
☐ test di ripetibilità

1. Gate di avanzamento allo Step 2
È consentito procedere allo Step 2 – Analisi meccanica L3 solo se:

tutti i test termici sono superati
l’interfaccia è stabile
il modulo è versionato

1. Prossimo step (NON ancora implementato)
Step 2 – Analisi meccanica beam‑fiber a caldo:

leggi costitutive dipendenti da temperatura
integrazione delle fibre
calcolo capacità resistente nel tempo

1. Collegamenti

FIRE_PROTOTIPO_L3_MINIMALE.md
FIRE_SOLVER_L3_FEM_CODICE.md
FIRE_GATE_RILASCIO_L3_FEM.md
PLAN_CALCOLO.md
