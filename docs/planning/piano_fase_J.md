# Fase J — Pressoflessione Deviata Multinorma

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | `73482f0` (J.1), corrente (J.2–J.8) |
| Data completamento | 2026-03-09 |
| Test totali | test copertura completa (dispatcher + dominio 3D) |
| File principali | `src/pressoflessione/`, `src/gui/widgets/dominio_canvas.py` |

---

## Descrizione

La Fase J implementa la **verifica a pressoflessione deviata multinorma** per sezioni in c.a., coprendo:

- Verifica TA elastica (Navier biassiale): RD2229, DM92, DM96
- Verifica SLU con wrapper NTC2018/NTC2008/EC2
- Instabilità biassiale (amplificazione momenti)
- Dominio di resistenza 3D N-Mx-My e sue proiezioni 2D
- Widget Qt interattivo (dominio_canvas.py) con 3 viste e slider

Il dispatcher multinorma `calcola_pressoflessione_deviata()` seleziona automaticamente il percorso TA o SLU in base alla norma configurata.

---

## Teoria e formule chiave

### Verifica TA — Navier biassiale (RD2229/DM92/DM96)

```text
Tensione in un punto (x_i, y_i) della sezione:
  σ_i = N/A_omog + Mx/I_x · y_i + My/I_y · x_i

Verifica:
  σ_c,max  ≤  σ_c_adm  (calcestruzzo, bordo più compresso)
  σ_s,max  ≤  σ_s_adm  (acciaio, barra più tesa)
  n · σ_c,arm ≤  σ_s_adm  (acciaio in zona compressa)

Applicabilità: sezione non fessurata (fase 1)
  → se fessurata: passare a metodo iterativo (sezione parzializzata)
```

### Metodo Bresler (TA — interazione Mx-My)

```text
1/M_Rd(Mx, My) = 1/M_Rdx + 1/M_Rdy - 1/M_Rd0

Verifica:
  (Mx/M_Rdx)^α + (My/M_Rdy)^α  ≤  1
  α selezionabile: 1.0 (conservativo), 1.5, 2.0 (EC2)
```

### Verifica SLU — NTC2018/EC2

```text
Wrapper di checks_ntc2018:
  - conversione unità (kg·cm → N·mm per EC2)
  - chiamata verifica_pressoflessione_slu(N, Mx, My, sezione, materiali)
  - ritorno risultato normalizzato (dominio di resistenza)
```

### Instabilità biassiale (amplificazione momenti)

```text
Momento amplificato:
  Mx,Ed = Mx · (1 + ω_x · N / N_cr,x)
  My,Ed = My · (1 + ω_y · N / N_cr,y)

N_cr,x = π² · E · I_x / L²  (carico critico di Eulero)
ω_x = f(λ_x) da tabella CNR 10011  (= instabilita.omega_ca)
```

### Dominio 3D N-Mx-My

```text
Generazione:
  Per ogni N_i in [N_min, N_max]:
    calcola curva di interazione M_x(θ), M_y(θ) per θ in [0, 2π]
  → superficie 3D chiusa

Proiezioni:
  - Piano N-Mx (My=0):  sezione verticale
  - Piano N-My (Mx=0):  sezione verticale
  - Piano Mx-My (N=N_Ed): sezione orizzontale alla quota N_Ed
```

---

## Diagramma dipendenze

```text
Fase J — flusso dati

  src/pressoflessione/
  ├── spec.py          ─── PressoflessSpec, PressoflessResult, DominioNMy
  ├── omogenizzata.py  ─── calcola_omogenizzata_biassiale(), crea_armatura_rettangolare()
  ├── ta.py            ─── Navier biassiale, Bresler TA (RD2229, DM92, DM96)
  ├── slu.py           ─── wrapper checks_ntc2018 (NTC2018, NTC2008, EC2)
  ├── instabilita.py   ─── amplifica_momenti_biassiale(), riuso omega_ca() da Fase H
  ├── dominio_3d.py    ─── calcola_dominio_3d(), disegna_dominio_3d/2d
  └── dispatcher.py    ─── calcola_pressoflessione_deviata() — routing TA/SLU
         │
         ▼
  src/gui/widgets/
  └── dominio_canvas.py   ─── 3 viste (3D, N-M, Mx-My), slider N_Ed
         │
  Fase K (esteso) ─── aggiunta combo norma, overlay punto di lavoro
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase I — `src/sections/omogenizzata.py` | Sezione omogeneizzata biassiale (I_x, I_y, A_omog) |
| Fase F — `src/methods/ntc2018/checks.py` | Backend SLU per J.4 |
| Fase H — `src/methods/rd2229/instabilita.py` | `omega_ca()` per amplificazione momenti |
| Fase A — `src/materials/` | f_ck, f_yk, σ_adm per verifica |
| Fase K — `src/gui/widgets/dominio_canvas.py` | Widget dominio — esteso in Fase K |

---

## Riferimenti normativi

| Norma | Articolo | Contenuto |
| --- | --- | --- |
| RD 2229/1939 | §39-50 | Pressoflessione TA, Navier |
| DM 09/01/1996 | §5.3 | Pressoflessione DM96 |
| NTC2018 | §4.1.2.2 | Pressoflessione SLU biassiale |
| EC2 EN 1992-1-1 | §5.8.9 | Interazione biassiale, α = 1.0÷2.0 |
| EC2 EN 1992-1-1 | §5.8.8 | Analisi del secondo ordine (momenti amplificati) |
| Bresler (1960) | — | Formula interazione biassiale TA |
| CNR 10011/1985 | Tab. 9 | ω_ca per instabilità biassiale |

---

## Struttura file

```text
src/pressoflessione/
├── __init__.py
├── spec.py           # J.2 — PressoflessSpec, PressoflessResult, DominioNMy
├── omogenizzata.py   # J.2 — calcola_omogenizzata_biassiale, crea_armatura_rettangolare
├── ta.py             # J.3 — Navier biassiale, Bresler TA
├── slu.py            # J.4 — wrapper NTC2018/EC2
├── instabilita.py    # J.6 — amplifica_momenti_biassiale, omega_ca
├── dominio_3d.py     # J.5 — dominio 3D e proiezioni 2D
└── dispatcher.py     # J.7 — calcola_pressoflessione_deviata

