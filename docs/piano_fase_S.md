# Fase S — Normative aggiuntive (DM92, NTC2008, EC2/EC3/EC8, CNR-DT 200)

> Nota 2026-03-11: questa fase resta distinta dalla nuova famiglia S1-S9 dedicata agli elementi secondari del §7.2 NTC2018.

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~120 |
| **Norma/e di riferimento** | DM 14/02/1992, NTC 2008, EN 1992-1-1, EN 1993-1-1, EN 1998-1, CNR-DT 200/2004 |
| **Priorità** | Bassa |

---

## Descrizione

Estende le verifiche normative del progetto con le norme non ancora coperte: DM 14/02/1992 completo (tensioni ammissibili e stati limite), NTC 2008 (wrapper su EC2), Eurocodici EC2/EC3/EC8, CNR-DT 200 per rinforzi FRP. Ogni norma aggiunta implementa l'interfaccia `SingleCheckResult` con `riferimento_normativo` puntuale, consentendo integrazione diretta con il report (Fase Q) e il confronto multinorma.

---

## Teoria e fondamenti strutturali

### DM 14/02/1992

Impostazione a tensioni ammissibili (TA) e stati limite (SL) in parallelo:

- Tensioni ammissibili: σ_amm = f_ck / (γ_c · η) dove γ_c=1.5 e η fattore condizioni d'opera
- Resistenza caratteristica: `Rck` (cubica) invece di `fck` (cilindrica): `fck ≈ 0.83 · Rck`
- Coefficienti parziali: γ_cls = 1.5, γ_acciaio = 1.15 (identici EC2)

### EC2 (EN 1992-1-1) — Cemento armato

**Flessione (§6.1):**

```text
M_Rd = A_s · f_yd · (d - 0.4·x)
```

dove x ricavato dall'equilibrio: `A_s·f_yd = 0.8·x·b·f_cd`; verifica deformazione ultima: `ε_cu = 0.0035` per cls normale.

**Taglio senza armatura (§6.2.2):**

```text
V_Rd,c = [C_Rd,c · k · (100·ρ_l·f_ck)^(1/3) + k_1·σ_cp] · b_w · d
```

con `k = 1 + √(200/d) ≤ 2.0` e `C_Rd,c = 0.18/γ_c`.

**Taglio con armatura (§6.2.3, modello a traliccio):**

```text
V_Rd,s = (A_sw / s) · z · f_ywd · cotg(θ)
V_Rd,max = α_cw · b_w · z · ν_1 · f_cd / (cotg(θ) + tanθ)
```

### EC3 (EN 1993-1-1) — Acciaio

**Classificazione sezione (§5.5):**

- Classe 1: può sviluppare momento plastico e rotazione plastica → W_pl
- Classe 2: può sviluppare momento plastico senza rotazione plastica → W_pl
- Classe 3: solo momento elastico → W_el
- Classe 4: efficace ridotta → W_eff

**Resistenza a flessione (§6.2.5):**

```text
M_Rd = W_pl · f_y / γ_M0    (classi 1-2)
M_Rd = W_el · f_y / γ_M0    (classe 3)
```

**Instabilità flessotorsionale (§6.3.2):**

```text
M_b,Rd = χ_LT · W_y · f_y / γ_M1
```

dove `χ_LT` da curva di instabilità in funzione di `λ_LT = √(W_y·f_y/M_cr)`.

### EC8 (EN 1998-1) — Duttilità e gerarchia

**Duttilità in curvatura richiesta (§5.2.3.4):**

```text
μ_φ ≥ 1 + 2·(q-1)·T_C/T_1    se T_1 < T_C
μ_φ ≥ 2·q - 1                  se T_1 ≥ T_C
```

Per CD-H (alta duttilità): μ_φ ≥ 13 (travi e pilastri elementi primari).

**Gerarchia resistenze (§5.4.2.3):**

```text
Σ M_Rc ≥ 1.3 · Σ M_Rb    (pilastri più resistenti delle travi nel nodo)
```

### CNR-DT 200/2004 — Rinforzi FRP

**Rinforzo a flessione con lamine:**

```text
ΔM_Rd = A_f · f_fd · z_f
f_fd = E_f · ε_fd    con ε_fd = min(ε_fu/γ_f, ε_cu·(h-x)/x, ε_de)
```

dove `ε_de` = deformazione limite per delamination.

