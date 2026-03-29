# Fase K — Grafici Strutturali

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | vedi tabella PIANO_LAVORO.md |
| Data completamento | 2026-03-09 |
| Test totali | 14 (K.1) + 13 (K.2) + skip (K.3 scipy) |
| File principali | `src/grafici/`, `src/gui/widgets/`, `src/report/grafici_html.py` |

---

## Descrizione

La Fase K implementa la **visualizzazione grafica delle grandezze strutturali** con architettura separata logica/GUI:

- **K.1** Diagrammi di sollecitazioni (M, T, N) e inviluppi combinazioni
- **K.2** Diagrammi di interazione N-M con overlay punto di lavoro e DominioFactory multinorma
- **K.3** Spostamenti v(x)/u(x) via doppia integrazione numerica (FEM in Fase M)
- **K.4** Export PNG/SVG e integrazione nel report HTML (`TabulatoCalcolo`)

**Principio architetturale**: `src/grafici/` contiene logica pura headless (no Qt); `src/gui/widgets/` contiene i widget Qt che wrappano la logica grafica.

---

## Teoria e formule chiave

### K.3 — Spostamenti (SolutoreAnalitico)

```text
Doppia integrazione di M(x)/EI:

  EI · v''(x) = M(x)

  v'(x) = ∫ M(x)/EI dx + C₁
  v(x)  = ∫ v'(x) dx + C₂

Condizioni al contorno (BC):
  semplicemente_appoggiata:  v(0)=0, v(L)=0
  incastro_appoggio:         v(0)=0, v'(0)=0
  doppio_incastro:           v(0)=0, v'(0)=0, v(L)=0, v'(L)=0

Verifica errore < 2% su casi noti:
  Carico concentrato:  f_max = PL³ / (48EI)
  Carico distribuito:  f_max = 5qL⁴ / (384EI)

u(x) = 0 per ora — riservato a Fase M (FEM spostamento orizzontale)
```

### K.2 — DominioFactory (routing multinorma)

```text
Norme TA:  RD2229, DM72, DM87, DM96, CIRC1981, OPCM3274
Norme SLU: NTC2008, NTC2018

Auto-routing:
  norma in NORME_TA  →  calcola dominio TA
  norma in NORME_SLU →  calcola dominio SLU (wrapper checks_ntc2018)

Overlay punto di lavoro:
  proiezione θ = atan2(My, Mx) → sezione N-M sul piano di flessione
  distanza dal bordo dominio → indice di sfruttamento
```

### K.1 — Inviluppo sollecitazioni

```text
Per N combinazioni di carico con la stessa ascissa x_i:
  M_max(x_i) = max(M_j(x_i))  per j = 1..N
  M_min(x_i) = min(M_j(x_i))  per j = 1..N

Busta inviluppo:
  Diagramma max/min a banda piena
  Singoli diagrammi sovrapposti in grigio (trasparenza)
```

---

## Diagramma dipendenze

