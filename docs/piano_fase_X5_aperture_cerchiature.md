# Fase X5 — Aperture e Cerchiature

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
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

- X5-APE-001: apertura >25% (attivare FEM)
- X5-APE-002: apertura >50% (verifica manuale obbligatoria)
- X5-CER-001: cerchiatura non coerente con schema statico
- X5-AREA-001: area influenza manuale

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X5-T01 | area ratio 8% | alpha_ap=0.05 |
| X5-T02 | area ratio 30% | X5-APE-001 |
| X5-T03 | area ratio 60% | X5-APE-002 |
| X5-T04 | cerchiatura attiva | redistribuzione + check warning |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X5.1 — Classificazione aperture
- [ ] X5.2 — Modello cautelativo EI
- [ ] X5.3 — Trigger FEM locale
- [ ] X5.4 — Cerchiature equivalenti
- [ ] X5.5 — Test specifici

---

## Domande, risposte e decisioni

- Domanda: (placeholder) — Risposta: (placeholder)

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

- 2026-03-15: creato modulo X5 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) Apertura rettangolare: solaio L = 6.00 m, apertura 120×120 cm (predalles/lamiera) — stima carico redistribuito sulla trave equivalente: area apertura 1.2×1.2 = 1.44 m²; carico equivalente se q = 300 kgf/m² → Q_ap = 300·1.44 = 432 kgf.

2) Cerchiatura trave equivalente: usare riduzione rigidezza cautelativa per cerchiature di tipo rigido: per un esempio pratico trave equivalente 30×50 cm, E=30 GPa → calcolo EI per redistribuzione (rif. DM96 e prassi RD2229).

3) Effetto bordo e punteggio: per aperture > (L/4) applicare warning X5-APE-001 e usare modello cautelativo; esempio L=6.00 m, ap=1.2 m → ap/L = 0.20 (soglia di attenzione secondo linee storiche).

Riferimenti: DM96, NTC2018 suggerimenti applicativi, letteratura RD2229 su cerchiature.
