# Documentazione Modulo: `wind`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `wind` |
| **Path** | `src/wind` |
| **Tipo** | package |
| **File .py rilevati** | 7 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo e ambito

Calcolo delle azioni del vento per tre framework normativi: NTC2018 §3.3, EN 1991-1-4:2005 (Eurocodice 1), CNR-DT 207 R1/2018. Orchestrato da `WindActionService`. Integrato nel pipeline principale.

---

## 3. Stato reale

**PARZIALE**

Motivazione oggettiva: Logica reale per tutti e tre i framework. Però parametri geografici zona (vb,0 per NTC2018) sono placeholder (TODO: caricare da JSON). Il fattore di risposta dinamica Cd (CNR-DT 207) non è implementato. Test presenti.

---

## 4. Evidenze

- `src/wind/ntc2018.py:1-3` — "NTC2018 wind – calcolo azioni del vento secondo NTC 2018 §3.3"
- `src/wind/ntc2018.py:40` — `_ZONE_PARAMS_NTC2018` placeholder (TODO: da tabella)
- `src/wind/ec1991_1_4.py:3` — "Riferimento: EN 1991-1-4:2005"
- `src/wind/cnr_dt207.py:1-3` — "CNR-DT 207 R1/2018"; Cd: TODO
- `src/wind/service.py` — `WindActionService.compute()` reale
- Test: `tests/test_wind_smoke.py`, `tests/test_wind_integration_pipeline.py`
- Chiamato da: `src/core/pipeline.py` step vento

---

## 5. Input/parametri

- `WindConfig(method: str, site: WindSite, building: BuildingGeom, apply_cnr_dt207: bool)`
- `WindSite(zone: str, altitude: float, terrain_category: str)`
- `BuildingGeom(height: float, width: float, depth: float)`

---

## 6. Output

- `WindActionResults` — `pressure_q: float`, `velocity_vb: float`, `method: str`, `warnings: list`

---

## 7. Dipendenze

- `src/core/pipeline.py` — chiama `WindActionService.compute()`
- `src/project/schema.py` — `WindInputs`

---

## 8. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| NTC2018 | `src/wind/ntc2018.py:1-3` — "NTC 2018 §3.3.2, §3.3.4"; `src/wind/models.py:3` |
| EN1991_1_4 | `src/wind/ec1991_1_4.py:3` — "EN 1991-1-4:2005" |
| CNR_DT207 | `src/wind/cnr_dt207.py:1-3` — "CNR-DT 207 R1/2018"; `src/wind/service.py:26` |

Clausole: §3.3.2 e §3.3.4 compaiono come stringhe in `ntc2018.py`.

---

## 9. Gap/TODO/Limitazioni

- Parametri zona NTC2018 (vb,0 per zone 1–9): placeholder, non da tabella reale
- Cd (CNR-DT 207): non implementato — risposta dinamica non disponibile
- EN 1991-1-4: valori NA (National Annex) non configurati

---

## 10. Next steps

- [ ] Creare `data/wind/ntc2018_zones.json` e caricare in `ntc2018.py`
- [ ] Implementare Cd (fattore risposta dinamica) in `cnr_dt207.py`
- [ ] Aggiungere test golden con zona e altitudine reali (es. zona 4, h=50m)
