
PLAN_INCENDIO_MASTER – Revisione 2026 Q1
Status: APPROVATO (revisione strutturale)
Versione: v2.0
Data: 2026‑02‑15
Ambito: Modulo di verifica al fuoco – Software di calcolo strutturale

1. Premessa – Motivo della revisione
La presente revisione del PLAN master del modulo INCENDIO si rende necessaria e non differibile a seguito dell’introduzione di modifiche sostanziali all’architettura, alle funzionalità e alla governance tecnica del modulo.
In particolare, rispetto alla versione precedente del PLAN, sono stati introdotti:

solver L3 completo in 1D e 2D
linea pareti portanti FEM 2D
benchmark automatici (R90, R120)
gate di rilascio vincolante
relazione di calcolo tipo per uso professionale assistito
estensione esplicita alle classi R120
Questa revisione allinea formalmente il PLAN allo stato reale del sistema.

1. Ambito del modulo INCENDIO (aggiornato)
Il modulo INCENDIO del software consente la verifica della resistenza al fuoco di elementi strutturali in calcestruzzo armato mediante:

L1 – Metodi tabellari
L2 – Metodi semplificati (sezione efficace)
L3 – Metodi avanzati prestazionali (analisi FEM)
1.1 Livelli L3 supportati
Il livello L3 è ora articolato come segue:

L3‑1D – elementi monodimensionali (travi, pilastri)
L3‑2D – pareti portanti (FEM 2D)
⚠️ L’uso del metodo L3 è assistito e controllato, non automatico.

1. Architettura aggiornata del modulo INCENDIO
2.1 Struttura logica dei solver

INCENDIO
 ├─ L1_TABELLARE
 ├─ L2_SEMPLIFICATO
 ├─ L3_1D_FEM
 │   ├─ Analisi termica 1D
 │   ├─ Analisi meccanica 1D
 │   ├─ Accoppiamento a caldo
 │   └─ Benchmark R60 / R90 / R120
 └─ L3_2D_FEM (PARETI)
     ├─ STEP 4.1 – Analisi termica 2D
     ├─ STEP 4.2 – Analisi meccanica 2D a freddo
     ├─ STEP 4.3 – Accoppiamento termo‑meccanico 2D a caldo
     ├─ Casi studio R90 / R120
     └─ Benchmark automatici R90 / R120

1. Stato di implementazione (2026 Q1)

Componente Stato
L1 – Tabellare ✅ stabile
L2 – Semplificato ✅ stabile
L3‑1D ✅ completo
L3‑2D (pareti) ✅ completo (prototipale avanzato)
Benchmark automatici ✅ R90 / ✅ R120
Relazione di calcolo tipo ✅ disponibile

1. Governance tecnica del metodo L3 (nuova sezione)
4.1 Principi fondamentali
Il metodo L3:

non sostituisce automaticamente L1/L2
è utilizzabile solo se motivato
è subordinato a verifica di coerenza tecnica

4.2 Benchmark automatici
Sono parte integrante del modulo:

FIRE_BENCHMARK_2D_R90_AUTOMATICO.md
FIRE_BENCHMARK_2D_R120_AUTOMATICO.md
Il mancato superamento dei benchmark inibisce il rilascio del solver L3.

4.3 Gate di rilascio
L’uso del solver L3 è consentito solo se:

superato FIRE_GATE_RILASCIO_L3_FEM.md
compilata FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
dichiarato lo stato del solver (PROTOTIPO / USO ASSISTITO)

1. Uso professionale assistito
Il modulo INCENDIO supporta l’uso professionale assistito del metodo L3, a condizione che:

sia prodotta una relazione di calcolo conforme
siano allegati benchmark e checklist
sia garantita la tracciabilità dei risultati
Documento di riferimento:

FIRE_RELAZIONE_CALCOLO_TIPO_L3_2D_PARETI.md

1. Classi di resistenza supportate
Attualmente il modulo supporta esplicitamente:

R60
R90
R120
Per R ≥ 120 l’uso del metodo L3 è fortemente raccomandato.

1. Roadmap aggiornata
7.1 Sviluppi futuri pianificati

Linea 2.5D – pareti estese in altezza
Linea 3D – solidi FEM completi
Validazione esterna su casi di letteratura

1. Limiti dichiarati
Il modulo INCENDIO:

non certifica i risultati L3
non sostituisce la responsabilità del progettista
richiede competenza specialistica

1. Tracciabilità delle revisioni

Versione Data Modifica
v1.x 2025 Modulo L3 1D
v2.0 2026‑02‑15 Introduzione L3 2D, benchmark, gate, R120

1. Collegamenti principali

FIRE_L3_STEP4_MODELLI_2D_PARETI.md
FIRE_CASE_STUDIO_2D_PARETE_R90.md
FIRE_CASE_STUDIO_2D_PARETE_R120.md
FIRE_BENCHMARK_2D_R90_AUTOMATICO.md
FIRE_BENCHMARK_2D_R120_AUTOMATICO.md
FIRE_RELAZIONE_CALCOLO_TIPO_L3_2D_PARETI.md
FIRE_GATE_RILASCIO_L3_FEM.md

Il presente documento sostituisce e aggiorna il PLAN master precedente per il modulo INCENDIO.
