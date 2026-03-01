<<<<<<< HEAD
# Modulo: `plugins`

## 1. Scopo e ambito

Sistema plugin per estendere funzionalità RD2229: `PluginRegistry`, `PluginSpec`, `ActionSpec`, `ParamSpec` dataclass; loader da cartella e da entry points `importlib.metadata`; plugin concreti (`export`, `info`, `run`).

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `__init__.py` (81 righe) ha `PluginRegistry` reale con metodi implementati. `loader.py` (147 righe) ha discovery reale (folder scan + `importlib.metadata`). Tre plugin concreti implementati. Test presenti.

## 3. Evidenze

- `src/plugins/__init__.py` — `PluginRegistry`, `PluginSpec`, `ActionSpec`, `ParamSpec` reali
- `src/plugins/loader.py` — `load_plugins_from_folder()`, `load_plugins_from_entry_points()`
- `src/plugins/export_plugin.py`, `info_plugin.py`, `run_plugin.py` — plugin concreti
- `src/config/app.yml:33-35` — entry_points group per plugin
- Test: `tests/test_plugin_system.py` — importa e verifica tutto il sistema

## 4. Input/parametri

- `load_plugins_from_folder(path: str) -> list[PluginSpec]`
- `load_plugins_from_entry_points(group: str) -> list[PluginSpec]`
- `PluginRegistry.register(spec: PluginSpec)`

## 5. Output

- `list[PluginSpec]` — specifiche plugin caricate
- `PluginSpec`: `name`, `version`, `actions: list[ActionSpec]`

## 6. Dipendenze

- `importlib.metadata` (stdlib)
- `src/rd2229/plugin_registry` — usa `PluginRegistry` da `src/plugins`
- `src/config/app.yml` — gruppo entry_points

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/plugins/__init__.py` — docstring modulo, `base.py` |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Plugin concreti (`export`, `run`) dipendono da pipeline che è PARZIALE
- Nessun test di integrazione E2E plugin → pipeline → report

## 9. Next steps

- [ ] Testare `run_plugin.py` con pipeline completa
- [ ] Documentare il formato atteso di un plugin esterno (contribuente terzo)
- [ ] Aggiungere test per `load_plugins_from_entry_points()` con mock entry_points
=======
# Documentazione Modulo: `plugins`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `plugins` |
| **Path** | `src/plugins` |
| **Tipo** | package |
| **File .py rilevati** | 6 |
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
| `tests/test_logging_and_plugins.py` | TBD | — |

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
