# SPEC_04 Plugins and .jsoncode (LOCKED)

Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md`.

## LOCKED
- Mantenere/estendere plugin discovery con `MODULE_SPEC`.
- `.jsoncode` è configurazione normativa centralizzata (non storage risultati).
- Tracciamento provenienza parametro: default normativo -> profilo progetto -> override utente.

## MODULE_SPEC minimo
- `id`, `name`, `version`
- `entrypoints`: `engine`, `ui`, `schemas` (opzionali)
- `capabilities`: checks, norms, output formats
- `dependencies`
- `data_contracts` (input/output minimi)

## Regole discovery/caricamento
- plugin id univoco
- versione compatibile con host
- fallback su incompatibilità: plugin disabilitato + warning tracciato

## `.jsoncode` tassonomia
- `norms/*`: coefficienti e regole globali
- `materials/*`: proprietà materiali
- `combinations/*`: set coefficienti

## Validazione minima `.jsoncode`
- chiavi obbligatorie: `id`, `version`, `namespace`, `payload`
- no valori normativi inventati: TODO espliciti ammessi
- unità di misura dichiarate nel payload quando necessarie
