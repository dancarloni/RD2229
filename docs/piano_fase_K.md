# Fase K — Grafici

## Stato: COMPLETATO ✅ — commit: (vedi tabella PIANO_LAVORO.md)

---

## Subfasi, checklist e storico

### K.1 — Sollecitazioni e inviluppi
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
- [x] `src/grafici/interazione.py` — `PuntoLavoro`, `DominioFactory`, `sovrapponi_punto_lavoro`
  - `DominioFactory`: registry multinorma con auto-routing TA / SLU
  - Norme TA: RD2229, DM72, DM87, DM96, CIRC1981, OPCM3274
  - Norme SLU: NTC2008, NTC2018
  - `sovrapponi_punto_lavoro`: overlay N_Ed/M_Ed su asse 2D N-M con proiezione θ
- [x] `src/gui/widgets/dominio_canvas.py` — ESTESO (Fase K)
  - Aggiunta combo norma (`DominioFactory.norme_disponibili()`)
  - Aggiunta checkbox "Punto di lavoro" + `imposta_punto_lavoro(PuntoLavoro)`
  - Aggiunta export PNG/SVG tramite `ExportMixin`
  - Override `_draw_2d_nm` con overlay punto di lavoro
- [x] `tests/test_grafici_interazione.py` — 13 test (tutti passati)

### K.3 — Spostamenti
- [x] `src/grafici/spostamenti.py`
  - `DiagrammaSpostamenti` — x_cm, v_cm, u_cm con v_max_cm, u_max_cm
  - `ISolutoreSpostamenti` — interfaccia ABC
  - `SolutoreAnalitico(bc)` — doppia integrazione numerica via scipy.integrate
    - BC: semplicemente_appoggiata, incastro_appoggio, doppio_incastro
    - u(x)=0 (riservato FEM Fase M)
  - `SolutoreFEM` — stub NotImplementedError ("Fase M")
  - `grafico_spostamenti` — 2 subplot v(x)/u(x), scala visiva, annotazione v_max
- [x] `src/gui/widgets/spostamenti_canvas.py` — `SpostamentiCanvas(ExportMixin, QWidget)`
  - SpinBox scala, toolbar navigazione, export PNG/SVG
- [x] `tests/test_grafici_spostamenti.py` — (skip se scipy assente, 1 skipped in env attuale)
  - Casi noti: f_max = PL³/48EI (carico concentrato), 5qL⁴/384EI (distribuito), errore < 2%

### K.4 — Export e integrazione report
- [x] `src/gui/widgets/_export_mixin.py` — `ExportMixin` con `esporta_png`, `esporta_svg`
  - Usato da: SollecitazioniCanvas, SpostamentiCanvas, DominioNMyCanvas
- [x] `src/report/grafici_html.py`
  - `figura_a_base64(fig, formato, dpi)` — Figure → data-URI base64
  - `html_grafico(fig, titolo, larghezza)` — blocco `<figure>` HTML
  - `aggiungi_grafico_a_tabulato(html, fig, titolo, posizione)` — inserimento in TabulatoCalcolo.come_html()

---

## Architettura implementata

```
src/grafici/               # logica pura (headless, no Qt)
├── __init__.py
├── sollecitazioni.py      # K.1
├── inviluppi.py           # K.1
├── interazione.py         # K.2
└── spostamenti.py         # K.3

src/gui/widgets/
├── _export_mixin.py       # K.4 — condiviso
├── sollecitazioni_canvas.py  # K.1
├── spostamenti_canvas.py     # K.3
└── dominio_canvas.py         # K.2 — esteso (pre-esistente)

src/report/
└── grafici_html.py        # K.4

tests/
├── test_grafici_sollecitazioni.py  # K.1
├── test_grafici_interazione.py     # K.2
└── test_grafici_spostamenti.py     # K.3
```

---

## Dipendenze future

| Modulo | Dipende da |
|--------|-----------|
| `SolutoreFEM.calcola()` | Fase M — FEM beam 2D (scipy sparse) |
| `u_cm` in spostamenti | Fase M — spostamento orizzontale per telai |
| `DominioFactory` per telai | Fase L — Cross-Pozzati (ingressi M/N) |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
|---------|----------|-----------|
| K1.1 — Tipo struttura | B — Travi + telai piani, FEM | Architettura separata logica/GUI |
| K1.2 — Sollecitazioni | (assunto B) M, T, N | Tre subplot, unità t·m e t |
| K1.3 — Inviluppo | B — Da moduli esistenti | Adapter `da_risultato_checks` |
| K2.1 — Dominio interazione | D — Punto lavoro + dominio TA | Entrambi implementati |
| K2.2 — Norme dominio | D — Tutte le norme | DominioFactory registry |
| K3.1 — Spostamenti | C — v(x) + u(x) | u(x)=0 ora, FEM in Fase M |
| K3.2 — Calcolo | B+C — Numerico + FEM | SolutoreAnalitico ora, SolutoreFEM stub |
| K4.1 — Collocazione | Miglior giudizio | src/grafici/ + src/gui/widgets/ |
| K4.2 — Output | D — Widget + export + report HTML | ExportMixin + grafici_html.py |

---

## Note storiche/archivio

- `DominioNMyCanvas` esteso mantenendo retrocompatibilità: metodo `salva()` conservato
- `import math` rimosso dal secondo `_draw_2d_nm` (doppio import eliminato)
- Test spostamenti saltati se scipy non installato (`pytest.importorskip`)
