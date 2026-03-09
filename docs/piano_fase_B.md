# Fase B — Sezioni e Geometrie

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | `bdd8c6a` |
| **Data completamento** | 2026-03-07 |
| **Test aggiunti** | ~30 |
| **Norma/e di riferimento** | Norma-agnostica (geometria pura) |

---

## Descrizione

Implementa il sistema completo di gestione delle **sezioni trasversali** per tutti gli elementi strutturali. Copre 12 tipi di sezione con calcolo automatico di tutti i parametri geometrici statici e torsionali. Include un editor grafico Qt con QPainter custom per la visualizzazione live.

---

## Teoria e fondamenti strutturali

### Proprietà geometriche delle sezioni

**Sezione rettangolare** (b×h):

```text
A = b·h
I_x = b·h³/12        W_x = b·h²/6
I_y = h·b³/12        W_y = h·b²/6
J_t ≈ k·b·h³         (k da tabella in funzione di h/b)
```

**Sezione T** (b_f, t_f, b_w, h_w):

```text
Centroide: y_G = (b_f·t_f·y_f + b_w·h_w·y_w) / A_tot
I_x = I_flangia + I_anima  (teorema di Steiner: I_i + A_i·d_i²)
W_x,sup = I_x / (h - y_G)
W_x,inf = I_x / y_G
```

**Sezione composta con fori** (es. cava):

```text
A_netta = A_lorda - Σ A_fori
I_netta = I_lorda - Σ(I_foro + A_foro·d²)
```

### Parametri torsionali

- **J_t** (momento di inerzia torsionale): per sezioni a parete sottile aperta: `J_t ≈ (1/3)·Σ(b_i·t_i³)`; per sezioni chiuse: formula di Bredt `J_t = 4·A_m²/∮(ds/t)`
- **C_w** (costante di gauchissement/warping): `C_w = ∫ ω²·dA` dove ω è la funzione di settore; per profilo I: `C_w = (b_f³·t_f/12)·h_w²/4·(1/(1+b_f·t_f/(b_w·t_w)))`
- **x_s, y_s** (centro di taglio): per sezioni con asse di simmetria il centro di taglio coincide con il baricentro; per sezioni aperte asimmetriche: `x_s = Σ(S_i·s_i)/I_y` dove S_i è il momento statico della i-esima parete

### Modulo di resistenza plastico (SLU)

```text
Z_x = ∫|y|·dA  =  A/2·(y_c_sup + y_c_inf)   [solo per SLU NTC2018]
Z_x ≥ W_x per qualsiasi sezione
```

---

## Diagramma dipendenze subfasi

```text
B.1 — Database sezioni (12 dataclass + torsion_params)
 └── B.2 — Editor Qt sezioni
           ├── sezione_canvas.py (QPainter)
           ├── input_parametri.py
           └── section_repository.py (JSON persistence)
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo in Fase B |
| --- | --- | --- |
| `src/materials/material_repository.py` | Repository materiali | Associazione sezione ↔ materiale per verifiche |
| `src/core/unita_misura.py` | Sistema unità | Display proprietà in cm vs mm |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| **Timoshenko**, "Mechanics of Materials" | Formule I_x, I_y, W, Z per tutte le sezioni |
| **Pilkey**, "Analysis and Design of Elastic Beams" | Parametri torsionali J_t, C_w, centro di taglio |
| **CNR 10011** Tab.1 | J_t per sezioni rettangolari (coefficiente k) |
| **EN 1993-1-1** §6.2.5 | Classificazione sezioni, Z_x plastico |

---

## Struttura file/directory

```text
src/sections/
├── section_types.py      (~400 righe — 12 dataclass sezione)
├── torsion_params.py     (~200 righe — J_t, C_w, centro taglio)
├── section_repository.py (~150 righe — CRUD + JSON persistence)
└── section_validator.py  (~100 righe — range fisici, consistenza)

src/ui/qt/
└── sezione_canvas.py     (~300 righe — QPainter + tabella proprietà)

data/sections/
└── sezioni_standard.json (~100 righe — sezioni predefinite editabili)

