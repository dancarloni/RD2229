# Documentazione Modulo: `codes`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `codes` |
| **Path** | `src/codes` |
| **Tipo** | package |
| **File .py rilevati** | 15 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

Infrastruttura per il routing delle normative (CodeModule), parametri normativi (YAML/JSON), e implementazioni specifiche NTC2018 incluso spectrum paste service e secondary elements.

---

## 3. Evidenze

- `src/codes/code_registry.py` — "STUB S2"; `bootstrap_codes()`, `get_code()` TODO
- `src/codes/ntc2018/spectrum_paste_service.py:1` — "Service for parsing and managing NTC2018 hazard profiles"
- `src/codes/ntc2018/secondary_elements/models.py` — dataclass reali `SecondaryElementSpec`
- `src/codes/ntc2018/secondary_elements/checks.py` — check reali (56 righe)
- Test: `tests/codes/test_vrdc_no_stirrups.py`, `tests/test_ntc2018_hazard_paste_parser.py`, `tests/codes/test_secondary_elements_*.py` (+4)
- `src/codes/params/NTC2018.json`, `src/codes/clauses/NTC2018.yml` — file presenti

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | `build_profile(text: str) -> HazardProfile` | parsing testo incollato da EdiLus-MS |
| Input | `SecondaryElementSpec` | dataclass con campi geometria/materiale |
| Input | `NTC2018CodeModule` | interfaccia CodeModule |
| Output | `HazardProfile` | profilo di pericolosità NTC2018 |
| Output | `CheckResult` | risultato verifica elementi secondari |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/codes/test_vrdc_no_stirrups.py` | TBD | — |
| `tests/test_ntc2018_hazard_paste_parser.py` | TBD | — |
| `tests/codes/test_secondary_elements_*.py` | TBD | — |

---

## 6. Fonti normative

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| NTC2018 | `src/codes/ntc2018/code_module.py:2`, `spectrum_paste_service.py:1` | — |

Clausole: TODO

---

## 7. Dipendenze interne

- `src/codes/ntc2018/spectrum_paste_service.py` — standalone
- `src/codes/code_registry.py` — importato da `src/tools/verify_cli.py`
- `src/codes/ntc2018/secondary_elements/` — importato da tests

---

## 8. Gap / TODO / Limitazioni

- `code_registry.py`: routing codici normativa non funzionale
- `params/` e `clauses/`: vuoti o quasi vuoti
- `NTC2018CodeModule`: skeleton senza logica

---

## 9. Next steps

- [ ] Implementare `bootstrap_codes()` e `get_code()` in `code_registry.py`
- [ ] Popolare `params/NTC2018.json` e `clauses/NTC2018.yml` con dati reali
- [ ] Collegare `NTC2018CodeModule` al pipeline
- [ ] Compilare sezioni TBD
- [ ] Tracciare fonti normative di riferimento
