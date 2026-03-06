# FASE O.3 — Azioni Sismiche Multinorma

**Data completamento**: 2026-03-06
**Stato**: COMPLETATO — 54 test, 0 falliti

---

## Obiettivo

Package `src/codes/seismic/` per calcolo taglio alla base + distribuzione triangolare
ai piani per 7 norme: RD2229, DM92, DM96, OPCM3274, EC8, NTC2008, NTC2018.

---

## Architettura

```text
src/codes/seismic/
├── __init__.py       — re-export PianoEdificio, calcola_azione_sismica
├── base.py           — PianoEdificio, distribuzione_triangolare, _base_contract
├── rd2229.py         — coefficienti storici regionali
├── dm92.py           — DM 3/6/1981 + agg.1992 (statico equivalente)
├── dm96.py           — DM 16/1/1996 (statico equivalente)
├── opcm3274.py       — OPCM 3274/2003, 4 zone, spettro elastico
├── ec8.py            — EN 1998-1 Tipo1/Tipo2
├── ntc2008.py        — NTC 2008 (riusa spectrum.py NTC2018)
└── dispatcher.py     — routing multinorma su norma_attiva
```

---

## Output comune (contratto base)

```python
{
    "esito": "OK",
    "norm_references": ["..."],
    "decision_log": [...],
    "trace": {"run_id": uuid},
    "F_base_kN": float,
    "C_effettivo": float,          # V_b / W_tot
    "metodo": "STATICO_EQUIVALENTE" | "SPETTRALE",
    "distribuzione": [
        {"piano": int, "h_m": float, "W_kN": float, "F_kN": float},
        ...
    ],
    # campi opzionali solo SPETTRALE:
    "ag_g": float,
    "Se_T1_ms2": float,
    "T_1_s": float,
}
```

---

## Coefficienti per norma

### RD2229 (storici)

```python
RD2229_COEFF = {"non_sismico": 0.00, "bassa": 0.05, "media": 0.07, "alta": 0.10}
```

### DM92 / DM96

```python
COEFF_C = {1: 0.10, 2: 0.07, 3: 0.04}  # zone 1-3
```

### OPCM3274

```python
ZONE_AG = {1: 0.35, 2: 0.25, 3: 0.15, 4: 0.05}  # g
TC_STAR_OPCM = {1: 0.42, 2: 0.37, 3: 0.30, 4: 0.25}  # s
```

### EC8 (Tipo1)

```python
EC8_TYPE1 = {
    "A": (1.00, 0.15, 0.40, 2.0),  # S, TB, TC, TD
    "B": (1.20, 0.15, 0.50, 2.0),
    "C": (1.15, 0.20, 0.60, 2.0),
    "D": (1.35, 0.20, 0.80, 2.0),
    "E": (1.40, 0.15, 0.50, 2.0),
}
```

---

## Valori di riferimento verificati

| Caso | F_base | Note |
|------|--------|------|
| DM96 zona 2, W=1500 kN | 105 kN | C=0.07 * 1500 |
| DM92 zona 2, W=1500 kN | 105 kN | identico a DM96 |
| EC8 Tipo1 cat B, ag=0.25g, T_1=TC=0.5s, q=1.5 | 750 kN | Se=7.3575 m/s², Sd=4.905 m/s² |
| NTC2008 = NTC2018 stessi params | identici | verificato in test |

---

## Dispatcher

```python
from src.codes.seismic import calcola_azione_sismica

res = calcola_azione_sismica("DM96", {
    "piani": [{"piano": 1, "h_m": 3.0, "W_kN": 500.0}, ...],
    "zona_sismica": 2,
})
```

Norme valide (case-insensitive): RD2229, DM92, DM96, OPCM3274, EC8, NTC2008, NTC2018.

---

## Test

File: `tests/test_azioni_sismiche_multinorma.py` — 54 test

| Classe | N | Descrizione |
|--------|---|-------------|
| TestDistribuzionePiani | 5 | distribuzione_triangolare, somma, errori |
| TestAzioneRD2229 | 8 | zone, avviso, contratto, zona invalida |
| TestAzioneDM92 | 8 | zone 1/2/3, importanza, epsilon, distribuzione |
| TestAzioneDM96 | 6 | zone, norm_ref diverso da DM92, metodo |
| TestAzioneOPCM3274 | 6 | zone, ag, zona invalida, Se_T1 |
| TestAzioneEC8 | 8 | Tipo1/Tipo2, cat A-E, q, errori, distribuzione |
| TestAzioneNTC2008 | 5 | F_base>0, metodo, norm_ref, coerenza NTC2018 |
| TestDispatcher | 8 | routing, norma invalida, case-insensitive, contratto |

---

## Dipendenze interne

- `opcm3274.py` e `ntc2008.py` importano lazy da `src.codes.ntc2018.spectrum`
- `dispatcher.py` NTC2018 branch importa lazy da `src.codes.ntc2018.spectrum`
- Nessun import circolare a livello modulo
