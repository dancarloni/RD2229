# Fase T — Verifiche al fuoco avanzate (isoterma 500°C, FEM termico)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~60 |
| **Norma/e di riferimento** | NTC2018 §4.1.6, EN 1992-1-2, EN 1993-1-2 |
| **Priorità** | Bassa |

---

## Descrizione

Verifiche strutturali avanzate al fuoco: metodo della curva isoterma 500°C per sezioni in c.a. (EN 1992-1-2 §4.2), solutore FEM termico 2D per calcolo del profilo di temperatura nella sezione trasversale, analisi strutturale con proprietà dei materiali ridotte in funzione della temperatura. Il modulo estende la verifica tabellare già implementata nelle fasi precedenti con un approccio analitico/numerico più accurato per sezioni non standard e situazioni di esposizione parziale.

---

## Teoria e fondamenti strutturali

### Curva di incendio standard ISO 834

```text
T(t) = 20 + 345 · log10(8·t + 1)    [°C]
```

dove t è il tempo in minuti. Per t=30 min: T≈842°C; t=60 min: T≈945°C; t=90 min: T≈1006°C.

Curve alternative: ASTM E119 (americana), curva idrocarburi (EN 1991-1-2 §3.2.3) per settore petrolchimico.

### Metodo isoterma 500°C (EN 1992-1-2 §4.2.2)

La zona di calcestruzzo con temperatura T > 500°C viene ignorata nel calcolo della resistenza; la sezione efficace è la parte con T < 500°C. L'acciaio delle armature mantiene le sue proprietà ridotte in funzione della temperatura locale T_s.

```text
b_fi = b - 2·a_500    (larghezza efficace ridotta)
h_fi = h - a_500      (altezza efficace ridotta, se esposta solo dal basso)
```

dove `a_500` = distanza dell'isoterma 500°C dalla faccia esposta.

Per sezione rettangolare esposta su 3 lati: `a_500 = f(t, b, h)` da tabelle EN 1992-1-2 Annex A o da calcolo FEM termico.

### Riduzione resistenza calcestruzzo con la temperatura

```text
f_ck,θ = k_c(θ) · f_ck
```

| θ [°C] | k_c(θ) cls siliceo | k_c(θ) cls calcareo |
| --- | --- | --- |
| 20 | 1.00 | 1.00 |
| 200 | 0.95 | 0.97 |
| 400 | 0.75 | 0.85 |
| 500 | 0.64 | 0.74 |
| 700 | 0.22 | 0.54 |
| 900 | 0.04 | 0.06 |

### Riduzione resistenza acciaio con la temperatura

```text
f_sy,θ = k_s(θ) · f_yk
```

| θ [°C] | k_s(θ) acciaio barre | k_s(θ) acciaio preteso |
| --- | --- | --- |
| 20 | 1.00 | 1.00 |
| 400 | 1.00 | 0.90 |
| 500 | 0.78 | 0.70 |
| 600 | 0.47 | 0.47 |
| 700 | 0.23 | 0.23 |

### Equazione di diffusione termica (FEM 2D)

Equazione di calore 2D in regime transitorio:

```text
ρ · c_p · ∂T/∂t = ∂/∂x(λ·∂T/∂x) + ∂/∂y(λ·∂T/∂y) + Q
```

dove ρ = densità, c_p = calore specifico, λ = conducibilità termica (funzioni di T per cls e acciaio).

Condizione al contorno sulle facce esposte (convezione + irraggiamento):

```text
q_n = h_c·(T_gas - T_surf) + ε·σ·(T_gas⁴ - T_surf⁴)
```

con h_c = 25 W/m²K (EN 1991-1-2 §3.1), ε = 0.7 (emissività cls).

### Verifica strutturale a fuoco

**Azione di progetto per fuoco (situazione eccezionale):**

```text
E_fi,d = G_k + ψ_fi · Q_k

η_fi = E_fi,d / E_d    con E_d calcolato per SLU ordinario
```

Tipicamente η_fi ≈ 0.6-0.7.

**Verifica:**

