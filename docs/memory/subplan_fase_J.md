# FASE J — Pressoflessione deviata multinorma

## Stato: COMPLETATO

**Test**: 70 in `tests/test_pressoflessione_deviata.py`, 0 falliti
**Retrocompat**: 91 test `test_sezione_omogenizzata.py` invariati

## Architettura

```
src/codes/pressoflessione/
  __init__.py          — re-export
  base.py              — PressoflessSpec, PressoflessResult, DominioNMy,
                         calcola_omogenizzata_biassiale(), crea_armatura_rettangolare()
  ta_cls.py            — verifica TA (sovrapposizione elastica + Bresler)
  slu.py               — wrapper SLU via checks_ntc2018
  dominio.py           — calcola_dominio_3d() + 3 funzioni matplotlib
  instabilita_biassiale.py — amplifica_momenti_biassiale()
  dispatcher.py        — calcola_pressoflessione_deviata() entry-point

src/gui/widgets/dominio_canvas.py — DominioNMyCanvas (Qt interattivo)
```

## Norme coperte

| Norma | Metodo | Riferimento |
|-------|--------|-------------|
| RD2229 | TA sovrapposizione/Bresler | Art. 29 |
| DM92 | TA sovrapposizione/Bresler | §7 |
| DM96 | TA sovrapposizione/Bresler | §3.4 |
| NTC2008 | SLU Bresler fiber | §4.1.2.1.3.1 |
| NTC2018 | SLU Bresler fiber | §4.1.2.1.3.1 |
| EC2 | SLU Bresler fiber | §5.8.9 |

## Decisioni chiave

- Codice esistente (checks_rd2229.py, checks_ntc2018.py) NON modificato
- Nuovo package e' motore di calcolo puro parallelo (PressoflessSpec -> PressoflessResult)
- BarraArmatura estesa con `x: float = 0.0` (backward-compatible)
- I_y_c calcolato via integrazione strip: integrate[b(y)^3/12]dy
- SLU delega a check_pressoflessione_slu (no duplicazione)
- Instabilita' riusa omega_ca() da instabilita.py
- Dominio 3D: TA analitico chiuso, SLU parametrico Bresler

## Formule principali

- Sovrapposizione: sigma_c = N/A_om + |Mx|*y_ext/I_x + |My|*x_ext/I_y
- Bresler TA: (|Mx|/M_Rdx)^alpha + (|My|/M_Rdy)^alpha <= 1
- M_Rd TA: (sigma_adm - |N|/A_om) * W
- Dominio: M_Rd(theta) = 1/((|cos|/M_Rdx)^a + (|sin|/M_Rdy)^a)^(1/a)
- Instabilita': alpha_M = 1/(1 - |N|/Pcr), Pcr = pi^2 *0.4*Ec * I / l0^2

## Dipendenze riusate (non modificate)

- `src/methods/section_fiber.py` — width_at_depth, get_section_height/width
- `src/codes/section_params/omogenizzata.py` — BarraArmatura
- `src/methods/rd2229/instabilita.py` — omega_ca()
- `src/methods/checks_ntc2018.py` — check_pressoflessione_slu()
