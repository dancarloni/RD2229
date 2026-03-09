# Fase G — Acciaio: Verifiche Strutturali

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | corrente |
| Data completamento | 2026-03-09 |
| Test totali | `tests/test_acciaio.py` |
| File principali | `src/steel/verifiche_ta.py`, `src/methods/rd2229/instabilita.py` |

---

## Descrizione

La Fase G implementa le **verifiche strutturali per elementi in acciaio** secondo le Tensioni Ammissibili (CNR 10011, RD2229) e gli stati limite (EC3, NTC2018 §4.2). Copre flessione, taglio, instabilità, pressoflessione e la verifica combinata di Von Mises, coprendo le principali tipologie di profili laminati a caldo (IPE, HEA/B/M, UPN) e a caldo.

**Nota**: le verifiche TA per profilo singolo e traliccio sono già state implementate nella Fase D (cordoli). La Fase G estende queste verifiche alle strutture in acciaio in generale (telai, colonne, travi), con routing multinorma (TA + SLU EC3).

---

## Teoria e formule chiave

### Flessione (TA — CNR 10011)

```text
σ = M / W_x  ≤  σ_adm

σ_adm acciaio Fe360: 1600 kg/cm²  (CNR 10011)
σ_adm acciaio Fe430: 1800 kg/cm²
σ_adm acciaio Fe510: 2200 kg/cm²
```

### Taglio (TA)

```text
τ = V / A_anima  ≤  τ_adm
τ_adm = σ_adm / √3  ≈  0.577 · σ_adm
A_anima = h_w · t_w
```

### Instabilità (TA — CNR 10011 Tab. 9)

```text
Snellezza:    λ = L_lib / i_min,  i_min = √(I_min / A)
Coefficiente: ω = f(λ)  (interpolazione da Tab. 9 CNR 10011)
Verifica:     σ_inst = ω · N / A  ≤  σ_adm
```

### Pressoflessione (TA)

```text
σ = N/A + Mx/Wx + My/Wy  ≤  σ_adm
con amplificazione momenti per instabilità biassiale (Fase J)
```

### Von Mises (combinata)

```text
σ_VM = √(σ_x² - σ_x·σ_y + σ_y² + 3·τ²)  ≤  σ_adm
caso comune (σ_y ≈ 0):  σ_VM = √(σ² + 3τ²)
```

### Classificazione sezione (EC3 — SLU)

```text
Classe 1: c/t ≤ 9ε  (piena duttilità plastica)
Classe 2: c/t ≤ 10ε (plastico, rotazione limitata)
Classe 3: c/t ≤ 14ε (elastico, senza instabilità locale)
Classe 4: c/t > 14ε  (sezione snella — instabilità locale)
ε = √(235 / f_y)   [con f_y in MPa]
```

---

## Diagramma dipendenze

```text
Fase G — flusso dati

  data/steel/sagomario_en10365.json   (da Fase D)
         │
         ▼
  src/steel/
  ├── sagomario.py          ─── profili e proprietà (da Fase D)
  ├── verifiche_ta.py       ─── flessione, taglio, instabilità, Von Mises (da Fase D)
  └── verifiche_ec3.py      ─── classificazione sezione, M_Rd, V_Rd EC3 (Fase G)
         │
  src/methods/rd2229/
  └── instabilita.py        ─── tabella ω CNR 10011 (Tab. 9)
         │
         ▼
  src/core/normative_registry.py  ─── routing TA / EC3
         │
         ▼
  Fase L (telai Cross-Pozzati) ─── usa verifiche G per travi/colonne acciaio
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase D — `src/steel/` | Sagomario, verifiche TA base (condivise) |
| Fase A — `src/materials/` | f_y, f_u, E_s per profili acciaio |
| Fase L — telai piani | Usa G per verifiche elementi telaio metallico |
| `src/report/tabulato.py` | Tabulato calcolo con passaggi intermedi |

---

## Riferimenti normativi

| Norma | Articolo/Tabella | Contenuto |
| --- | --- | --- |
| CNR 10011/1985 | §4.2, Tab. 9 | σ_adm, τ_adm, ω instabilità |
| RD 2229/1939 | §66-72 | Strutture metalliche TA |
| NTC2018 | §4.2 | Verifiche SLU acciaio |
| EC3 EN 1993-1-1 | §5.5, §6.2, §6.3 | Classificazione sezione, M_Rd, N_Rd, instabilità |
| EC3 EN 1993-1-8 | — | Connessioni (integra Fase D.5) |

---

## Struttura file

```text
src/steel/
├── sagomario.py          # profili laminati — condiviso con Fase D
├── verifiche_ta.py       # verifiche TA — condiviso con Fase D
└── verifiche_ec3.py      # classificazione sezione + verifiche EC3 SLU

src/methods/rd2229/
└── instabilita.py        # tabella ω CNR 10011

tests/
└── test_acciaio.py       # verifiche G (flessione, taglio, instabilità, Von Mises, EC3)
```

---

## Subfasi, checklist e storico

### G.1 — Verifiche acciaio (TA + EC3)

**Stato**: ✅ COMPLETATO

- [x] Flessione (σ = M/W ≤ σ_adm, M_Rd EC3)
- [x] Taglio (τ = V/A_anima ≤ τ_adm, V_Rd EC3)
- [x] Instabilità (ω CNR 10011, curve di instabilità EC3)
- [x] Pressoflessione (N + Mx + My, interazione EC3)
- [x] Von Mises (√(σ² + 3τ²))
- [x] Classificazione sezione EC3 (Classi 1-4)
- [x] Test: `tests/test_acciaio.py`

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Fase G estende Fase D (non duplica) | Le verifiche TA sono già in `src/steel/verifiche_ta.py` |
| `verifiche_ec3.py` separato | Logica EC3 distinta, future evoluzioni indipendenti |
| Routing via `normative_registry.py` | Selezione norma trasparente per GUI e report |
| Instabilità ω in `methods/rd2229/instabilita.py` | Condiviso con pressoflessione (Fase J) e cordoli (Fase D) |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| G.1 Norme da coprire | TA (CNR 10011) + EC3 | Due moduli separati, routing via registry |
| G.1 Classificazione EC3 | Sì, classi 1-4 | `classificazione_sezione(profilo, f_y)` in `verifiche_ec3.py` |

---

## Note storiche/archivio

- Le verifiche TA per cordoli metallici (Fase D) e verifiche generali acciaio (Fase G) condividono `src/steel/verifiche_ta.py`
- La Fase G è complementare alla Fase D: D si occupa di cordoli e tralicci, G estende alle strutture in acciaio generali
- EC8 per strutture in acciaio sismiche (duttilità, fattore q) rinviato a Fase S (multinorma avanzata)