src/gui/widgets/
└── dominio_canvas.py  # J.8 — QWidget 3 viste + slider (esteso in Fase K)
```

---

## Subfasi, checklist e storico

### J.1 — Refactoring BarraArmatura

**Stato**: ✅ COMPLETATO — commit `73482f0`

- [x] Aggiunta coordinata `x` a `BarraArmatura` (Fase B/I usano solo `y`)
- [x] Retrocompatibilità: `x` default a 0

### J.2 — Tipi e sezione omogeneizzata biassiale

**Stato**: ✅ COMPLETATO

- [x] `PressoflessSpec`, `PressoflessResult`, `DominioNMy`
- [x] `calcola_omogenizzata_biassiale()`, `crea_armatura_rettangolare()`

### J.3 — Verifica TA calcestruzzo

**Stato**: ✅ COMPLETATO

- [x] Sovrapposizione elastica (Navier), Bresler TA, α selezionabile
- [x] Norme: RD2229, DM92, DM96

### J.4 — Verifica SLU

**Stato**: ✅ COMPLETATO

- [x] Wrapper `checks_ntc2018`, conversione unità
- [x] Norme: NTC2018, NTC2008, EC2

### J.5 — Dominio 3D N-Mx-My

**Stato**: ✅ COMPLETATO

- [x] `calcola_dominio_3d()`, `disegna_dominio_3d()`, `disegna_dominio_2d_mxmy()`, `disegna_dominio_2d_nm()`

### J.6 — Instabilità biassiale

**Stato**: ✅ COMPLETATO

- [x] `amplifica_momenti_biassiale()`, riuso `omega_ca()` da `instabilita.py`

### J.7 — Dispatcher multinorma

**Stato**: ✅ COMPLETATO

- [x] `calcola_pressoflessione_deviata()` — routing TA/SLU, amplificazione integrata

### J.8 — Widget Qt dominio

**Stato**: ✅ COMPLETATO

- [x] `dominio_canvas.py` — 3 viste (3D, N-M, Mx-My), slider interattivi N_Ed

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Navier per TA (non iterativo) | Sufficiente per fase 1 (sezione integra); per fessurata usare iterativo (futuro) |
| Bresler con α configurabile | EC2 prescrive α = 1÷2 in funzione di N/N_Rd; utente può sovrascrivere |
| Wrapper SLU (non reimplementazione) | Evita duplicazione; `checks_ntc2018` è già testato e aggiornato |
| Dominio 3D generato proceduralmente | Nessun dato precalcolato; ricalcolo ad ogni cambio materiale/geometria |
| `dominio_canvas.py` preesistente esteso (non nuovo) | Fase K aggiunge overlay punto di lavoro e combo norma mantenendo retrocompatibilità |

---

## Bug corretti

| Bug | Causa | Fix |
| --- | --- | --- |
| Dominio 3D non chiuso ai poli | N_max e N_min generavano ellissi degeneri | Clamp N a ±0.99·N_cr |
| Bresler α=2 fuori dominio TA | Formula non converge per α>1.5 con Bresler originale | Uso formula di interazione generalizzata |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| J.2 Tipo armatura | Rettangolare simmetrica (4 barre agli angoli, distribuita) | `crea_armatura_rettangolare(n_barre, phi, copriferro)` |
| J.3 Metodo TA | Navier + Bresler (non iterativo parzializzata) | Sezione integra; fessurata rinviata |
| J.5 Viste dominio | 3D + 2 proiezioni (N-M e Mx-My) | 3 viste nel widget Qt |
| J.8 Slider interattivi | N_Ed come slider per proiezione Mx-My | `QSlider` con aggiornamento in tempo reale |

---

## Note storiche/archivio

- `dominio_canvas.py` è stato prima creato in Fase J (J.8) poi esteso in Fase K (overlay punto di lavoro, combo norma, export PNG/SVG)
- L'amplificazione momenti (J.6) riusa `omega_ca()` da `src/methods/rd2229/instabilita.py` — stessa funzione usata anche per verifiche acciaio (Fasi D, G)
- `BarraArmatura` con coordinate x aggiunto in J.1 era necessario per il calcolo biassiale; le fasi precedenti (B, I) usano solo y (flessione retta)