```text
Fase K — architettura

  src/grafici/               logica pura headless (no Qt, no display)
  ├── sollecitazioni.py ─── K.1: DiagrammaSollecitazioni, grafico_sollecitazioni
  ├── inviluppi.py      ─── K.1: InviluppoSollecitazioni, grafico_inviluppo
  ├── interazione.py    ─── K.2: PuntoLavoro, DominioFactory, sovrapponi_punto_lavoro
  └── spostamenti.py    ─── K.3: DiagrammaSpostamenti, SolutoreAnalitico, SolutoreFEM(stub)
         │
         ▼ wrappati da
  src/gui/widgets/
  ├── sollecitazioni_canvas.py  ─── K.1: SollecitazioniCanvas(ExportMixin, QWidget)
  ├── spostamenti_canvas.py     ─── K.3: SpostamentiCanvas(ExportMixin, QWidget)
  └── dominio_canvas.py         ─── K.2: esteso (pre-esistente da Fase J)
         │
         ▼
  src/gui/widgets/_export_mixin.py  ─── K.4: ExportMixin (esporta_png, esporta_svg)
  src/report/grafici_html.py        ─── K.4: figura_a_base64, html_grafico

Dipendenze esterne:
  Fase J — dominio_canvas.py (esteso, non creato ex novo)
  Fase M — SolutoreFEM.calcola() (stub, da implementare)
  Fase L — DominioFactory per telai Cross-Pozzati
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase J — `src/pressoflessione/dominio_3d.py` | Backend dominio N-M per DominioFactory |
| Fase J — `src/gui/widgets/dominio_canvas.py` | Widget preesistente esteso in K.2 |
| Fase F — `src/methods/*/checks.py` | Adapter `da_risultato_checks` in K.1 |
| Fase M — `src/fem/beam_2d.py` | `SolutoreFEM` stub — completato in Fase M |
| `src/report/tabulato.py` | `TabulatoCalcolo.come_html()` — integrazione K.4 |

---

## Riferimenti normativi

| Norma | Contenuto rilevante |
| --- | --- |
| NTC2018 §4.1.5 | Freccia limite per SLE (usata in K.3 annotazione v_max) |
| NTC2018 §7.8 | Inviluppi sollecitazioni per muratura (K.1 adapter) |
| EC2 §5.8 | Spostamenti di secondo ordine (input per K.3) |

---

## Struttura file

```text
src/grafici/
├── __init__.py               # esporta tutte le API pubbliche
├── sollecitazioni.py         # K.1
├── inviluppi.py              # K.1
├── interazione.py            # K.2
└── spostamenti.py            # K.3

src/gui/widgets/
├── _export_mixin.py          # K.4 — ExportMixin condiviso
├── sollecitazioni_canvas.py  # K.1 — SollecitazioniCanvas
├── spostamenti_canvas.py     # K.3 — SpostamentiCanvas
└── dominio_canvas.py         # K.2 — esteso (pre-esistente da Fase J)

src/report/
└── grafici_html.py           # K.4 — figura_a_base64, html_grafico, aggiungi_grafico_a_tabulato

tests/
├── test_grafici_sollecitazioni.py   # 14 test (K.1)
├── test_grafici_interazione.py      # 13 test (K.2)
└── test_grafici_spostamenti.py      # K.3 (skip se scipy assente)
```

---

## Subfasi, checklist e storico

### K.1 — Sollecitazioni e inviluppi

**Stato**: ✅ COMPLETATO

- [x] `src/grafici/sollecitazioni.py` — `DiagrammaSollecitazioni`, `grafico_sollecitazioni`
  - Costruttore diretto, `da_valori_estremi`, `da_risultato_checks` (adapter da checks_*)
  - Unità: kg·cm → t·m per display, kg → t
- [x] `src/grafici/inviluppi.py` — `InviluppoSollecitazioni`, `inviluppo_sollecitazioni`, `grafico_inviluppo`
  - Busta max/min puntuale su N combinazioni con stessa ascissa
  - Sovrapposizione singoli diagrammi in grigio
- [x] `src/grafici/__init__.py` — esporta tutte le API pubbliche
- [x] `src/gui/widgets/sollecitazioni_canvas.py` — `SollecitazioniCanvas(ExportMixin, QWidget)`
  - Combo combinazione, checkbox inviluppo, toolbar navigazione, export PNG/SVG
- [x] `tests/test_grafici_sollecitazioni.py` — 14 test (tutti passati)

### K.2 — Diagrammi di interazione (estensione)

**Stato**: ✅ COMPLETATO

- [x] `src/grafici/interazione.py` — `PuntoLavoro`, `DominioFactory`, `sovrapponi_punto_lavoro`
  - `DominioFactory`: registry multinorma con auto-routing TA / SLU
  - Norme TA: RD2229, DM72, DM87, DM96, CIRC1981, OPCM3274
  - Norme SLU: NTC2008, NTC2018
  - `sovrapponi_punto_lavoro`: overlay N_Ed/M_Ed su asse 2D N-M con proiezione θ
- [x] `src/gui/widgets/dominio_canvas.py` — ESTESO
  - Aggiunta combo norma (`DominioFactory.norme_disponibili()`)
  - Aggiunta checkbox "Punto di lavoro" + `imposta_punto_lavoro(PuntoLavoro)`
  - Aggiunta export PNG/SVG tramite `ExportMixin`
  - Override `_draw_2d_nm` con overlay punto di lavoro
- [x] `tests/test_grafici_interazione.py` — 13 test (tutti passati)

### K.3 — Spostamenti

**Stato**: ✅ COMPLETATO

- [x] `src/grafici/spostamenti.py`
  - `DiagrammaSpostamenti` — x_cm, v_cm, u_cm con v_max_cm, u_max_cm
  - `ISolutoreSpostamenti` — interfaccia ABC
  - `SolutoreAnalitico(bc)` — doppia integrazione numerica via `scipy.integrate`
  - BC: `semplicemente_appoggiata`, `incastro_appoggio`, `doppio_incastro`
  - u(x) = 0 (riservato FEM Fase M)
  - `SolutoreFEM` — stub `NotImplementedError` ("Fase M")
  - `grafico_spostamenti` — 2 subplot v(x)/u(x), scala visiva, annotazione v_max
- [x] `src/gui/widgets/spostamenti_canvas.py` — `SpostamentiCanvas(ExportMixin, QWidget)`
  - SpinBox scala, toolbar navigazione, export PNG/SVG
- [x] `tests/test_grafici_spostamenti.py` — skip se scipy assente, 1 skipped in env attuale
  - Casi noti: f_max = PL³/48EI (carico concentrato), 5qL⁴/384EI (distribuito), errore < 2%

### K.4 — Export e integrazione report

**Stato**: ✅ COMPLETATO

- [x] `src/gui/widgets/_export_mixin.py` — `ExportMixin` con `esporta_png`, `esporta_svg`
  - Usato da: `SollecitazioniCanvas`, `SpostamentiCanvas`, `DominioNMyCanvas`
- [x] `src/report/grafici_html.py`
  - `figura_a_base64(fig, formato, dpi)` — Figure → data-URI base64
  - `html_grafico(fig, titolo, larghezza)` — blocco `<figure>` HTML
  - `aggiungi_grafico_a_tabulato(html, fig, titolo, posizione)` — inserimento in `TabulatoCalcolo.come_html()`

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| `src/grafici/` separato da `src/gui/widgets/` | Test headless senza display Qt; logica riusabile da script CLI |
| `ExportMixin` condiviso (non per-widget) | Zero duplicazione codice export PNG/SVG |
| `da_risultato_checks` come adapter | Disaccoppia grafici da struttura interna dei risultati verifica |
| `SolutoreFEM` come stub | Interfaccia ABC definita ora; implementazione in Fase M |
| `dominio_canvas.py` esteso (non nuovo) | Retrocompatibilità con Fase J; metodo `salva()` conservato |
| `DominioFactory` come registry | Aggiunta nuove norme senza modifica del chiamante |

---

## Bug corretti

| Bug | Causa | Fix |
| --- | --- | --- |
| Doppio `import math` in `_draw_2d_nm` | Copia-incolla durante estensione | Rimosso import duplicato |
| Test spostamenti falliscono senza scipy | `scipy.integrate` non disponibile in tutti gli env | `pytest.importorskip('scipy')` |
| Export SVG con caratteri speciali (σ, τ) | Encoding matplotlib su Windows | `bbox_inches='tight'` + encoding UTF-8 |

---

## Dipendenze future

| Modulo | Dipende da |
| --- | --- |
| `SolutoreFEM.calcola()` | Fase M — FEM beam 2D (scipy sparse) |
| `u_cm` in spostamenti | Fase M — spostamento orizzontale per telai |
| `DominioFactory` per telai | Fase L — Cross-Pozzati (ingressi M/N) |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| K1.1 — Tipo struttura | B — Travi + telai piani, FEM | Architettura separata logica/GUI |
| K1.2 — Sollecitazioni | M, T, N (assunto) | Tre subplot, unità t·m e t |
| K1.3 — Inviluppo | B — Da moduli esistenti | Adapter `da_risultato_checks` |
| K2.1 — Dominio interazione | D — Punto lavoro + dominio TA | Entrambi implementati |
| K2.2 — Norme dominio | D — Tutte le norme | DominioFactory registry |
| K3.1 — Spostamenti | C — v(x) + u(x) | u(x)=0 ora, FEM in Fase M |
| K3.2 — Calcolo | B+C — Numerico + FEM | SolutoreAnalitico ora, SolutoreFEM stub |
| K4.1 — Collocazione | Miglior giudizio | `src/grafici/` + `src/gui/widgets/` |
| K4.2 — Output | D — Widget + export + report HTML | ExportMixin + grafici_html.py |

---

## Note storiche/archivio

- `DominioNMyCanvas` esteso mantenendo retrocompatibilità: metodo `salva()` conservato
- `import math` rimosso dal secondo `_draw_2d_nm` (doppio import eliminato)
- Test spostamenti saltati se scipy non installato (`pytest.importorskip`)
- L'unità di misura interna è sempre kg·cm; conversione a t·m avviene solo nel layer di visualizzazione
