# Fase O — Griglia Sismica INGV + Spettro NTC2018

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | `d6e589a` (O.3), corrente (O.1/O.2) — 2026-03-09 |
| Data completamento | 2026-03-09 |
| Test totali | 47 (test_spettro_ntc2018) + 38 (test_ingv_hazard_csv) + 54 (test_azioni_sismiche_multinorma) |
| File principali | `src/seismic/ingv_hazard.py`, `src/seismic/spettro_ntc2018.py`, `data/seismic/griglia_ingv.csv` |

---

## Descrizione

La Fase O implementa la **pericolosità sismica di sito** e il **calcolo dello spettro di risposta NTC2018** per qualsiasi posizione geografica italiana. Copre:

- **O.1** Import dati griglia INGV: webservice online + fallback CSV locale (10.751 punti WGS84)
- **O.2** Spettro elastico e di progetto NTC2018: curva completa Sa(T) con tutti i 4 rami
- **O.3** Azioni sismiche multinorma: 7 norme, taglio alla base, dispatcher

Questo modulo è il backend sismico condiviso da Fase E (cinematica muratura), Fase L (telai), Fase R (vulnerabilità globale) e Fase S (verifiche multinorma avanzate).

---

## Teoria e formule chiave

### O.1 — Parametri di pericolosità INGV

```text
Griglia INGV NTC2018 Allegato B:
  ~10.751 punti irregolari in WGS84 (lat, lon)
  TR disponibili: [30, 50, 72, 101, 140, 201, 475, 975, 2475] anni

Per ogni TR: ag [m/s²], F0 [-], TC* [s]
  ag_g = ag_TR / 9.81  (conversione g)

Interpolazione spaziale: nearest-neighbor (griglia irregolare)
  → punto più vicino in senso euclideo su lat/lon

Interpolazione TR: log-lineare (NTC2018 §3.2.1):
  P(TR) = 1 - exp(-VR/TR)
  Tra TR_1 e TR_2: log(ag) interpolato linearmente in log(TR)
```

### O.2 — Spettro elastico NTC2018 (4 rami)

```text
Parametri di input:
  ag [g], F0 [-], TC* [s]   (da INGV per TR dato)
  Categoria suolo: A, B, C, D, E
  Categoria topografica: T1, T2, T3, T4
  Classe d'uso: I, II, III, IV

Amplificazioni:
  SS = calcola_SS(suolo, ag, F0)     (amplificazione stratigrafica)
  ST = calcola_ST(topografia, ag)    (amplificazione topografica)
  S  = SS · ST

Periodi caratteristici:
  TB = TC / 3
  TC = CC · TC*   (CC da Tab. 3.2.V NTC2018 per categoria suolo)
  TD = max(4·ag/g + 1.6, 2.0)

Curva Sa(T) — 4 rami:
  T ∈ [0,  TB]:  Sa = ag·S·F0·(1 + T/TB·(η·F0 - 1))
  T ∈ [TB, TC]:  Sa = ag·S·η·F0
  T ∈ [TC, TD]:  Sa = ag·S·η·F0·(TC/T)
  T ∈ [TD, ∞]:  Sa = ag·S·η·F0·(TC·TD/T²)

η = smorzamento:  η = √(10/(5+ξ)) ≥ 0.55  (ξ in %)

Spettro di progetto (q > 1):
  Sd(T) = Sa(T) / q   per T ≥ TB  (semplificato)
```

### O.3 — Azioni sismiche multinorma

```text
Taglio alla base:
  Fb = Sd(T1) · W · λ

  dove T1 = periodo fondamentale (stima empirica o da analisi modale)
  λ = 0.85 se n ≥ 3 piani e T1 < 2·TC, altrimenti 1.0

Distribuzione per piano (distribuzione lineare NTC2018 §7.3.3.2):
  Fi = Fb · zi·Wi / Σ(zj·Wj)

7 norme coperte:
  RD2229, DM96, OPCM3274, NTC2008, NTC2018, EC8, NTC2018+Circ
```

