# Fase P — Geotecnica e fondazioni

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~102 |
| **Norma/e di riferimento** | NTC2018 §6.4, EC7 (EN 1997-1), DM 11/03/1988 |
| **Priorità** | Media |

---

## Descrizione

Modulo completo per geotecnica e fondazioni: portanza di fondazioni superficiali (Terzaghi-Vesic), cedimenti elastici e da consolidazione, fondazioni profonde su pali (punta + laterale), muri di sostegno (spinta attiva e passiva Rankine/Coulomb), rischio liquefazione (Seed-Idriss). Il modulo fornisce verifiche agli stati limite NTC2018 (SLU GEO e STR) con tabulato di calcolo tracciabile. Integrazione con lo spettro sismico (Fase O) per componente sismica della spinta e verifica liquefazione.

---

## Teoria e fondamenti strutturali

### Portanza fondazione superficiale (Terzaghi generalizzata, Vesic)

Formula di portanza generale:

```text
q_lim = c · N_c · i_c · s_c · d_c
       + q · N_q · i_q · s_q · d_q
       + 0.5 · γ · B' · N_γ · i_γ · s_γ · d_γ
```

dove:

- `N_c, N_q, N_γ` = fattori di portanza di Vesic: `N_q = e^(π·tanφ)·tan²(45+φ/2)`; `N_c = (N_q-1)/tanφ`; `N_γ = 2·(N_q+1)·tanφ`
- `i` = fattori di inclinazione del carico
- `s` = fattori di forma (rettangolare, circolare, nastriforme)
- `d` = fattori di profondità
- `B'` = larghezza efficace ridotta per eccentricità: `B' = B - 2·e_B`

Carico di progetto SLU: `q_Ed ≤ q_Rd = q_lim / γ_R` dove `γ_R` da NTC2018 Tab.6.4.I.

### Cedimenti

**Cedimento elastico (Boussinesq):**

```text
ρ = q · B · (1 - ν²) / E_s · I_ρ
```

dove `I_ρ` = fattore di influenza (funzione di L/B e D/B).

**Cedimento da consolidazione primaria (Terzaghi 1D):**

```text
ρ_c = C_c / (1 + e_0) · H · log10(σ'_f / σ'_0)
```

dove `C_c` = indice di compressione, `e_0` = indice dei vuoti iniziale, `H` = spessore strato.

**Grado di consolidazione:** U(t) = f(T_v) dove `T_v = c_v · t / H²`.

### Portanza palo singolo

```text
Q_lim = Q_punta + Q_laterale = A_p · q_b + Σ(f_s,i · A_s,i)
```

- In argilla (UU): `q_b = N_c · c_u` con `N_c = 9`; `f_s = α · c_u`
- Da SPT (sabbia): `q_b = α_b · N_SPT`; correlazioni Meyerhof
- Da CPT: `q_b = k_c · q_c`; `f_s = q_c / n_s`

**Efficienza gruppo pali:** `η = Q_gruppo / (n · Q_singolo)` secondo formula Converse-Labarre o blocco di gruppo.

### Spinta su muri di sostegno

**Rankine (terreno orizzontale, muro verticale):**

```text
K_a = tan²(45° - φ/2)
K_p = tan²(45° + φ/2)
p_a = K_a · γ · z - 2·c·√K_a
```

**Coulomb (angolo attrito muro δ, inclinazione β, inclinazione paramento α):**

```text
K_a = sin²(α+φ) / [sin²α · sin(α-δ) · (1 + √(sin(φ+δ)·sin(φ-β)/(sin(α-δ)·sin(α+β))))²]
```

### Indice di liquefazione (Seed-Idriss)

**Domanda ciclica (CSR):**

```text
CSR = 0.65 · (σ_v / σ'_v) · (a_max / g) · r_d
```

**Resistenza ciclica da SPT (CRR a M=7.5):**

```text
CRR_7.5 = 1/(34 - N_{1,60}) + N_{1,60}/135 + 50/(10·N_{1,60}+45)² - 1/200
```

**Fattore di sicurezza:** `FS = CRR · MSF / CSR` dove `MSF = 10^2.24 / M^2.56`.

---

