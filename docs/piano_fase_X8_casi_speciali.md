# Fase X8 — Casi Speciali (Predalles, Collaboranti, CLT)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Estensioni fuori V1 minima |

---

## Scopo del modulo

Documentare i casi speciali richiesti nel round 3:
- predalles avanzato
- solai collaboranti acciaio-calcestruzzo
- CLT

Questi casi sono fuori dal perimetro implementativo V1 ma devono avere percorso tecnico già impostato.

---

## Dipendenze reali del repo

- src/materials/
- src/core/registro_log.py
- moduli futuri compositi / legno avanzato

---

## Fonti normative (parafrasi rigorosa)

- EN 13747: elementi prefabbricati e predalles.
- EN 1994: strutture composte acciaio-calcestruzzo.
- EN 1995: strutture in legno (base CLT e connessioni).
- NTC2018: inquadramento generale e livelli di verifica.

---

## Schede tecniche casi speciali

### Predalles

- controllo fase prefabbricato + getto integrativo
- verifica collaborazione e connessioni
- sensibilità elevata a sequenza costruttiva

### Collaboranti acciaio-calcestruzzo

- richiede modello interazione e scorrimento
- non assimilare a solaio pieno c.a.
- necessaria normativa composita dedicata

### CLT

- comportamento ortotropo
- verifiche dipendono da stratificazione e connessioni
- vibrazioni e deformabilità spesso governanti

---

## Formula usata / fallback / motivo selezione

| Caso | Formula usata in V1 | Fallback | Motivo |
| --- | --- | --- | --- |
| Predalles | placeholder documentale | input manuale avanzato | attesa modulo dedicato |
| Collaboranti | escluso da calcolo V1 | report warning + TODO | rischio errore elevato |
| CLT | escluso da calcolo V1 | report warning + TODO | anisotropia non coperta |

---

## Warning code del modulo

- X8-SPC-001: caso speciale fuori V1
- X8-SPC-002: norma specifica non caricata
- X8-SPC-003: richiesta modellazione avanzata

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X8-T01 | predalles avanzato | X8-SPC-001 + guida modulo futuro |
| X8-T02 | collaborante acciaio-c.a. | X8-SPC-003 |
| X8-T03 | CLT multi-strato | X8-SPC-003 |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X8.1 — Raccolta requisiti normativi dettagliati
- [ ] X8.2 — Contratto dati esteso per casi speciali
- [ ] X8.3 — Benchmark preliminari dedicati
- [ ] X8.4 — Integrazione graduale post-V1

---

## Domande, risposte e decisioni

- Domanda: (placeholder) — Risposta: (placeholder)

---

## Teoria e fondamenti (riferimenti sintetici)

- Casi speciali (predalles, collaboranti, CLT) richiedono moduli dedicati; in V1 solo documentazione e warning.

---

## Diagramma dipendenze subfasi

```text
X8.1 → X8.2 → X8.3 → X8.4
```

---

## Rischi normativi residui

- Mancata copertura normativa completa se introdotti in V1 senza modello dedicato.
- Alto rischio di non conservatività per ipotesi isotrope su CLT.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X8 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) Predalles multi-campata (semplificato): L = 5.50 m, G = 250 kgf/m², Q = 200 kgf/m² → conversione SI e confronto con schemi tabellari DM96 (uso BM-X02 come riferimento).

2) Collaboranti acciaio-calcestruzzo: trave collaborante equivalente sezione 30×50 cm; E_eq calcolato come combinazione materiale secondo EN1992 e confronto rigidezze per verifica di interazione.

3) CLT (legno massiccio): caso esistente con classe servizio 1 e f_m,k tipico; usare DM16 estratto per verifica preliminare (esempio classe legno massiccio, fattore sicurezza γ_m=1.5, usare valori tabellari per f_m,k).

Riferimenti: DM96, DM16, NTC2018 e linee guida RD2229 per casi speciali.
- 2026-03-15: confermato che i casi speciali restano documentati ma fuori V1 minima.
