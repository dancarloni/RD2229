# Documentazione Modulo: `gui`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `gui` |
| **Path** | `src/gui` |
| **Tipo** | package |
| **File .py rilevati** | 8 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

Layer GUI thin: entry point verso `src/ui/modern/app.main()`, selettore normativa NTC2018, stub per finestre elementi secondari e widget.

---

## 3. Evidenze

- `src/gui/entrypoint.py` — delega a `src.ui.modern.app.main()`
- `src/gui/ntc2018_selector.py` — `list_available_codes()` reale
- `src/gui/secondary_elements/editor.py` — ~15 righe, classe skeleton
- `src/gui/secondary_elements/results_view.py` — ~10 righe, classe skeleton
- `src/gui/widgets/norm_selector.py` — ~7 righe, skeleton
- Test: `tests/legacy_qt/test_norm_selector.py`, `tests/legacy_qt/test_secondary_editor.py`

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | `list_available_codes() -> list[str]` | Restituisce codici normativi disponibili |
| Output | `list[str]` | Lista codici (`["RD2229", "NTC2018", ...]`) |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/legacy_qt/test_norm_selector.py` | TBD | — |
| `tests/legacy_qt/test_secondary_editor.py` | TBD | — |

---

## 6. Fonti normative

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/gui/entrypoint.py` — docstring |
| NTC2018 | `src/gui/ntc2018_selector.py` — codice listato |

Clausole: TODO

---

## 7. Dipendenze interne

- `src/ui/modern/app` — `main()` (delegato)
- `src/codes/ntc2018/secondary_elements/` — modelli elementi secondari

---

## 8. Gap / TODO / Limitazioni

- Sub-package `secondary_elements/` quasi completamente non implementato
- `entrypoint.py` è un thin proxy — nessuna logica GUI diretta
- Widget in `widgets/` sono skeleton

---

## 9. Next steps

- [ ] Implementare `secondary_elements/editor.py` come finestra Qt funzionale
- [ ] Collegare `gui/entrypoint.py` a un entry point autonomo se necessario
- [ ] Aggiungere test headless per `secondary_elements/` widgets
- [ ] Compilare sezioni TBD
