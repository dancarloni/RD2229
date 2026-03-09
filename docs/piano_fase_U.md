# Fase U — Analisi sismica dettagliata (q, duttilità, gerarchia, pushover)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~100 |
| **Norma/e di riferimento** | NTC2018 §7, Circ. 7/2019 §C7, EN 1998-1 (EC8) |
| **Priorità** | Media |

---

## Descrizione

Analisi sismica dettagliata per edifici nuovi e esistenti: fattori q di struttura per diverse classi di duttilità (CD-A/CD-B), verifica duttilità in curvatura, gerarchia delle resistenze e progetto dei nodi trave-pilastro, analisi modale con spettro di risposta, analisi pushover statica non lineare. Integra il solutore FEM (Fase M) per assemblaggio matrici di rigidezza e massa, e lo spettro NTC2018 (Fase O) per la domanda sismica.

---

## Teoria e fondamenti strutturali

### Fattori di struttura q (NTC2018 §7.3.1)

Per edifici in c.a.:

```text
q = q_0 · k_w ≥ 1.5

q_0 per CD-A: 4.5 · (α_u / α_1)
q_0 per CD-B: 3.0 · (α_u / α_1)
q_0 per CD-L: 1.5 (strutture non dissipative)
```

- α_u/α_1 = rapporto tra moltiplicatore sismico al collasso e alla prima plasticizzazione
- k_w = fattore sistema strutturale: k_w=1.0 per telaio; k_w=(1+α_0)/3 ≤ 1.0 per pareti

### Duttilità in curvatura richiesta (EC8 §5.2.3.4)

```text
μ_φ = 1 + 2·(q-1)·T_C/T_1    se T_1 < T_C
μ_φ = 2·q - 1                  se T_1 ≥ T_C
```

Per CD-A (alta duttilità): μ_φ ≥ 13 per elementi primari; Per CD-B: μ_φ ≥ 7.

### Duttilità disponibile (EC8 §5.4.3.2.2)

```text
μ_φ,avail = ε_cu / (ε_y · x/d)
```

Con confinamento delle staffe, ε_cu aumenta:

```text
ε_cu,c = 0.0035 + 0.1 · α · ρ_sx · f_yw / f_c
```

dove α = fattore efficacia confinamento; ρ_sx = rapporto volumetrico staffe nella direzione x.

### Armatura minima di confinamento (EC8 §5.4.3.2.2)

```text
ρ_sx ≥ max(
    0.08 · (f_cd/f_yd) · ν_d · (μ_φ · ε_sy,d · d_s/b_0 - 0.035),
    0.01
)
```

### Gerarchia delle resistenze (EC8 §5.4.2.3)

```text
Σ M_Rc ≥ γ_Rd · Σ M_Rb    con γ_Rd = 1.3 (CD-A), 1.2 (CD-B)
```

**Taglio di progetto da gerarchia (trave, §5.4.3.1.2):**

```text
V_CD = (M_Rb,l + M_Rb,r) / L_cl + V_G±E/2
```

**Taglio di progetto da gerarchia (pilastro, §5.4.3.2.1):**

```text
V_CD = γ_Rd · (M_Rc,top + M_Rc,bot) / H_cl
```

### Verifica nodo trave-pilastro (EC8 §5.5.3.3)

Forza di taglio orizzontale nel nodo:

```text
V_jhd = A_s1 · f_yd · (1 + N_G / (A_s1 · f_yd)) - V_C
```

Verifica compressione diagonale:

```text
V_jhd ≤ η · f_cd · b_j · h_jc · √(1 - ν_d/η)
```

dove η = 0.6·(1 - f_ck/250), ν_d = N_Ed/(A_c·f_cd).

### Analisi modale con spettro (NTC2018 §7.3.3)

Assemblaggio matrici di rigidezza e massa per telaio multi-GDL:

```text
[K]{φ} = ω² · [M]{φ}    (problema agli autovalori)
T_i = 2π / ω_i
```

Taglio base per modo i: `V_b,i = M_eff,i · S_a(T_i)` dove `M_eff,i = L_i² / M_tot`

Combinazione modale SRSS (se T_i < 0.9·T_j per tutti i modi): `E = √(Σ E_i²)`

Combinazione CQC (modi ravvicinati): `E = √(Σ_i Σ_j ρ_ij · E_i · E_j)`

