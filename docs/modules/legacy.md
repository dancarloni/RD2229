# Modulo: `legacy`

## 1. Scopo e ambito

Codice legacy preservato: applicazione Tkinter completa, repository materiali storici, verifica TA storica, sezioni, utilities. Designato come "DO NOT MODIFY" dall'architettura.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: 28+ file Python reali con logica estesa. `historical_materials.py` (576 righe) e `material_sources.py` (657 righe) hanno dati e logica materiali reali. `ui/` sub-package è un'applicazione Tkinter funzionale. Legacy è designata DO NOT MODIFY.

## 3. Evidenze

- `src/legacy/historical_materials.py` — 576 righe; dati materiali storici
- `src/legacy/material_sources.py` — 657 righe; sorgenti materiali
- `src/legacy/ui/` — GUI Tkinter completa (main_window, module_selector, section_manager, ecc.)
- `src/legacy/__main__.py` — entry point legacy
- `src/legacy/ui/__main__.py` — entry point UI legacy
- Nessun test nella nuova suite `tests/` importa da `src.legacy`

## 4. Input/parametri

TBD — GUI Tkinter; input via form utente; file `.jsonp` per persistenza.

## 5. Output

TBD — report su console/file; GUI Tkinter.

## 6. Dipendenze

- Tkinter (stdlib)
- Matplotlib (opzionale, per grafici sezione)
- File dati JSON locali in `src/legacy/`

## 7. Fonti normative collegate

TBD — codice legacy non scansionato per riferimenti normativi in questa pass. Presumibilmente contiene riferimenti a RD2229, DM92, DM96.

## 8. Gap/TODO/Limitazioni

- DO NOT MODIFY per policy architetturale
- Non testato via nuova suite
- Dipendenze Tkinter impediscono test in CI headless

## 9. Next steps

- [ ] TBD — nessun next step pianificato per il legacy (DO NOT MODIFY)
- [ ] Documentare i riferimenti normativi presenti nel legacy (scan futuro)
