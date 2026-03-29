
FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE – Analisi termica 2D reale (codice)
Status: IN IMPLEMENTAZIONE
Ruolo: STEP 4.1 – Implementazione reale dell’analisi termica 2D per pareti in c.a.

1. Scopo
Questo documento implementa l’analisi termica 2D reale per le pareti in c.a. in incendio, come primo sottostep operativo della linea 2D.
Output atteso:

campo di temperatura 2D \\(T(x,y,t)\\)
stabilità numerica
riuso diretto nello STEP 4.2 (meccanica 2D)

1. Modello termico adottato

Incendio: ISO 834
Dominio: sezione 2D della parete
Discretizzazione: mesh regolare (quad)
Temperatura iniziale: 20 °C
Semplificazione iniziale:

gradiente termico per strati in funzione della distanza dalla superficie esposta
diffusione termica semplificata (no conduzione avanzata)

1. Discretizzazione 2D

Coordinate locali: \\(x,y\\)
Spessore parete discretizzato in n strati
Ogni cella FEM contiene:temperatura
riferimento materiale

1. Legge termica ISO 834
\\[ T(t) = 20 + 345 \\log_{10}(8t + 1) \\]
con \\(t\\) in minuti.
Gradiente 2D semplificato:

superficie esposta → \\(T_{ISO}(t)\\)
attenuazione lineare verso l’interno

1. Interfaccia del solver termico 2D

class ThermalSolverL3_2D:
    def step(self, time_s: float) -> None:
        ...

    def get_temperature_field(self):
        """Restituisce T(x,y)"""
        ...

6. Scheletro di codice (reale)

class ThermalSolverL3_2D:
    def __init__(self, mesh, exposed_faces):
        self.mesh = mesh
        self.T = {cell: 20.0 for cell in mesh.cells}
        self.exposed_faces = exposed_faces

    def iso_834(self, time_s):
        t_min = time_s / 60.0
        return 20 + 345 * math.log10(8 * t_min + 1)

    def step(self, time_s):
        Tsurf = self.iso_834(time_s)
        for cell in self.mesh.cells:
            d = cell.distance_to_exposed_face()
            self.T[cell] = max(20.0, Tsurf - d * self.mesh.gradient_coeff)

    def get_temperature_field(self):
        return self.T

7. Test minimi obbligatori

☐ test ISO 834 a tempi noti
☐ gradiente monotono
☐ confronto qualitativo con modello 1D

1. Gate di avanzamento
Si può procedere allo STEP 4.2 solo se:

campo termico 2D stabile
test superati

1. Collegamenti

FIRE_L3_STEP4_MODELLI_2D_PARETI.md
FIRE_L3_COSTITUTIVE_NONLINEARI.md
FIRE_GATE_RILASCIO_L3_FEM.md
