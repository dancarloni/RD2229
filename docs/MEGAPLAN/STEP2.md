Status: checking whether PLAN_INPUT_COMUNE.md defines ProjectModel fields so I include the optional update block only if relevant. I'll search the MEGAPLAN folder for the file and look for ProjectModel mentions.

# filename: docs/MEGAPLAN/PLAN_NORMATIVE_STATE_CONTRACT.md
Scopo e ambito

Allineamento contrattuale (SPEC‑ONLY) per la gestione univoca della norma attiva nel ProjectModel e del routing verso engine/report.
Scope: documentazione delle regole di lettura/scrittura, compatibilità con nomi legacy e regole di comportamento sicuro per normative miste. Nessuna modifica al Core o alla GUI: SOLO SPEC.
Campo canonico (definizione)

project_model.norma_attiva — campo canonico che identifica la norma di riferimento per l’intero progetto (string).
Valori es.: NTC2018, RD2229 (esempi; elenco definitivo in config/calculation_codes).
Vincolo: valore obbligatorio prima di eseguire verifiche.
Chi scrive / chi legge (regole vincolanti)

Scrive: la GUI di selezione normativa (azione utente: “Applica normativa”) → aggiorna esclusivamente project_model.norma_attiva.
Legge: Binding GUI↔Engine, VerificationFactory, ReportBuilder e ogni componente che decida template/parametri normativi.
Regola hard: nessun altro campo del ProjectModel sancisce la norma attiva; i vecchi nomi sono solo alias documentali (vedi compatibilità).
Compatibilità / alias (documentazione)

Alias storici nei documenti (normativa_attiva, normativa_verifica, ecc.) devono essere trattati come sinonimi a fini di lettura storica, ma ogni nuova documentazione e nuovo codice deve usare norma_attiva.
Mappatura operativa (SPEC): normativa_attiva → norma_attiva (alias only).
Routing rules (Engine e Report) — senza nuove API

VerificationEngine routing: il Binding usa project_model.norma_attiva per:
selezionare la VerificationFactory appropriata (factory lookup by norma_attiva), e
abilitare/disabilitare capitoli/verifiche applicabili (es. CAP_7 per NTC2018).
ReportBuilder routing: prende project_model.norma_attiva per scegliere il template/report‑builder comportamentale e per la verifica di omogeneità dei risultati.
Fall‑fast rule: se project_model.norma_attiva non è valorizzato, il binding blocca l’esecuzione e richiede selezione della norma in GUI.
No‑mixing rule (normative miste = comportamento safe)

Default safe behaviour: il ReportBuilder rifiuta (block) la generazione se VerificationResultItem.norm_references[] presenti nel ProjectModel.verifiche_in_relazione contengono valori non coerenti con project_model.norma_attiva.
UX: messaggio diagnostico che richiede separazione dei risultati per normativa o riallineamento di project_model.norma_attiva.
Nota: policy alternative (consentire mix con marcatura) devono essere esplicitate e tracciate come eccezioni approvate (non implicite).
Validazione e invarianti

project_model.norma_attiva deve essere presente per ogni sessione di verifica significativa.
Tutti i VerificationResultItem prodotti devono includere norm_references[] e il report deve verificare corrispondenza con project_model.norma_attiva prima della finalizzazione.
Acceptance criteria (AC2‑01 .. AC2‑05)

AC2‑01: Nei blocchi nuovi/aggiornati della documentazione viene usato esclusivamente il nome norma_attiva.
AC2‑02: La GUI di selezione norma aggiorna solo project_model.norma_attiva (testabile).
AC2‑03: Il binding di invocazione del motore legge esclusivamente project_model.norma_attiva per routing/verifiche.
AC2‑04: Il routing verso VerificationEngine e ReportBuilder è definito (non ambiguo) tramite project_model.norma_attiva e le regole di capitoli/applicabilità.
AC2‑05: In presenza di risultati con norm_references[] non coerenti rispetto a project_model.norma_attiva, il comportamento di default è safe (block report) e la UX fornisce diagnosi e opzioni di separazione.
Esempi di test locali (brevi)

TL1: unit test GUI → selezione impostata → project_model.norma_attiva == 'NTC2018'.
TL2: binding unit → project_model.norma_attiva = None → run_verifications() fallisce con messaggio valido.
TL3: report integration → verifiche_in_relazione con mix normativo → ReportBuilder rifiuta (status = CONFLICT_NORMS).
Note operative

Aggiornare tutti i documenti e i test esistenti che riferivano ai vecchi nomi (alias) e prediligere norma_attiva come unica denominazione autorizzata in nuovi blocchi SPEC.
Ogni modifica di comportamento policy‑driven dovrà essere documentata e approvata (Step 3: KB/config).
# filename: docs/MEGAPLAN/PLAN_ANALYSIS_METHOD_UI_FLAG.md
Scopo (UI‑only)

Definire il flag UI canonico che guida la presentazione/preview del metodo di analisi senza alcun impatto sui risultati numerici o sul core.
Campo UI canonico

ui_state.analysis_method — campo UI‑only (non persistente nel ProjectModel come fonte di verità normativa).
Valori ammessi (enum string):
DEFAULT — comportamento standard della GUI (nessuna preview specifica);
CROSS_PREVIEW — UI mostra suggerimenti/preview per Metodo di Cross (legend/labels only);
FEM_RESERVED — UI abilita elementi di preview per workflow FEM (placeholder; non esegue calcoli).
Regole vincolanti (separazione netta)

ui_state.analysis_method è esclusivamente UI: non può alterare project_model, non può essere letto dal Core per modificare risultati né registrato in project_model come fonte di verità.
Se l’utente sceglie una modalità non compatibile con project_model.norma_attiva la GUI mostra un avviso ma non cambia l’esito delle verifiche.
Comportamento/Impatto UI (solo gating/label)

Effetti ammessi:
mostrare etichette, help text, o disabilitare temporaneamente widget di preview;
abilitare tutorial/overlays specifici per quel metodo.
Effetti vietati:
non modificare fattori/coefficients; non scegliere combinazioni normative; non influire su VerificationEngine.
Acceptance criteria (AC2‑06 .. AC2‑07)

AC2‑06: ui_state.analysis_method è definito nel layer UI e non scrive/legge project_model per cambiare risultati.
AC2‑07: La scelta di ui_state.analysis_method ha effetto esclusivamente su gating/label/preview nella GUI; i risultati numerici rimangono invariati.
Acceptance tests locali (brevi)

TU1: selezionare CROSS_PREVIEW → UI mostra label/tooltip Cross; project_model invariato.
TU2: selezionare FEM_RESERVED → preview widget attivo; esecuzione verifiche usa comunque project_model.norma_attiva.
Linee guida di UX brevissime

Etichettare chiaramente che il flag è “UI preview only” (microcopy: “Modalità di visualizzazione — non influisce sui risultati”).
Quando ui_state.analysis_method ≠ DEFAULT, mostrare piccolo badge „Preview mode“ in header.
Update blocks — da incollare / sostituire nei file esistenti
FILE: GUI_SELEZIONE_NORMATIVA.md
REPLACE: sezione "Integrazione nel ProjectModel (vincolante)" e tutti i riferimenti a nomi legacy

REPLACE:

Integrazione nel ProjectModel (vincolante) — aggiornamento obbligatorio
Campo canonico del ProjectModel: project_model.norma_attiva (string).
Nota: questo campo sostituisce le denominazioni legacy (normativa_attiva, normativa_verifica) nelle nuove SPEC.
Regole operative:
la View di selezione aggiorna esclusivamente project_model.norma_attiva quando l’utente conferma la scelta;
project_model.norma_attiva deve essere valorizzato prima di eseguire run_verifications(); la GUI blocca l’azione e mostra il messaggio: "Selezionare la norma attiva" se assente.
UX / microcopy:
Badge persistente nella header: "Norma attiva: {project_model.norma_attiva}"
Messaggio di conferma: "Norma impostata: {project_model.norma_attiva}"
Aggiornamento terminologia: tutte le sezioni del documento sono aggiornate per usare solo norma_attiva nei nuovi blocchi; i vecchi nomi sono documentati come alias storici esclusivamente per retro‑compatibilità testuale.
Acceptance tests locali (da aggiungere)

GUI‑UT: selezione → project_model.norma_attiva impostato correttamente (es.: 'NTC2018').
GUI‑UT: tentativo di eseguire verifiche con project_model.norma_attiva == None mostra errore bloccante.
FILE: GUI_VERIFICATION_ENGINE_BINDING.md
REPLACE: tutte le occorrenze rilevanti di project_model.normativa_verifica / project_model.normativa_attiva; aggiungere regole di routing basate su norma_attiva

REPLACE:

Invarianti di binding (aggiornamento)
Il Binding legge esclusivamente project_model.norma_attiva per determinare:
quali capitoli/categorie di verifica abilitare (es. CAP_4, CAP_7), e
quale VerificationFactory utilizzare (factory lookup by norma_attiva).
Controllo pre‑esecuzione: se project_model.norma_attiva non è definito il binding rifiuta l’esecuzione e la GUI deve invitare a selezionare la norma.
Regole di abilitazione (esempi SPECIFICI, non implementativi):
cap4_enabled → true se project_model.norma_attiva indica una norma che prevede CAP_4;
cap7_enabled → true se project_model.norma_attiva supporta CAP_7.
Nota: non vengono introdotte nuove API; il binding rimane responsabile del lookup/dispatch sulla base del valore stringa project_model.norma_attiva.
Acceptance tests locali (da aggiungere)

Binding‑UT: impostare project_model.norma_attiva='NTC2018' → _cap7_enabled() ritorna true se NTC2018 supporta CAP_7 (assert sul comportamento del binding, non sul contenuto del core).
Binding‑UT: project_model.norma_attiva mancante → run_verifications() fallisce con messaggio "Selezionare la norma attiva".
FILE: GUI_RISULTATI_TO_RELAZIONE_BINDING.md
REPLACE / ADD: tracciabilità esplicita con project_model.norma_attiva + regola di safe‑handling per normative miste

REPLACE / ADD:

Tracciabilità e coerenza normativa (estensione, vincolante)
Header report obbligatorio: includere run_id, generated_on e project_model.norma_attiva.
Prima della finalizzazione, il ReportBuilder verifica che per ogni voce in ProjectModel.verifiche_in_relazione l’array VerificationResultItem.norm_references[] contenga project_model.norma_attiva.
Se viene rilevata incongruenza (una o più voci con norm_references[] non coerenti con project_model.norma_attiva) il comportamento di default è SAFETY‑BLOCK: il builder rifiuta la generazione e presenta messaggio diagnostico che richiede separazione dei risultati per normativa.
UX: messaggio esplicito "Selezione non omogenea: separare i risultati per normativa" + suggerimento per creare più relazioni distinte.
Indicazione per risultati N.A. e policy‑driven (ricorda: project_settings definisce eccezioni)
Restano valide le policy descritte (warn/block/allow), ma la coerenza normativa rispetto a project_model.norma_attiva è requisito primario.
Acceptance tests locali (da aggiungere)

Report‑IT: quando project_model.norma_attiva == 'NTC2018' e verifiche_in_relazione contiene risultati con norm_references[] = ['RD2229'] → ReportBuilder rifiuta (status = CONFLICT_NORMS).
Report‑IT: normale flusso con norm_references[] coerenti → header contiene project_model.norma_attiva, run_id e norm_references[].
FILE: PLAN_INPUT_COMUNE.md
ADD: sezione "Naming & Invariants" (inserire dopo "Metadati normativi: norma primaria, fallback consentiti")

ADD:

Naming & Invariants (Aggiunta)
Campo canonico per la norma: project_model.norma_attiva (string). Usare esclusivamente questo campo nei nuovi blocchi di SPEC e nell’integrazione GUI↔Core.
UI‑only flag: ui_state.analysis_method (vedi PLAN_ANALYSIS_METHOD_UI_FLAG.md) — non parte dello schema persistente del ProjectModel.
Invarianti:
ogni esecuzione di verifica richiede project_model.norma_attiva valorizzato;
nessuna GUI deve introdurre campi non presenti nello schema comune;
le estensioni addizionali devono rimanere compatibili (backward compatible) via schema_version.
Policy per normative miste: la generazione dei report richiede omogeneità rispetto a project_model.norma_attiva (default: block).
Acceptance tests locali (da aggiungere)

Schema‑UT: project_model contiene norma_attiva e nessuna GUI può aggiungere un campo normativo non documentato.
Migration‑UT: ogni estensione aggiuntiva è additive e documentata tramite schema_version.
Note finali (quick)

Tutte le aggiunte qui sono PLAN‑ONLY: aggiornare i file indicati con i blocchi sopra.
Dopo l’inserimento, eseguire una passata di ricerca/sostituzione nei documenti MEGAPLAN per allineare i vecchi alias a norma_attiva (documentare le eccezioni).