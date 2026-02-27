# SPEC_01 Domain Model (LOCKED)

Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md` (decisioni consolidate + vincoli vincolanti).

## Scopo
Definire il modello concettuale minimo per MVP con separazione rigorosa:
- Model (dati tipizzati)
- Engine (calcolo)
- Persistence/Repository (SQLite)
- UI (launcher/pagine)

## LOCKED
- App desktop offline, mono-utente, un progetto alla volta.
- Dominio strutturale: TA, SLU, SLE (estendibile), modulo incendio separato dal core strutturale.
- Ogni `VerificationResult` deve contenere trace completo con `run_id` e `norm_references[]`.
- Nessun hardcode normativo: valori da config/versioned data (`.jsoncode`), TODO espliciti se non disponibili.
- Distinzione concettuale elemento primario/secondario tramite ruolo esplicito nell’entità elemento.

## OPEN
- Estensione futura per geotecnica, FEM globale, collaboration/cloud.
- Profondità del modello incendio oltre lo scaffold MVP.

## Entità minime (MVP)
- `Project`: id, name, norma_attiva, created_at, schema_version.
- `Material`: id, project_id, code, kind, properties.
- `Section`: id, project_id, kind, dimensions.
- `Element`: id, project_id, section_id, material_id, role (`PRIMARY`/`SECONDARY`), metadata.
- `LoadCase`: id, project_id, name, category, actions, environmental.
- `Combination`: id, project_id, name, factors.
- `CheckRequest`: id, project_id, element_id, combination_id, check_code.
- `VerificationResult`: id, request_id, status (`OK/WARN/FAIL`), value, trace.
- `TraceRecord`: run_id, norm_code, norm_references[], method_id, assumptions, warnings.

## Invarianti
- `Project.schema_version` obbligatorio.
- `Project.norma_attiva` obbligatoria per esecuzione check.
- `TraceRecord.run_id` non vuoto.
- `TraceRecord.norm_references[]` non vuoto (anche con entry TODO tracciata).
- `Element.role=SECONDARY` abilita flussi secondari senza fondere il core principale.

## Glossario minimo
- Caso di carico: insieme di azioni elementari in una condizione specifica.
- Combinazione: composizione di load case con coefficienti normativi.
- Verifica: controllo normativo su elemento+combinazione.
- Risultato: esito verificabile con trace.
- Profilo normativo: parametri provenienti da `.jsoncode` e override progetto.