---

## Diagramma dipendenze

```text
Fase O — flusso dati

  data/seismic/griglia_ingv.csv   (10.751 punti, ~15 MB)
         │
         ▼
  src/seismic/ingv_hazard.py      ─── O.1
  ├── carica_griglia_csv()        ← offline fallback
  ├── query_webservice_ingv()     ← online (lat, lon → row INGV)
  └── parametri_hazard(lat, lon, TR) → HazardRow(ag, F0, TC_star)
         │
         ▼
  src/seismic/spettro_ntc2018.py  ─── O.2
  ├── calcola_VR(), calcola_CC()
  ├── calcola_SS(), calcola_ST(), calcola_alpha_S()
  ├── calcola_periodi() → (TB, TC, TD)
  ├── spettro_elastico(T) → Sa
  ├── spettro_progetto(T, q) → Sd
  └── profilo_spettrale_completo() → [(T, Sa), ...] — curva completa 4 rami
         │
         ▼
  src/seismic/azioni_sismiche.py  ─── O.3
  └── dispatcher multinorma → taglio_alla_base, distribuzione_per_piano

Utilizzato da:
  Fase E — cinematica muratura (a_g, S, Se per verifica a terra/quota)
  Fase L — telai Cross-Pozzati (T1, Fb)
  Fase R — vulnerabilità globale (spettro di capacità vs domanda)
  Fase S — verifiche multinorma avanzate
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase E — `src/methods/muratura/cinematica.py` | Usa a_g, S, Se per verifica cinematica lineare/non lineare |
| Fase L — `src/telai/cross_pozzati.py` | Usa T1, Fb per distribuzione forze sismiche |
| Fase R — vulnerabilità | Usa `profilo_spettrale_completo()` per curva di domanda |
| `data/seismic/griglia_ingv.csv` | File dati INGV NTC2018 Allegato B (spettri2008.csv rinominato) |

---

## Riferimenti normativi

| Norma | Articolo/Tab | Contenuto |
| --- | --- | --- |
| NTC2018 | §3.2.1 | Pericolosità sismica, interpolazione TR log-lineare |
| NTC2018 | Tab. 3.2.V | Coefficiente CC per categoria suolo |
| NTC2018 | Tab. 3.2.II | Categoria suolo A–E: SS, TB, TC, TD |
| NTC2018 | Tab. 3.2.III | Categoria topografica T1–T4: ST |
| NTC2018 | Tab. 2.4.II | Classe d'uso I–IV → VR, CU |
| NTC2018 | §7.3.3.2 | Distribuzione forze sismiche per piano |
| EC8 EN 1998-1 | §3.2.2 | Spettro elastico EC8 (alternativo) |
| INGV Allegato B NTC2018 | — | Griglia pericolosità ~10.751 punti WGS84 |

---

## Struttura file

```text
src/seismic/
├── __init__.py
├── ingv_hazard.py           # O.1 — carica_griglia_csv, query_webservice, parametri_hazard
├── spettro_ntc2018.py       # O.2 — CategoriaSuolo, CategoriaTopografica, ClasseUso, spettro_*
├── azioni_sismiche.py       # O.3 — dispatcher 7 norme, taglio_alla_base, distribuzione_piano
└── spectrum_paste_service.py # incolla dati da EdiLus-MS (integra O.2)

data/seismic/
└── griglia_ingv.csv          # ~10.751 punti WGS84, ag/F0/TC* per 9 TR