### Analisi pushover (NTC2018 §7.3.4.1)

Curva forza-spostamento (pushover curve): F_b vs δ_top per pattern di carico triangolare o uniforme.

Punto di prestazione (EN 1998-1 Annex B, metodo N2):

```text
1. Trasformare pushover curve in formato ADRS (S_a vs S_d)
2. Trovare intersezione con spettro di domanda inelastico
3. Verifica: δ_target ≤ δ_u (capacità di spostamento)
```

---

## Diagramma dipendenze subfasi

```text
U.1 — Fattori q di struttura (q_0, k_w, CD-A/B/L)
 └── U.2 — Duttilità (μ_φ richiesta vs disponibile, confinamento)
      └── U.3 — Gerarchia resistenze (Σ M_Rc ≥ γ_Rd·Σ M_Rb, V_CD)
           └── U.4 — Progetto nodi trave-pilastro (V_jhd, diagonal compression)
                └── U.5 — Analisi modale ([K],[M], autovalori, SRSS/CQC)
                     └── U.6 — Analisi pushover (curva F-δ, punto prestazione ADRS)
                          └── U.7 — Test confronto software riferimento
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Solutore FEM (Fase M) | `src/fem/` | Assemblaggio [K]; estensione per [M] |
| Spettro NTC2018 (Fase O) | `src/seismic/spettro_ntc2018.py` | S_a(T) per taglio base e pushover |
| checks_ntc2018 | `src/checks_ntc2018.py` | M_Rd per gerarchia e duttilità |
| Pressoflessione (Fase J) | `src/checks_ntc2018.py` | Dominio N-M per pilastri, verifica nodi |
| MaterialRepository | `src/materials/material_repository.py` | f_cd, f_yd per fattori gerarchia |
| registro_log | `src/core/registro_log.py` | Log analisi modale, warning duttilità insufficiente |
| numpy/scipy | dipendenze esterne | Soluzione problema agli autovalori (scipy.linalg.eigh) |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.3 | Analisi strutturale per azioni sismiche |
| NTC2018 §7.3.1 | Fattori q di struttura per diverse tipologie |
| NTC2018 §7.4 | Edifici — criteri di progetto per duttilità |
| Circ. 7/2019 §C7.3 | Commenti analisi sismica, gerarchia, duttilità |
| EN 1998-1 §5.2 | Fattori q, classi di duttilità DCH/DCM/DCL |
| EN 1998-1 §5.4 | Progettazione elementi per duttilità, armature confinamento |
| EN 1998-1 §5.5 | Progetto nodi trave-pilastro CD-A |
| EN 1998-1 Annex B | Metodo N2 per analisi pushover |
| Fajfar P. — A Nonlinear Analysis Method for Performance-Based Seismic Design (2000) | Metodo N2 (ADRS) |
| Priestley M.J.N. et al. — Seismic Design and Retrofit of Bridges (2007) | Duttilità, confinamento |
| Cosenza E., Manfredi G. — Progettazione Sismica degli Edifici in C.A. (2000) | Gerarchia resistenze, dettagli |

---

## Struttura file/directory prevista

```text
src/seismic/
├── __init__.py                   # Export pubblico (estende modulo seismic esistente)
├── fattori_struttura.py          # (~150 righe) q_0, k_w, α_u/α_1 per CD-A/B/L
├── duttilita.py                  # (~200 righe) μ_φ richiesta/disponibile, confinamento, θ_u
├── gerarchia.py                  # (~200 righe) Σ M_Rc ≥ γ_Rd·Σ M_Rb, V_CD travi e pilastri
├── nodi_trave_pilastro.py        # (~200 righe) V_jhd, verifica compressione diagonale
├── analisi_modale.py             # (~300 righe) [K],[M], autovalori, T_i, SRSS/CQC
└── pushover.py                   # (~400 righe) curva F-δ, ADRS, punto prestazione

