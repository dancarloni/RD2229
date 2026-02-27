# SPEC_03 Data Layer SQLite (LOCKED)

Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md`.

## Scopo
Definire SQLite come persistenza principale MVP per progetto e risultati.

## LOCKED
- SQLite è storage principale (OPZIONE B).
- Versionamento schema obbligatorio (`schema_version` + migrazioni incrementali).
- Repository per entità, senza imporre Unit-of-Work nell’MVP.

## Repository minimi
- `ProjectRepository`
- `MaterialRepository`
- `SectionRepository`
- `ElementRepository`
- `LoadCaseRepository`
- `CombinationRepository`
- `VerificationResultRepository`

## Contratti minimi repository
- `save(entity)`
- `get(id)`
- `list_by_project(project_id)` (ove applicabile)
- `delete(id)` (opzionale MVP)

## Source of Truth vs Derived
Source of Truth:
- progetto + entità input + risultati verifiche + trace
Derived/Cache:
- report renderizzati
- indici secondari ricostruibili

## Migrazioni
- tabella metadata con versione schema
- migrazioni forward-only, additive per MVP
- fallback: errore esplicito se DB troppo nuovo

## Retrocompatibilità
- tolleranza campi opzionali assenti
- default applicati da repository durante hydrate