**Verifica delamination (distacco FRP-cls):**

```text
τ_b ≤ f_bd = 1.8 · f_ctm / γ_f    (bond stress)
```

---

## Diagramma dipendenze subfasi

```text
S.1 — DM92 verifiche complete (TA + SL)
 └── S.2 — NTC2008 verifiche (wrapper EC2 con adattamenti italiani)
      └── S.3 — EC2 flessione/taglio/torsione/SLE
           ├── S.4 — EC3 acciaio (classi sezione, instabilità, connessioni)
           ├── S.5 — EC8 dettagli duttili (gerarchia, μ_φ, nodi)
           └── S.6 — CNR-DT 200 rinforzi FRP
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| checks_ntc2018 | `src/checks_ntc2018.py` | Riferimento per interfaccia SingleCheckResult |
| checks_dm96 | `src/checks_dm96.py` | Pattern DA replicare per DM92 |
| MaterialRepository | `src/materials/material_repository.py` | Materiali con fck, fyk, f_frd (FRP) |
| adapter | `src/materials/adapter.py` | Conversione Rck↔fck, kg/cm²↔MPa |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Tabulato verifiche con passaggi intermedi |
| registro_log | `src/core/registro_log.py` | Log per ogni norma applicata |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| DM 14/02/1992 | Norme tecniche per le costruzioni in zona sismica — verifiche TA e SL |
| NTC 2008 | Norme tecniche per le costruzioni 2008 — precedente versione NTC |
| EN 1992-1-1 (EC2) | Progettazione strutture in c.a. — flessione, taglio, torsione, SLE |
| EN 1993-1-1 (EC3) | Progettazione strutture in acciaio — classi sezione, instabilità |
| EN 1993-1-8 (EC3) | Progettazione dei collegamenti — bullonature, saldature |
| EN 1998-1 (EC8) | Progettazione strutture sismoresistenti — duttilità, gerarchia |
| CNR-DT 200/2004 | Istruzioni per la progettazione di rinforzi con FRP |
| CNR-DT 200 R1/2013 | Revisione CNR-DT 200 — aggiornamento delamination |
| Cosenza E., Manfredi G., Pecce M. — Strutture in C.A. secondo EC2 (2008) | Riferimento teorico EC2 |
| Mazzolani F.M. — Strutture in Acciaio secondo EC3 (2004) | Riferimento teorico EC3 |

---

## Struttura file/directory prevista

```text
src/methods/
├── dm92/
│   ├── __init__.py
│   └── checks.py             # (~300 righe) TA + SL: flessione, taglio, torsione, pressoflessione
├── ntc2008/
│   ├── __init__.py
│   └── checks.py             # (~200 righe) wrapper EC2 con adattamenti italiani (NTC2008 §4)
└── ec/
    ├── __init__.py
    ├── ec2_ca.py             # (~400 righe) flessione, taglio, torsione, SLE EC2
    ├── ec3_acciaio.py        # (~350 righe) classi sezione, instabilità, M_b,Rd, V_Rd
    ├── ec3_connessioni.py    # (~200 righe) bullonature (Cat.A/B/C), saldature
    └── ec8_duttilita.py      # (~300 righe) μ_φ, gerarchia, confinamento, nodi

src/rinforzi/
├── __init__.py
└── frp_cnr_dt200.py          # (~300 righe) lamine FRP: flessione, taglio, delamination

