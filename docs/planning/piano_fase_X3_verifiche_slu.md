
# Fase X3 — Verifiche SLU (Flessione, Taglio, Punzonamento)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | COMPLETATO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 (52 test implementati/validati in X3) |
| Ambito | Verifiche a resistenza SLU |

---

## Scopo del modulo

Implementare verifiche SLU con livello documentale vicino alla trascrizione normativa, mantenendo parafrasi rigorosa e tracciabile.

---

## Dipendenze reali del repo

- src/codes/params/NTC2018.json
- src/core_calculus/core/
- src/core/registro_log.py

---

## Fonti normative principali

- NTC2018 §4.1.2.4: verifiche di resistenza elementi in c.a.
- NTC2018 §4.1.2.5: verifica a taglio e punzonamento.
- EN 1992-1-1 §6.1: Flessione
- EN 1992-1-1 §6.2: Taglio
- EN 1992-1-1 §6.4: Punzonamento
- DM 9/1/96: tabelle laterocemento
- DM 16/1/96: parametri legno

---

## Tabella sintetica verifiche, formule e riferimenti

| Verifica         | Formula principale                                                                 | Riferimento normativo         | Fallback         | Note                         |
|------------------|-----------------------------------------------------------------------------------|-------------------------------|------------------|------------------------------|
| Flessione c.a.   | f_cd = f_ck/γ_c<br>f_yd = f_yk/γ_s<br>x = As·f_yd/(0.85·b·f_cd)<br>z = d - 0.4·x<br>M_Rd = As·f_yd·z | EN 1992-1-1 §6.1.2, §6.1.3; NTC2018 §4.1.2.4 | M=W·σ preliminare | x ≤ x_lim, sezione rettang. |
| Taglio           | d_mm = 10·d_cm<br>k = 1 + √(200/d_mm) ≤ 2<br>ρ_l = Asl/(bw·d)<br>V_Rd,c = 0.18·k·(100·ρ_l·f_ck)^(1/3)·bw·d | EN 1992-1-1 §6.2.2; NTC2018 §4.1.2.5 | dominio sperim.  | k, ρ_l come da norma         |
| Punzonamento     | V_Rd,c = [C_Rd,c·k·(100·ρ_l·f_cd)^(1/3) + k1·σ_cp]·b0·d<br>C_Rd,c=0.18; k1=0.15 | EN 1992-1-1 §6.4.2; NTC2018 §4.1.2.5 | —                | C_Rd,c=0.18; k1=0.15         |
| DM96 laterocem.  | Tabella casi LC-01/02/03                                                          | DM 9/1/96                     | input manuale    | Estratto tabellare           |
| DM16 legno       | Tabella casi LG-01/02/03                                                          | DM 16/1/96                    | prova/letteratura| Estratto tabellare           |

---

## Warning code del modulo

- X3-FLEX-001, X3-FLEX-002
- X3-TAG-001, X3-TAG-002
- X3-PUNZ-001
- X3-DM96-001
- X3-DM16-001

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X3-T01 | b,d,As,f_ck,f_yk | M_Rd e UC_M |
| X3-T02 | bw,d,Asl,f_ck | V_Rd,c |
| X3-T03 | b0,d,rho_l,f_cd,sigma_cp | V_Rd,c punzonamento |
| X3-T04 | caso DM96 fuori tabella | X3-DM96-001 |
| X3-T05 | legno senza f_mk | X3-DM16-001 |

---

## Stato avanzamento sub-fasi

- [x] X3.1 — Flessione c.a.
- [x] X3.2 — Taglio
- [x] X3.3 — Punzonamento
- [x] X3.4 — Fallback DM96/DM16
- [x] X3.5 — Test e benchmark

---

## Domande, risposte e decisioni

