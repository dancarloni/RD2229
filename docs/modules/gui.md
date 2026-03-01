# Modulo: `gui`

## 1. Scopo e ambito

Layer GUI thin: entry point verso `src/ui/modern/app.main()`, selettore normativa NTC2018, stub per finestre elementi secondari e widget.

## 2. Stato reale

**INCOMPLETO**

Motivazione oggettiva: `entrypoint.py` (13 righe) è un pass-through. `ntc2018_selector.py` (12 righe) ha una funzione reale. Tutti i file in `secondary_elements/` e `widgets/` sono quasi vuoti (8–15 righe, solo class skeleton). Non collegato come entry point autonomo.

## 3. Evidenze

- `src/gui/entrypoint.py` — delega a `src.ui.modern.app.main()`
- `src/gui/ntc2018_selector.py` — `list_available_codes()` reale
- `src/gui/secondary_elements/editor.py` — ~15 righe, classe skeleton
- `src/gui/secondary_elements/results_view.py` — ~10 righe, classe skeleton
- `src/gui/widgets/norm_selector.py` — ~7 righe, skeleton
- Test: `tests/legacy_qt/test_norm_selector.py`, `tests/legacy_qt/test_secondary_editor.py`

## 4. Input/parametri

- `list_available_codes() -> list[str]` — restituisce codici normativi disponibili

## 5. Output

- `list[str]` — lista codici (`["RD2229", "NTC2018", ...]`)

## 6. Dipendenze

- `src/ui/modern/app` — `main()` (delegato)
- `src/codes/ntc2018/secondary_elements/` — modelli elementi secondari

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/gui/entrypoint.py` — docstring |
| NTC2018 | `src/gui/ntc2018_selector.py` — codice listato |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Sub-package `secondary_elements/` quasi completamente non implementato
- `entrypoint.py` è un thin proxy — nessuna logica GUI diretta
- Widget in `widgets/` sono skeleton

## 9. Next steps

- [ ] Implementare `secondary_elements/editor.py` come finestra Qt funzionale
- [ ] Collegare `gui/entrypoint.py` a un entry point autonomo se necessario
- [ ] Aggiungere test headless per `secondary_elements/` widgets
