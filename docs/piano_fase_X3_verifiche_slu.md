# Fase X3 — Verifiche SLU (Flessione, Taglio, Punzonamento)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
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

## Fonti normative (parafrasi rigorosa)

- NTC2018 §4.1.2.4: verifiche di resistenza elementi in c.a.
- NTC2018 §4.1.2.5: verifica a taglio e punzonamento.
- EN 1992-1-1 §6.1, §6.2, §6.4: flessione, taglio, punzonamento.
- DM 9/1/96: tabelle di riferimento per laterocemento.
- DM 16/1/96: parametri resistenti legno.

---

## Schede normative (trascrizione operativa)

### Flessione c.a. (rettangolare, semplice armatura)

- f_cd = f_ck/gamma_c
- f_yd = f_yk/gamma_s
- x = As*f_yd/(0.85*b*f_cd)
- z = d - 0.4*x
- M_Rd = As*f_yd*z

Condizioni:
- x <= x_lim
- sezione rettangolare assimilabile

Warning:
- X3-FLEX-001: x>x_lim
- X3-FLEX-002: sezione fuori dominio semplificato

### Taglio

- d_mm = 10*d_cm
- k = 1 + sqrt(200/d_mm) <= 2
- rho_l = Asl/(bw*d)
- V_Rd,c = 0.18*k*(100*rho_l*f_ck)^(1/3)*bw*d

Warning:
- X3-TAG-001: rho_l fuori range
- X3-TAG-002: V_Ed/V_Rd,c > 0.6

### Punzonamento

- V_Rd,c = [C_Rd,c*k*(100*rho_l*f_cd)^(1/3) + k1*sigma_cp]*b0*d
- C_Rd,c=0.18; k1=0.15

Warning:
- X3-PUNZ-001: V_Ed > 0.8*V_Rd,c

---

## DM96/DM16 — estratti minimi implementativi (casistiche multiple)

### DM96 laterocemento (schema tabellare operativo)

| Caso | Luce [m] | Interasse [cm] | Altezza solaio [cm] | k_DM96 indicativo | Note |
| --- | --- | --- | --- | --- | --- |
| LC-01 | 3.5-4.5 | 50 | 20-24 | 0.15-0.17 | uso tabella prodotto |
| LC-02 | 4.5-5.5 | 50 | 24-28 | 0.16-0.18 | verificare freccia |
| LC-03 | 5.5-6.5 | 60 | 28-32 | 0.17-0.20 | caso sensibile a deformabilità |

### DM16 legno (schema tabellare operativo)

| Caso | Classe legno | Classe servizio | gamma_m | Parametro richiesto |
| --- | --- | --- | --- | --- |
| LG-01 | massiccio | 1 | 1.5 | f_m,k da tabella |
| LG-02 | lamellare | 1 | 1.5 | f_m,k da tabella |
| LG-03 | esistente | da indagine | >=1.5 | valore da prova/letteratura |

Nota: valori tabellari completi da trascrivere in appendice dedicata prima di implementazione finale.

---

## Formula usata / fallback / motivo selezione

| Verifica | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| Flessione c.a. | equilibrio sezione | M=W*sigma preliminare | maggiore aderenza normativa |
| Taglio | EN/NTC con k e rho_l | dominio sperimentale | standard codificato |
| Punzonamento | EN/NTC completa | no | necessario per bidirezionali |
| DM96 | estratto tabellare | input manuale | tabelle non integralmente trascritte |
| DM16 | estratto tabellare | prova/letteratura | caso esistente variabile |

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

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X3.1 — Flessione c.a.
- [ ] X3.2 — Taglio
- [ ] X3.3 — Punzonamento
- [ ] X3.4 — Fallback DM96/DM16
- [ ] X3.5 — Test e benchmark

---

## Domande, risposte e decisioni

- Decisione: la formulazione di flessione in c.a. viene adottata come riferimento principale per X3; le tabelle DM96/DM16 restano come fallback/tabellari da usare quando necessario.

---

## Teoria e fondamenti (riferimenti sintetici)

- Flessione: equilibrio sezione, f_cd = f_ck/γ_c, controllo x_lim.
- Taglio: formula EC2 con k, ρ_l e V_Rd,c; calcoli in SI.

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

---

## Esempi numerici (estratti da letteratura normativa)

1) Flessione c.a. (EN 1992-1-1 / NTC): sezione rettangolare b=300 mm, d=500 mm; As = 1600 mm² (4Φ16), f_ck=25 MPa → f_cd = 25/1.5 = 16.67 MPa; f_yk=420 MPa, γ_s=1.15 → f_yd=365.22 MPa.
 x = As*f_yd/(0.85*b*f_cd) ≈ 137 mm; z = d - 0.4*x ≈ 445 mm → M_Rd = As*f_yd*z ≈ 2.60e8 N·mm ≈ 260 kN·m (calcolo di verifica secondo EN1992).

2) Taglio (EN/NTC): bw = 300 mm, d = 500 mm, Asl = 200 mm² → ρ_l = 200/(300*500)=0.001333; f_ck=25 MPa; k = 1 + sqrt(200/d_mm) = 1 + sqrt(200/500) ≈ 1.632; (100·ρ_l·f_ck)^(1/3) ≈ 1.494 →
 V_Rd,c ≈ 0.18·k·(100·ρ_l·f_ck)^(1/3)·bw·d ≈ 65.98 kN (formula EN1992-1-1 §6).

3) Punzonamento (EN/NTC estratto): uso valori tipici: b0 = 1000 mm, d = 200 mm, ρ_l ≈ 0.02, f_cd = 16.67 MPa → V_Rd,c (ord. grandezza) calcolata con la formulazione EN1992 → usare la procedura completa del modulo per risultati puntuali (qui si riporta la modalità di calcolo e il riferimento normativo piuttosto che un singolo valore tabellare).

Riferimenti: EN 1992-1-1 §6, NTC2018 §4.1.2.
