# REPOSITORY CONTRACTS

> Fonte primaria: `docs/MEGAPLAN/archived/AGGREGAZIONE.md` + `docs/specs/SPEC_03_DataLayer_SQLite.md` — LOCKED

## Storage primario: SQLite

- File: percorso configurabile (default `mvp_project.db`).
- Schema versioning: `PRAGMA user_version` + tabella `schema_migrations`.
- Migrazione: catena di funzioni `_migrate_N_to_M(conn)` in `sqlite_store.py`.
- Atomic writes: operazioni critiche in transazione `BEGIN IMMEDIATE`.

## Contratto repository generico

Ogni repository implementa:

- `save(entity) -> None` — upsert per id
- `get(id: str) -> Entity | None` — lettura per id
- `list(project_id: str) -> list[Entity]` — lista per progetto

## Repository presenti (MVP)

| Repository | Entità | Tabella SQLite |
|-----------|--------|---------------|
| `ProjectRepository` | `Project` | `projects` |
| `MaterialRepository` | `Material` | `materials` |
| `SectionRepository` | `Section` | `sections` |
| `ElementRepository` | `Element` | `elements` |
| `LoadCaseRepository` | `LoadCase` | `load_cases` |
| `CombinationRepository` | `Combination` | `combinations` |
| `CheckRequestRepository` | `CheckRequest` | `check_requests` |
| `VerificationResultRepository` | `VerificationResult` | `verification_results` |

## Invarianti

1. `project_id` sempre presente come foreign key sulle entità dipendenti.
2. `id` è sempre UUID hex (32 caratteri esadecimali).
3. `created_at` è ISO 8601 UTC (generato con `datetime.now(UTC).isoformat()`).
4. `schema_version` nella tabella `projects` indica la versione del modello dati.

## Migrazione schema

- Versione corrente: `1` (PRAGMA user_version).
- Nuove versioni: incremento intero, mai decremento.
- Ogni migrazione è idempotente e transazionale.
- Compatibilità: file DB versione N può essere aperto da codice versione N+k solo se esiste catena di migrazione completa.

## Source of truth

- SQLite è la fonte primaria per i dati di progetto.
- I file `.jsoncode` sono configurazioni di calcolo, non dati di progetto.
- I risultati delle verifiche sono persistiti in SQLite con trace completo.
