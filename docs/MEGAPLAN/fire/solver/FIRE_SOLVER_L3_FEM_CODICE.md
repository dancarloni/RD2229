
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM – Checklist di validazione L3 FEM
Status: STABILE
Ruolo: Checklist tecnico‑scientifica e professionale per analisi L3 FEM al fuoco

1. Scopo della checklist
Questa checklist definisce i controlli obbligatori affinché un’analisi L3 FEM al fuoco possa essere considerata:

tecnicamente corretta
normativamente coerente
professionalmente e tecnico‑legalmente difendibile
La checklist è specifica per L3 FEM ed è aggiuntiva rispetto a:

FIRE_CHECKLIST_TECNICO_LEGALE.md

1. Ammissibilità del metodo L3
Verificare che l’uso di L3 sia motivato:

☐ Classe di resistenza elevata (R90 / R120)
☐ Caso fuori campo o non affidabile per L1/L2
☐ Presenza di snellezza elevata o II ordine significativo
☐ Obiettivo prestazionale (ottimizzazione o verifica avanzata)
⛔ Red flag: uso di L3 senza motivazione esplicita.

1. Modello FEM – requisiti minimi
3.1 Geometria e discretizzazione

☐ Geometria dell’elemento chiaramente definita
☐ Tipo di modello dichiarato:beam‑fiber
solido 2D / 3D
☐ Studio di sensibilità su:numero di elementi
numero di fibre

3.2 Analisi termica

☐ Curva di incendio dichiarata (ISO 834 / parametrica)
☐ Modello termico coerente con EN 1991‑1‑2
☐ Ipotesi semplificative esplicitate
☐ Coerenza tra dominio termico e meccanico

3.3 Analisi meccanica

☐ Leggi costitutive dipendenti dalla temperatura
☐ Non linearità materiale attiva
☐ Non linearità geometrica (II ordine) valutata
☐ Condizioni al contorno dichiarate

1. Accoppiamento termo‑meccanico

☐ Schema di accoppiamento dichiarato (weak / strong)
☐ Passo temporale $\Delta t$ giustificato
☐ Criteri di convergenza definiti
☐ Verifica di stabilità numerica eseguita

1. Criterio di collasso

☐ Criterio di collasso chiaramente definito
☐ Criterio coerente con il tipo di elemento (trave / pilastro)
☐ Soglie di deformazione motivate
☐ Coerenza con definizione di tempo di resistenza R

1. Confronti e validazione incrociata

☐ Confronto con risultati L2 (quando applicabile)
☐ Confronto con esempi di letteratura o benchmark
☐ Discussione critica delle differenze

1. Output e tracciabilità

☐ Tempo di collasso $t_{coll}$ chiaramente riportato
☐ Metodo indicato come L3
☐ Parametri FEM versionati
☐ Log di calcolo disponibile e archiviato

1. Limiti di validità e avvertenze

☐ Limiti di applicabilità dichiarati
☐ Sensibilità ai parametri discussa
☐ Avvertenza sull’uso professionale del risultato

1. Red flags (analisi NON accettabile)

⛔ Assenza di controllo di convergenza
⛔ Nessun confronto con L1/L2
⛔ Parametri FEM impliciti o non documentati
⛔ Uso automatico di L3 senza giudizio ingegneristico

1. Uso della checklist
Questa checklist deve essere:

allegata alla relazione L3 FEM
utilizzata come controllo finale obbligatorio
richiamata nei report automatici

1. Collegamenti

FIRE_PROTOTIPO_L3_MINIMALE.md
FIRE_PROGRAMMA_FUTURO_L3_FEM.md
FIRE_ANALISI_AVANZATA_L3_FEM.md
FIRE_CHECKLIST_TECNICO_LEGALE.md
