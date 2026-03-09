# Fase N — Carote cls in sito

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | `8f52479` (N.1), corrente (N.2–N.11) |
| Data completamento | 2026-03-09 |
| Test totali | 70 (`test_carote.py`) |
| File principali | `src/carote/`, `src/gui/widgets/carote_canvas.py` |

---

## Descrizione

La Fase N implementa il **modulo di analisi delle carote di calcestruzzo in sito** (prove distruttive su campioni estratti da strutture esistenti). Copre:

- 10 formulazioni di conversione resistenza carota → resistenza cilindrica/cubica
- Statistiche NTC2018 e EN 13791 per valutazione in opera
- Test di outlier (Grubbs, Chauvenet) e classificazione calcestruzzo
- Pipeline completa da input grezzo a parametri derivati (f_cm, E_cm, f_ctm, Rck, σ_c_adm)
- Integrazione con il catalogo materiali (Fase A) via `registra_materiale_in_situ()`
- Report HTML, export JSON/CSV, 4 grafici matplotlib, widget Qt 4 viste

---

## Teoria e formule chiave

### N.2 — Formulazioni di conversione

```text
Resistenza di riferimento della carota:
  f_core = F_rot / A_carota         [N/mm²]

Fattori di correzione EN 12504-1:
  f_core_corr = f_core · k_d · k_h · k_dir · k_diam

dove:
  k_d    = fattore diametro (1.0 per d=100mm, riduzione per d<100mm)
  k_h    = fattore snellezza h/d (1.0 per h/d=2.0)
  k_dir  = fattore direzione carotaggio (0.92 per perpendicolare alla gettata)
  k_diam = fattore diametro aggregato

10 formulazioni (esempi principali):
  BS1881:   f_c = 1.25 · f_core_corr                     (britannica)
  ACI214:   f_c = f_core / (0.92 · k_dir)                (americana)
  NTC2018:  f_c = f_core_corr / 0.85                     (italiana, Circ. n.7 §C8.2)
  EN13791:  f_ck = min(f_m - k·s, f_is,min + 4)          (europea)
  RILEM:    f_c = f_core_corr · α_m                      (α_m da tabella)
  Masi:     f_c = f_core · (1 + k_0 · (h/d - 1))        (ricerca italiana)
```

### N.3 — Statistiche NTC2018

```text
Valore caratteristico resistenza in opera (NTC2018 Circ. n.7 §C8.2):
  f_cm = media aritmetica campioni corretti
  COV = s / f_cm  (coefficiente di variazione)

  f_ck,is = f_cm · (1 - 1.645 · COV)   (distribuzione normale)

EN 13791 — Metodo A (n ≥ 15 provini):
  f_ck,is = min(f_m(n) - k₁·s, f_is,lowest + 4 MPa)
  k₁ = 1.48 per n ≥ 15

EN 13791 — Metodo B (n < 15 provini):
  f_ck,is = f_m(n) - k₂
  k₂ = 5 per n = 3..14

Test outlier Grubbs (α = 5%):
  G = |x_i - x̄| / s  >  G_crit(n, α)  → outlier
```

### N.4 — Parametri derivati

```text
Da f_cm (NTC2018/EC2):
  E_cm = 22000 · (f_cm / 10)^0.3        [MPa]
  f_ctm = 0.30 · f_ck^(2/3)             (per f_ck ≤ 50 MPa)
  f_ctm = 2.12 · ln(1 + f_cm/10)        (per f_ck > 50 MPa)
  Rck = f_ck / 0.83                      [N/mm², cubica italiana]

Tensione ammissibile storica (RD2229/TA):
  σ_c_adm = f_cm / (γ_m · FS)           (con FS = 2.5..3.0)
```

---

## Diagramma dipendenze

