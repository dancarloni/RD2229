# FASE I — Sezioni parametri statici completi

**Data completamento**: 2026-03-06
**Stato**: COMPLETATO — 91 test, 0 falliti

---

## Obiettivo

Package `src/codes/section_params/` per calcolo parametri statici sezioni c.a.:
- Rapporto di omogeneizzazione n per 6 norme
- Sezione omogeneizzata integra (A_om, I_om, y_G_om)
- Asse neutro fessurato + inerzia fessurata
- Tensioni SLE (sigma_c, sigma_s)
- Sezione composta acciaio-cls (IPE + soletta)
- Disegno matplotlib + widget Qt

---

## Architettura

```text
src/codes/section_params/
├── __init__.py          — re-export principali
├── norme_n.py           — get_n_for_norm() per RD2229/DM92/DM96/NTC2008/NTC2018/EC2
├── omogenizzata.py      — BarraArmatura, calcola_sezione_omogenizzata,
│                          calcola_asse_neutro_fessurato, calcola_tensioni_sle,
│                          calcola_parametri_sezione_completi
├── composita.py         — IPE_TABLE (18 profili), calcola_sezione_composta,
│                          calcola_tensioni_sle_composita
└── disegno_sezione.py   — disegna_sezione(), crea_figura_sezione_sle(), salva_figura()

src/gui/widgets/
└── sezione_canvas.py    — SezioneSLECanvas (QWidget + FigureCanvasQTAgg)
```

---

## Valori n per norma

| Norma | Valore | Fonte |
|-------|--------|-------|
| RD2229 | 8/10/12/15 (user select) | Default=15 |
| DM92 | E_s/E_c o default 10 | Calcolo automatico |
| DM96 | E_s/E_c o default 10 | Calcolo automatico |
| NTC2008 | E_s/E_c o default 15 | §4.1.2.1.4.2 |
| NTC2018 | E_s/E_c o default 15 | §4.1.2.1.4.2 long-term |
| EC2 | E_s/E_c_eff = E_s/(E_c/(1+phi)) o default 15 | §7.4.3 |

---

## Formule chiave

### Sezione omogenizzata integra
```python
A_om = A_c + (n-1) * sum(A_si)
y_G_om = (A_c * y_G_c + (n-1) * sum(A_si * y_i)) / A_om
I_om = I_c + A_c*(y_G_c - y_G_om)^2 + (n-1)*sum(A_si*(y_i - y_G_om)^2)
```

### Asse neutro fessurato (rettangolare, N=0, singola fila)
```python
(b/2)*x^2 + n*As*x - n*As*d = 0  →  x = (-n*As + sqrt((n*As)^2 + 2*b*n*As*d)) / b
I_fess = b*x^3/3 + n*As*(d-x)^2
```

### Tensioni SLE
```python
sigma_c = M * y_na / I_fess
sigma_s_i = n * M * (y_i - y_na) / I_fess
```

---

## Valori di riferimento verificati

| Caso | Valore | Metodo |
|------|--------|--------|
| Rett. 30×50, As=10cm² d=45, n=10 | A_om=1590 cm² | A_c+(n-1)*As |
| Stessa sez. | y_G_om=26.1321 cm | Formula |
| Stessa sez. | x_na=14.305 cm | Analitico |
| IPE300 + soletta b=100,t=15, n=15 | I_comp > I_ipe=8356 cm⁴ | Steiner |

---

## Interfaccia principale

```python
from src.codes.section_params import (
    BarraArmatura, get_n_for_norm,
    calcola_parametri_sezione_completi,
    calcola_sezione_composta,
)

# n per norma
p = get_n_for_norm("NTC2018")       # p.n = 15
p = get_n_for_norm("RD2229", n_user=10)  # p.n = 10

# Sezione c.a. completa
barre = [BarraArmatura(y=45.0, A=10.0, zona="tesa")]
res = calcola_parametri_sezione_completi(section, barre, n=15.0, M_kgcm=500_000)
# res["integra"]["I_omogenizzata_cm4"]
# res["fessurata"]["y_na_cm"]
# res["tensioni_sle"]["sigma_c_max_kgcm2"]

# Sezione composta
res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
```

---

## Duck typing sezioni

Le funzioni usano `section_fiber.py::width_at_depth` e `get_section_height`
per integrare numericamente su qualsiasi tipo di sezione (stessa interfaccia
di `src/codes/ntc2018/checks_ntc2018.py`). Supportati tutti i 12 tipi.

---

## Torsione (pre-esistente)

J_t, C_w, x_s, y_s sono calcolati da `apps/sections/models/sections.py::_compute_torsion_properties()`
chiamato automaticamente da `Section.compute_properties()`. Non richiedono
il package section_params. Test: `tests/test_section_torsion.py`.

---

## Test

File: `tests/test_sezione_omogenizzata.py` — 91 test

| Classe | N | Descrizione |
|--------|---|-------------|
| TestNormaHnParams | 15 | n per norma, opzioni RD2229, calcolo automatico, EC2+phi |
| TestSezOmogenizzataRettangolare | 10 | A_om, y_G_om, I_om, W, barre |
| TestSezOmogenizzataDueFile | 3 | doppia armatura, senza armatura, n=1 |
| TestAssNeutroFessuratoRettangolare | 8 | analitico, equilibrio, varia n/As |
| TestAssNeutroFessuratoCircolare | 3 | circolare iterativo |
| TestAssNeutroFessuratoTSection | 2 | T sezione iterativo |
| TestTensioniSLE | 7 | sigma_c, sigma_s, errori |
| TestPipelineCompleta | 6 | integra+fessurata+SLE+norm_references |
| TestAllSectionTypes | 16 | 8 tipi × (omogenizzata + fessurata) |
| TestSezioneComposta | 11 | IPE+soletta, n, W, tensioni |
| TestDisegnoSezione | 4 | matplotlib headless, salva |

---

## Dipendenze interne

- `omogenizzata.py` e `disegno_sezione.py` importano lazy `src.methods.section_fiber`
- `composita.py` standalone (solo numpy standard)
- `sezione_canvas.py` importa lazy PySide6/PyQt6 e matplotlib backend Qt
- Nessun import circolare
