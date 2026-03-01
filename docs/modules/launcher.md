# Modulo: `launcher`

## 1. Scopo e ambito

Bootstrap dell'applicazione: configurazione logging e avvio dell'app tramite import dinamico di `apps.sections.app`.

## 2. Stato reale

**INCOMPLETO**

Motivazione oggettiva: Singolo file `bootstrap.py` (~50 righe) con logica reale ma dipendenza da `apps.sections.app` che si trova fuori da `src/`. Nessun `__init__.py` rilevato (non è un package Python corretto). Nessun test.

## 3. Evidenze

- `src/launcher/bootstrap.py` — `configure_logging()`, `run_app()` reali
- Dipendenza da `apps.sections.app` (fuori `src/`)
- Nessun `__init__.py` nella cartella
- Nessun test

## 4. Input/parametri

TBD — `run_app()` senza parametri espliciti.

## 5. Output

TBD — avvia l'applicazione Tkinter.

## 6. Dipendenze

- `apps.sections.app` (fuori `src/`, percorso non standard)
- `src.rd2229.logging_bridge` — `setup_logging()`

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/launcher/bootstrap.py` — menzione nel logging |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Nessun `__init__.py` — non importabile come package
- Dipendenza su percorso `apps/` fuori da `src/`
- Nessun test
- Non integrato nel pipeline principale

## 9. Next steps

- [ ] Aggiungere `__init__.py` per renderlo importabile
- [ ] Valutare se spostare `apps/sections/app.py` dentro `src/`
- [ ] Aggiungere test smoke per `configure_logging()`