```text
Fase N — flusso dati

  Input: lista carotature {d, h, F_rot, quota, data, ...}
         │
         ▼
  src/carote/core_sample.py    ─── N.1: CoreSample, CorrectionFactors, ConversionResult
         │
         ▼
  src/carote/formulazioni.py   ─── N.2: 10 formulazioni + engine custom 3 livelli
         │
         ▼
  src/carote/statistiche.py    ─── N.3: NTC2018, EN13791 A/B, Grubbs, Chauvenet
         │
         ▼
  src/carote/parametri.py      ─── N.4: f_cm, E_cm, f_ctm, Rck, sigma_c_adm
         │
         ▼
  src/carote/pipeline.py       ─── N.5: CoreAnalysisResult, pipeline(list[CoreSample])
         │
    ┌────┴────┐
    ▼         ▼
  Fase A    src/carote/
  materials  ├── report.py     ─── N.7: HTML, JSON, CSV
  (N.6)      └── plots.py      ─── N.8: 4 grafici matplotlib headless

  src/gui/widgets/
  └── carote_canvas.py         ─── N.10: 4 viste Qt, combo formulazione
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase A — `src/materials/` | `registra_materiale_in_situ()` — aggiunge materiale da carote al catalogo |
| Fase F — `src/methods/*/checks.py` | Usa f_ck, E_cm derivati da carote |
| `src/report/tabulato.py` | Report HTML integrato con TabulatoCalcolo |

---

## Riferimenti normativi

| Norma | Articolo | Contenuto |
| --- | --- | --- |
| NTC2018 | Circ. n.7 §C8.2.1 | Resistenza in opera da carote, f_ck,is |
| EN 12504-1:2019 | — | Estrazione e prova di carote: fattori k_d, k_h, k_dir |
| EN 13791:2019 | §6, §7 | Metodo A (n≥15) e Metodo B (n<15) |
| ACI 214.4R-10 | — | Formulazione ACI per conversione carota → cilindro |
| BS 1881-120 | — | Formulazione britannica |
| RILEM TC 43-CND | — | Formulazione RILEM |
| Masi et al. (2011) | — | Formulazione adattata per edifici italiani esistenti |

---

## Struttura file

```text
src/carote/
├── __init__.py
├── core_sample.py     # N.1 — CoreSample, CorrectionFactors, ConversionResult
├── formulazioni.py    # N.2 — 10 formulazioni + engine custom 3 livelli
├── statistiche.py     # N.3 — NTC2018, EN13791 A/B, Grubbs, Chauvenet
├── parametri.py       # N.4 — f_cm, E_cm, f_ctm, Rck, sigma_c_adm
├── pipeline.py        # N.5 — CoreAnalysisResult, pipeline()
├── integrazione.py    # N.6 — LC/FC bridge, registra_materiale_in_situ()
├── report.py          # N.7 — HTML report, JSON/CSV export
└── plots.py           # N.8 — 4 grafici matplotlib headless

src/gui/widgets/
└── carote_canvas.py   # N.10 — QWidget 4 viste, combo formulazione

tests/
└── test_carote.py     # 70 test (N.1–N.9)
```

---

## Subfasi, checklist e storico

### N.1 — CoreSample, CorrectionFactors, ConversionResult

**Stato**: ✅ COMPLETATO — commit `8f52479`

- [x] `core_sample.py`: dataclass principali

### N.2 — Checklist formulazioni di conversione

**Stato**: ✅ COMPLETATO

- [x] 10 formulazioni: BS1881, ACI214, TR11, RILEM, Masi, Fiore, NTC2018, EN13791, Giacchetti, custom
- [x] Engine custom 3 livelli (base, corretto, statistico)

### N.3 — Statistiche

**Stato**: ✅ COMPLETATO

- [x] NTC2018, EN 13791 Metodo A/B, Grubbs, Chauvenet, classificazione calcestruzzo

### N.4 — Checklist parametri derivati

**Stato**: ✅ COMPLETATO

- [x] f_cm, E_cm, f_ctm, Rck, sigma_c_adm storica

### N.5 — Analisi pipeline

**Stato**: ✅ COMPLETATO

- [x] `CoreAnalysisResult`, `pipeline(list[CoreSample])`

### N.6 — Integrazione materiali

**Stato**: ✅ COMPLETATO

- [x] LC/FC bridge, `registra_materiale_in_situ()`

### N.7 — Report

**Stato**: ✅ COMPLETATO

- [x] HTML report, JSON/CSV export

### N.8 — Grafici

**Stato**: ✅ COMPLETATO

- [x] 4 grafici matplotlib headless (distribuzione, Gauss, box-plot, confronto formulazioni)

### N.9 — Test

**Stato**: ✅ COMPLETATO

- [x] `test_carote.py` (70 test)

### N.10 — Widget Qt

**Stato**: ✅ COMPLETATO

- [x] `carote_canvas.py`: 4 viste, combo formulazione

### N.11 — Aggiornamento documentazione

**Stato**: ✅ COMPLETATO

- [x] `PIANO_LAVORO.md`, `PIANO_SVILUPPO_CORRENTE.md`, `memory/`

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| 10 formulazioni come funzioni separate (non classe) | Selezione a runtime via dict, aggiunta nuova formulazione senza refactoring |
| Engine custom 3 livelli | Livello 1: solo carota grezza; 2: con fattori correzione; 3: con statistica |
| `registra_materiale_in_situ()` in Fase N | Fase A gestisce catalogo; N aggiunge bridge specifico per in-situ |
| 4 grafici headless (no Qt in `plots.py`) | Test senza display; rendering in widget Qt separato |
| Outlier test doppio (Grubbs + Chauvenet) | Grubbs: standard EN/NTC; Chauvenet: alternativa per piccoli campioni |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| N.2 Quante formulazioni | 10 (tutte le principali + custom) | Engine custom a 3 livelli |
| N.3 Quale statistica | NTC2018 + EN13791 A+B + outlier | Tutte implementate, selezione via parametro |
| N.6 Bridge materiali | LC/FC coefficienti + registrazione catalogo | `registra_materiale_in_situ()` in integrazione.py |
| N.10 GUI | Widget Qt 4 viste con combo formulazione | `carote_canvas.py` QWidget embeddabile |

---

## Note storiche/archivio

- `tests/test_carote.py` originalmente falliva con `ModuleNotFoundError: No module named 'scipy'` — scipy non era installato nell'ambiente di test. Poi risolto con install scipy o skip selettivo
- Il "Livello 3" dell'engine custom include anche l'analisi statistica degli outlier prima di calcolare f_cm
- Giacchetti (2021) è una formulazione empirica specifica per edifici italiani anni '50-'70 con cls di bassa qualità
