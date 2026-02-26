
FIRE_PROMPT_MASTER – Prompt operativo per GitHub Copilot (modulo incendio)
Status: STABILE
Ruolo: Prompt master vincolante per l’uso corretto della knowledge base incendio


1. Scopo del documento
Questo documento definisce il prompt master ufficiale da utilizzare in VS Code con GitHub Copilot per:

sviluppo del modulo incendio
implementazione del CodeModule_INCENDIO
verifica, debug e test delle verifiche di resistenza al fuoco
Il prompt garantisce:

uso corretto delle fonti
rispetto dei vincoli architetturali
assenza di hard‑coding normativo
coerenza tecnico‑legale


2. Principio fondamentale (da non violare)


I PLAN sono vincoli architetturali.
I FIRE_*.md sono base di conoscenza tecnico‑normativa.


Copilot non deve mai:

duplicare teoria nei PLAN
introdurre formule o coefficienti non presenti nei FIRE_*.md
inventare parametri normativi


3. Prompt master (versione da copiare e usare)

CONTESTO DEL REPOSITORY

Nel repository sono presenti documenti con ruoli distinti:

1) VINCOLI ARCHITETTURALI (OBBLIGATORI)
- docs/plan/PLAN_MASTER.md
- docs/plan/PLAN_CALCOLO.md
- docs/plan/PLAN_INPUT_COMUNE.md
- docs/plan/PLAN_OUTPUT_COMUNE.md
- docs/plan/PLAN_GUI.md

2) KNOWLEDGE BASE – INCENDIO
- docs/knowledge/fire/FIRE_MASTER.md
- docs/knowledge/fire/FIRE_NORMATIVA_NTC.md
- docs/knowledge/fire/FIRE_NORMATIVA_EC.md
- docs/knowledge/fire/FIRE_TEORIA_CALCOLO.md
- docs/knowledge/fire/FIRE_CODEMODULE_INCENDIO.md
- docs/knowledge/fire/FIRE_ESEMPIO_R60_PILASTRO.md
- docs/knowledge/fire/FIRE_CHECKLIST_TECNICO_LEGALE.md
- docs/knowledge/fire/FIRE_INTEGRAZIONE_SOFTWARE.md

REGOLE VINCOLANTI
- I PLAN definiscono l’architettura e NON contengono teoria
- I file FIRE_* contengono la teoria, la normativa e gli esempi
- Nessun parametro normativo deve essere hardcoded
- Tutti i risultati devono essere espressi come VerificationResultItem
- Metodo (L1/L2/L3), norma e versione devono essere sempre dichiarati
- Se un caso è fuori campo normativo, restituisci NOT_APPLICABLE

TASK
[descrivi qui l’operazione richiesta: implementazione, verifica, refactor, test]




4. Prompt derivati consigliati
4.1 Implementazione solver

Usa come vincoli i PLAN_*.md.
Usa come base teorica esclusiva i file FIRE_*.md.

Implementa il CodeModule_INCENDIO per il metodo L2,
coerente con FIRE_CODEMODULE_INCENDIO.md e FIRE_TEORIA_CALCOLO.md.

Non introdurre nuovi campi di input.
Non hardcodare coefficienti normativi.




4.2 Debug di una verifica incendio

Analizza la verifica incendio utilizzando:
- FIRE_ESEMPIO_R60_PILASTRO.md come benchmark
- FIRE_CHECKLIST_TECNICO_LEGALE.md come controllo

Individua eventuali violazioni normative o di architettura.




4.3 Estensione normativa

Estendi il modulo incendio a un nuovo caso
senza modificare i PLAN.

Aggiorna solo i file FIRE_* se necessario,
indicando chiaramente il riferimento normativo.




5. Errori da evitare (check automatico)
Copilot sta sbagliando se:

introduce numeri senza fonte normativa
usa formule non presenti in FIRE_TEORIA_CALCOLO.md
modifica i PLAN per aggiungere teoria
restituisce risultati senza metodo o norma


6. Uso in pratica
Questo prompt deve essere:

incollato all’inizio della sessione Copilot
riutilizzato per ogni task incendio
considerato parte integrante della documentazione


7. Collegamenti

PLAN_MASTER.md
FIRE_MASTER.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_CHECKLIST_TECNICO_LEGALE.md
