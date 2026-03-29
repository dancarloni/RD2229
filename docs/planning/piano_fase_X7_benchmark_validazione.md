# Fase X7 — Benchmark e Validazione

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Benchmark numerici, validazione, regressione |

---

## Scopo del modulo

Garantire validazione quantitativa del modulo solai con tolleranza target <=2% rispetto ai riferimenti noti.

---

## Dipendenze reali del repo

- tests/
- src/core/combinations/ntc2018_combinations.py
- src/core/registro_log.py

---

## Fonti normative e riferimenti di confronto

- NTC2018 §2.5, §4.1.2, §7.2.6
- EN 1992-1-1 §6, §7
- Letteratura storica per benchmark RD2229

---

## Matrice benchmark (storico + SI)

| ID | Caso | Input storici | Input SI | Controllo |
| --- | --- | --- | --- | --- |
| BM-X01 | laterocemento appoggiato | G=300 Q=200 kgf/m2 | G~2.94 Q~1.96 kN/m2 | M,V,f |
| BM-X02 | predalles multi-campata | G=250 Q=200 kgf/m2 | G~2.45 Q~1.96 kN/m2 | Mneg/Mpos,f |
| BM-X03 | legno storico | b/h/i/L in cm | b/h/i/L in m | confronto doppio storico/NTC |
| BM-X04 | bidirezionale con apertura | L=600 cm, ap 120x120 cm | L=6 m, ap 1.2x1.2 m | EI_eff + warning |
| BM-X05 | cerchiatura | trave eq 30x50 cm | 0.30x0.50 m | redistribuzione |

---

## Formula usata / fallback / motivo selezione

| Caso | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| BM-X01/02 | SLU/SLE NTC + formule lineari | FEM | confrontabilità alta |
| BM-X03 | storico + NTC | solo storico | doppia validazione |
| BM-X04 | modello cautelativo + trigger FEM | FEM locale completo | sicurezza |
| BM-X05 | trave equivalente | modello continuo fine | semplicità V1 |

---

## Warning code del modulo

- X7-BENCH-001: errore >2%
- X7-BENCH-002: benchmark non riproducibile
- X7-BENCH-003: mismatch unità storico/SI

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X7-T01 | BM-X01 | errore <=2% |
| X7-T02 | BM-X03 | doppio esito storico/NTC |
| X7-T03 | unità incoerenti | X7-BENCH-003 |
| X7-T04 | errore >2% | X7-BENCH-001 |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X7.1 — Definizione reference values
- [ ] X7.2 — Test automatici benchmark
- [ ] X7.3 — Report scostamenti
- [ ] X7.4 — Regressione continua

---

## Domande, risposte e decisioni

- Decisione: i benchmark saranno a doppia colonna (storico + SI) e la matrice benchmark deve riportare colonna `Validato numericamente` per ogni caso; tolleranza target <= 2%. 

---

## Teoria e fondamenti (riferimenti sintetici)

- Benchmark double-column: storico vs SI; tolleranza target <=2%.

---

## Diagramma dipendenze subfasi

```text
X7.1 → X7.2 → X7.3 → X7.4
```

---

## Rischi normativi residui

- Riferimenti letteratura non uniformi tra scuole storiche.
- Confronto bidirezionale sensibile al modello adottato.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X7 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) BM-X01 (laterocemento): G = 300 kgf/m², Q = 200 kgf/m² → in SI G≈2.94 kN/m², Q≈1.96 kN/m²; usare formulazione SLU per confronto M,V; esempio atteso errore <=2% rispetto ai riferimenti storici.

2) BM-X04 (bidirezionale con apertura): L = 6.00 m, apertura 1.2×1.2 m → confronto modello cautelativo vs FEM; esempio numerico: momento di prova M_ref = 85 kN·m, calcolo semplificato M_calc = 86.5 kN·m → scarto 1.8% → pass (rif. tolleranza <=2%).

3) BM-X03 (legno storico): convertire b/h/L da cm→m e confrontare coppia storico/SI; esempio: b=30 cm,h=20 cm,L=400 cm → b=0.30 m,h=0.20 m,L=4.00 m; controllare che i risultati su M differiscano <2% dopo conversione e adattamento materiale.

Riferimenti: NTC2018, EN1992, letteratura RD2229 per casi storici.