## Diagramma dipendenze subfasi

```text
P.1 — Fondazioni superficiali (portanza Vesic)
 ├── P.2 — Cedimenti (elastico + consolidazione)
 └── P.3 — Fondazioni profonde / pali
      └── (P.1, P.3) — P.4 — Muri di sostegno
           └── P.5 — Liquefazione (richiede spettro O)
                └── P.6 — Test e validazione NTC2018 Allegato A
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Spettro sismico NTC2018 | `src/seismic/spettro_ntc2018.py` | a_g per CSR liquefazione, spinta sismica Mononobe-Okabe |
| MaterialRepository | `src/materials/material_repository.py` | Materiali suolo (γ, φ, c, E_s, c_u) |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Tabulato fondazioni con passaggi intermedi |
| registro_log | `src/core/registro_log.py` | Log verifiche, avvisi condizioni limite |
| unita_misura | `src/core/unita_misura.py` | Conversione kg/cm² ↔ kPa per interfaccia |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §6.4 | Verifiche fondazioni superficiali e profonde, SLU/SLE |
| NTC2018 §6.5 | Muri di sostegno, verifiche ribaltamento/scorrimento/schiacciamento |
| NTC2018 §7.11 | Rischio liquefazione in zona sismica |
| EN 1997-1 (EC7) §6, §7 | Fattori di portanza, metodo di progetto |
| DM 11/03/1988 | Norma geotecnica storica — riferimento per edifici esistenti |
| Terzaghi K. — Theoretical Soil Mechanics (1943) | Formula portanza originale |
| Vesic A.S. — Analysis of Ultimate Loads of Shallow Foundations (1973) | Fattori N_c, N_q, N_γ, fattori correttivi |
| Mandolini A., Viggiani C. — Fondazioni su Pali (1992) | Portanza pali, efficienza gruppi |
| Seed H.B., Idriss I.M. — Simplified Procedure for Evaluating Soil Liquefaction Potential (1971) | Metodo CSR/CRR |
| Meyerhof G.G. — Bearing Capacity and Settlement of Pile Foundations (1976) | Correlazioni N_SPT — portanza palo |

---

## Struttura file/directory prevista

```text
src/geotecnica/
├── __init__.py                     # Export pubblico modulo
├── fondazioni_superficiali.py      # (~300 righe) portanza Vesic, fattori correttivi, SLU NTC2018
├── cedimenti.py                    # (~200 righe) cedimento elastico, consolidazione, grado U(t)
├── pali.py                         # (~300 righe) portanza palo singolo e gruppo, cedimento palo
├── muri_sostegno.py                # (~250 righe) Rankine, Coulomb, verifiche ribaltamento/scorrimento
└── liquefazione.py                 # (~200 righe) CSR, CRR da SPT, FS, mappe pericolosità

