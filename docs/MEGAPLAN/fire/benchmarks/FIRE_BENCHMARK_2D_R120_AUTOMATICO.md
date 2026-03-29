
FIRE_BENCHMARK_2D_R120_AUTOMATICO – Benchmark automatico L3 2D (parete R120)
Status: STABILE
Ambito: Validazione numerica interna – test di regressione avanzata
Ruolo: Benchmark ufficiale per il solver L3 2D (pareti portanti in c.a.) – classe R120

1. Scopo del benchmark
Il presente documento definisce il benchmark automatico R120 per il solver L3 2D, derivato dall’estensione del caso studio:

FIRE_CASE_STUDIO_2D_PARETE_R120.mdLo scopo del benchmark è:
garantire riproducibilità numerica dell’analisi L3 2D a durate elevate
intercettare regressioni algoritmiche
validare la stabilità del solver per incendi prolungati (R ≥ 120)
costituire gate vincolante per il rilascio del solver L3 2D
⚠️ Il benchmark non ha valore certificativo.

1. Caso di riferimento
Il benchmark è basato esclusivamente sul caso studio:

FIRE_CASE_STUDIO_2D_PARETE_R120.mdOgni modifica al caso studio richiede:
aggiornamento del benchmark
aggiornamento del Gate di rilascio

1. Dati di riferimento congelati
3.1 Geometria

Spessore parete: 0.25 m
Larghezza di calcolo: 1.00 m
Altezza: unitaria (analisi di sezione 2D)
Copriferro: 0.03 m
Superfici esposte: 1 lato
3.2 Materiali

Calcestruzzo: C25/30
Acciaio di armatura: B450C
Leggi costitutive: FIRE_L3_COSTITUTIVE_NONLINEARI.md3.3 Azioni

Sforzo normale in incendio: N_Ed_fi_ref (costante)
Azioni orizzontali: assenti
Tutti i dati sopra elencati sono immutabili nel benchmark.

1. Configurazione numerica standard

Incendio di riferimento: ISO 834
Stato di sforzo: piano‑deformazioni
Passo temporale di riferimento: Δt = 5 s
Mesh FEM 2D: regolare – livello MEDIUM
Metodo risolutivo: Newton‑Raphson incrementale

1. Output attesi (assert del benchmark)
Il benchmark è considerato superato se l’analisi restituisce:

fire_method == "L3"\\[ 90\\,\ ext{min} \\le t_{coll,2D}^{R120} \\le 105\\,\ ext{min} \\]
risultato deterministico a parità di input

1. Sensibilità numerica controllata
Il benchmark include test di robustezza rispetto a:

variazione del passo temporale:Δt = 2.5 s
Δt = 5 s
Δt = 10 s
variazione della densità di mesh (COARSE / MEDIUM / FINE)Criterio di accettazione:
il tempo di collasso non deve uscire dall’intervallo ammesso
non devono comparire instabilità numeriche

1. Struttura dei test automatici

tests/
└── fire_l3_2d/
    ├── test_wall_r120_benchmark.py
    ├── test_wall_r120_dt_sensitivity.py
    └── test_wall_r120_mesh_sensitivity.py

1. Pseudocodice del test principale

def test_wall_r120_l3_2d_benchmark(solver_l3_2d):
    result = solver_l3_2d.run(fire_time_target=120)

    assert result["fire_method"] == "L3"
    assert result["esito"] == "NOT_OK"
    assert 90.0 <= result["fire_time_achieved"] <= 105.0

9. Criteri di fallimento
Il benchmark fallisce se:

l’esito cambia (OK ↔ NOT_OK)
il tempo di collasso esce dall’intervallo ammesso
il solver non converge
compaiono oscillazioni numeriche o dipendenza patologica da Δt

1. Integrazione con Gate di rilascio
Il superamento del benchmark R120 è condizione necessaria per:
superare FIRE_GATE_RILASCIO_L3_FEM.md11. Tracciabilità
Ogni esecuzione del benchmark deve registrare:

versione del solver
parametri numerici utilizzati
tempo di collasso
log di convergenza

1. Stato del benchmark

✅ definito
✅ automatico
✅ riproducibile
✅ collegato al caso studio R120
✅ vincolante per il rilascio L3 2D

1. Collegamenti

FIRE_CASE_STUDIO_2D_PARETE_R120.md
FIRE_BENCHMARK_2D_R90_AUTOMATICO.md
FIRE_RELAZIONE_CALCOLO_TIPO_L3_2D_PARETI.md
FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO.md
FIRE_GATE_RILASCIO_L3_FEM.md

consentire l’uso del solver L3 2D per R ≥ 120
attivare modalità di uso professionale assistito

esito == "NOT_OK"
tempo di collasso compreso nell’intervallo:
