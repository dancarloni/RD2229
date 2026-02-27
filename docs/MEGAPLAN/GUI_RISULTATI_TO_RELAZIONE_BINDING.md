Status: aggiorno la specifica esistente per applicare i vincoli richiesti. Prossimo passo: fornisco la versione rivista pronta da incollare in GUI_RISULTATI_TO_RELAZIONE_BINDING.md.

Aggiornamento: GUI_Risultati → Relazione (binding) — allineamenti vincolanti
TL;DR — Manteniamo la regola che la selezione per la relazione è sempre basata su ProjectModel.verifiche_in_relazione; l’inclusione automatica diventa un default configurabile; il comportamento per NOT_APPLICABLE è policy‑driven (default = warning, blocco solo se configurato); il ratio deve provenire da VerificationResultItem (GUI solo formatta). Inoltre la relazione deve riportare norm_references[] e run_id per piena tracciabilità.

Modifiche chiave (sintesi)
Selezione per report = univocamente da ProjectModel.verifiche_in_relazione. L’“inclusione automatica” è un comportamento predefinito configurabile (non una regola fissa).
Gestione NOT_APPLICABLE: default = inclusione consentita con warning; blocco solo se la policy di progetto lo richiede.
ratio è fonte‑of‑truth: usare VerificationResultItem.ratio; la GUI può soltanto format‑display (3 decimali).
Aggiunta tracciabilità: ProjectModel.norm_references[] e ProjectModel.run_id devono comparire nell’header della relazione e nei metadati.
Specifica aggiornata (sezioni rilevanti)
Principio fondamentale (invariato)
La Relazione di Calcolo NON ricalcola nulla. Input esclusivo: VerificationResult già validati.
Autorità della selezione
La selezione dei risultati da inserire in relazione è sempre governata da ProjectModel.verifiche_in_relazione.
L’opzione “Includi automaticamente tutte le verifiche eseguite” è un default configurabile (es. project_settings.report.inclusion_default = 'auto' | 'manual'). Non è più un comportamento rigido del view.
Policy per risultati N.A. (NOT_APPLICABLE)
Default project policy: na_handling = 'warn' → consentire inclusione ma evidenziare con warning.
Alternative configurabili: na_handling = 'block' (impedisce inclusione/generazione) o 'allow' (inclusione senza warning).
La GUI riflette la policy (checkbox disabilitata se block, checkbox abilitata + icona warning se warn).
Tracciabilità estesa (obbligatoria)
ProjectModel deve esporre:
verifiche_in_relazione: lista autorevole per il builder
norm_references[]: elenco stringhe (normative citate) inserite nell’header del report
run_id: identificatore unico della sessione/verifica da riportare in header/metadata
Il ReportBuilder inserisce run_id e norm_references[] nell’intestazione Markdown e in metadata (audit trail).
Fonte del Ratio
ratio deve essere letto da VerificationResultItem.ratio.
La GUI applica solo formattazione testuale a 3 decimali (es.: display / Markdown: 0.732).
È vietato derivare ratio nella view o ricalcolarlo per la relazione.
Ruoli GUI vs Builder (coerenza)
RisultatiView espone selezione (modale estesa) e salva l’esatta lista in ProjectModel.verifiche_in_relazione.
ReportBuilder esegue un’ultima validazione policy‑driven (rispettando project_settings.report.*) ma NON modifica i dati.
Se la policy richiede blocco (es. na_handling == 'block') il builder rifiuta e fornisce messaggio diagnostico coerente con l’UI.
UX / controllo comportamentale (concretezza)
Modalità base: tutte le verifiche eseguite possono essere incluse automaticamente solo se inclusion_default == 'auto'; altrimenti l’utente seleziona manualmente.
NOT_APPLICABLE: riga con status == N.A. mostra icona ⚠️ e tooltip:
Default: "Verifica N.A. — inclusione consentita (configurazione: avviso)."
Se policy == block: checkbox disabilitata + tooltip "Includere disabilitato dalla policy di progetto".
Configurazioni utente/progetto disponibili (descrizione UX):
Toggle Report: Inclusione automatica (default ON = auto, OFF = manual)
Select Report: NA handling → [Warn (default) | Block | Allow]
Anteprima: header dell’anteprima mostra run_id + norm_references[] + conteggio voci incluse.
Mappatura dati aggiornata (visual → report)
VerificationResult.reference.paragrafo → titolo voce
capitolo_ntc → sezione (CAP_4 / CAP_7)
demand → Ed
capacity → Rd
ratio → Ed/Rd (presa da VerificationResultItem.ratio; GUI format a 3 decimali)
status → Esito
norm_references[] (ProjectModel) → header/note normative
run_id (ProjectModel) → header / metadata di tracciamento
Policy‑driven validation (sostituisce i blocchi rigidi)
Le regole di inclusione/generazione sono determinate dalle impostazioni di progetto (project_settings.report.*).
Comportamento predefinito (safe): inclusione automatica permessa, N.A. provoca solo warning.
Se il team richiede rigore, impostare na_handling = 'block' e inclusion_default = 'manual'.
Criteri di accettazione (aggiornati e testabili)
Functional

FA1: Se ProjectModel.verifiche_in_relazione contiene 3 verification (normativa NTC2018), ReportBuilderNTC2018.build() produce Markdown con header contenente run_id e norm_references[], e 3 voci con ratio uguale a VerificationResultItem.ratio formattato a 3 decimali.
FA2: Default behavior (policy 'warn'): voce status == N.A. è selezionabile ma genera un avviso in UI; builder include la voce con marcatura di avviso.
FA3: Se project_settings.report.na_handling == 'block', il builder rifiuta la generazione se verifiche_in_relazione contiene voci N.A.; UI e test devono mostrare messaggio coerente.
FA4: Se inclusion_default == 'auto', dopo l’esecuzione delle verifiche ProjectModel.verifiche_in_relazione viene popolato automaticamente; se 'manual', rimane vuoto finché l’utente non seleziona.
FA5: ratio mostrato nella UI e riportato nel Markdown corrisponde esattamente al valore VerificationResultItem.ratio formattato (verificare che UI non esegua calcolo).
Traceability / Metadata

T1: Il Markdown generato contiene header con run_id, generated_on e norm_references[].
T2: Le selezioni salvate in ProjectModel.verifiche_in_relazione sopravvivono a save/load progetto.
Non‑functional

N1: Generazione Markdown (fino a 200 verifiche) completata in < 2s.
Messaggi d’errore / microcopy (standard)
"Esegui le verifiche prima di generare la relazione"
"Verifica non eseguita — inclusione consentita (configurazione: avviso)"
"Inclusione di verifiche N.A. bloccata dalla policy di progetto"
"Normativa attiva non compatibile con il ReportBuilder selezionato"
"Selezione non omogenea: separare i risultati per normativa"
Acceptance checklist (da verificare in PR / test)
 ProjectModel.verifiche_in_relazione è l’unica fonte per la generazione del report
 inclusion_default è configurabile e rispetta il comportamento UI
 na_handling default = warn; opzioni block/allow testate
 ratio proviene da VerificationResultItem.ratio (UI format a 3 decimali)
 norm_references[] e run_id presenti nell’header Markdown
 Test unit + integrazione per tutti i casi policy‑driven
Decisione principale

Conversione delle regole rigide in policy configurabili (default safe = inclusione automatica consentita + warning per N.A.). Persistenza e tracciabilità tramite verifiche_in_relazione, norm_references[] e run_id.
Nota finale ✨
Questa è la versione aggiornata PLAN‑ONLY da sostituire in GUI_RISULTATI_TO_RELAZIONE_BINDING.md. Nessuna modifica di codice è proposta qui — solo regole UX, contratto dati e criteri di accettazione pronti per implementazione