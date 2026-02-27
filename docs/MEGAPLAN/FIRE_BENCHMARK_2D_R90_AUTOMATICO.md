
FIRE_BENCHMARK_2D_R90_AUTOMATICO – Benchmark automatico L3 2D (parete R90)
Status: STABILE
Ambito: Validazione numerica interna – test di regressione
Ruolo: Benchmark ufficiale per il solver L3 2D (pareti portanti in c.a.)


1. Scopo del benchmark
Il presente documento ricrea ex‑novo il benchmark automatico associato al caso studio 2D R90, con l’obiettivo di trasformare il caso applicativo in uno strumento di test automatico e riproducibile.
Il benchmark è utilizzato per:

test di regressione del solver L3 2D
controllo di stabilità numerica nel tempo
integrazione in pipeline CI/CD
supporto al Gate di rilascio L3
⚠️ Il benchmark non ha valore certificativo.


2. Caso di riferimento
Il benchmark deriva direttamente da:

FIRE_CASE_STUDIO_2D_PARETE_R90.mdOgni modifica al caso studio deve essere riflessa tramite nuova versione del benchmark.


3. Dati di riferimento congelati
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
Tutti i valori sono immutabili all’interno del benchmark.


4. Configurazione numerica standard

Incendio: ISO 834
Stato di sforzo: piano‑deformazioni
Passo temporale base: Δt = 5 s
Mesh: regolare – livello MEDIUM


5. Output attesi (assert del benchmark)
Il benchmark è superato se:

fire_method == "L3"\\[ 70\\,\	ext{min} \\le t_{coll,2D} \\le 85\\,\	ext{min} \\]
il risultato è deterministico a parità di input


6. Sensibilità numerica controllata
Il benchmark verifica anche:

variazione del passo temporale (Δt = 2.5 / 5 / 10 s)
variazione della densità di meshIl tempo di collasso non deve uscire dall’intervallo di accettazione.


7. Struttura dei test automatici

tests/
└── fire_l3_2d/
    ├── test_wall_r90_benchmark.py
    ├── test_wall_r90_dt_sensitivity.py
    └── test_wall_r90_mesh_sensitivity.py




8. Pseudocodice del test principale

def test_wall_r90_l3_2d_benchmark(solver_l3_2d):
    result = solver_l3_2d.run(fire_time_target=90)

    assert result["fire_method"] == "L3"
    assert result["esito"] == "NOT_OK"
    assert 70.0 <= result["fire_time_achieved"] <= 85.0




9. Criteri di fallimento
Il benchmark fallisce se:

l’esito cambia (OK ↔ NOT_OK)
il tempo di collasso esce dall’intervallo
il solver non converge
compaiono oscillazioni numeriche non giustificate


10. Integrazione con Gate di rilascio
Il superamento del benchmark è condizione necessaria per:
superare FIRE_GATE_RILASCIO_L3_FEM.md11. Tracciabilità
Ogni esecuzione del benchmark deve registrare:

versione del solver
parametri numerici
tempo di collasso
log di convergenza


12. Collegamenti

FIRE_CASE_STUDIO_2D_PARETE_R90.md
FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md
FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO.md
FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO.md
FIRE_GATE_RILASCIO_L3_FEM.md



consentire l’uso L3 2D in modalità assistita

esito == "NOT_OK"
il tempo di collasso soddisfa:
