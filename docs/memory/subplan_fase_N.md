# FASE N — Carote cls in sito

## Stato: COMPLETATO

**Test**: 70 in `tests/test_carote.py`, 0 falliti
**Retrocompat**: 2233 test suite completa, 0 falliti

## Architettura

```
src/codes/carote/
  __init__.py              — re-export
  core_sample.py           — CoreSample, CorrectionFactors, ConversionResult
  formulas.py              — 10 formulazioni + custom engine (3 livelli)
  statistics.py            — NTC2018, EN 13791 A/B, Grubbs, Chauvenet, classificazione
  derived_params.py        — E_cm, f_ctm, Rck, sigma_c_adm storica
  analysis.py              — Pipeline: list[CoreSample] -> CoreAnalysisResult
  integration.py           — LC/FC bridge + registra_materiale_in_situ()
  report.py                — HTML report + JSON/CSV export
  plots.py                 — matplotlib headless (istogramma, scatter, boxplot, barre)

src/gui/widgets/carote_canvas.py  — Qt widget (4 viste, combo formulazione)
tests/test_carote.py              — ~66 test
```

## Formulazioni

| ID | Fonte | k_ld |
|---|---|---|
| BS1881 | BS 1881:Part 120 | Tabella: {2.0:1.00, 1.75:0.97, 1.5:0.92, 1.25:0.87, 1.0:0.80} |
| ACI214 | ACI 214.4R-10 | k=2/(1.04+0.04*LD) per LD<1.75, altrimenti 1.0 |
| TR11 | Concrete Society TR11 | Tabella aggiornata |
| RILEM1979 | RILEM NDT 2 | Tabella specifica |
| MASI2005 | Masi A. 2005 | Regressione a_0+a_1*LD |
| FIORE2008 | Fiore et al. 2008 | Modello regressione cls storico |
| NTC2018 | NTC2018+Circ.7 C8.5.3 | Tabella codice |
| EN13791 | EN 13791:2019 | Fattori da annesso |
| GIACCHETTI | Giacchetti R. et al. | Regressione pratica italiana |
| CUSTOM | Utente | 3 livelli: moltipl./param./expr. |

## Decisioni chiave

- Unita' interne MPa, conversione a kg/cm2 solo ai confini
- apply_lc_fc_adjustments() richiede f_yk>0: passa f_yk=450 nominale con nota
- Material(famiglia="calcestruzzo") con nota in-situ, no nuova sottoclasse
- Custom formula: sandboxed eval con namespace ristretto
- EN 13791 Method B, k: {3:3.37, 5:2.27, 8:1.90, 10:1.73, 12:1.62, 14:1.55}
- Grubbs usa scipy.stats.t.ppf()

## Valori di riferimento

**8 carote test**: f_core = [22.5, 24.1, 23.8, 25.0, 22.0, 24.5, 23.2, 24.8] MPa
- mean=23.74, s=1.072, CoV=0.045
- EN13791 B (n=8, k=1.90): f_ck,is = 21.71 MPa
- NTC2018 (k=1.64): f_ck,is = 21.99 MPa
- Classificazione: C20/25

**Derivati da f_ck=25 MPa**:
- f_cm=33, E_cm=31476, f_ctm=2.565, Rck=30.12, sigma_c_adm~37.9 kg/cm2

## Dipendenze riusate (non modificate)

- `src/core_calculus/lc_fc_adjustments.py` — apply_lc_fc_adjustments(), get_typical_fc_for_lc()
- `src/materials/material_model.py` — Material, create_material()
- `src/materials/material_repo.py` — MaterialRepository
- `src/materials/adapter.py` — _MPA_TO_KG_CM2
- `src/report/tabulati_calcolo.py` — TabulatoCalcolo
