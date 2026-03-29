# SPEC_05 VBA Migration and Test Strategy (LOCKED)

Fonte primaria: `docs/MEGAPLAN/archived/AGGREGAZIONE.md`.

## LOCKED

- Migrazione VBA -> Python backend moderno è obbligatoria.
- MVP: predisposizione + golden tests, non conversione totale immediata.
- Modulo incendio separato dal core strutturale; in MVP scaffold/contratti dati.

## Strategia migrazione

1. Inventario macro e dipendenze (input/output/Excel references)
2. Decomposizione in funzioni pure equivalenti
3. Golden tests (baseline VBA vs Python con tolleranze)
4. Integrazione progressiva nel motore plugin

## Scheda macro (template obbligatorio)

- nome macro
- responsabilità
- input richiesti
- output attesi
- dipendenze esterne
- unità di misura
- tolleranza confronto
- stato migrazione

## Test minimi non regressione

- round-trip persistence SQLite
- invarianti dominio
- migrazione schema base
- trace `run_id` + `norm_references[]`
- end-to-end headless

## OPEN

- Strategia automatica di estrazione macro da cartelle VBA storiche.
- Catalogo tolleranze per famiglia di calcolo.
