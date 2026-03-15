# Fase X5 — Aperture e Cerchiature

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | COMPLETATO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | 31 implementati/validati (17 check + 11 benchmark + 3 e2e) |
| Ambito | Aperture, riduzione rigidezza, trigger FEM locale, cerchiature |

---

## Scopo del modulo

Definire regole tecniche per aperture e cerchiature distinguendo chiaramente:
- prescrizioni normative (necessità di analisi locale)
- modello interno cautelativo (alpha_ap)
- attivazione FEM locale

---

## Dipendenze reali del repo

- src/core/registro_log.py
- src/core/combinations/ntc2018_combinations.py
- src/aree_influenza.py (non disponibile: fallback manuale)

---

## Fonti normative (parafrasi rigorosa)

- NTC2018 §7.2.6.2: modifiche locali, aperture e necessità di valutazione della rigidezza efficace.
- EN 1992-1-1 §7.3: impatto della rigidezza sulla risposta in esercizio.
- Letteratura tecnica: criteri cautelativi in assenza di modellazione locale dettagliata.

---

## Schede operative

### Classificazione aperture

- piccola: area_ap/area_pannello < 10%
- media: 10%-25%
- grande: >25%
- estrema: >50%

### Modello cautelativo interno

- EI_eff = EI*(1-alpha_ap)
- alpha_ap: 0.05 / 0.20 / 0.40 per classi crescente di apertura

Nota: questa non e formula normativa diretta, ma modello prudenziale di V1.

### Trigger FEM locale

- apertura >25%
- apertura in prossimita appoggi/zone di picco taglio
- presenza cerchiatura con redistribuzione significativa

---

## Formula usata / fallback / motivo selezione

| Voce | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| Riduzione EI | modello alpha_ap | FEM locale | copertura V1 in assenza modulo completo |
| Cerchiatura | trave equivalente | modellazione FEM dettagliata | robustezza e semplicità |
| Area influenza | input manuale | modulo Y futuro | dipendenza mancante |

---

## Warning code del modulo

| Warning code | Condizione | Check correlato |
| --- | --- | --- |
| X5-APE-001 | apertura >25% (attivare FEM) | x5_aperture_classificazione |
| X5-APE-002 | apertura >50% (verifica manuale obbligatoria) | x5_aperture_classificazione |
| X5-CER-001 | cerchiatura non coerente con schema statico | x5_cerchiatura_redistribuzione |
| X5-AREA-001 | area influenza manuale | x5_aperture_rigidezza |

---

## Quick reference testabile

| Test | Check | Input | Output atteso |
| --- | --- | --- | --- |
| X5-T01 | x5_aperture_classificazione | area ratio 8% | classe piccola + alpha_ap=0.05 |
| X5-T02 | x5_aperture_classificazione | area ratio 30% | warning X5-APE-001 |
| X5-T03 | x5_aperture_rigidezza | area ratio 60% | warning X5-APE-002 + riduzione EI_eff |
| X5-T04 | x5_cerchiatura_redistribuzione | cerchiatura attiva | redistribuzione + check warning |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [x] X5.1 — Classificazione aperture
- [x] X5.2 — Modello cautelativo EI
- [x] X5.3 — Trigger FEM locale
- [x] X5.4 — Cerchiature equivalenti
- [x] X5.5 — Test specifici

---

## Domande, risposte e decisioni

- Core X5 completo.
- Modello cautelativo: conservative primary.
- Cerchiature: livello esteso V1.
- Unità: storiche cm/kgf interne + output SI utile.
- Test: unit + benchmark + e2e.
- Naming allineato a prefisso `x5_`.

---

## Implementazione effettuata (file creati/modificati)

- src/methods/ntc2018/checks_x5.py
- src/codes/ntc2018/code_module.py
- src/codes/params/NTC2018.json
- tests/codes/test_x5_aperture_cerchiature_checks.py
- tests/codes/test_x5_aperture_cerchiature_benchmark.py
- tests/codes/test_x5_aperture_cerchiature_e2e.py

---

## Risultati test e regressione

- Checks X5: **17/17 PASS**.
- Benchmark X5: **11/11 PASS**.
- E2E X5: **3/3 PASS**.
- Totale X5: **31/31 PASS**.
- Regressione check X3+X4+X5: comando `pytest -q tests/codes/test_x3_slu_checks.py tests/codes/test_x4_sle_checks.py tests/codes/test_x5_aperture_cerchiature_checks.py` con esito **74/74 PASS**.

---

## Teoria e fondamenti (riferimenti sintetici)

- Classificazione aperture per area relativa; criterio di attivazione FEM >25%.

---

## Diagramma dipendenze subfasi

```text
X5.1 → X5.2 → X5.3 → X5.4 → X5.5
```

---

## Rischi normativi residui

- Uso del modello cautelativo oltre il campo geometrico previsto.
- Mancata analisi locale nei casi con forte concentrazione di tensione.

---

## Cronologia e decisioni

- 2026-03-15: completate sub-fasi X5.1–X5.5; implementati `x5_aperture_classificazione`, `x5_aperture_rigidezza`, `x5_cerchiatura_redistribuzione`; validazione **31/31 PASS** e regressione check X3+X4+X5 **74/74 PASS**.

---

## Esempi numerici (estratti da letteratura normativa)

1) Apertura rettangolare: solaio L = 6.00 m, apertura 120×120 cm (predalles/lamiera) — stima carico redistribuito sulla trave equivalente: area apertura 1.2×1.2 = 1.44 m²; carico equivalente se q = 300 kgf/m² → Q_ap = 300·1.44 = 432 kgf.

2) Cerchiatura trave equivalente: usare riduzione rigidezza cautelativa per cerchiature di tipo rigido: per un esempio pratico trave equivalente 30×50 cm, E=30 GPa → calcolo EI per redistribuzione (rif. DM96 e prassi RD2229).

3) Effetto bordo e punteggio: per aperture > (L/4) applicare warning X5-APE-001 e usare modello cautelativo; esempio L=6.00 m, ap=1.2 m → ap/L = 0.20 (soglia di attenzione secondo linee storiche).

Riferimenti: DM96, NTC2018 suggerimenti applicativi, letteratura RD2229 su cerchiature.