tests/
├── test_fattori_struttura.py     # (~15 test) q per diverse tipologie e CD
├── test_duttilita.py             # (~20 test) μ_φ richiesta vs disponibile, confinamento
├── test_gerarchia.py             # (~20 test) nodi, V_CD travi e pilastri
├── test_nodi.py                  # (~15 test) V_jhd, verifica diagonale
├── test_analisi_modale.py        # (~20 test) autovalori, T_i, taglio base SRSS/CQC
└── test_pushover.py              # (~15 test) curva F-δ, punto prestazione
```

---

## Subfasi pianificate

### U.1 — Fattori di struttura q

**Stato**: TODO

- [ ] Enum `ClasseDuttilita` (CD_A, CD_B, CD_L) con q_0 corrispondente
- [ ] Calcolo α_u/α_1 da tipo edificio (telaio, parete, misto) — valori tabellati NTC2018
- [ ] Calcolo k_w in funzione di α_0 (rapporto altezza/lunghezza pareti dominanti)
- [ ] q finale: `q = q_0 · k_w`, verifica q ≥ 1.5
- [ ] Log: classe duttilità scelta e vincoli dettagli costruttivi attivati
- [ ] Test: telaio CD-A con α_u/α_1=1.3 — q atteso = 4.5·1.3·1.0 = 5.85

### U.2 — Duttilità in curvatura

**Stato**: TODO

- [ ] Calcolo μ_φ richiesta da q e T_1/T_C (formula EC8 §5.2.3.4)
- [ ] Calcolo μ_φ disponibile da geometria sezione (x/d, ε_cu, ε_y)
- [ ] Calcolo ε_cu,c con confinamento staffe (formula EC8 §5.4.3.2.2)
- [ ] Calcolo armatura minima staffe ρ_sx per soddisfare μ_φ richiesta
- [ ] Calcolo rotazione plastica θ_u (Circ.7/2019 §C8.7.2.4) per edifici esistenti
- [ ] Verifica μ_φ,avail ≥ μ_φ,req; avviso se non soddisfatta
- [ ] Test: pilastro 40×40, q=4.5, T_1=0.8s, T_C=0.5s — verifica μ_φ e ρ_sx minimo

### U.3 — Gerarchia delle resistenze

**Stato**: TODO

- [ ] Calcolo M_Rd per ogni trave e pilastro (positivo e negativo)
- [ ] Verifica nodo: Σ M_Rc ≥ γ_Rd · Σ M_Rb per ogni nodo interno
- [ ] Calcolo V_CD trave da gerarchia: (M_Rb,l + M_Rb,r)/L_cl + V_G
- [ ] Calcolo V_CD pilastro da gerarchia: γ_Rd·(M_Rc,top + M_Rc,bot)/H_cl
- [ ] Lista nodi che non soddisfano la gerarchia con γ_Rd effettivo
- [ ] Test: portale 2 piani — verifica gerarchia nodi angolari e interni

### U.4 — Progetto nodi trave-pilastro

**Stato**: TODO

- [ ] Calcolo forza di taglio orizzontale V_jhd nel nodo
- [ ] Verifica compressione diagonale: V_jhd ≤ η·f_cd·b_j·h_jc·√(1-ν_d/η)
- [ ] Calcolo armatura orizzontale nodo A_sh per resistere a V_jhd
- [ ] Geometria efficace nodo: b_j (larghezza efficace), h_jc (altezza pilastro)
- [ ] Test: nodo trave 25×50 — pilastro 40×40: V_jhd e verifica

### U.5 — Analisi modale con spettro

**Stato**: TODO

- [ ] Estendere FEM (Fase M) con matrice di massa [M] (massa concentrata ai nodi o massa coerente)
- [ ] Soluzione problema agli autovalori: `scipy.linalg.eigh(K, M)` → ω_i², {φ_i}
- [ ] Calcolo periodi T_i = 2π/ω_i; verifica massa modale effettiva Σ M_eff ≥ 85% M_tot
- [ ] Taglio base per modo i: V_b,i = M_eff,i · S_a(T_i) da spettro Fase O
- [ ] Combinazione SRSS per modi non ravvicinati
- [ ] Combinazione CQC per modi ravvicinati (ρ_ij da smorzamento ξ)
- [ ] Distribuzione forze sismiche ai piani: f_i = F_b · z_i·m_i / Σ(z_j·m_j)
- [ ] Test: telaio 3 piani — confronto T_1 con formula empirica NTC2018 (C_T·H^(3/4))

### U.6 — Analisi pushover

**Stato**: TODO

- [ ] Definire pattern di carico laterale: triangolare (proporzionale a massa×altezza) e uniforme
- [ ] Incremento forze laterali con controllo spostamento (displacement control)
- [ ] Rilevare formazione cerniere plastiche (M > M_Rd in sezione)
- [ ] Ridurre rigidezza sezione plasticizzata (EI → 0 o valore residuo)
- [ ] Costruire curva F_b vs δ_top (pushover curve)
- [ ] Conversione in formato ADRS: S_a = F_b/M_eff, S_d = δ_top/Γ (Γ fattore partecipazione)
- [ ] Trovare punto di prestazione (intersezione spettro inelastico): metodo N2 (Fajfar 2000)
- [ ] Verifica: δ_target (domanda) ≤ δ_u (capacità ultima)
- [ ] Test: telaio 2 piani 2 campate — curva pushover e meccanismo di collasso

### U.7 — Test e confronto con software di riferimento

**Stato**: TODO

- [ ] Edificio 3 piani 2 campate: confronto T_1 con SAP2000 o OpenSees (da letteratura)
- [ ] Verifica gerarchia: confronto V_CD trave con calcolo manuale EC8
- [ ] Verifica nodo: confronto V_jhd con esempio EC8 Commentary
- [ ] Pushover: confronto punto di prestazione con metodo alternativo (EC8 Annex B)
- [ ] Benchmark performance analisi modale per telaio 10 piani

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/seismic/fattori_struttura.py` | 150 | q_0, k_w, α_u/α_1, classi CD |
| `src/seismic/duttilita.py` | 200 | μ_φ richiesta/disponibile, confinamento, θ_u |
| `src/seismic/gerarchia.py` | 200 | Σ M_Rc/M_Rb, V_CD travi e pilastri |
| `src/seismic/nodi_trave_pilastro.py` | 200 | V_jhd, verifica compressione diagonale |
| `src/seismic/analisi_modale.py` | 300 | [K],[M], autovalori, T_i, SRSS/CQC |
| `src/seismic/pushover.py` | 400 | Curva F-δ, ADRS, metodo N2 |
| `tests/test_fattori_struttura.py` | 15 test | q per tipologie e classi CD |
| `tests/test_duttilita.py` | 20 test | μ_φ richiesta vs disponibile, ρ_sx |
| `tests/test_gerarchia.py` | 20 test | Nodi, V_CD travi e pilastri |
| `tests/test_nodi.py` | 15 test | V_jhd, verifica diagonale |
| `tests/test_analisi_modale.py` | 20 test | Autovalori, T_i, SRSS/CQC |
| `tests/test_pushover.py` | 15 test | Curva F-δ, punto prestazione |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Analisi modale: massa concentrata o coerente? | A) Massa concentrata (diagonale — semplice) / B) Massa coerente (più precisa, matrice piena) |
| Pushover: controllo forza o spostamento? | A) Controllo spostamento (displacement control — robusto post-picco) / B) Controllo forza (semplice, non funziona post-picco) |
| Cerniere plastiche in pushover: modello rigido-plastico o con degrado? | A) Rigido-plastico (M=M_Rd poi rigidezza zero — semplice) / B) Con degrado (più realistico) |
| Integrazione con Fase M: estendere FEM esistente o separare? | A) Estendere (aggiungere [M] a elemento_beam.py) / B) Modulo separato (evita side effects) |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Autovalori mal condizionati | Se K e M hanno ordini di grandezza molto diversi | Normalizzazione masse, uso di scipy.linalg.eigh (stabile) |
| Pushover post-picco | Curva F-δ può avere softening — instabilità numerica | Displacement control con incrementi piccoli vicino al collasso |
| α_u/α_1 non noto a priori | Richiede analisi pushover per essere calcolato | Usare valori tabellati NTC2018 come stima iniziale |
| Smorzamento CQC | Dipende da smorzamento modale ξ — spesso 5%, a volte variabile | Default ξ=5% per tutti i modi, configurabile |

---

## Note di pianificazione

- La Fase U dipende dalla Fase M (FEM strutturale) per l'assemblaggio di [K] e dalla Fase O (spettro NTC2018) per S_a(T).
- Il modulo pushover è il più complesso della Fase U e può essere avviato come sotto-fase indipendente dopo che U.5 (analisi modale) è validata.
- α_u/α_1 è un parametro circolare (richiede pushover per essere calcolato esattamente): usare valori tabellati NTC2018 per il progetto, pushover per la verifica.
- La Fase U è fortemente collegata alla Fase R (edifici esistenti LV3): il modello globale muratura (R.4) usa l'analisi modale di U.5.

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