tests/
├── test_fondazioni_superficiali.py  # (~30 test) portanza, fattori, verifica SLU
├── test_cedimenti.py               # (~20 test) Boussinesq, consolidazione Terzaghi
├── test_pali.py                    # (~20 test) palo singolo, gruppo, correlazioni SPT
├── test_muri_sostegno.py           # (~15 test) Rankine, Coulomb, equilibrio
└── test_liquefazione.py            # (~10 test) CSR/CRR, FS, MSF
```

---

## Subfasi pianificate

### P.1 — Fondazioni superficiali

**Stato**: COMPLETATO

- [x] Implementare fattori di portanza N_c, N_q, N_γ (Vesic) in funzione di φ
- [x] Implementare fattori di forma s_c, s_q, s_γ per geometria rettangolare/circolare/nastriforme
- [x] Implementare fattori di inclinazione i_c, i_q, i_γ in funzione di inclinazione carico
- [x] Implementare fattori di profondità d_c, d_q, d_γ
- [x] Calcolo larghezza efficace B' per eccentricità
- [x] Verifica SLU GEO: q_Ed ≤ q_Rd con γ_R da NTC2018 Tab.6.4.I
- [x] Verifica SLE: cedimento ≤ limite ammissibile
- [x] Aggiungere `passaggi_calcolo: list[str]` con formula intermedia per ogni termine
- [x] Test: confronto con esempio numerico NTC2018 Allegato A §A.5

### P.2 — Cedimenti

**Stato**: COMPLETATO

- [x] Cedimento elastico immediato: formula Boussinesq, fattore I_ρ per L/B variabile
- [x] Cedimento da consolidazione: formula Terzaghi 1D, profili σ'_0 e σ'_f
- [x] Cedimento totale: ρ_tot = ρ_immediato + ρ_consolidazione + ρ_secondario (opzionale)
- [x] Grado di consolidazione U(t) per determinare cedimento nel tempo
- [x] Distribuzione tensioni verticali in profondità (Boussinesq, 2:1)
- [x] Test: strato argilloso 5m, C_c=0.3, e_0=0.8 — verifica cedimento atteso

### P.3 — Fondazioni profonde (pali)

**Stato**: COMPLETATO

- [x] Portanza punta in argilla (N_c=9, c_u) e sabbia (correlazioni N_SPT Meyerhof)
- [x] Portanza laterale: fattore α per argilla; correlazioni q_c da CPT per sabbia
- [x] Portanza palo singolo: Q_lim = Q_punta + Q_laterale
- [x] Verifica SLU NTC2018 §6.4.3: Q_Ed ≤ Q_Rd con γ_R punta e laterale separati
- [x] Gruppo pali: formula Converse-Labarre per efficienza η
- [x] Cedimento palo singolo: metodo Randolph-Wroth o correlazioni empiriche
- [x] Test: palo Φ500, L=15m in argilla c_u=80 kPa — confronto con formula manuale

### P.4 — Muri di sostegno

**Stato**: COMPLETATO

- [x] Coefficiente spinta attiva Rankine (terreno orizzontale e inclinato)
- [x] Coefficiente spinta attiva Coulomb (formula generale con α, β, δ)
- [x] Coefficiente spinta passiva Rankine e Coulomb
- [x] Contributo coesione nella spinta: p_a = K_a·γ·z - 2·c·√K_a
- [x] Spinta idrostatica e pressioni neutre
- [x] Verifica ribaltamento: M_ribaltante ≤ M_stabilizzante / γ_R
- [x] Verifica scorrimento: H_Ed ≤ H_Rd = (V_Ed·tanδ + c_a·A) / γ_R
- [x] Verifica schiacciamento terreno di fondazione (integrazione P.1)
- [x] Spinta sismica Mononobe-Okabe (integrazione spettro Fase O)
- [x] Test: muro H=4m, γ=18 kN/m³, φ=30° — verifica analitica

### P.5 — Liquefazione

**Stato**: COMPLETATO

- [x] Calcolo CSR da a_max (da spettro Fase O), σ_v/σ'_v, r_d(z)
- [x] Calcolo N_{1,60} da N_SPT grezzo (correzioni overburden, energia, fines)
- [x] Calcolo CRR_7.5 da N_{1,60} (formula Seed-Idriss 1985 + aggiornamento Youd 2001)
- [x] Fattore di scala magnitudine MSF per M ≠ 7.5
- [x] Fattore di sicurezza FS = CRR·MSF / CSR per ogni strato
- [x] Indice di potenziale liquefazione IL = Σ F(FS)·W(z)·dz
- [x] Classificazione: IL<2 (bassa), 2-15 (media), >15 (alta) pericolosità liquefazione
- [x] Test: sito con N_SPT=10, falda a 1m, M=6.5 — verifica FS

### P.6 — Test e validazione

**Stato**: COMPLETATO

- [x] Validazione portanza su esempio NTC2018 §A.5 (fondazione rettangolare)
- [x] Validazione cedimento su esempio Terzaghi classico
- [x] Validazione pali su esempio Viggiani-Mandolini
- [x] Validazione muro di sostegno su esempio Rankine manuale
- [x] Validazione liquefazione su caso studio da letteratura (Seed 1985)
- [x] Test integrazione: fondazione + cedimento + verifica SLU + tabulato

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/geotecnica/__init__.py` | 25 | Export pubblico modulo (creato) |
| `src/geotecnica/models.py` | 280 | Dataclass input/output e contratti geotecnici (creato) |
| `src/geotecnica/utils.py` | 80 | Conversioni unità e helper geotecnici (creato) |
| `src/geotecnica/norme.py` | 140 | Factory normativa + coefficienti DA1 (creato) |
| `src/geotecnica/fondazioni_superficiali.py` | 300 | Portanza Vesic, fattori correttivi, SLU (creato) |
| `src/geotecnica/cedimenti.py` | 200 | Boussinesq, consolidazione Terzaghi 1D (creato) |
| `src/geotecnica/pali.py` | 300 | Portanza palo singolo e gruppo, cedimento |
| `src/geotecnica/muri_sostegno.py` | 250 | Rankine, Coulomb, verifiche statiche e sismiche |
| `src/geotecnica/liquefazione.py` | 200 | CSR, CRR, FS, indice IL |
| `tests/test_fondazioni_superficiali.py` | 30 test | Portanza, fattori, SLU (creato) |
| `tests/test_cedimenti.py` | 20 test | Cedimento elastico, consolidazione (creato) |
| `tests/test_pali.py` | 20 test | Palo singolo, gruppo, SPT |
| `tests/test_muri_sostegno.py` | 15 test | Rankine, Coulomb, equilibrio |
| `tests/test_liquefazione.py` | 10 test | CSR/CRR, FS, classificazione |

