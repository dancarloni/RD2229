# Modulo: `repositories`

## 1. Scopo e ambito

TBD — nessuna logica Python. Container di dati JSON/CSV: materiali storici, sorgenti materiali, materiali, tabella RD2229.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `src/repositories/__init__.py` è una sola riga di docstring. Nessun codice Python. Solo file dati in `data/`.

## 3. Evidenze

- `src/repositories/__init__.py` — 1 riga: `"""Repository abstractions for persistence of materials/sections."""`
- `src/repositories/data/historical_materials.json` — dati materiali storici
- `src/repositories/data/material_sources.json` — sorgenti materiali
- `src/repositories/data/materials.json` — catalogo materiali
- `src/repositories/data/rd2229_table.csv` — tabella RD2229
- `src/repositories/data/tables.schema.json` — schema tabelle
- Nessun test

## 4. Input/parametri

TBD — dati consumati da altri moduli tramite lettura file diretta.

## 5. Output

TBD.

## 6. Dipendenze

- `src/legacy/historical_materials.py` potrebbe leggere questi file
- `src/materials/material_repo.py` (STUB) potrebbe usarli

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Nessuna API Python di accesso ai dati
- Nessun test di validazione dei file JSON/CSV
- Relazione con `src/materials/` non chiara (entrambi gestiscono materiali)

## 9. Next steps

- [ ] Implementare `load_materials(path) -> list[Material]` in `__init__.py`
- [ ] Aggiungere test di validazione schema per i file dati
- [ ] Chiarire la relazione con `src/materials/material_repo.py`
