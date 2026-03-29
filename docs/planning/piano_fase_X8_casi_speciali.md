# Fase X8 — Casi Speciali (Predalles, Collaboranti, CLT)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | COMPLETATO |
| Commit | — |
| Data | 2026-03-16 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~40 |
| Ambito | Package standalone post-V1 + benchmark preliminari + warning blocking |

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

- [x] X8.1 — Raccolta requisiti normativi dettagliati
- [x] X8.2 — Contratto dati esteso per casi speciali
- [x] X8.3 — Benchmark preliminari dedicati
- [x] X8.4 — Integrazione graduale post-V1 (standalone, non agganciato al dispatcher core)

### Artefatti implementati

- `src/x8_special_cases/__init__.py`
- `src/x8_special_cases/x8_models.py`
- `src/x8_special_cases/x8_warnings.py`
- `src/x8_special_cases/x8_predalles.py`
- `src/x8_special_cases/x8_collaboranti.py`
- `src/x8_special_cases/x8_clt.py`
- `src/x8_special_cases/x8_dispatcher.py`
- `src/x8_special_cases/x8_benchmarks.py`
- `tests/test_x8_special_cases.py` (22 test PASS)

---

## Domande, risposte e decisioni

- Q1 Scope: documentazione + stub di implementazione (ponte V2), senza integrazione nel dispatcher principale.
- Q2 Norme prioritarie: EN 13747 + EN 1994 + EN 1995/DM16 + NTC2018.
- Q3 Esempi benchmark: livello completo con 4+ casi; implementati 6 casi (2 per tipologia).
- Q4 Strategia warning: modalità massima conservativa; `X8-SPC-003` blocca output in strict mode.
- Q5 Test automation: unit + integration + snapshot; implementata suite dedicata in `tests/test_x8_special_cases.py`.
- Q6 Timeline integrazione: post-V1, package completamente standalone.
- Q7 Audience: ingegneri strutturisti italiani; testo operativo e tabelle normative in italiano.
- Q8 Fallback: modalità semplificata opzionale con `X8-SPC-002` (strict=False).
- Q9 Organizzazione file: package dedicato `src/x8_special_cases/`.
- Q10 Decision trace: tracciabilità completa documentata in questo file e in `docs/PIANO_LAVORO.md`.

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
- 2026-03-16: implementato package standalone `src/x8_special_cases/` con contratto dati esteso, warning codificati X8-SPC-001/002/003, dispatcher locale e benchmark fixtures.
- 2026-03-16: implementata suite `tests/test_x8_special_cases.py` con 22 test (unit + integration + snapshot + quick reference X8-T01/T02/T03).
- 2026-03-16: confermata policy post-V1 (non integrazione al pipeline core) e modalità strict-blocking come default.

---

## Esempi numerici (estratti da letteratura normativa)

1) Predalles caso A: L = 5.50 m, G = 250 kgf/m², Q = 200 kgf/m², h = 25 cm.
	- strict=True: warning `X8-SPC-001` + `X8-SPC-003`, output bloccato.
	- strict=False: warning `X8-SPC-002`, `q_tot = 450 kgf/m²`, rigidezza equivalente preliminare.

2) Predalles caso B: L = 6.20 m, G = 320 kgf/m², Q = 300 kgf/m², h = 28 cm.
	- valutazione preliminare per campata maggiore, stessi warning di policy.

3) Collaborante caso A: L = 7.20 m, G = 280 kgf/m², Q = 350 kgf/m², `n_equiv = 6.0`.
	- strict=True: blocco con `X8-SPC-003`.
	- strict=False: modulo equivalente con `E_eq = 2.1e6 / n_equiv`.

4) Collaborante caso B: L = 8.00 m, G = 300 kgf/m², Q = 450 kgf/m², `n_equiv = 8.0`.
	- confronto sensibilità su coefficiente omogeneizzazione.

5) CLT caso A: L = 5.00 m, G = 160 kgf/m², Q = 200 kgf/m², `E0_mean = 110000`, `k_ortho = 0.35`.
	- strict=True: blocco e richiesta modello ortotropo.
	- strict=False: `E_eq = E0_mean * k_ortho` con caveat isotropo.

6) CLT caso B: L = 6.50 m, G = 210 kgf/m², Q = 300 kgf/m², `E0_mean = 120000`, `k_ortho = 0.30`.
	- benchmark comparativo con caso A su deformabilità e frequenza attesa.

Riferimenti: DM96, DM16, NTC2018 e linee guida RD2229 per casi speciali.
- 2026-03-15: confermato che i casi speciali restano documentati ma fuori V1 minima.
- 2026-03-16: estensione a package tecnico standalone con benchmark preliminari e test automatici.
