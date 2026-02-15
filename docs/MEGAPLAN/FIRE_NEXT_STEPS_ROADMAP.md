
FIRE_NEXT_STEPS_ROADMAP – Roadmap operativa completa
Status: STABILE Ruolo: Piano esecutivo dei prossimi step (sviluppo, test, estensioni)


0. Scopo
Questo documento raccoglie tutti i prossimi step, ordinati e vincolanti, per portare il modulo INCENDIO da knowledge base completa a sistema operativo, testato e difendibile.
Ogni step è progettato per essere indipendente, versionabile e compatibile con i PLAN esistenti.


1. Sviluppo core (obbligatorio)
1.1 Implementazione CodeModule_INCENDIO (L2)

Implementare il flusso definito in FIRE_CODEMODULE_INCENDIO.md
Copertura completa del Metodo L2 (sezione efficace)
Separazione netta:input validation
combinazioni di carico incendio
calcolo termico semplificato
calcolo meccanico sezione ridotta
Deliverable

modulo eseguibile
logging minimo
output conforme a VerificationResultItem


1.2 Implementazione Metodo L1 (tabellare)

Lookup tabellare EN 1992-1-2
Verifica automatica di ammissibilità
Esito diretto (OK / NOT_OK / NOT_APPLICABLE)
Deliverable

sub‑modulo L1
mapping input → tabella → esito


2. Test e validazione (obbligatorio)
2.1 Test automatici – benchmark

Trasformare FIRE_ESEMPIO_R60_PILASTRO.md in test automatico
Verifica di regressione
Test di non‑regressione su input limite
Deliverable

suite di test (unit + integrazione)
report test automatico


2.2 Checklist tecnico‑legale automatizzata

Tradurre FIRE_CHECKLIST_TECNICO_LEGALE.md in:controlli runtime
warning bloccanti
Deliverable

validatore automatico pre‑output


3. Estensioni funzionali (prioritarie)
3.1 Estensione a R90 / R120

Generalizzazione del tempo di esposizione
Verifica stabilità numerica del solver
Deliverable

supporto completo R30–R120


3.2 Estensione a travi in c.a.

Flessione semplice a caldo
Presso‑flessione non applicabile
Deliverable

nuovo esempio benchmark: FIRE_ESEMPIO_R60_TRAVE.md


4. Metodo avanzato (L3 – opzionale ma strategico)
4.1 Analisi termo‑meccanica avanzata

Loop temporale
Collasso esplicito
Interfaccia FEM (placeholder)
Deliverable

solver L3 sperimentale
flag di utilizzo avanzato


5. Integrazione GUI (quando il core è stabile)
5.1 GUI Input Incendio

Attivazione verifica incendio
Selezione classe R
Selezione metodo (L1/L2/L3)


5.2 GUI Output Incendio

Esito grafico R richiesta / R raggiunta
Tempo di collasso
Evidenza warning e limiti di validità


6. Reporting e output professionale
6.1 Report tecnico automatico

Sezione dedicata all’incendio
Richiami normativi automatici
Inserimento checklist compilata
Deliverable

report PDF/Markdown


7. Estensioni normative future

Pareti portanti in c.a.
Strutture in acciaio (EN 1993-1-2)
Strutture composte (EN 1994-1-2)


8. Controllo qualità e governance

Versionamento norme
Changelog tecnico
Blocco hard‑coding normativo


9. Criteri di completamento
Il modulo INCENDIO è considerato completo quando:

L1 e L2 sono implementati e testati
almeno 1 benchmark automatico è superato
checklist tecnico‑legale è soddisfatta
output è riproducibile


10. Collegamenti

FIRE_PROMPT_MASTER.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_ESEMPIO_R60_PILASTRO.md
FIRE_CHECKLIST_TECNICO_LEGALE.md
PLAN_CALCOLO.md