tests/
├── test_spettro_ntc2018.py           # 47 test (O.2)
├── test_ingv_hazard_csv.py           # 38 test (O.1)
└── test_azioni_sismiche_multinorma.py # 54 test (O.3)
```

---

## Subfasi, checklist e storico

### O.1 — Import dati pericolosità sismica INGV

**Stato**: ✅ COMPLETATO — 2026-03-09

- [x] Import da webservice INGV (lat, lon → ag, F0, TC*)
- [x] Tabella locale griglia INGV (fallback offline, CSV)
- [x] Funzione unificata con routing webservice/CSV
- [x] File CSV griglia INGV NTC2018 Allegato B — `data/seismic/griglia_ingv.csv` (ex spettri2008.csv)
- [x] Import parametri da EdiLus-MS (`spectrum_paste_service`)
- [x] Validazione e normalizzazione formato output

**Note tecniche**:

- Griglia irregolare ~10.751 punti (non regolare 0.05°)
- ag in CSV: [m/s²] — conversione automatica: ag_g = T{TR}ag / 9.81
- Interpolazione spaziale: nearest-neighbor (griglia irregolare)
- Interpolazione TR: log-lineare (NTC2018 §3.2.1) tra TR disponibili

### O.2 — Modulo spettro NTC2018

**Stato**: ✅ COMPLETATO — 2026-03-09

- [x] Enum `CategoriaSuolo`, `CategoriaTopografica`, `ClasseUso`
- [x] `calcola_VR`, `calcola_CC`, `calcola_SS`, `calcola_ST`, `calcola_alpha_S`, `calcola_periodi`
- [x] `spettro_elastico`, `spettro_progetto`, `calcola_S_d_T1`, `spettro_da_hazard_row`
- [x] `profilo_spettrale_completo()` — curva completa Sa(T) per T in [0, T_max], 4 rami, punti esatti su TB/TC/TD
- [x] Integrazione con `spectrum_paste_service`, O.1 (INGV)
- [x] Test: `test_spettro_ntc2018.py` (47 test) + `test_ingv_hazard_csv.py` (38 test)

### O.3 — Azioni sismiche multinorma

**Stato**: ✅ COMPLETATO — commit `d6e589a`

- [x] Package per 7 norme: distribuzione taglio alla base, dispatcher
- [x] Test: `test_azioni_sismiche_multinorma.py` (54 test)

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Nearest-neighbor (non interpolazione bilineare) | Griglia irregolare: interpolazione bilineare richiederebbe triangolazione (Delaunay) — nearest-neighbor più semplice e sufficiente per griglia densa |
| Fallback CSV locale | Uso offline senza connessione al webservice INGV |
| `profilo_spettrale_completo()` con punti speciali TB/TC/TD | Evita aliasing ai "ginocchi" della curva; numpy linspace + inserimento esplicito punti critici |
| Dispatcher O.3 separato dallo spettro O.2 | Responsabilità separate: O.2 calcola Sa(T), O.3 calcola Fb e distribuzione |
| 7 norme in O.3 | Copertura storica completa per edifici esistenti (RD2229 → NTC2018) |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Q | Domanda | Risposta | Decisione |
| --- | --- | --- | --- |
| Q-O1 | CSV griglia INGV | A — file fornito (spettri2008.csv) | Copiato in `data/seismic/griglia_ingv.csv` |
| Q-O2 | `profilo_spettrale_completo()` | A — implementa subito tutti i branch | Implementato con numpy linspace + punti speciali TB/TC/TD |
| Q-O3 | Aggiornamento documentazione | B — PIANO_LAVORO.md + PIANO_SVILUPPO_CORRENTE.md | Aggiornati entrambi |

---

## Note storiche/archivio

### Formato CSV spettri2008.csv

- Riga 1: super-header (`,,,,,,"TR = 30",...`) — saltata automaticamente
- Riga 2: nomi colonne (`OBJECTID, ID, LON, LAT, T30ag, T30F0, T30Tc, ...`)
- ag in [m/s²]: verificato su punti noti (Norcia 0.261g, Calabria 0.268g, Sardegna 0.041g a TR=475)
- La griglia NON è regolare 0.05°×0.05° — lat/lon sono coordinate WGS84 di una mesh irregolare

### Verifica punti noti

| Località | TR | ag atteso [g] | ag calcolato [g] |
| --- | --- | --- | --- |
| Norcia (PG) | 475 | ~0.261 | verificato |
| Calabria (RC) | 475 | ~0.268 | verificato |
| Sardegna (CA) | 475 | ~0.041 | verificato |
