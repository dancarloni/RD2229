# Documentazione Modulo: `checks`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `checks` |
| **Path** | `src/checks` |
| **Tipo** | package |
| **File .py rilevati** | 2 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo e ambito

Registro centralizzato di specifiche di verifica (`CheckSpec`) per tutte le normative supportate. Ogni `CheckSpec` associa un ID verificabile a una norma, dei tag, e un callable `compute` (attualmente `None` per tutte le voci built-in).

---

## 3. Stato reale

**PARZIALE**

Motivazione oggettiva: `src/checks/registry.py` (~350 righe) ha infrastruttura reale (`CheckRegistry`, `CheckSpec`, `NormRef`) con metodi implementati (`register`, `get`, `filter_by_tags`, `coverage_for_norm`). Le ~20 voci seed built-in hanno `compute=None` (TODO) — nessun calcolo effettivo è cablato. Nessun test trovato.

---

## 4. Evidenze

- `src/checks/registry.py` — `CheckRegistry` con metodi reali; voci seed build-in con `compute=None`
- Riferimenti normativi: RD2229 (flessione/pressoflessione/taglio TA), DM96 (SLU), NTC2018 (SLU/SLE/vento) — come stringhe ID nelle voci
- Nessun test trovato in `tests/` o `src/tests/`

---

## 5. Input/parametri

- `register(spec: CheckSpec)` — registra una specifica
- `get(check_id: str) -> CheckSpec` — recupera per ID
- `coverage_for_norm(norm_id: str) -> list[CheckSpec]` — filtra per norma

---

## 6. Output

- `CheckSpec` dataclass: `id`, `norm_id`, `tags`, `compute` (callable | None)

---

## 7. Dipendenze

- `src/checks/__init__.py` re-esporta `CheckRegistry`, `CheckSpec`, `NormRef`, `get_registry`, `reset_registry`

---

## 8. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/checks/registry.py` — voci seed con `norm_id="RD2229"` |
| DM96 | `src/checks/registry.py` — voci seed con `norm_id="DM96"` |
| NTC2018 | `src/checks/registry.py` — voci seed con `norm_id="NTC2018"` |

Clausole specifiche: TBD (non compaiono come stringhe nel codice).

---

## 9. Gap/TODO/Limitazioni

- Tutti i `compute` callable sono `None` — nessun calcolo eseguibile
- Nessun test di integrazione o smoke
- Non usato dal pipeline principale (`src/core/pipeline.py` non importa `src.checks`)

---

## 10. Next steps

- [ ] Collegare `compute` callable alle funzioni in `src/methods/checks_*.py`
- [ ] Aggiungere test che verifichino almeno un check end-to-end
- [ ] Integrare `get_registry()` nel dispatcher `src/methods/verification/dispatcher.py`
