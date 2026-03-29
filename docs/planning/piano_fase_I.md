# Fase I — Sezioni: Parametri Statici Completi

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | `3bed1a7` (I.1), corrente (I.2–I.5) |
| Data completamento | 2026-03-09 |
| Test totali | 91 (I.1) + 27 (I.3) + ulteriori I.4/I.5 |
| File principali | `src/sections/`, `src/gui/widgets/sezione_canvas.py` |

---

## Descrizione

La Fase I implementa il **calcolo completo dei parametri statici delle sezioni in c.a.**, inclusi la sezione omogeneizzata (integra e fessurata), i parametri torsionali (J_t, C_w, x_s, y_s), la sezione composta acciaio-cls e la visualizzazione grafica della sezione.

Questi parametri sono il fondamento condiviso per tutte le verifiche strutturali (Fasi F, J, K):

- n (rapporto moduli) dipende dalla norma selezionata
- I_omog, y_c, y_s usati in verifiche TA flessione (Fase F)
- J_t usato in verifiche torsione (Fase F §4.1.2.4)
- x_s, y_s (centro di taglio) usati in torsione non uniforme (Fase J)

---

## Teoria e formule chiave

### I.1 — Rapporto di omogeneizzazione n

```text
Definizione:
  n = E_s / E_c

Per norma:
  RD2229:  n = 15 (fisso, §36)
  DM92:    n = 15 (fisso)
  DM96:    n = 10 (fisso)
  NTC2008: n = max(E_s/E_c, 7) — E_c = 22000·(f_cm/10)^0.3
  NTC2018: n = max(E_s/E_c, 7) — idem NTC2008
  EC2:     n = E_s / E_cm  (§3.1.3)
```

### I.2 — Sezione omogeneizzata integra

```text
Area omogeneizzata:
  A_omog = A_c + (n-1) · A_s

Asse neutro (dal bordo compresso):
  y_G = [A_c · y_G,c + (n-1) · A_s · y_s_i] / A_omog

Inerzia omogeneizzata:
  I_omog = I_c + A_c·(y_G - y_G,c)² + (n-1)·Σ[A_si·(y_G - y_si)²]

Moduli di resistenza:
  W_c = I_omog / y_G          (bordo compresso)
  W_s = I_omog / (h - y_G)   (bordo teso, all'armatura)
```

### I.2 — Asse neutro fessurato

```text
Equazione di equilibrio (sezione rettangolare):
  b · x² / 2 + (n-1) · A_s' · (x - d') - n · A_s · (d - x) = 0
  Risoluzione: equazione di 2° grado → x_n positivo

I_fess = b·x_n³/3 + (n-1)·A_s'·(x_n - d')² + n·A_s·(d - x_n)²
```

### I.3 — Parametri torsionali

```text
Momento di inerzia torsionale (Bredt — sezione aperta):
  J_t ≈ (1/3) · Σ(b_i · t_i³)   (sezioni aperte sottili)

Momento di inerzia settoriale (warping):
  C_w = ∫ ω² dA   (integrale del settore principale)

Centro di taglio (per sezioni asimmetriche):
  x_s = -∫(y · ω) dA / I_x
  y_s = +∫(x · ω) dA / I_y
  (per sezione a doppia simmetria: x_s = y_s = 0)
```

### I.4 — Sezione composta acciaio-cls

```text
Sezione composta IPE + soletta cls (NTC2018 §4.3):
  n_comp = E_s / E_c_eff  (con E_c_eff ridotto per fluage)

Area equivalente acciaio:
  A_cls_equiv = A_cls / n_comp

Asse neutro composta: identico a I.2 con n_comp

Tensioni SLE:
  σ_cls = M / (n_comp · W_cls,omog)
  σ_s   = M · n_comp / W_s,omog
```

---

## Diagramma dipendenze

