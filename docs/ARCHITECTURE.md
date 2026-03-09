# Architecture Summary (LOCKED/OPEN)

Questo documento sintetizza le decisioni architetturali correnti derivate da `docs/MEGAPLAN/AGGREGAZIONE.md`.

## Principi

- Separazione netta: UI != Engine != Persistence != Domain Model.
- Modularità via plugin (`MODULE_SPEC`) e contratti dati.
- Tracciabilità completa dei risultati (`run_id`, `norm_references[]`, parametri usati).
- Configurazione normativa centralizzata con `.jsoncode`.

## Vista a blocchi

- `UI (PySide6/PyQt6 launcher)`
  - orchestration di flussi utente
  - nessuna formula normativa hardcoded
- `Application/Engine`
  - esecuzione check tramite moduli/plugin
  - produzione `VerificationResult`
- `Domain Model`
  - entità tipizzate e invarianti
- `Persistence`
  - SQLite (MVP principale), schema versioning, migrazioni
- `Config`
  - `.jsoncode` con validazione minima e provenance

## Scope MVP implementativo

- progetto + entità minime (material/section/element/loadcase/combination)
- 1 verifica placeholder dichiarata e tracciata
- persistenza SQLite per input e risultati
- plugin core + scaffold incendio
- test minimi end-to-end

## LOCKED

- Offline mono-utente
- incendio separato
- plugin/discovery mantenuto
- no inventare valori normativi

## OPEN

- evoluzione del launcher unico su tutte le GUI
- migrazione completa legacy GUI
- orchestrazione multi-progetto/batch

## Motivazioni

- Ridurre rischio di regressione in codebase eterogenea.
- Consentire implementazione incrementale verificabile.
- Rendere persistenza e trace auditable fin da MVP.
