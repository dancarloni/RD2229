# Fase X6 — Report e Tracciabilita

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Report HTML/MD, audit trail, riferimenti normativi |

---

## Scopo del modulo

Costruire report tecnici completi con:
- formule usate
- fallback disponibili
- motivazione della selezione
- warning e passaggi numerici
- riferimenti normativi puntuali

---

## Dipendenze reali del repo

- src/codes/ntc2018/secondary_elements/*/report_adapter.py
- src/core/registro_log.py
- src/reporting/report_builder.py

---

## Fonti normative e qualità documentale

- NTC2018/Circolare: tracciabilità del percorso di verifica.
- EN 1992: chiarezza su formule usate e condizioni di validità.
- Buona pratica tecnica: riproducibilità del calcolo e auditabilità.

---

## Contratto contenuti report

Ogni report deve includere:
- input e unità
- combinazione governante
- formula usata
- fallback disponibile
- motivo della scelta
- valori sostituiti
- esito e UC
- warning codificati

---

## Tabella obbligatoria formula/fallback

| Verifica | Formula usata | Fallback disponibile | Motivo selezione |
| --- | --- | --- | --- |
| Flessione | equilibrio sezione c.a. | elastica preliminare | aderenza normativa |
| Taglio | EC2/NTC con conversione SI | none | standard codificato |
| Freccia | q_l + formula trave | FEM globale | benchmarkabile |
| Vibrazioni | formula SI | stima semplificata | coerenza dimensionale |
| Aperture | modello cautelativo | FEM locale | V1 con trigger sicurezza |

---

## Warning code del modulo

- X6-REP-001: formula usata non tracciata
- X6-REP-002: riferimento normativo assente
- X6-REP-003: unità non esplicitate

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X6-T01 | risultato completo | report con sezioni obbligatorie |
| X6-T02 | warning attivo | warning codificato visibile |
| X6-T03 | fallback non usato | fallback comunque dichiarato |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X6.1 — Template report
- [ ] X6.2 — Integrazione log formula
- [ ] X6.3 — Tabella formula/fallback
- [ ] X6.4 — Export HTML/MD
- [ ] X6.5 — Test snapshot

---

## Domande, risposte e decisioni

- Domanda: (placeholder) — Risposta: (placeholder)

---

## Teoria e fondamenti (riferimenti sintetici)

- Principi di tracciabilità: includere input, formule, fallback, riferimenti normativi e warning codificati.

---

## Diagramma dipendenze subfasi

```text
X6.1 → X6.2 → X6.3 → X6.4 → X6.5
```

---

## Rischi normativi residui

- Report incompleto su formule derivate o cautelative.
- Mancato allineamento tra risultati numerici e unità mostrate.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X6 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) Caso di tracciabilità semplice: test automatico che registra per un input standard (L=4.5 m, q_s=300 kgf/m², tipologia laterocemento) le seguenti voci: input raw, unità convertite, combinazioni generate (count=4), M,V calcolati e warning prodotti. Esempio atteso: 4 combinazioni SLU generate (rif. X2-T01).

2) Report numerico: per il caso BM-X01 (vedi X7) includere colonne: `M_calc [kN·m]`, `V_calc [kN]`, `Formula usata` — esempio: M=120 kN·m, V=25 kN per un caso di prova; verificare che il campo `formula` punti a EN/NTC o fallback DM96.

3) Tracciabilità commit/test: per ogni esecuzione automatica salvare hash input + risultato numerico + riferimento normativo (es. NTC2018 §4.1.2) per riproducibilità (esempio di metadata generati per un run campione).

Riferimenti: linee guida interne, NTC2018 per formati di reporting e tracciabilità scientifica.
