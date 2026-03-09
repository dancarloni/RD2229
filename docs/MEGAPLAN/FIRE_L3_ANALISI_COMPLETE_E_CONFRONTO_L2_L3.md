
FIRE_L3_ANALISI_COMPLETE_E_CONFRONTO_L2_L3 – Analisi L3, confronto e percorso evolutivo
Status: STABILE
Ruolo: Documento operativo per esecuzione analisi L3 complete, confronto L2 vs L3 e roadmap di evoluzione verso FEM avanzato

1. Scopo del documento
Questo documento definisce:

come eseguire analisi L3 complete (in ambito prototipale, end‑to‑end)
come confrontare in modo tecnicamente sensato L2 vs L3
come evolvere il sistema verso:solver FEM interno maturo
modelli 2D / 3D
uso professionale assistito e controllato
Il documento è operativo, non teorico.

1. Esecuzione di analisi L3 complete (ambito prototipale)
2.1 Quando eseguire L3
L’analisi L3 deve essere eseguita quando:

L2 è non applicabile o non conservativo
R90 / R120 con snellezza significativa
comportamento fortemente non lineare
richiesta di valutazione del tempo di collasso

2.2 Flusso operativo L3 completo
Per ogni elemento strutturale:

Definizione input incendio (classe R, curva, lati esposti)
Costruzione modello L3 (STEP 1–2–3)
Esecuzione loop termo‑meccanico completo
Determinazione:$t_{coll}$
meccanismo di collasso
Produzione VerificationResultItem
Output minimo:

fire_method = L3
fire_time_achieved
esito
warning_note

2.3 Stato dei risultati L3
I risultati L3 sono classificati come:

PROTOTIPALI (default)
VALIDATI (solo dopo gate completo)
⚠️ I risultati prototipali non sono certificativi.

1. Confronto L2 vs L3 (metodologia corretta)
3.1 Obiettivo del confronto
Il confronto L2 vs L3 non serve a:

dimostrare che L3 è “migliore”
Serve a:

comprendere dove e perché L2 è conservativo o meno
individuare limiti di applicabilità

3.2 Grandezze da confrontare
Per lo stesso elemento:

tempo di resistenza:$t_{L2}$
$t_{L3}$
meccanismo di collasso
sensibilità a:$\Delta t$
leggi costitutive

3.3 Interpretazione dei risultati
Casi tipici:

$t_{L3} \approx t_{L2}$ → L2 adeguato
$t_{L3} < t_{L2}$ → L2 non conservativo (attenzione)
$t_{L3} > t_{L2}$ → L2 conservativo
⚠️ Non è ammesso usare L3 per “forzare” risultati più favorevoli.

1. Evoluzione verso solver FEM interno
4.1 Obiettivo
Passare da:

solver L3 prototipale
A:

solver FEM interno robusto e validato

4.2 Step di evoluzione

Consolidamento solver beam‑fiber 1D
Raffinamento numerico (convergenza, stabilità)
Modularizzazione:termico
meccanico
accoppiamento

1. Evoluzione verso modelli 2D / 3D
5.1 Quando servono modelli 2D / 3D

pareti portanti
sezioni complesse
meccanismi locali

5.2 Percorso suggerito

Fase 1: sezioni 2D isolate
Fase 2: elementi solidi semplificati
Fase 3: accoppiamento globale selettivo
Ogni fase richiede:

nuovi test
nuova checklist
nuovo gate

1. Uso professionale assistito
6.1 Concetto
L3 non deve mai diventare:

“calcolo automatico invisibile”
Deve essere:

assistito
trasparente
controllato

6.2 Requisiti minimi

avvertenze esplicite
richiesta di motivazione dell’uso L3
allegazione checklist e gate
tracciabilità completa

1. Gate di utilizzo professionale
L’uso professionale assistito è ammesso solo se:

superato FIRE_GATE_RILASCIO_L3_FEM.md
checklist L3 completa
revisione ingegneristica documentata

1. Stato finale del sistema
Con questo documento il sistema supporta:

✅ analisi L3 complete (prototipali)
✅ confronto L2 vs L3 consapevole
✅ percorso di crescita controllato

1. Collegamenti

FIRE_L3_STEP1_ANALISI_TERMICA.md
FIRE_L3_STEP2_ANALISI_MECCANICA.md
FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md
FIRE_L3_TESTS_PYTEST_END_TO_END.md
FIRE_L3_COSTITUTIVE_NONLINEARI.md
FIRE_GATE_RILASCIO_L3_FEM.md
