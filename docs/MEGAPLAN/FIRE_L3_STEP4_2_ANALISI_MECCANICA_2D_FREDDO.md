
FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO – Analisi meccanica 2D a freddo
Status: STABILE
Ruolo: STEP 4.2 – Analisi meccanica FEM 2D a freddo per pareti portanti in c.a.

1. Scopo dello STEP 4.2
Questo documento sviluppa lo STEP 4.2 della linea 2D, introducendo l’analisi meccanica 2D a freddo delle pareti portanti in calcestruzzo armato.
Lo scopo è:

validare il modello FEM 2D prima dell’incendio
verificare la correttezza delle leggi costitutive
disporre di una base solida per l’accoppiamento termo‑meccanico 2D (STEP successivo)

1. Perché l’analisi a freddo è obbligatoria
L’analisi a freddo consente di:

separare gli errori meccanici da quelli termici
eseguire confronti diretti con:metodi L2
soluzioni di letteratura
validare mesh, vincoli e carichi
Regola di progetto:

Nessuna analisi L3 2D a caldo è ammessa senza una validazione meccanica a freddo.

1. Ambito di applicazione
In questo STEP si considera:

parete rettangolare in c.a.
analisi 2D di sezione
carico assiale uniforme
assenza di gradiente termico (T = 20 °C)
Sono esclusi:

instabilità globale di parete
comportamento fuori piano
carichi orizzontali

1. Modello FEM 2D
4.1 Tipo di elementi

elementi solidi 2D (quad a 4 nodi)
mesh regolare strutturata
integrazione di Gauss standard

4.2 Stato di sforzo
Lo stato di sforzo è selezionabile:

piano‑sforzi → pareti snelle
piano‑deformazioni → pareti tozze
La scelta è un parametro di input esplicito.

1. Leggi costitutive (T = 20 °C)
5.1 Calcestruzzo

comportamento non lineare in compressione
ramo parabolico‑rettangolare
trazione trascurata
5.2 Acciaio di armatura

comportamento bilineare elastico‑plastico
snervamento a \\(f_y\\)
perfetta aderenza acciaio‑cls (prima iterazione)
Le leggi sono le stesse definite per L3 a caldo, con coefficienti termici unitari.

1. Equazioni risolte
Il solver risolve il problema di equilibrio statico:
\\[ \\mathbf{K(u)}\\, \\mathbf{u} = \\mathbf{F} \\]
con:

\\(\\mathbf{K}\\) matrice di rigidezza non lineare
\\(\\mathbf{u}\\) spostamenti nodali
\\(\\mathbf{F}\\) vettore dei carichi

1. Interfaccia del solver meccanico 2D

class MechanicalSolverL3_2D:
    def solve(self, loads, bc):
        """
        Risolve il problema meccanico a freddo
        Restituisce campi di spostamento e tensione
        """
        ...

1. Scheletro di implementazione (codice prototipale)

class MechanicalSolverL3_2D:
    def __init__(self, mesh, materials, stress_state):
        self.mesh = mesh
        self.materials = materials
        self.stress_state = stress_state

    def solve(self, loads, bc):
        # assemblaggio della matrice di rigidezza
        # applicazione condizioni al contorno
        # risoluzione iterativa (Newton-Raphson)
        return {
            "displacement_field": ...,
            "stress_field": ...
        }

9. Verifiche a freddo obbligatorie
Prima di considerare valido lo STEP 4.2 devono essere superate:

☐ patch test FEM (tensione costante)
☐ equilibrio globale delle forze
☐ distribuzione coerente delle tensioni
☐ confronto con L2 a freddo

1. Gate di avanzamento
È consentito procedere allo STEP 4.3 – Accoppiamento termo‑meccanico 2D solo se:

il solver 2D a freddo è stabile
le verifiche sono superate
la checklist L3 è soddisfatta

1. Collegamenti

FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md
FIRE_L3_STEP4_MODELLI_2D_PARETI.md
FIRE_L3_COSTITUTIVE_NONLINEARI.md
FIRE_GATE_RILASCIO_L3_FEM.md
