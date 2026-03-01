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
