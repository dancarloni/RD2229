# SPEC_02 Functional Flows (LOCKED)

Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md`.

## Flusso 1 — Creazione progetto + setup norma
Input:
- nome progetto
- norma attiva
- metadati minimi
Output:
- progetto persistito con `schema_version`
Validazioni:
- norma non vuota
- versione schema nota
Errori tipici:
- norma assente/non supportata
Estensioni plugin:
- hook `on_project_created`

## Flusso 2 — Definizione entità di modello
Input:
- materiali, sezioni, elementi
- load case + combinazioni
Output:
- entità persistite e referenze coerenti
Validazioni:
- FK logiche (element->section/material)
- categorie load case valide
Errori tipici:
- referenze mancanti
- unità incoerenti
Estensioni plugin:
- validator per categorie specifiche (es. secondari, incendio)

## Flusso 3 — Esecuzione verifica + report + persistenza risultati
Input:
- check request (elemento, combinazione, check_code)
- parametri normativi caricati da `.jsoncode`
Output:
- `VerificationResult` persistito + output esportabile
Validazioni:
- presenza `norma_attiva`
- trace completo (`run_id`, `norm_references[]`)
Errori tipici:
- plugin check non disponibile
- parametri normativi mancanti
Estensioni plugin:
- nuovo check engine
- nuovo formato report

## LOCKED
- Pipeline minima end-to-end deve essere ripetibile headless.
- Ogni esecuzione produce trace verificabile.

## OPEN
- Orchestrazione asincrona multi-run.
- Scheduling batch.
