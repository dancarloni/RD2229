# Modulo: `codes`

## 1. Scopo e ambito

Infrastruttura per il routing delle normative (CodeModule), parametri normativi (YAML/JSON), e implementazioni specifiche NTC2018 incluso spectrum paste service e secondary elements.

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: `code_registry.py` è STUB S2 (tutti i metodi TODO). `spectrum_paste_service.py` (161 righe) ha logica reale di parsing NTC2018 hazard. `secondary_elements/` sub-package ha modelli e check reali. `params/` e `clauses/` contengono solo JSON/YAML vuoti o template.

## 3. Evidenze

- `src/codes/code_registry.py` — "STUB S2"; `bootstrap_codes()`, `get_code()` TODO
- `src/codes/ntc2018/spectrum_paste_service.py:1` — "Service for parsing and managing NTC2018 hazard profiles"
- `src/codes/ntc2018/secondary_elements/models.py` — dataclass reali `SecondaryElementSpec`
- `src/codes/ntc2018/secondary_elements/checks.py` — check reali (56 righe)
- Test: `tests/codes/test_vrdc_no_stirrups.py`, `tests/test_ntc2018_hazard_paste_parser.py`, `tests/codes/test_secondary_elements_*.py` (+4)
- `src/codes/params/NTC2018.json`, `src/codes/clauses/NTC2018.yml` — file presenti

## 4. Input/parametri

- `build_profile(text: str) -> HazardProfile` — parsing testo incollato da EdiLus-MS
- `SecondaryElementSpec` — dataclass con campi geometria/materiale
- `NTC2018CodeModule` — interfaccia CodeModule

## 5. Output

- `HazardProfile` — profilo di pericolosità NTC2018
- `CheckResult` — risultato verifica elementi secondari

## 6. Dipendenze

- `src/codes/ntc2018/spectrum_paste_service.py` — standalone
- `src/codes/code_registry.py` — importato da `src/tools/verify_cli.py`
- `src/codes/ntc2018/secondary_elements/` — importato da tests

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| NTC2018 | `src/codes/ntc2018/code_module.py:2`, `spectrum_paste_service.py:1` |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- `code_registry.py`: routing codici normativa non funzionale
- `params/` e `clauses/`: vuoti o quasi vuoti
- `NTC2018CodeModule`: skeleton senza logica

## 9. Next steps

- [ ] Implementare `bootstrap_codes()` e `get_code()` in `code_registry.py`
- [ ] Popolare `params/NTC2018.json` e `clauses/NTC2018.yml` con dati reali
- [ ] Collegare `NTC2018CodeModule` al pipeline