tests/
├── test_dm92.py              # (~30 test) TA + SL, confronto con DM96
├── test_ntc2008.py           # (~20 test) wrapper EC2, adattamenti
├── test_ec2.py               # (~30 test) flessione/taglio/torsione/SLE
├── test_ec3.py               # (~25 test) classi, instabilità, connessioni
├── test_ec8.py               # (~20 test) μ_φ, gerarchia, nodi
└── test_frp.py               # (~15 test) incremento M_Rd, delamination
```

---

## Subfasi pianificate

### S.1 — DM92 verifiche complete

**Stato**: TODO

- [ ] Resistenza caratteristica calcestruzzo: da Rck a fck (`fck = 0.83·Rck`)
- [ ] Verifica flessione TA: σ_cls ≤ σ_amm,cls; σ_acc ≤ σ_amm,acc
- [ ] Verifica flessione SL: M_Ed ≤ M_Rd con γ_cls=1.5, γ_acc=1.15
- [ ] Verifica taglio: metodo bielle inclinate come DM96/EC2
- [ ] Verifica torsione: analogia trave a parete sottile
- [ ] Pressoflessione: dominio N-M con diagramma di interazione
- [ ] Aggiungere catalogo materiali DM92 in `data/materials/`
- [ ] Test: sezione 30×50, Rck 250, Fe44 — confronto TA vs SL vs NTC2018

### S.2 — NTC2008 verifiche

**Stato**: TODO

- [ ] Identificare differenze NTC2008 vs NTC2018 (§4.1, §7)
- [ ] Wrapper `checks_ntc2008.py` su `ec2_ca.py` con parametri NTC2008
- [ ] Aggiornare fattori amplificazione dinamica (NTC2008 §3.2 vs NTC2018 §3.2)
- [ ] Combinazioni di carico NTC2008 (ψ_0, ψ_1, ψ_2 da Tab.2.5.I NTC2008)
- [ ] Test: stessa sezione verificata NTC2008 e NTC2018 — delta < 5%

### S.3 — EC2 flessione/taglio/torsione/SLE

**Stato**: TODO

- [ ] Flessione semplice: equilibrio sezione, x neutro, M_Rd (§6.1)
- [ ] Flessione con sforzo normale: dominio N-M per pressoflessione (§6.1)
- [ ] Taglio senza armatura: V_Rd,c con fattore k (§6.2.2)
- [ ] Taglio con armatura: V_Rd,s e V_Rd,max con angolo θ (§6.2.3)
- [ ] Torsione: analogia sezione a parete sottile; verifica T_Rd,c e T_Rd,s (§6.3)
- [ ] Interazione taglio-torsione (§6.3.2 formula combinata)
- [ ] SLE fessurazione: w_k = s_r,max · (ε_sm - ε_cm) (§7.3.4)
- [ ] SLE deformazione: freccia con I_eff interpolato (§7.4.3)
- [ ] Test: 10 sezioni standard con verifica manuale su EC2 Handbook

### S.4 — EC3 acciaio: classi sezione, instabilità, connessioni

**Stato**: TODO

- [ ] Classificazione sezione acciaio: rapporti c/t per ali e anima (§5.5 Tab.5.2)
- [ ] Resistenza a flessione: M_Rd per classi 1-2 (W_pl) e 3 (W_el) (§6.2.5)
- [ ] Resistenza a taglio: V_Rd = A_v·f_y/(√3·γ_M0) (§6.2.6)
- [ ] Resistenza a compressione: N_Rd = A·f_y/γ_M0 (§6.2.4)
- [ ] Instabilità flessionale: χ da curva di buckling (§6.3.1), λ = √(A·f_y/N_cr)
- [ ] Instabilità flessotorsionale: χ_LT, M_b,Rd (§6.3.2)
- [ ] Bullonature: resistenza a taglio Cat.A (§3.6.1 EC3-1-8)
- [ ] Saldature a cordone d'angolo: F_w,Rd = a·f_vw,d (§4.5.3 EC3-1-8)
- [ ] Test: HEA200, S275 — verifica instabilità flessionale L=4m

### S.5 — EC8 dettagli duttili e gerarchia resistenze

**Stato**: TODO

- [ ] Calcolo duttilità richiesta μ_φ in funzione di q e T_1/T_C
- [ ] Verifica μ_φ disponibile: μ_φ = ε_cu/ε_y · 1/(x/d) (sezione con confinamento)
- [ ] Calcolo armatura confinamento (staffe): formula EC8 §5.4.3.2.2
- [ ] Gerarchia resistenze nodo trave-pilastro: Σ M_Rc ≥ 1.3·Σ M_Rb
- [ ] Taglio progetto trave da gerarchia: V_CD = (M_Rb,l + M_Rb,r)/L + V_G (§5.4.3.1.2)
- [ ] Taglio progetto pilastro: V_CD = (M_Rc,top + M_Rc,bot)/H_cl (§5.4.3.2.1)
- [ ] Nodi trave-pilastro: verifica compressione diagonale V_jhd ≤ η·f_cd·b_j·h_jc (§5.5.3.3)
- [ ] Test: nodo 30×50 trave + 40×40 pilastro — verifica gerarchia

### S.6 — CNR-DT 200 rinforzi FRP

**Stato**: TODO

- [ ] Materiali FRP: CFRP (E_f=170 GPa, f_fu=2800 MPa), GFRP, AFRP
- [ ] Fattori di riduzione: γ_f per tipo FRP; η_a per condizioni ambientali
- [ ] Rinforzo a flessione con lamine: incremento ΔM_Rd, verifica ε_fd ≤ ε_de
- [ ] Verifica delamination end: lunghezza ancoraggio L_b,max
- [ ] Rinforzo a taglio con tessuto: incremento ΔV_Rd per wrapping totale e parziale
- [ ] Confinamento pilastri con FRP: incremento f_cc = f_c + k_1·f_l (Mander)
- [ ] Test: trave 30×50, rinforzo CFRP — confronto M_Rd prima/dopo FRP

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/methods/dm92/__init__.py` | 10 | Export modulo DM92 |
| `src/methods/dm92/checks.py` | 300 | Verifiche TA + SL DM92 |
| `src/methods/ntc2008/__init__.py` | 10 | Export modulo NTC2008 |
| `src/methods/ntc2008/checks.py` | 200 | Wrapper EC2 con adattamenti NTC2008 |
| `src/methods/ec/__init__.py` | 15 | Export modulo EC |
| `src/methods/ec/ec2_ca.py` | 400 | EC2: flessione, taglio, torsione, SLE |
| `src/methods/ec/ec3_acciaio.py` | 350 | EC3: classi, instabilità flessionale e flessotorsionale |
| `src/methods/ec/ec3_connessioni.py` | 200 | EC3-1-8: bullonature, saldature |
| `src/methods/ec/ec8_duttilita.py` | 300 | EC8: μ_φ, gerarchia, confinamento, nodi |
| `src/rinforzi/__init__.py` | 10 | Export modulo rinforzi |
| `src/rinforzi/frp_cnr_dt200.py` | 300 | CNR-DT 200: lamine FRP, delamination, confinamento |
| `tests/test_dm92.py` | 30 test | TA + SL DM92 |
| `tests/test_ntc2008.py` | 20 test | Wrapper NTC2008 |
| `tests/test_ec2.py` | 30 test | EC2 flessione/taglio/torsione/SLE |
| `tests/test_ec3.py` | 25 test | EC3 classi, instabilità, connessioni |
| `tests/test_ec8.py` | 20 test | EC8 duttilità, gerarchia |
| `tests/test_frp.py` | 15 test | FRP: M_Rd, V_Rd, delamination |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| NTC2008: wrapper su EC2 o implementazione autonoma? | A) Wrapper (minima duplicazione, dipendenza da S.3) / B) Autonomo (isolato, più codice) |
| EC3 connessioni: incluse in Fase S o fase separata? | A) Incluse in S.4 (scope già ampio) / B) Fase separata per non ritardare S.3-S.5 |
| Catalogo materiali EC2/EC3: file JSON separato o estensione catalogo NTC2018? | A) File separato `catalogo_ec2.json` / B) Estensione con flag `norma: EC2` nel catalogo NTC2018 |
| CNR-DT 200 R1/2013 vs edizione 2004: quale usare? | A) Edizione 2013 (più aggiornata) / B) Entrambe con flag versione |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Sovrapposizione DM92/NTC2018 | Alcune formule identiche — rischio duplicazione | Funzioni condivise in modulo `src/methods/common/` |
| Angolo θ in EC2 §6.2.3 | Angolo bielle variabile: ottimizzazione o valore fisso 45°? | Default θ=45° (conservativo), ottimizzazione come opzione |
| Classificazione sezione EC3 | Dipende da geometria e carico — classificazione dinamica | Calcolo a ogni verifica, non memorizzata |
| FRP: variabilità proprietà meccaniche | f_fu e E_f dipendono da produttore specifico | Catalogo FRP con valori certificati, input manuale possibile |

---

## Note di pianificazione

- La Fase S ha bassa priorità perché le verifiche NTC2018 (già implementate in fasi precedenti) coprono la maggior parte dei casi d'uso italiani correnti.
- EC2 e NTC2018 sono strutturalmente molto simili: la Fase S.3 deve riutilizzare il codice NTC2018 dove possibile, non duplicarlo.
- I rinforzi FRP (S.6) sono strettamente collegati alla Fase R (edifici esistenti): considerare di anticipare S.6 contestualmente a Fase R se richiesto.
- La Fase S deve garantire che ogni norma produca `SingleCheckResult` con `riferimento_normativo` completo per il confronto multinorma (Q.7).

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