tests/
├── test_sezioni.py            (~200 righe)
└── test_editor_sezioni.py     (~100 righe)
```

---

## Subfasi, checklist e storico

### B.1 — Database sezioni (12 tipi)

**Stato**: COMPLETATO — commit `bdd8c6a`

- [x] `RettangolareSezione` — b, h; A, Ix, Iy, Wx, Wy, J_t
- [x] `TSezione` — b_f, t_f, b_w, h_w; centroide, Ix asimmetrico, Wx sup/inf
- [x] `LSezione` — b, t_f, h, t_w; centroide, Ix/Iy, centro taglio
- [x] `CSezione` — analogo L con anima su entrambi i lati
- [x] `ISezione` — simmetrica doppia; J_t da somma tre parti
- [x] `USezione` — U rovescia (prefabbricati)
- [x] `CircolareSezione` — D; A = π·D²/4; I = π·D⁴/64; J_t = π·D⁴/32
- [x] `EllitticaSezione` — a, b; A = π·a·b; I_x = π·a·b³/4
- [x] `TrapeziaSezione` — b_sup, b_inf, h; centroide, Ix
- [x] `PoligonaleSezione` — lista vertici (x,y); A e I via formula Shoelace + Steiner
- [x] `CavaSezione` — sezione esterna - sezione interna (entrambe rettangolari o circolari)
- [x] `MistaSezione` — composizione arbitraria di sotto-sezioni rettangolari
- [x] Parametri torsionali: `J_t`, `C_w`, `x_s`, `y_s` per tutti i tipi implementati
- [x] `sezioni_standard.json` con sezioni predefinite IPE-like per c.a.
- [x] Test: `tests/test_sezioni.py` — proprietà verificate vs valori analitici noti

**Dipendenze**: nessuna (base del progetto)

---

### B.2 — Editor Qt sezioni

**Stato**: COMPLETATO — commit `bdd8c6a`

- [x] `sezione_canvas.py` — `SezionCanvas(QWidget)` con QPainter custom: disegno sezione, centroide, assi principali, colori differenziati per flangia/anima/fori
- [x] Input parametri: form dinamico con campi per il tipo di sezione selezionato (QComboBox tipo + QFormLayout parametri)
- [x] Calcolo automatico: aggiornamento live di A, Ix, Iy, Wx, Wy, J_t, C_w al cambio di ogni parametro
- [x] Salvataggio/lettura JSON: `section_repository.py` con CRUD completo su `data/sections/sezioni_standard.json`
- [x] Test: `tests/test_editor_sezioni.py` — logica calcolo (senza Qt)

**Dipendenze**: B.1

---

## File creati/modificati

| File | Righe | Descrizione |
| --- | --- | --- |
| `src/sections/section_types.py` | ~400 | 12 dataclass sezione con `calcola()` |
| `src/sections/torsion_params.py` | ~200 | J_t, C_w, centro di taglio |
| `src/sections/section_repository.py` | ~150 | CRUD + JSON persistence |
| `src/sections/section_validator.py` | ~100 | Validazione range fisici |
| `src/ui/qt/sezione_canvas.py` | ~300 | QPainter + tabella proprietà |
| `data/sections/sezioni_standard.json` | ~100 | Sezioni predefinite |
| `tests/test_sezioni.py` | ~200 | Test proprietà geometriche |
| `tests/test_editor_sezioni.py` | ~100 | Test logica editor |

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| 12 dataclass distinte (non gerarchia) | Ogni tipo ha parametri diversi; dataclass è più esplicita e mypy-friendly |
| `torsion_params.py` separato da `section_types.py` | Parametri torsionali non servono a tutte le verifiche (es. non per compressione pura) |
| JSON per sezioni standard | Editabili dall'utente senza ricompilazione; schema versionato |
| QPainter custom (non libreria grafica) | Controllo totale sul rendering; nessuna dipendenza aggiuntiva |
| Calcolo live (non on-demand) | Feedback immediato per l'utente che modifica i parametri |

---

## Bug corretti durante lo sviluppo

| Bug | File | Descrizione |
| --- | --- | --- |
| Centroide sezione T asimmetrica | `section_types.py` | Formula centroide usava altezza totale invece di altezze parziali; corretto con formula pesata per aree |
| Centro di taglio sezione L | `torsion_params.py` | x_s calcolato rispetto all'asse sbagliato (corpo vs flangia); corretto con formula di Bredt |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-07

Implementazione autonoma da specifiche — nessun Q&A esplicito. Decisioni operative:

| Decisione | Motivazione |
| --- | --- |
| 12 tipi coperti (non solo rettangolare+T) | Copertura completa del patrimonio edilizio italiano (travi prefabbricate, pilastri circolari, scale metalliche) |
| Parametri torsionali subito (non solo in Fase I) | Richiesti già da Fase D per cordolo reticolare e Fase G per acciaio |
| sezione_canvas.py in Qt (non matplotlib) | Responsività nel widget Qt live — matplotlib troppo lento per aggiornamento a ogni keystroke |

---

## Note storiche/archivio

Il calcolo dei parametri torsionali per sezioni aperte (C_w, centro di taglio) è storicamente trascurato nei testi italiani classici, che si concentrano sulla torsione uniforme (Saint-Venant). La torsione non uniforme (gauchissement) è invece critica per travi in acciaio a parete sottile e profili aperti come C e U, dove il centro di taglio è significativamente spostato rispetto al baricentro. La Fase B copre entrambi gli aspetti per completezza.
