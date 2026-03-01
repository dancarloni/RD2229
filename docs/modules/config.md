<<<<<<< HEAD
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
=======
# Documentazione Modulo: `config`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `config` |
| **Path** | `src/config` |
| **Tipo** | package |
| **File .py rilevati** | 1 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

> Descrivere in 2-3 righe il *perché* esiste questo modulo e quale problema risolve.

TBD

---

## 3. File / Classi / Funzioni principali

> Elencare i simboli pubblici rilevanti. Non inventare: se non si conosce la firma esatta, annotare TBD.

| File | Classe/Funzione | Descrizione |
|------|-----------------|-------------|
| TBD | TBD | TBD |

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | TBD | TBD |
| Output | TBD | TBD |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/rd2229_39/test_configurable_factor.py` | TBD | — |

---

## 6. Fonti normative

> Solo riferimenti a ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`. NESSUN testo copiato.

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| TBD | TBD | — |

---

## 7. Dipendenze interne

> Moduli `src/` da cui questo modulo dipende (import diretti).

- TBD

---

## 8. Note e TODO

- [ ] Compilare sezioni TBD
- [ ] Verificare test correlati
- [ ] Tracciare fonti normative di riferimento
>>>>>>> d5ef881 (feat: audit/docs infrastructure - audit_repo, RTM, governance, normative catalog, module docs)
