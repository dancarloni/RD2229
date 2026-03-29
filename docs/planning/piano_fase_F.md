# Fase F — Calcestruzzo Armato: Verifiche

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | corrente |
| Data completamento | 2026-03-09 |
| Test totali | test_flesso_taglio_torsione.py + test_armature.py + test_sle.py |
| File principali | `src/methods/ntc2018/checks.py`, `src/methods/rd2229/checks.py`, `src/methods/dm96/checks.py` |

---

## Descrizione

La Fase F implementa le **verifiche strutturali per elementi in calcestruzzo armato** secondo le principali norme italiane (RD2229, DM72, DM87, DM92, DM96, NTC2008, NTC2018) e l'EC2. Copre tre aree:

- **F.1** Verifiche di resistenza: flessione retta e deviata, taglio, torsione
- **F.2** Armature minime e massime secondo NTC2018
- **F.3** Verifiche agli stati limite di esercizio (SLE): fessurazione, deformazione, vibrazione

---

## Teoria e formule chiave

### F.1 — Flessione semplice (SLU, NTC2018/EC2)

```text
Momento resistente (sezione rettangolare):
  M_Rd = A_s · f_yd · (d - 0.4·x)

Profondità asse neutro:
  0.8·x·b·f_cd = A_s · f_yd  →  x = A_s·f_yd / (0.8·b·f_cd)

Flessione TA (RD2229):
  σ_c = M / (I_omog / y_c)  ≤  σ_c_adm
  σ_s = n · M / (I_omog / y_s)  ≤  σ_s_adm
  n = E_s / E_c  (rapporto di omogeneizzazione)
```

### F.1 — Taglio (SLU, NTC2018 §4.1.2.3)

```text
Resistenza a taglio senza armatura:
  V_Rd,c = [C_Rd,c · k · (100·ρ_l·f_ck)^(1/3) + k_1·σ_cp] · b_w · d
  k = 1 + √(200/d)  ≤  2.0
  ρ_l = A_sl / (b_w · d)  ≤  0.02

Con armatura a taglio (staffe):
  V_Rd,s = (A_sw / s) · z · f_ywd · cot(θ)
  θ: 21.8°÷45° (1 ≤ cot(θ) ≤ 2.5)

Controllo massima inclinazione dei puntoni:
  V_Rd,max = α_cw · b_w · z · ν_1 · f_cd / (cot(θ) + tan(θ))
```

### F.1 — Torsione (NTC2018 §4.1.2.4)

```text
Sezione cava equivalente (thin-walled):
  T_Rd = 2 · A_k · t_ef · τ_t,i
  A_k = area racchiusa dalla linea mediana
  t_ef = spessore efficace parete

Armatura longitudinale torsione:
  A_sl = T_Ed · u_k / (2 · A_k · f_yd · cot(θ))

Interazione flessione-torsione-taglio:
  (T_Ed / T_Rd)² + (V_Ed / V_Rd)²  ≤  1.0
```

### F.2 — Armature minime/massime

```text
Armatura minima flessione (NTC2018 §4.1.6.1):
  A_s,min = max(0.26·(f_ctm/f_yk)·b·d, 0.0013·b·d)

Armatura massima:
  A_s,max = 0.04 · A_c   (zona corrente)

Staffe minime (taglio):
  A_sw,min / s = 0.08 · √f_ck / f_yk · b_w
```

### F.3 — SLE fessurazione (NTC2018 §4.1.4)

```text
Ampiezza fessura caratteristica:
  w_k = s_r,max · (ε_sm - ε_cm)
  s_r,max = k_3·c + k_1·k_2·k_4·φ / ρ_p,eff
  ε_sm - ε_cm = [σ_s - k_t·(f_ct,eff/ρ_p,eff)·(1+α_e·ρ_p,eff)] / E_s
  w_lim: 0.2 mm (espos. XC3/4), 0.3 mm (XC1/2), 0.4 mm (XC0)
```

---

## Diagramma dipendenze