---

## Decisioni architetturali confermate

| Decisione | Scelta approvata |
| --- | --- |
| Modello materiale suolo | B) kg/cm² interno con conversione kPa in input/output |
| Correlazioni SPT-CPT default | B) Robertson-Campanella |
| Verifica SLU NTC2018 | A) DA1 completo (SET1 + SET2) |
| Integrazione GUI Qt geotecnica | B) Widget fondazioni in P.6 |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia | Regole operative |
| --- | --- | --- | --- |
| Consistenza unità di misura | Mix kg/cm² (sistema progetto) e kPa (NTC2018/EC7) | Adattatore in `materials/adapter.py`, input accetta entrambe | Usare kg/cm² come storage interno; conversioni centralizzate in `src/geotecnica/utils.py`; testare equivalenza input kg/cm² vs kPa |
| Correlazioni SPT empiriche | Alta variabilità locale, correlazioni approssimate | Documentare origine e limiti di validità di ogni correlazione | Ogni correlazione deve avere `fonte`, range validità e warning runtime per input fuori campo |
| Spinta sismica Mononobe-Okabe | Dipende da spettro Fase O non ancora integrato | Stub con TODO, completare dopo Fase O integrata | Introdurre interfaccia dedicata, usare TODO normativo e test `xfail` fino al collegamento definitivo |
| Profili stratificati | Calcolo multi-strato complesso per cedimento e liquefazione | Iterazione su lista strati, risultato per strato | Modellare ogni strato con dataclass; evitare liste parallele; aggregare risultati per strato con passaggi tracciati |

---

## Note di pianificazione

- La Fase P dipende dalla Fase O per la componente sismica (a_g per CSR e spinta Mononobe-Okabe).
- I materiali suolo vanno aggiunti al `MaterialRepository` con schema compatibile (aggiungere tipo `SUOLO` con γ, φ, c, E_s, c_u, e_0, C_c).
- La verifica SLU NTC2018 §6.4 richiede di usare fattori parziali distinti per le azioni (A1/A2) e per i parametri del terreno (M1/M2) e la resistenza (R1/R2/R3).
- Per la Fase R (edifici esistenti), le verifiche di fondazione vengono richiamate con parametri ridotti dai livelli di conoscenza LC1-LC3.
- Le decisioni confermate in sessione sono già recepite nel codice iniziale (`kg/cm²` interno, DA1 set1/set2, default Robertson-Campanella).

## Storicizzazione

- 2026-03-10 — Avvio implementazione Fase P (P.1 + avvio P.2): creato package `src/geotecnica/` con `models.py`, `utils.py`, `norme.py`, `fondazioni_superficiali.py`, `cedimenti.py` e export pubblico.
- 2026-03-10 — Test iniziali verdi: `tests/test_fondazioni_superficiali.py` + `tests/test_cedimenti.py` (12 passed, 0 failed).