```text
Fase I — flusso dati

  src/materials/         (E_s, E_c per norma) ─── Fase A
         │
         ▼
  src/sections/
  ├── omogenizzata.py    ─── I.1/I.2: n, A_omog, y_G, I_omog, x_n_fess
  ├── torsione.py        ─── I.3: J_t, C_w, x_s, y_s
  ├── composta.py        ─── I.4: sezione mista acciaio-cls
  └── disegno.py         ─── I.5: matplotlib + Qt canvas
         │
         ▼
  Fase F — checks.py (TA/SLU) usa I_omog, W_c, W_s
  Fase J — pressoflessione deviata usa I.2 biassiale
  Fase K — grafici usa canvas I.5
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase A — `src/materials/` | E_s, E_c per calcolo n per norma |
| Fase B — `src/sections/` | Geometria sezione (A_c, I_c, y_G,c) |
| Fase F — `src/methods/*/checks.py` | Usa I_omog, W_c, W_s per verifiche TA |
| Fase J — pressoflessione | Usa `calcola_omogenizzata_biassiale()` |
| `src/gui/widgets/sezione_canvas.py` | Widget Qt per visualizzazione I.5 |

---

## Riferimenti normativi

| Norma | Articolo | Contenuto |
| --- | --- | --- |
| RD 2229/1939 | §36 | n = 15 fisso per c.a. |
| NTC2018 | §4.1.2.1.1 | E_cm, n per SLE |
| NTC2018 | §4.1.4 | Sezione fessurata per SLE |
| NTC2018 | §4.3 | Sezioni composte acciaio-cls |
| EC2 EN 1992-1-1 | §3.1.3, §7.4 | E_cm, calcoli deformazione |
| Timoshenko, "Strength of Materials" | — | Parametri torsionali J_t, C_w, centro di taglio |

---

## Struttura file

```text
src/sections/
├── omogenizzata.py     # I.1/I.2 — n, calcola_sezione_omogenizzata, calcola_asse_neutro_fessurato
├── torsione.py         # I.3 — J_t, C_w, x_s, y_s per tutti i tipi sezione
├── composta.py         # I.4 — IPE_TABLE, calcola_sezione_composta, calcola_tensioni_sle_composita
└── disegno.py          # I.5 — disegna_sezione, crea_figura_sezione_sle, salva_figura

src/gui/widgets/
└── sezione_canvas.py   # I.5 — QWidget con matplotlib embed, mostra sezione + armature

tests/
├── test_sezione_omogenizzata.py    # 91 test (I.1/I.2)
└── test_section_torsion.py         # 27 test (I.3)
```

---

## Subfasi, checklist e storico

### I.1 — Rapporto di omogeneizzazione n per norma

**Stato**: ✅ COMPLETATO — commit `3bed1a7`

- [x] n per RD2229, DM92, DM96, NTC2008, NTC2018, EC2
- [x] Opzioni selezionabili, default e override utente
- [x] Test: `tests/test_sezione_omogenizzata.py` (91 test)

### I.2 — Sezione omogeneizzata integra + fessurata

**Stato**: ✅ COMPLETATO

- [x] `calcola_sezione_omogenizzata()` — A_omog, y_G, I_omog, W_c, W_s
- [x] `calcola_asse_neutro_fessurato()` — x_n, I_fess
- [x] Tutti i tipi di sezione (rettangolare, T, L, I, circolare)

### I.3 — Checklist parametri torsionali

**Stato**: ✅ COMPLETATO

- [x] J_t (Bredt per sezioni aperte sottili)
- [x] C_w (momento di inerzia settoriale — warping)
- [x] x_s, y_s (centro di taglio)
- [x] Test: `tests/test_section_torsion.py` (27 test)

### I.4 — Checklist sezione composta acciaio-cls

**Stato**: ✅ COMPLETATO

- [x] `IPE_TABLE` — proprietà profili IPE per sezioni composte
- [x] `calcola_sezione_composta()` — A_equiv, y_G, I_comp
- [x] `calcola_tensioni_sle_composita()` — σ_cls, σ_s SLE

### I.5 — Disegno sezione c.a

**Stato**: ✅ COMPLETATO

- [x] `disegna_sezione()` — matplotlib, barre armatura, etichette
- [x] `crea_figura_sezione_sle()` — diagramma tensioni SLE sovrapposto
- [x] `salva_figura()` — PNG/SVG
- [x] Widget Qt: `sezione_canvas.py`

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| n dipendente da norma (non fisso) | Norme diverse prescrivono n diversi; override utente per casi speciali |
| Sezione fessurata separata da integra | I due stati hanno equazioni e usi distinti (SLE vs TA) |
| J_t approssimazione Bredt sezioni aperte | Sufficiente per c.a.; per sezioni chiuse usare formula esatta |
| `sezione_canvas.py` come QWidget (non finestra) | Embeddabile in pannelli multi-vista (Fase J, K) |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| I.1 Valori n per DM72/DM87 | DM72: n=15, DM87: n=15 (come RD2229) | Stessa logica RD2229 |
| I.3 Centro di taglio per sezioni simmetriche | x_s = y_s = 0 | Calcolo generico ma cortocircuito per simmetria |
| I.5 Output grafico | matplotlib embed in Qt | `FigureCanvasQTAgg` in `sezione_canvas.py` |

---

## Note storiche/archivio

- `test_sezione_omogenizzata.py` con 91 test copre tutti i casi: n per norma, sezioni multiple, armatura compressa, override n
- `C_w` (warping) è complesso per sezioni aperte non simmetriche — implementazione usa metodo dei settori principali
- Fase I è prerequisito fondamentale di Fase F (TA) e Fase J (pressoflessione biassiale)
