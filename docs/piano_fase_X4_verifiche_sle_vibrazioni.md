# Fase X4 — Verifiche SLE e Vibrazioni

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Freccia, tensioni SLE, frequenze e comfort |

---

## Scopo del modulo

Gestire verifiche in esercizio con approccio normativo rigoroso:
- deformabilità
- tensioni SLE
- vibrazioni e comfort

---

## Dipendenze reali del repo

- src/codes/params/NTC2018.json
- src/core/registro_log.py
- src/core/combinations/ntc2018_combinations.py

---

## Fonti normative (parafrasi rigorosa)

- NTC2018 §7.2.6: limiti deformabilità per elementi orizzontali.
- NTC2018 §4.1.2.2.4: controlli tensionali in esercizio.
- NTC2018 §C7.10.5: criteri comfort vibrazionale.
- EN 1992-1-1 §7.3 e §7.4: fessurazione e deformazioni.
- EN ISO 10137: criteri prestazionali vibrazioni.

---

## Schede normative (trascrizione operativa)

### Freccia

- q_l = q_s*i/10^4
- f_max = 5*q_l*L^4/(384*E*I)
- limiti: L/250, L/300, L/400 in base uso

Warning:
- X4-DEF-001 se f_max > f_lim
- X4-DEF-002 se E_eff ridotto oltre soglia senza motivazione

### Tensioni SLE

- combinazioni rara/frequente/quasi-permanente da X2
- verifica tensionale cls con limiti da NTC (rara e quasi-permanente)

Warning:
- X4-SLE-001 superamento tensione rara
- X4-SLE-002 superamento tensione quasi-permanente

### Vibrazioni

- formulazione primaria SI: f1 = pi/(2L^2)*sqrt(EI/m)
- m = rho*A
- controllo f1 >= 4 Hz e a_RMS <= 0.5 m/s2

Warning:
- X4-VIB-001 f1 < 4 Hz
- X4-VIB-002 a_RMS > 0.5 m/s2

---

## Formula usata / fallback / motivo selezione

| Verifica | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| Freccia | trave appoggiata + q_l | FEM lineare globale | modello trasparente per benchmark |
| Tensioni SLE | combinazioni NTC | check semplificato | coerenza con X2 |
| Vibrazioni | formula SI + mapping storico | stima semplificata empirica | robustezza dimensionale |

---

## Warning code del modulo

- X4-DEF-001, X4-DEF-002
- X4-SLE-001, X4-SLE-002
- X4-VIB-001, X4-VIB-002

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X4-T01 | q_s,i,L,E,I | f_max e check limite |
| X4-T02 | combinazioni SLE | sigma_rara/sigma_qp |
| X4-T03 | L,E,I,rho,A | f1 |
| X4-T04 | a_RMS elevata | X4-VIB-002 |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X4.1 — Deformabilità
- [ ] X4.2 — Tensioni SLE
- [ ] X4.3 — Vibrazioni
- [ ] X4.4 — Test e benchmark

---

## Domande, risposte e decisioni

- Domanda: (placeholder) — Risposta: (placeholder)

---

## Teoria e fondamenti (riferimenti sintetici)

- Freccia: formula beam-end con q_l e conversioni; limiti L/250 etc.
- Vibrazioni: f1 approssimativa + controllo a_RMS.

---

## Diagramma dipendenze subfasi

```text
X4.1 → X4.2 → X4.3 → X4.4
```

---

## Rischi normativi residui

- Criteri comfort dipendenti dalla destinazione d'uso non sempre nota.
- Possibile sottostima in casi bidirezionali complessi senza FEM.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X4 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) SLE frequente (NTC/EN): solaio semplicemente appoggiato, L = 4.50 m, q_s = 300 kgf/m², convertirsi in SI per calcolo di freccia; q_l = 300·50/10000 = 1.50 kgf/cm (se i=50 cm). Uso della formula di deflessione per trave semplicemente appoggiata:
 w_max = 5·q·L^4/(384·E·I) — valutare con E=30 GPa e I della sezione equivalente per confronto SLE (rif. EN/NTC su deformabilità).

2) Verifica vibrazioni (linee guida): massa superficiale m = 300 kgf/m² ≈ 2.94 kN/m²; prendere modello semplice per primo modo: T ≈ 2π·√(m·L^4/(EI·k_factor)) — usare confronto storico vs SI (rif. letteratura RD2229/NTC per soglie accettabilità).

3) SLE quasi-permanente: caso di lungo periodo con Gk=450 kgf/m², carichi variabili ridotti ψ2→ si usano ψ2 tipici da NTC/EN per valutazione permanenza delle deformazioni.

Riferimenti: NTC2018 (SLE e deformabilità), EN1992 e linee guida letteratura RD2229 per vibrazioni.
