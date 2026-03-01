# Modulo: `config`

## 1. Scopo e ambito

TBD — nessuna docstring trovata. Contenitore di file di configurazione YAML per l'applicazione (`app.yml`, `features.yml`, `numerics.yml`, `units.yml`).

## 2. Stato reale

**STUB**

Motivazione oggettiva: `src/config/__init__.py` è vuoto (1 linea). Nessuna logica Python nel modulo. Solo 4 file YAML di configurazione.

## 3. Evidenze

- `src/config/__init__.py` — 7 righe, solo import placeholder
- `src/config/app.yml` — configurazione applicazione (plugins, logging, ecc.)
- `src/config/features.yml` — feature flags
- `src/config/numerics.yml` — parametri numerici
- `src/config/units.yml` — definizioni unità di misura
- Nessun test

## 4. Input/parametri

TBD — file YAML consumati da altri moduli tramite caricamento file diretto.

## 5. Output

TBD — dizionari Python letti da consumer.

## 6. Dipendenze

- `src/config/app.yml` referenziato da `src/plugins/loader.py` (entry_points group)

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Nessun loader Python nel modulo stesso
- Nessun test per la validità dei YAML
- `__init__.py` non espone funzioni di caricamento

## 9. Next steps

- [ ] Aggiungere `load_config()` utility in `__init__.py`
- [ ] Aggiungere test di validazione schema YAML
- [ ] Documentare ogni chiave in `app.yml` con tipo e default
