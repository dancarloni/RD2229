# Kernel Normativo — Architettura (STEP 3 – Opzione A)

## Scopo

Definire una architettura in grado di supportare:

- normative moderne (NTC2018/EC8) e legacy (RD2229/39, DM92, DM96);
- metodi eterogenei (spettro, forze di piano, modelli a coefficienti);
- tracciabilità completa e difendibilità tecnico‑legale.

## Principi non negoziabili

1. **No hardcoding**: costanti e scelte interpretative devono essere parametrizzabili o dichiarate come capability.
2. **Trace-first**: ogni risultato numerico deve includere un `TraceRecord` strutturato.
3. **Plugin-like**: ogni norma vive in `src/codes/<code_id>/...` con cartelle standard.
4. **Separation of concerns**:
   - metodi in `methods/`
   - scelte interpretative in `policies/`
   - validazioni in `validators/`
   - riferimenti normativi in `docs_ref/`

## Entità chiave (concettuali)

- **NormativeCode**: identifica la norma (NTC2018, EC8, RD2229_39, DM92, DM96, ...)
- **SeismicMethodId**: identifica il modello di calcolo (spettro, statica equivalente, forze di piano, ...)
- **Capabilities**: matrice che dichiara cosa è supportato e con quali opzioni
- **Request/Response DTO**: input/output standardizzati
- **TraceRecord**: metadati di tracciabilità (fonte, metodo, assunzioni, warning, validità)

## Prodotti di calcolo (output) — STEP 3

Il kernel deve supportare almeno:

1. **Response Spectrum** (quando previsto dalla norma)
2. **Floor Forces** (forze sismiche per piano, tipiche norme legacy)

## Note su Eurocodici

- **EC8** va trattato come norma sismica.
- **EC2** va trattato come norma di **verifica materiale** (CA) e non come generatore di azioni sismiche.
