# Fase X2 — Carichi e Combinazioni

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Carichi, combinazioni, LC/FC applicativo |

---

## Scopo del modulo

Definire il percorso deterministico:
input carichi -> normalizzazione unità -> combinazioni SLU/SLE -> output azioni di progetto.

---

## Dipendenze reali del repo

- src/core/combinations/ntc2018_combinations.py
- src/codes/params/NTC2018.json
- src/codes/clauses/NTC2018.yml
- src/core_calculus/lc_fc_adjustments.py
- src/core/registro_log.py

---

## Fonti normative (parafrasi rigorosa)

- NTC2018 §2.5 + Tab.2.5.I + Tab.2.6.I: combinazioni e coefficienti psi/gamma.
- NTC2018 Cap.8 §C8.5.4: riduzione resistenze tramite FC.
- EN 1990/EN 1991: base europea per combinazioni e azioni.

---

## Trascrizione operativa combinazioni

### SLU fondamentale

Ed = gamma_G1*G1 + gamma_G2*G2 + gamma_Q1*Q1 + sum(gamma_Qi*psi0_i*Qi)

### SLE rara

Ed = Gk + Qk1 + sum(psi0_i*Qki)

### SLE frequente

Ed = Gk + psi1_1*Qk1 + sum(psi2_i*Qki)

### SLE quasi-permanente

Ed = Gk + sum(psi2_i*Qki)

---

## Conversioni obbligatorie

- q_s[kgf/m2] -> q_l[kgf/cm] = q_s*i/10^4
- kN -> kgf: *101.97
- MPa -> kgf/cm2: *10.1972

---

## Formula usata / fallback / motivo selezione

| Voce | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| Combinazioni NTC | wrapper ntc2018_combinations | calcolo manuale tabellare | evitare duplicazione logica |
| FC esistenti | lc_fc_adjustments | FC manuale | allineamento repository |
| Area influenza | input manuale | modulo Fase Y futuro | dipendenza non disponibile |

---

## Warning code del modulo

- X2-COMB-001: categoria d'uso assente
- X2-COMB-002: psi non disponibile per categoria
- X2-LC-001: FC applicato da LC
- X2-AREA-001: area di influenza manuale

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X2-T01 | G1,G2,Q,cat A | 1 combinazione SLU + 3 SLE |
| X2-T02 | LC2 | FC=1.20 applicato |
| X2-T03 | categoria sconosciuta | X2-COMB-002 |
| X2-T04 | area manuale | X2-AREA-001 |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X2.1 — Normalizzazione carichi
- [ ] X2.2 — Combinazioni NTC (wrapper)
- [ ] X2.3 — Applicazione LC/FC
- [ ] X2.4 — Test + benchmark base

---

## Domande, risposte e decisioni

- Decisione 2026-03-10 (confermata 2026-03-15): la logica delle aree di influenza è centralizzata in `src/aree_influenza.py`; fino alla consegna del modulo Fase Y l'area va fornita manualmente e si usa il warning `X2-AREA-001`.

---

## Teoria e fondamenti (riferimenti sintetici)

- Combinazioni SLU/SLE secondo NTC2018; applicare conversioni unità con wrapper centralizzato.

---

## Diagramma dipendenze subfasi

```text
X2.1 → X2.2 → X2.3 → X2.4
```

---

## Rischi normativi residui

- Categorie d'uso non mappate nel catalogo locale.
- Incoerenze tra dati manuali e classificazione azioni permanenti.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X2 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) SLU (semplice combinazione, EN/NTC): G1=300 kgf/m², G2=150 kgf/m², Q1=200 kgf/m²; γ_G=1.35, γ_Q=1.5 →
 Ed = γ_G*(G1+G2) + γ_Q*Q1 = 1.35*(300+150) + 1.5*200 = 1.35*450 + 300 = 907.5 kgf/m² (valori tipici NTC/EN).

2) SLE rara (NTC): Gk = 450 kgf/m², Qk1 = 200 kgf/m² → Ed = Gk + Qk1 = 650 kgf/m² (schema tabellare SLE rara).

3) Conversione superficie→linea: q_s = 300 kgf/m², i = 60 cm → q_l = 300*60/10000 = 1.80 kgf/cm.

Riferimenti: NTC2018 §2.5, EN 1990/EN1991 (psi/γ indicative per combinazioni).