```text
Fase F — flusso dati

  NTC2018/EC2/RD2229/DM72/DM87/DM96
         │
         ▼
  src/methods/
  ├── ntc2018/checks.py   ─── SLU: M_Rd, V_Rd, T_Rd, SLE: w_k, δ
  ├── rd2229/checks.py    ─── TA: σ_c, σ_s, τ (via I_omogenizzata)
  ├── dm96/checks.py      ─── TA DM96 (tabelle diverse da RD2229)
  └── protocols.py        ─── ABC ChecksProtocol (interfaccia comune)
         │
         ▼
  Fase I — sezione_omogenizzata.py  (n, I_omog, y_c, y_s)
  Fase J — pressoflessione deviata multinorma
  Fase K — grafici sollecitazioni + dominio interazione
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase I — `src/sections/` | Proprietà sezione omogeneizzata (n, I, W, A) |
| Fase J — pressoflessione | Estende F.1 per flessione biassiale |
| Fase A — `src/materials/` | f_ck, f_yk, E_s, E_c per i calcoli |
| `src/report/tabulato.py` | Formattazione tabulato verifiche |
| `src/core/normative_registry.py` | Routing dinamico per norma selezionata |

---

## Riferimenti normativi

| Norma | Articolo | Contenuto |
| --- | --- | --- |
| NTC2018 | §4.1.2.1 | Flessione SLU — M_Rd, asse neutro |
| NTC2018 | §4.1.2.3 | Taglio — V_Rd,c, V_Rd,s, V_Rd,max |
| NTC2018 | §4.1.2.4 | Torsione — sezione cava equivalente |
| NTC2018 | §4.1.4 | SLE fessurazione — w_k |
| NTC2018 | §4.1.5 | SLE deformazione — freccia limite |
| NTC2018 | §4.1.6 | Armature minime e massime |
| EC2 EN 1992-1-1 | §6.1, §6.2, §6.3 | Flessione, taglio, torsione SLU |
| RD 2229/1939 | §39-65 | Verifiche TA: σ_c, σ_s, τ |
| DM 09/01/1996 | §5 | Verifiche SLU — criteri DM96 |

---

## Struttura file

```text
src/methods/
├── ntc2018/
│   └── checks.py         # F.1–F.3 SLU+SLE per NTC2008/NTC2018/EC2
├── rd2229/
│   └── checks.py         # F.1 TA per RD2229/DM72/DM87/DM92
├── dm96/
│   └── checks.py         # F.1 TA/SLU per DM96
└── protocols.py           # ChecksProtocol ABC — interfaccia comune

tests/
├── test_flesso_taglio_torsione.py   # F.1
├── test_armature.py                 # F.2
└── test_sle.py                      # F.3
```

---

## Subfasi, checklist e storico

### F.1 — Verifiche flessione, taglio, torsione

**Stato**: ✅ COMPLETATO

- [x] Flessione retta e deviata (SLU + TA)
- [x] Taglio senza armatura (V_Rd,c) e con armatura (V_Rd,s + V_Rd,max)
- [x] Torsione: sezione cava equivalente, armature longitudinali e staffe
- [x] Interazione taglio-torsione
- [x] Test: `tests/test_flesso_taglio_torsione.py`

### F.2 — Armature minime e massime

**Stato**: ✅ COMPLETATO

- [x] Armatura minima flessione (NTC2018 §4.1.6.1)
- [x] Armatura massima
- [x] Staffe minime a taglio
- [x] Test: `tests/test_armature.py`

### F.3 — Verifiche SLE

**Stato**: ✅ COMPLETATO

- [x] Fessurazione: w_k, s_r,max, limite per classe esposizione
- [x] Deformazione: freccia elastica e differita, limite l/250 e l/500
- [x] Vibrazione: frequenza propria (stima semplificata)
- [x] Test: `tests/test_sle.py`

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Un file `checks.py` per norma (non un monolite) | Separazione netta norme TA vs SLU, aggiornamenti indipendenti |
| `ChecksProtocol` ABC | Interfaccia comune per dispatcher multinorma e test |
| Routing via `normative_registry.py` | Zero dipendenze hardcoded nella GUI/report |
| `passaggi_calcolo: list[str]` nel risultato | Tracciabilità completa per tabulato calcolo |
| Coefficiente θ (inclinazione puntoni) come parametro | Ottimizzazione armature staffe (θ ottimale = 21.8°) |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Norme da coprire F.1 | Tutte: RD2229, DM72/87/92, DM96, NTC2008, NTC2018, EC2 | File `checks.py` separati per norma (Fase H) |
| SLE: quali verifiche | Fessurazione + deformazione + vibrazione | Tre sotto-funzioni in `checks_ntc2018.py` |
| Armature minime: norma | NTC2018 §4.1.6 come riferimento principale | Configurabile via `norma` enum |

---

## Note storiche/archivio

- La Fase F è implementata come estensione della struttura creata in Fase H (riorganizzazione `methods/`)
- I file `checks_rd2229.py`, `checks_ntc2018.py`, `checks_dm96.py` originalmente flat, migrati in Fase H
- La verifica SLE vibrazione usa stima semplificata (f_1 = π²/2L² · √(EI/m)); per analisi modale completa vedere Fase M