- Decisione: la formulazione di flessione in c.a. viene adottata come riferimento principale per X3; le tabelle DM96/DM16 restano come fallback/tabellari da usare quando necessario.
- Q&A bloccante pre-implementazione (2026-03-15):
  - Scope: implementazione core completa (flessione/taglio/punzonamento + fallback DM96/DM16 + wiring code module + test mirati).
  - Profondità test prima tranche: set esteso (25+).
  - Validazione immediata: pytest mirato sui nuovi test X3.
- Decisioni operative congelate:
  - NTC2018 primaria, EN 1992-1-1 secondaria di coerenza.
  - Fallback DM96/DM16 solo tramite check espliciti dedicati (no fallback automatico implicito).
  - Output standard con `trace`, `norm_references`, `ok`, `value`, `utilisation`, `steps` dettagliati.

---

## Implementazione tranche 1 (2026-03-15)

File creati:
- `src/methods/ntc2018/checks_x3.py`
- `tests/codes/test_x3_slu_checks.py`

File modificati:
- `src/codes/ntc2018/code_module.py`

Check implementati:
- `x3_slu_flessione`
- `x3_slu_taglio`
- `x3_slu_punzonamento`
- `x3_dm96_laterocemento`
- `x3_dm16_legno`

Warning code implementati:
- `X3-FLEX-001`, `X3-FLEX-002`
- `X3-TAG-001`, `X3-TAG-002`
- `X3-PUNZ-001`
- `X3-DM96-001`
- `X3-DM16-001`

Esito test X3:
- `tests/codes/test_x3_slu_checks.py` -> **35 pass / 0 fail**
- `tests/codes/test_x3_slu_benchmark.py` -> **17 pass / 0 fail**
- Totale validato su X3 (mirato): **52 pass / 0 fail**

---

## Diagramma dipendenze subfasi

```text
X3.1 → X3.2 → X3.3 → X3.4 → X3.5
```

---

## Rischi normativi residui

- Mancata trascrizione integrale tabelle DM96/DM16.
- Uso improprio fallback elastico al posto della verifica resistente.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X3 da split master Fase X.
- 2026-03-15: avviata implementazione X3 tranche 1 con modulo dedicato, wiring su `NTC2018CodeModule` e 35 test mirati verdi.
- 2026-03-15: completata X3.5 con benchmark numerici aggiuntivi; suite X3 aggiornata a 52/52 PASS.

---

## Esempi numerici (con riferimento normativo)

1) Flessione c.a. (EN 1992-1-1 §6.1.2, §6.1.3; NTC2018 §4.1.2.4):
   sezione rettangolare b=300 mm, d=500 mm; As = 1600 mm² (4Φ16), f_ck=25 MPa → f_cd = 25/1.5 = 16.67 MPa; f_yk=420 MPa, γ_s=1.15 → f_yd=365.22 MPa.
   x = As·f_yd/(0.85·b·f_cd) ≈ 137 mm; z = d - 0.4·x ≈ 445 mm → M_Rd = As·f_yd·z ≈ 2.60e8 N·mm ≈ 260 kN·m.

2) Taglio (EN 1992-1-1 §6.2.2; NTC2018 §4.1.2.5):
   bw = 300 mm, d = 500 mm, Asl = 200 mm² → ρ_l = 200/(300·500)=0.001333; f_ck=25 MPa; k = 1 + √(200/500) ≈ 1.632; (100·ρ_l·f_ck)^(1/3) ≈ 1.494 →
   V_Rd,c ≈ 0.18·k·(100·ρ_l·f_ck)^(1/3)·bw·d ≈ 65.98 kN.

3) Punzonamento (EN 1992-1-1 §6.4.2; NTC2018 §4.1.2.5):
   b0 = 1000 mm, d = 200 mm, ρ_l ≈ 0.02, f_cd = 16.67 MPa → V_Rd,c calcolata con la formulazione EN1992.

---

## Storico modifiche

- 2026-03-15: Ristrutturazione file, eliminazione ridondanze, aggiunta riferimenti normativi puntuali — dancarloni