```text
M_fi,Rd(t) ≥ M_fi,Ed    per ogni istante t della durata REI richiesta
```

### Acciaio — riduzione a temperatura (EN 1993-1-2)

```text
k_y(θ) = f_y,θ / f_y    (riduzione snervamento)
k_E(θ) = E_a,θ / E_a    (riduzione modulo elastico)
```

Instabilità a fuoco: curva di buckling modificata χ_fi(λ_θ) dove `λ_θ = λ · √(k_y(θ)/k_E(θ))`.

---

## Diagramma dipendenze subfasi

```text
T.1 — Curva isoterma 500°C (profilo termico, sezione efficace)
 └── T.2 — FEM termico 2D (diffusione calore, mappa T(x,y,t))
      └── T.3 — Proprietà ridotte k_c(θ), k_s(θ), k_E(θ)
           ├── T.4 — Verifica strutturale c.a. a fuoco (M_fi,Rd, V_fi,Rd)
           └── T.5 — Verifica strutturale acciaio a fuoco (χ_fi)
                └── T.6 — Test confronto tabelle EC2 Annex C
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Verifica fuoco tabellare | `src/fire/` | Base esistente da estendere con metodo analitico |
| checks_ntc2018 | `src/checks_ntc2018.py` | Resistenza M_Rd, V_Rd a temperatura ridotta |
| MaterialRepository | `src/materials/material_repository.py` | cls e acciaio — proprietà a temperatura k_c/k_s |
| FEM beam (Fase M) | `src/fem/` | Post-processing sollecitazioni per verifica a fuoco |
| registro_log | `src/core/registro_log.py` | Log profilo termico, tempo raggiungimento REI |
| numpy | dipendenza esterna | Griglia temperatura FEM 2D |
| scipy | dipendenza esterna | Soluzione sistema FEM termico |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| EN 1992-1-2 §4.2 | Metodo isoterma 500°C per c.a. |
| EN 1992-1-2 §3.2 | Proprietà calcestruzzo a temperatura (k_c, k_E) |
| EN 1992-1-2 §3.3 | Proprietà acciaio a temperatura (k_s) |
| EN 1992-1-2 Annex A | Tabelle isoterme per sezioni rettangolari standard (REI 30-120) |
| EN 1992-1-2 Annex B | Metodo degli elementi in zona — alternativa all'isoterma 500°C |
| EN 1993-1-2 §3.2 | Proprietà acciaio strutturale a temperatura |
| EN 1993-1-2 §4.2 | Verifica instabilità a fuoco, χ_fi |
| EN 1991-1-2 §3 | Azioni termiche — curva ISO 834, curva idrocarburi |
| NTC2018 §4.1.6 | Resistenza al fuoco — requisiti generali |
| Franssen J.M., Vila Real P. — Fire Design of Steel Structures (2010) | Metodo χ_fi acciaio |

---

## Struttura file/directory prevista

```text
src/fire/
├── __init__.py                   # Export pubblico (estende modulo fire esistente)
├── isoterma_500.py               # (~200 righe) curva 500°C, a_500, sezione efficace b_fi/h_fi
├── fem_termico.py                # (~300 righe) FEM 2D transitorio, mappa T(x,y,t), scipy.sparse
├── proprieta_temperatura.py      # (~150 righe) k_c(θ), k_s(θ), k_E(θ) per cls e acciaio
├── verifica_ca_fuoco.py          # (~200 righe) M_fi,Rd, V_fi,Rd con proprietà ridotte
└── verifica_acciaio_fuoco.py     # (~200 righe) f_y,θ, E_a,θ, χ_fi, M_b,fi,Rd

