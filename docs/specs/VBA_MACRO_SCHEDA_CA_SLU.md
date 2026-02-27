# Scheda Macro Bandiera — Stream C

## Identificativo

| Campo | Valore |
|-------|--------|
| **Nome modulo VBA** | `CA_SLU` |
| **Nome routine** | `VerifResistCA_SLU_TensNorm` (sub-calcolo: limiti assiali Nu_max/Nu_min) |
| **File sorgente** | `visual_basic/CA_SLU.bas` / `visual_basic/CA_SLU.txt` |
| **Stato migrazione** | IN CORSO — sub-calcolo Nu_max/Nu_min implementato in Python |
| **Criterio di selezione** | Alta frequenza d'uso; sub-calcolo autonomo e verificabile; nessuna dipendenza da GUI Excel |

---

## Responsabilità

Verifica di resistenza allo SLU (Stato Limite Ultimo) per tensioni normali di una sezione in c.a. di forma qualunque soggetta a sforzo normale `N`, momento `My`, momento `Mz`. Costruisce il dominio di rottura Nx-My o My-Mz e verifica che le sollecitazioni di progetto ne siano all'interno.

**Sub-calcolo pilota scelto**: calcolo dei limiti assiali `Nu_max` (max resistenza a trazione) e `Nu_min` (max resistenza a compressione) per sezione rettangolare c.a. ordinario senza FRP, senza confinamento.

---

## Input richiesti (sub-calcolo Nu_max/Nu_min)

| Variabile | Simbolo | Unità | Descrizione |
|-----------|---------|-------|-------------|
| Larghezza sezione | B | cm | Larghezza sezione rettangolare |
| Altezza sezione | H | cm | Altezza sezione rettangolare |
| Area totale acciaio | Aft | cm² | Area totale armatura longitudinale |
| Resistenza caratt. cls | fck | MPa | Resistenza caratteristica cilindrica calcestruzzo |
| Resistenza caratt. acc. | fyk | MPa | Resistenza caratteristica acciaio |
| Coeff. parziale cls | γc | — | Tipicamente 1.5 (NTC2018/EC2) |
| Coeff. parziale acc. | γs | — | Tipicamente 1.15 (NTC2018/EC2) |

---

## Output attesi

| Variabile | Simbolo | Unità | Descrizione |
|-----------|---------|-------|-------------|
| Resistenza max trazione | Nu_max | kN | Max sforzo normale a trazione |
| Resistenza max compressione | Nu_min | kN | Max sforzo normale a compressione (negativo) |
| Esito verifica assiale | ok_axial | bool | True se Ned in [Nu_min, Nu_max] |
| Utilization ratio | eta | — | |Ned| / max(|Nu_max|, |Nu_min|) |

---

## Formule (caso semplificato rettangolare, c.a. ordinario)

```
fcd = fck / γc              [MPa → kN/cm²: ÷ 10]
fyd = fyk / γs              [MPa → kN/cm²: ÷ 10]
Asez = B * H                [cm²]  (area lorda sezione)
Nu_max = Aft * fyd          [kN]
Nu_min = -fcd * Asez - Aft * fyd   [kN]  (semplificato: acciaio a fyd in compressione)
```

**Nota**: la formula completa VBA usa `f_Sigf(Eps_c2)` per la tensione nell'acciaio all'asse neutro critico. Per Eps_c2 = 0.002 e acciai tipici (Eps_yd ≈ 0.002), la semplificazione `f_Sigf ≈ fyd` introduce un errore trascurabile (< 1%).

---

## Dipendenze esterne (VBA originale)

- Excel Worksheet `Foglio4` (output risultati dominio)
- Variabili globali del modulo `PrincipCA_TA` (`Ned`, `Medy`, `Medz`, `Pilastro`, etc.)
- Funzione `f_Sigf(eps)`: legge costitutiva acciaio (bilineare)
- Funzione `DominioRotturaMyMz`: calcolo dominio completo (NON migrata in questa scheda)

---

## Unità di misura

- Forze: kN
- Lunghezze: cm
- Tensioni: kN/cm² (conversione da MPa: dividi per 10)
- Momenti: kN·m (non usati nel sub-calcolo pilota)

---

## Tolleranza confronto golden test

| Grandezza | Tolleranza relativa |
|-----------|-------------------|
| Nu_max | ≤ 0.5% |
| Nu_min | ≤ 0.5% |
| eta | ≤ 1% |

---

## Golden baseline (caso di riferimento)

```
Sezione: B=30 cm, H=50 cm
Calcestruzzo: C25/30, fck=25 MPa, γc=1.5
Acciaio: B450C, fyk=450 MPa, γs=1.15
Armatura: 4φ16, Aft = 4 * π * 1.6²/4 ≈ 8.042 cm²
Sollecitazione di progetto: Ned = -800 kN (compressione)

Risultati attesi:
  fcd = 25/1.5 = 16.667 MPa = 1.667 kN/cm²
  fyd = 450/1.15 = 391.30 MPa = 39.130 kN/cm²
  Asez = 30 * 50 = 1500 cm²
  Nu_max = 8.042 * 39.130 ≈ 314.7 kN
  Nu_min = -(1.667 * 1500 + 8.042 * 39.130) ≈ -2814.7 kN
  ok_axial = True  (−2814.7 ≤ −800 ≤ 314.7)
  eta ≈ |−800| / |−2814.7| ≈ 0.284
```

---

## TODO normativi

- `TODO(NTC/EC/RD)`: confermare che la formula semplificata Nu_min = -fcd*Asez - Aft*fyd corrisponda al cap. 4.1.2.1.2 NTC2018 (caso sezione rettangolare, interazione N-M).
- `TODO(EC2)`: verificare che la formula sia coerente con EN1992-1-1 §6.1 (interaction domain method).
- `TODO(NTC/EC/RD)`: per armature in compressione, il VBA usa `f_Sigf(Eps_c2)` — in futuro da implementare la funzione bilineare completa.

---

## Stato migrazione

- [x] Scheda macro compilata
- [x] Formula Nu_max/Nu_min implementata in Python (`src/rd2229/mvp/vba_migration/ca_slu_nu_limits.py`)
- [x] Golden test implementato (`tests/test_golden_ca_slu_nu_limits.py`)
- [ ] Formula completa dominio Nx-My (richiede f_Sigf e DominioRotturaMyMz) — stream futuro
- [ ] Verifica con output VBA reale da foglio Excel — stream futuro
