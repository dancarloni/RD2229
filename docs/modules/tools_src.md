# Modulo: `tools` (src/tools/)

## 1. Scopo e ambito

Strumenti CLI di supporto: `verify_cli.py` (verifica strutturale da CLI), `export_results.py` (export risultati). Layer tra CLI principale e repository/engine.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `verify_cli.py` è marcato STUB S2. `parse_args()` parziale (argparse definito), `load_user_config()` TODO, `run_verifications()` TODO, `export_report()` TODO. `export_results.py` ha logica parziale.

## 3. Evidenze

- `src/tools/verify_cli.py` — "STUB S2"; `run_verifications()` TODO, `export_report()` TODO
- `src/tools/export_results.py` — logica parziale
- `src/tools/__init__.py` — 6 righe
- Nessun test

## 4. Input/parametri

- `verify_cli.py`: argparse con `--project`, `--norm`, `--output`

## 5. Output

TBD — dovrebbe produrre report su file.

## 6. Dipendenze

- `src/materials/material_repo` — `MaterialRepository` (STUB)
- `src/elements/element_repo` — `ElementRepository` (STUB)
- `src/report/renderer_html`, `renderer_md` (STUB)
- `src/codes/code_registry` — `bootstrap_codes()` (STUB)

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Completamente non funzionale (tutte le funzioni chiave TODO)
- Dipende da molti altri moduli STUB
- Non testato

## 9. Next steps

- [ ] Implementare `verify_cli.py` solo dopo che le dipendenze (MaterialRepo, ElementRepo) sono funzionali
- [ ] Aggiungere test di integrazione con dati fixture minimali
- [ ] Considerare se consolidare con `src/cli/entrypoint.py` (sovrapposizione funzionale)