tests/
├── test_isoterma_500.py          # (~15 test) a_500 per sezioni standard, confronto Annex A
├── test_fem_termico.py           # (~15 test) mappa T(x,y), confronto con soluzione analitica
├── test_proprieta_temperatura.py # (~15 test) k_c/k_s/k_E per θ tabellati
├── test_verifica_ca_fuoco.py     # (~10 test) M_fi,Rd, confronto con metodo tabellare
└── test_verifica_acciaio_fuoco.py # (~10 test) χ_fi, M_b,fi,Rd
```

---

## Subfasi pianificate

### T.1 — Curva isoterma 500°C

**Stato**: TODO

- [ ] Implementare curva ISO 834: T(t) in funzione dei minuti
- [ ] Calcolo profilo termico semplificato per sezione rettangolare (tabelle EN 1992-1-2 Annex A)
- [ ] Calcolo `a_500` (distanza isoterma 500°C dalla faccia esposta) per REI 30/60/90/120
- [ ] Sezione efficace ridotta: b_fi, h_fi per 1-4 facce esposte
- [ ] Area efficace A_fi e momento di inerzia I_fi della sezione ridotta
- [ ] Test: sezione 30×50, 3 lati esposti, REI 60 — verifica b_fi con tabella Annex A

### T.2 — FEM termico 2D

**Stato**: TODO

- [ ] Griglia FEM 2D della sezione: mesh quadrilaterale regolare (es. 10×10 per 30×50 cm)
- [ ] Proprietà materiale in funzione di T: λ(T), ρ·c_p(T) per cls (EN 1992-1-2 §3.3)
- [ ] Condizioni al contorno: convezione + irraggiamento su facce esposte, adiabatica su simmetrie
- [ ] Integrazione temporale implicita (Crank-Nicolson): stabilità per Δt qualsiasi
- [ ] Soluzione con `scipy.sparse.linalg.spsolve` ad ogni step temporale
- [ ] Output: mappa T(x,y) per ogni istante t richiesto (es. t=30, 60, 90, 120 min)
- [ ] Test: sezione quadrata 30×30 esposta su 4 lati, t=60 min — confronto con soluzione analitica

### T.3 — Proprietà materiali ridotte a temperatura

**Stato**: TODO

- [ ] Implementare k_c(θ) per cls siliceo e calcareo (EN 1992-1-2 Tab.3.1)
- [ ] Implementare k_s(θ) per acciaio barre e preteso (EN 1992-1-2 Tab.3.2-3.3)
- [ ] Implementare k_E(θ) per modulo elastico cls e acciaio
- [ ] Implementare k_y(θ) e k_E(θ) per acciaio strutturale (EN 1993-1-2 Tab.3.1)
- [ ] Interpolazione lineare tra valori tabulati
- [ ] Test: k_c(500°C) = 0.64, k_s(600°C) = 0.47 — verifica con tabelle norma

### T.4 — Verifica strutturale c.a. a fuoco

**Stato**: TODO

- [ ] Calcolo azione di progetto fuoco: E_fi,d = G_k + ψ_fi·Q_k; η_fi = E_fi,d/E_d
- [ ] Resistenza a flessione con sezione efficace (T.1) e armature a T ridotta (T.2+T.3)
- [ ] M_fi,Rd calcolato con f_yk·k_s(T_s) per ogni barra di armatura
- [ ] Resistenza a taglio: V_fi,Rd con f_ck·k_c(θ_med) della sezione efficace
- [ ] Verifica REI: t_fi ≥ t_req dove t_fi = tempo in cui M_fi,Rd(t) < M_fi,Ed
- [ ] Confronto risultato con metodo tabellare (Fase fire esistente): coerenza entro 10%
- [ ] Test: trave 25×50, 3 barre φ16, REI 60 — verifica M_fi,Rd metodo analitico vs tabella

### T.5 — Verifica strutturale acciaio a fuoco

**Stato**: TODO

- [ ] Temperatura di progetto θ_a per elemento non protetto: da EN 1993-1-2 §4.2.5
- [ ] Temperatura di progetto per elemento protetto (intumescente, lastra): §4.3.4
- [ ] Resistenza a flessione: M_fi,Rd = k_y(θ)·W_pl·f_y/γ_M,fi (γ_M,fi=1.0)
- [ ] Resistenza a compressione: instabilità a fuoco, λ_θ, curva χ_fi
- [ ] Deformazione limite: δ/L = 1/30 o L²/(400h) per trave da verificare
- [ ] Test: HEA200 S275, non protetto, REI 30 — verifica temperatura θ_a e M_fi,Rd

### T.6 — Test confronto con tabelle EC2 Annex C

**Stato**: TODO

- [ ] Sezione 20×40: confronto ricoprimento minimo da Annex C con metodo isoterma 500°C
- [ ] Sezione 30×50: confronto per REI 30/60/90/120
- [ ] Sezione circolare Φ300: confronto con Annex C (metodo A)
- [ ] Verifica FEM termico su sezione 30×30: mappa T(x,y) a 60 min vs soluzione tabulata
- [ ] Test regressione: risultati verifiche identici a output precedente dopo refactoring

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/fire/isoterma_500.py` | 200 | Curva 500°C, a_500, sezione efficace b_fi/h_fi |
| `src/fire/fem_termico.py` | 300 | FEM 2D transitorio, mappa T(x,y,t) |
| `src/fire/proprieta_temperatura.py` | 150 | k_c(θ), k_s(θ), k_E(θ) per cls e acciaio |
| `src/fire/verifica_ca_fuoco.py` | 200 | M_fi,Rd, V_fi,Rd con proprietà ridotte |
| `src/fire/verifica_acciaio_fuoco.py` | 200 | f_y,θ, χ_fi, M_b,fi,Rd |
| `tests/test_isoterma_500.py` | 15 test | a_500 per sezioni standard |
| `tests/test_fem_termico.py` | 15 test | Mappa T(x,y), confronto analitico |
| `tests/test_proprieta_temperatura.py` | 15 test | k_c/k_s/k_E per θ tabulati |
| `tests/test_verifica_ca_fuoco.py` | 10 test | M_fi,Rd, confronto tabellare |
| `tests/test_verifica_acciaio_fuoco.py` | 10 test | χ_fi, M_b,fi,Rd |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| FEM termico: mesh fissa o adattiva? | A) Mesh regolare fissa (semplice, sufficiente per sezioni standard) / B) Adattiva (accurata per geometrie complesse — molto più complessa) |
| Integrazione temporale: Euler esplicito o Crank-Nicolson? | A) Euler esplicito (semplice, vincolo Δt per stabilità) / B) Crank-Nicolson (stabile per Δt qualsiasi, incondizionato) |
| Curva alternativa idrocarburi | A) Non prevista in Fase T / B) Aggiunta come opzione (stessa struttura FEM) |
| Acciaio: solo elementi non protetti o anche protetti? | A) Solo non protetti (scope ridotto) / B) Anche protetti con materiale intumescente (T.5 esteso) |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Convergenza FEM termico | Proprietà k(T) non lineari — possibile instabilità numerica | Linearizzare per ogni Δt (proprietà calcolate a T del passo precedente) |
| Mesh FEM vs precisione | Mesh 10×10 insufficiente per sezioni piccole | Adattare risoluzione a dimensione sezione (min 1 cm per cella) |
| Compatibilità con fire esistente | Modulo fire tabellare già presente — evitare duplicazione | T.4 chiama modulo fire per confronto, non lo sostituisce |
| Temperatura armature | La T delle barre dipende dalla posizione (ricoprimento) — interpolazione dalla mappa FEM | Interpolazione bilineare dalla griglia FEM al punto barra |

---

## Note di pianificazione

- La Fase T dipende dal FEM termico indipendentemente dalla Fase M (FEM strutturale): sono due FEM distinti — termico (T.2) e strutturale (M).
- Il metodo isoterma 500°C (T.1) è sufficiente per la maggior parte dei casi pratici; il FEM termico (T.2) è necessario solo per sezioni non standard o esposizione parziale.
- L'integrazione con il modulo fire tabellare esistente deve essere conservata: T.4 aggiunge il metodo avanzato come alternativa, non sostituto.
- La Fase T può essere avviata indipendentemente dalle Fasi P, Q, R, S — ha solo dipendenza debole da Fase M per il post-processing.

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
