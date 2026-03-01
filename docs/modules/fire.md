# Modulo: `fire`

## 1. Scopo e ambito

Verifiche di resistenza al fuoco per strutture in c.a.: curva incendio standard ISO 834, eligibility check (copertura minima, dimensioni sezione), verifica asse-distanza armature per classi R (EN 1992-1-2, metodo tabulare).

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: `curves.py` e `eligibility.py` hanno logica reale completa. `rc_fire_check.py` ha il framework di verifica reale ma la tabella asse-distanza è un placeholder (TODO: caricare da JSON). Integrato nel pipeline. Test presenti.

## 3. Evidenze

- `src/fire/curves.py` — `iso834_temperature(t)`, `iso834_profile(times)` reali (formula ISO 834)
- `src/fire/eligibility.py` — `evaluate_fire_eligibility(element, section)` reale (100 righe)
- `src/fire/rc_fire_check.py:7` — riferimento a NTC 2018 §3.6.1 e EN 1992-1-2
- `src/fire/rc_fire_check.py` — tabella asse-distanza: `TODO: caricare da data/fire/axis_distance_table.json`
- Test: `tests/test_fire_selection_eligibility.py`
- Chiamato da: `src/core/pipeline.py` step incendio

## 4. Input/parametri

- `iso834_temperature(t: float) -> float` — t in minuti, restituisce °C
- `evaluate_fire_eligibility(element, project) -> FireEligibility`
- `run_rc_fire_check(element, section, material, resistance_class: str) -> FireCheckResult`

## 5. Output

- `float` — temperatura ISO 834
- `FireEligibility` — `eligible: bool`, `reason: str`
- `FireCheckResult` — `passed: bool`, `axis_distance_required`, `axis_distance_provided`

## 6. Dipendenze

- `src/core/pipeline.py` — chiama `evaluate_fire_eligibility()` e `run_rc_fire_check()`
- `src/project/schema.py` — `FireInputs` dataclass

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| EN 1992-1-2 | `src/fire/rc_fire_check.py:7` — "EN 1992-1-2:2004" |
| NTC2018 | `src/fire/rc_fire_check.py:7` — "NTC 2018, §3.6.1" |
| ISO 834 | (indiretto via `curves.py:8` — "Eurocodice EN 1991-1-2"; formula ISO 834 implementata) |

Clausole: §3.6.1 NTC2018 e §5.6/Table 5.4-5.5 EN 1992-1-2 appaiono come commenti in `rc_fire_check.py`.

## 8. Gap/TODO/Limitazioni

- Tabella asse-distanza: placeholder, non caricata da file
- Solo curva incendio standard (ISO 834); curve parametriche non implementate
- Nessun test per `run_rc_fire_check()` con dati reali di sezione

## 9. Next steps

- [ ] Creare `data/fire/axis_distance_table.json` e caricarla in `rc_fire_check.py`
- [ ] Aggiungere test golden per `run_rc_fire_check()` con classi R30/R60/R90/R120
- [ ] Implementare curve incendio parametriche (EN 1991-1-2 Annex A)
