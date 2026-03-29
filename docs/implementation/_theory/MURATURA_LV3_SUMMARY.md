# Muratura LV3 — Quick Reference (Sommario Esecutivo)

**Data**: 2026-03-29
**Documento completo**: [`muratura_lv3_macro_elemento.md`](./muratura_lv3_macro_elemento.md) (1012 righe)

---

## 1. Equazioni Fondamentali (Un foglio)

### Stato di stress 2D
$$\boldsymbol{\sigma} = \begin{pmatrix} \sigma_x & \tau_{xy} \\ \tau_{xy} & \sigma_y \end{pmatrix}$$

### Tensioni principali
$$\sigma_{1,2} = \frac{\sigma_x + \sigma_y}{2} \pm \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}$$

### Rotazione assi
$$\theta = \frac{1}{2} \arctan\left(\frac{2\tau_{xy}}{\sigma_x - \sigma_y}\right)$$

### Mohr-Coulomb (resistenza a taglio)
$$\tau_{\max} = v_0 + \mu \cdot \sigma_n \quad \text{dove } \sigma_n = \sigma_1 \text{ (compressione principale)}$$

### Criterio Turnšek-Čačovič (fessurazione diagonale)
$$V_t = L \cdot t \cdot 1.5 \frac{v_0}{b} \sqrt{1 + \frac{\sigma_0}{1.5 v_0}}$$

---

## 2. Parametri Essenziali

| Parametro | Simbolo | Range Tipico | Fonte |
|-----------|---------|--------------|-------|
| **Resistenza taglio (senza pressione)** | v₀ | 0.15–0.50 kg/cm² | EN 1996-1-1, Circ 7/2019 |
| **Coefficiente attrito** | μ | 0.40–0.70 | Muratura: 0.40–0.65 |
| **Resistenza compressione** | f_d | 10–50 kg/cm² | NTC2018 Tab 4.5.IV |
| **Modulo elastico** | E_m | 800–2500 kg/cm² | NTC2018 Tab 4.5.III |
| **Pre-compressione media** | σ₀ | 0.5–3.0 kg/cm² | N / (L × t) |

---

## 3. Algoritmo SVD Iterativo (Pseudocodice)

```python
for step in range(num_steps_pushover):
    delta = incremento spostamento laterale

    # Strain di taglio
    gamma_xy = delta / h

    # Stress elastico
    tau_xy = G * gamma_xy

    # Iterazione per convergenza
    for iter in range(20):
        # 1. Diagonalizzazione (SVD)
        sigma_1, sigma_2 = eigenvalue(sigma_x, sigma_y, tau_xy)
        theta = atan2(2*tau_xy, sigma_x - sigma_y) / 2

        # 2. Resistenza Mohr-Coulomb
        tau_max = v0 + mu * max(sigma_1, 0)

        # 3. Controllo snervamento
        if |tau_xy| > tau_max:
            tau_xy *= 0.95  # Riduzione graduale
        else:
            break  # Convergenza

    # 4. Salva risultato
    V = tau_xy * A
    passaggi.append(...)

    return V, sigma_1, sigma_2, theta
```

---

## 4. Esempio Numerico Sintetico

### Dati
- Maschio: L=300 cm, t=50 cm, h=350 cm, N₀=1500 kg
- Materiale: v₀=0.25 kg/cm², μ=0.50, E_m=1000 kg/cm², G_m=400 kg/cm²

### Risultati per δ = 1 cm

| Quantità | Valore | Unità |
|----------|--------|-------|
| σ₀ (pre-compressione) | 0.10 | kg/cm² |
| γ_xy (strain taglio) | 0.00286 | rad |
| τ_xy (taglio elastico) | 1.14 | kg/cm² |
| σ₁ (principale max) | 1.19 | kg/cm² |
| σ₂ (principale min) | -1.09 | kg/cm² (trazione) |
| τ_max (resistenza M-C) | 0.845 | kg/cm² |
| Sfruttamento (τ/τ_max) | 135% | → snervamento |
| **V risultante (corretto)** | **12675** | **kg** |

### Curva di capacità (pushover)
| δ [cm] | V [kg] | Stato |
|--------|--------|-------|
| 0.0 | 0 | Elastico |
| 0.5 | ~9000 | Snervamento iniziale |
| 1.0 | ~12700 | Snervato |
| 2.0 | ~21000 | Plateau (degradazione iniziale) |
| 3.0+ | ~21000 | Plateau (resistenza stabile) |

**Interpretazione**: Piccola precompressione → fessurazione diagonale precoce → curva bilineare con plateau marcato.

---

## 5. Criteri di Rottura (Envelope)

La **resistenza finale** è il minimo tra:

### A. Fessurazione diagonale (Turnšek)
$$V_{\text{diag}} = L \cdot t \cdot 1.5 \frac{v_0}{b} \sqrt{1 + \frac{\sigma_0}{1.5 v_0}}$$
**Applica quando**: σ₀ bassa (< 1.0 kg/cm²)

### B. Scorrimento (Mohr-Coulomb)
$$V_{\text{scor}} = L \cdot t \cdot (v_0 + \mu \sigma_0)$$
**Applica quando**: σ₀ elevata (> 1.5 kg/cm²)

### C. Pressoflessione
$$V_{\text{press}} = \frac{2 f_d L t}{h_0} \left(1 - \frac{M}{f_d L t (t/2)}\right)$$
**Applica quando**: h/L < 1.0 (parete snella)

---

## 6. Fenomeno Critico: Rotazione degli Assi Principali

Durante il **pushover**:
1. **δ = 0**: Assi allineati a x-y; σ₁ = verticale
2. **δ > 0**: τ_xy cresce → σ₁ ruota di ~45° (diventa diagonale)
3. **Effetto**: Fessura diagonale cambia orientazione → **resistenza varia**

**Impatto**: Se σ₁ passa da **compressione a trazione** (σ₂ < 0), il beneficio dell'attrito μ·σ₁ **crolla** e rimane solo v₀.

---

## 7. Parametri NTC2018 per LC1/LC2/LC3

### Coefficiente sicurezza γ_M
- **LC1** (limitata): γ_M = 3.0 → resistenza molto ridotta
- **LC2** (media): γ_M = 2.4 → standard
- **LC3** (completa): γ_M = 1.8 → con prove

### Tabella 4.5.IV NTC2018 (f_d muratura)
| Tipo | f_d [kg/cm²] |
|------|---------|
| Mattoni pieni | 15–25 |
| Blocchi CLS | 25–40 |
| Pietra squadrata | 20–35 |
| Tufo | 10–15 |

---

## 8. Connessione al Codice RD2229

### File da creare (Fase U.6b)
```
src/methods/muratura/
  └─ macro_elemento_lv3.py       # Classe MacroElementoLV3 + SVD iterativo
  └─ verifica_lv3.py             # Verifica sismica globale LV3
  └─ curve_capacita.py           # Pushover, curve bilineare

tests/
  └─ test_macro_elemento_lv3.py  # SVD, convergenza, benchmark ASCE
```

### Interfaccia principale
```python
elem = MacroElementoLV3(id=1, geom=GeometriaMacroElemento(...),
                        param=ParamMuratura(...), N0=1500)
risultato = elem.calcolo_step_pushover(delta=1.0)
# → V, sigma_1, sigma_2, theta, tau_max, sfruttamento, criterio, convergenza

capacita = elem.pushover_completo(delta_max=3.0, num_step=30)
# → curva completa: V(δ), delta_y, delta_u, V_Rd, k_elastica
```

---

## 9. Benchmark ASCE 41-06 (Validazione)

**Caso test**: Pannello muratura storica (mattoni + malta debolina)
- L=300 cm, t=50 cm, h=360 cm, σ₀=0.5 kg/cm²
- **ASCE 41 predice**: V_max ≈ 65 kN a δ ≈ 0.5% drift

**Test numerici proposti**:
1. Confronto V_max tra modello NTC2018 e ASCE 41
2. Validazione δ_u (drift ultimo)
3. Post-picco: degradazione di rigidezza

---

## 10. Stato della Ricerca (2026-03-29)

| Aspetto | Status | Note |
|---------|--------|------|
| **Ricerca teorica** | ✅ COMPLETATA | Formule consolidate, algoritmo SVD chiaro |
| **Parametri materiale** | ✅ COMPLETATA | Tabelle NTC2018/EN1996 estratte |
| **Esempio numerico** | ✅ COMPLETATA | Step-by-step muratura storica |
| **Pseudo-codice** | ✅ COMPLETATA | SVD iterativo + return-mapping |
| **Implementazione Python** | ⏳ PENDING (U.6b) | Entro 1 settimana |
| **Unit test + benchmark ASCE** | ⏳ PENDING (U.6c) | Entro 2 settimane |
| **Integrazione in LV3 report** | ⏳ PENDING (R.4) | Entro 3 settimane |

---

## 11. Riferimenti Normative Chiave

### Italiane
- **NTC2018 §7.8.2.2** — Resistenza pannelli murari (diagonale, scorrimento, pressoflessione)
- **Circ. 7/2019 §C8.7.1.3.1.1** — Parametri muratura per LC1/LC2/LC3
- **Circ. 7/2019 §C4.5.6** — Compressione, snellezza, fattore Φ

### Europee
- **EN 1996-1-1** Cap. 3 (materiali), Cap. 6 (resistenza)
  - Tab. 3.4: resistenza taglio v₀ per tipo muratura
  - Tab. 3.6: moduli elastici E_m, G_m

### USA (benchmark)
- **ASCE 41-06** Cap. 6–7: macro-elementi, curve capacità, fattori degradazione
- **FEMA 356** Tab. 5–6: modelli di rottura, drift ammessi

---

## 12. Prossimi Step (Implementazione)

1. **Fase U.6b** (1 settimana): Implementare `MacroElementoLV3.calcolo_step_pushover()` con SVD iterativo
2. **Fase U.6c** (1 settimana): Unit test + validazione benchmark ASCE
3. **Fase R.4** (1 settimana): Integrazione in report vulnerabilità LV3
4. **Estensioni future**: Danno cumulativo, torsione fuori-piano, interazione con cordoli

---

**Quick Link**: [Documento Completo](./muratura_lv3_macro_elemento.md)
**Data**: 2026-03-29
**Stato**: RICERCA TERMINATA — Pronto per codifica
