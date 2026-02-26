
FIRE_GATE_RILASCIO_L3_FEM – Gate di rilascio del solver L3 FEM
Status: VINCOLANTE
Ruolo: Criterio formale di accettazione e rilascio del solver L3 FEM al fuoco


1. Scopo del documento
Questo documento definisce il gate di rilascio obbligatorio per qualsiasi versione del solver L3 FEM al fuoco, sia essa:

prototipo operativo
versione interna di validazione
futura versione professionale assistita
Il solver NON può essere rilasciato né utilizzato se anche una sola condizione di questo gate non è soddisfatta.


2. Documenti di riferimento obbligatori
Il gate di rilascio si basa congiuntamente su:

FIRE_CHECKLIST_TECNICO_LEGALE.md
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
FIRE_PROTOTIPO_L3_MINIMALE.md
FIRE_SOLVER_L3_FEM_CODICE.md
FIRE_PROGRAMMA_FUTURO_L3_FEM.md


3. Pre‑requisiti non negoziabili
Prima di qualsiasi valutazione di rilascio devono essere disponibili:

☐ Codice sorgente del solver L3 FEM versionato
☐ Log di calcolo completo (termico + meccanico)
☐ Output strutturato conforme a VerificationResultItem
☐ Dichiarazione esplicita dello status del solver (PROTOTIPO / VALIDATO)
⛔ In assenza di uno solo di questi elementi il rilascio è automaticamente negato.


4. Gate 1 – Conformità normativa
Derivato dalla normativa tecnica e dalla checklist tecnico‑legale.
Tutte le seguenti condizioni devono essere soddisfatte:

☐ Norma di riferimento dichiarata (EN 1991‑1‑2, EN 1992‑1‑2)
☐ Metodo di verifica esplicitamente indicato come L3
☐ Motivazione tecnica dell’uso di L3 esplicitata
☐ Limiti di validità chiaramente dichiarati


5. Gate 2 – Conformità tecnica del modello

☐ Modello FEM chiaramente descritto (beam‑fiber / solido)
☐ Accoppiamento termo‑meccanico implementato e documentato
☐ Criterio di collasso definito e motivato
☐ Parametri FEM espliciti e versionati


6. Gate 3 – Qualità numerica

☐ Studio di convergenza numerica eseguito
☐ Stabilità verificata al variare del passo temporale $\Delta t$
☐ Assenza di collassi numerici non giustificati


7. Gate 4 – Validazione incrociata

☐ Confronto con metodo L2 (quando applicabile)
☐ Confronto con casi di letteratura o benchmark noti
☐ Analisi critica delle differenze


8. Gate 5 – Test automatici

☐ Test pytest L3 superati
☐ Test negativi (NOT_OK) verificati
☐ Test di regressione L2 vs L3 superati


9. Gate 6 – Responsabilità professionale

☐ Avvertenza sull’uso professionale del solver presente
☐ Dichiarazione di non certificabilità (se prototipo)
☐ Revisione ingegneristica documentata


10. Esito del gate di rilascio
Il solver L3 FEM può essere dichiarato:

✅ RILASCIABILE PER USO INTERNO CONTROLLATO
⛔ NON RILASCIABILE
Ogni rilascio deve essere:

motivato
tracciato
associato a una versione specifica del codice


11. Uso del gate
Questo gate deve essere:

applicato prima di ogni rilascio
allegato alla documentazione di progetto
richiamato nei report automatici del software


12. Collegamenti

FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
FIRE_CHECKLIST_TECNICO_LEGALE.md
FIRE_SOLVER_L3_FEM_CODICE.md
FIRE_PROTOTIPO_L3_MINIMALE.md
FIRE_PROGRAMMA_FUTURO_L3_FEM.md
