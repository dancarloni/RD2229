# Fase S — Normative aggiuntive (DM92, NTC2008, EC2/EC3/EC8, CNR-DT 200)

> Nota 2026-03-11: questa fase resta distinta dalla nuova famiglia S1-S9 dedicata agli elementi secondari del §7.2 NTC2018.

### Mappatura della nuova famiglia di fasi (S1–S9)

Questa mappatura definisce le tipologie di elementi secondari spostate dalla pianificazione generale in fasi dedicate (S1–S9). Usare questi identificatori per i file `piano_fase_S1.md` … `piano_fase_S9.md` e per i tag di indicizzazione.

| Fase | Tipologia | Ambito principale |
|------|-----------|-------------------|
| S1 | Tamponamenti | fuori piano, ancoraggi, giunti, danno da drift |
| S2 | Tramezzi e partizioni leggere | tramezzi tradizionali e in cartongesso, compatibilita deformativa |
| S3 | Parapetti e balaustre | verifica locale, urti, azioni orizzontali e ancoraggi |
| S4 | Controsoffitti | sospensioni, controventi, nodi pendinati |
| S5 | Impianti e componenti impiantistici | apparecchiature, staffaggi, piping, canalizzazioni |
| S6 | Facciate e rivestimenti | pannelli, sottostrutture, fissaggi, giunti |
| S7 | Camini, comignoli e canne fumarie | comportamento a mensola, snellezza, ancoraggi |
| S8 | Scaffalature, arredi fissati e contenuti | ribaltamento, scorrimento, ancoraggi, interazione col contenuto |
| S9 | Insegne, cancelli e componenti speciali | elementi esposti, chiusure tecniche, casi fuori catalogo |

---

### Sessione 2026-03-11 — Domande, risposte e decisioni (estratto)

Questo estratto raccoglie le decisioni operative prese nella sessione del 2026-03-11 relative alla riorganizzazione in S1–S9. La traccia completa delle Q&A e le relative scelte tecniche sono salvate anche in `docs/PIANO_LAVORO.md` ma la fonte dettagliata di progetto per S è qui.

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Codifica nuove fasi | Prefissi numerici aggiuntivi (`S1`, `S2`, `S3`, ...) | Adottata famiglia S1-S9 nel piano principale, mantenendo separata la Fase S gia esistente |
| Tipologie da istanziare | Tamponamenti, tramezzi, parapetti, controsoffitti, impianti, facciate, camini, scaffalature, insegne/cancelli | Creata una fase dedicata per ciascuna tipologia |
| Livello di meta-codice | Medio | Ogni piano include dataclass/interfacce essenziali + pseudocodice di flusso |
| Struttura documentale | Allineata agli altri `piano_fase_*.md` | Obbligo di diagrammi, dipendenze, riferimenti normativi, tabelle, struttura file, storicizzazione |
| Tranche implementativa reale | Prerequisiti comuni + S2 completo | Dispatcher tipizzato, storage arricchito, completamento verticale S2 |
| Commit documentali senza commit git reale | Usare `—` | Rimossi identificatori semantici non coerenti dalla colonna `Ultimo commit` |


## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATA |
| **Commit** | — |
| **Data prevista** | 2026-03-12 (avvio) |
| **Test pianificati** | ~120 (52 test mirati verdi) |
| **Norma/e di riferimento** | DM 14/02/1992, NTC 2008, EN 1992-1-1, EN 1993-1-1, EN 1998-1, CNR-DT 200/2004 |
| **Priorità** | Bassa |

---

## Descrizione

Estende le verifiche normative del progetto con le norme non ancora coperte: DM 14/02/1992 completo (tensioni ammissibili e stati limite), NTC 2008 (wrapper su EC2), Eurocodici EC2/EC3/EC8, CNR-DT 200 per rinforzi FRP. Ogni norma aggiunta implementa l'interfaccia `SingleCheckResult` con `riferimento_normativo` puntuale, consentendo integrazione diretta con il report (Fase Q) e il confronto multinorma.

---

## Teoria e fondamenti strutturali

### DM 14/02/1992

Impostazione a tensioni ammissibili (TA) e stati limite (SL) in parallelo:

- Tensioni ammissibili: σ_amm = f_ck / (γ_c · η) dove γ_c=1.5 e η fattore condizioni d'opera
- Resistenza caratteristica: `Rck` (cubica) invece di `fck` (cilindrica): `fck ≈ 0.83 · Rck`
- Coefficienti parziali: γ_cls = 1.5, γ_acciaio = 1.15 (identici EC2)

### EC2 (EN 1992-1-1) — Cemento armato

**Flessione (§6.1):**

```text
M_Rd = A_s · f_yd · (d - 0.4·x)
```

dove x ricavato dall'equilibrio: `A_s·f_yd = 0.8·x·b·f_cd`; verifica deformazione ultima: `ε_cu = 0.0035` per cls normale.

**Taglio senza armatura (§6.2.2):**

```text
V_Rd,c = [C_Rd,c · k · (100·ρ_l·f_ck)^(1/3) + k_1·σ_cp] · b_w · d
```

con `k = 1 + √(200/d) ≤ 2.0` e `C_Rd,c = 0.18/γ_c`.

**Taglio con armatura (§6.2.3, modello a traliccio):**

```text
V_Rd,s = (A_sw / s) · z · f_ywd · cotg(θ)
V_Rd,max = α_cw · b_w · z · ν_1 · f_cd / (cotg(θ) + tanθ)
```

### EC3 (EN 1993-1-1) — Acciaio

**Classificazione sezione (§5.5):**

- Classe 1: può sviluppare momento plastico e rotazione plastica → W_pl
- Classe 2: può sviluppare momento plastico senza rotazione plastica → W_pl
- Classe 3: solo momento elastico → W_el
- Classe 4: efficace ridotta → W_eff

**Resistenza a flessione (§6.2.5):**

```text
M_Rd = W_pl · f_y / γ_M0    (classi 1-2)
M_Rd = W_el · f_y / γ_M0    (classe 3)
```

**Instabilità flessotorsionale (§6.3.2):**

```text
M_b,Rd = χ_LT · W_y · f_y / γ_M1
```

dove `χ_LT` da curva di instabilità in funzione di `λ_LT = √(W_y·f_y/M_cr)`.

### EC8 (EN 1998-1) — Duttilità e gerarchia

**Duttilità in curvatura richiesta (§5.2.3.4):**

```text
μ_φ ≥ 1 + 2·(q-1)·T_C/T_1    se T_1 < T_C
μ_φ ≥ 2·q - 1                  se T_1 ≥ T_C
```

Per CD-H (alta duttilità): μ_φ ≥ 13 (travi e pilastri elementi primari).

**Gerarchia resistenze (§5.4.2.3):**

```text
Σ M_Rc ≥ 1.3 · Σ M_Rb    (pilastri più resistenti delle travi nel nodo)
```

### CNR-DT 200/2004 — Rinforzi FRP

**Rinforzo a flessione con lamine:**

```text
ΔM_Rd = A_f · f_fd · z_f
f_fd = E_f · ε_fd    con ε_fd = min(ε_fu/γ_f, ε_cu·(h-x)/x, ε_de)
```

dove `ε_de` = deformazione limite per delamination.

**Verifica delamination (distacco FRP-cls):**

```text
τ_b ≤ f_bd = 1.8 · f_ctm / γ_f    (bond stress)
```

---

## Diagramma dipendenze subfasi

```text
S.1 — DM92 verifiche complete (TA + SL)
 └── S.2 — NTC2008 verifiche (wrapper EC2 con adattamenti italiani)
      └── S.3 — EC2 flessione/taglio/torsione/SLE
           ├── S.4 — EC3 acciaio (classi sezione, instabilità, connessioni)
           ├── S.5 — EC8 dettagli duttili (gerarchia, μ_φ, nodi)
           └── S.6 — CNR-DT 200 rinforzi FRP
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| checks_ntc2018 | `src/checks_ntc2018.py` | Riferimento per interfaccia SingleCheckResult |
| checks_dm96 | `src/checks_dm96.py` | Pattern DA replicare per DM92 |
| MaterialRepository | `src/materials/material_repository.py` | Materiali con fck, fyk, f_frd (FRP) |
| adapter | `src/materials/adapter.py` | Conversione Rck↔fck, kg/cm²↔MPa |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Tabulato verifiche con passaggi intermedi |
| registro_log | `src/core/registro_log.py` | Log per ogni norma applicata |

---

## Aspetti informatici salienti

### Contratti software e output

- Le funzioni di verifica restituiscono dizionari strutturati con campi minimi: `esito`, `rateo`, `riferimento_normativo`.
- Le verifiche NTC2008 sono implementate come wrapper su EC2 con arricchimento metadati (`norma`, riferimento al paragrafo NTC).
- I moduli sono esportati a package-level via file `__init__.py` per semplificare integrazione in pipeline/report.

### Organizzazione modulare

- Separazione per dominio normativo: `src/methods/dm92/`, `src/methods/ntc2008/`, `src/methods/ec/`, `src/rinforzi/`.
- Separazione per responsabilita: verifiche di sezione, connessioni acciaio, utility combinazioni/spettro, rinforzi FRP.
- Architettura orientata al riuso: NTC2008 riusa EC2 per minimizzare duplicazione.

### Tracciabilita numerica

- Ogni controllo espone il `rateo` di sfruttamento e i parametri resistenti principali (ad esempio `M_Rd`, `V_Rd`, `T_Rd`).
- Le formule semplificate usate sono annotate con riferimento al paragrafo normativo nel campo `riferimento_normativo`.

### Dati e cataloghi

- Catalogo DM92 presente in `data/materials/catalogo_dm92.json`, caricato dal repository materiali tramite pattern `catalogo_*.json`.
- Coerenza cataloghi verificata con test dedicati multi-norma.

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| DM 14/02/1992 | Norme tecniche per le costruzioni in zona sismica — verifiche TA e SL |
| NTC 2008 | Norme tecniche per le costruzioni 2008 — precedente versione NTC |
| EN 1992-1-1 (EC2) | Progettazione strutture in c.a. — flessione, taglio, torsione, SLE |
| EN 1993-1-1 (EC3) | Progettazione strutture in acciaio — classi sezione, instabilità |
| EN 1993-1-8 (EC3) | Progettazione dei collegamenti — bullonature, saldature |
| EN 1998-1 (EC8) | Progettazione strutture sismoresistenti — duttilità, gerarchia |
| CNR-DT 200/2004 | Istruzioni per la progettazione di rinforzi con FRP |
| CNR-DT 200 R1/2013 | Revisione CNR-DT 200 — aggiornamento delamination |
| Cosenza E., Manfredi G., Pecce M. — Strutture in C.A. secondo EC2 (2008) | Riferimento teorico EC2 |
| Mazzolani F.M. — Strutture in Acciaio secondo EC3 (2004) | Riferimento teorico EC3 |

---

## Matrice copertura normativa implementata

| Norma | Stato implementazione | Moduli principali | Ambiti coperti |
| --- | --- | --- | --- |
| DM 14/02/1992 | Completa (fase S) | `src/methods/dm92/checks.py` | TA+SL, flessione, pressoflessione, taglio, torsione |
| NTC 2008 | Completa (wrapper+utility) | `src/methods/ntc2008/checks.py`, `src/methods/ntc2008/combinazioni.py` | Flessione/taglio via EC2, combinazioni ψ, spettro elastico semplificato |
| EN 1992-1-1 (EC2) | Completa (core semplificato) | `src/methods/ec/ec2.py` | Flessione, pressoflessione, taglio, torsione, interazione T-V, SLE |
| EN 1993-1-1 / 1-8 (EC3) | Completa (core+connessioni) | `src/methods/ec/ec3.py`, `src/methods/ec/ec3_connessioni.py` | Classi, flessione, compressione, instabilita, bulloni, saldature |
| EN 1998-1 (EC8) | Completa (dettagli duttili) | `src/methods/ec/ec8.py` | duttilita richiesta/disponibile, gerarchia, taglio gerarchia, nodi, confinamento |
| CNR-DT 200 / R1 2013 | Completa (core FRP) | `src/rinforzi/frp_cnr_dt200.py` | flessione FRP, delaminazione, taglio FRP, confinamento, fattori riduzione |

---

## Struttura file/directory prevista

```text
src/methods/
├── dm92/
│   ├── __init__.py
│   └── checks.py             # (~300 righe) TA + SL: flessione, taglio, torsione, pressoflessione
├── ntc2008/
│   ├── __init__.py
│   ├── checks.py             # (~200 righe) wrapper EC2 con adattamenti italiani (NTC2008 §4)
│   └── combinazioni.py       # utility combinazioni ψ e spettro §3.2
└── ec/
    ├── __init__.py
    ├── ec2.py                # flessione, taglio, torsione, SLE EC2
    ├── ec3.py                # classi sezione, instabilita, M_b,Rd, V_Rd
    ├── ec3_connessioni.py    # (~200 righe) bullonature (Cat.A/B/C), saldature
    └── ec8.py                # μ_φ, gerarchia, confinamento, nodi

src/rinforzi/
├── __init__.py
└── frp_cnr_dt200.py          # (~300 righe) lamine FRP: flessione, taglio, delamination

tests/
├── test_dm92.py              # (~30 test) TA + SL, confronto con DM96
├── test_ntc2008.py           # (~20 test) wrapper EC2, adattamenti
├── test_ec_modules.py        # EC2/EC3/EC8 integrati
└── test_frp.py               # (~15 test) incremento M_Rd, delamination
```

---

## Subfasi pianificate

### S.1 — DM92 verifiche complete

**Stato**: COMPLETATA (core)

- [x] Resistenza caratteristica calcestruzzo: da Rck a fck (`fck = 0.83·Rck`)
- [x] Verifica flessione TA: σ_cls ≤ σ_amm,cls; σ_acc ≤ σ_amm,acc
- [x] Verifica flessione SL: M_Ed ≤ M_Rd con γ_cls=1.5, γ_acc=1.15
- [x] Verifica taglio: metodo bielle inclinate come DM96/EC2
- [x] Verifica torsione: analogia trave a parete sottile
- [x] Pressoflessione: dominio N-M con diagramma di interazione
- [x] Aggiungere catalogo materiali DM92 in `data/materials/`
- [x] Test base DM92 completati (`tests/test_dm92.py`)

### S.2 — NTC2008 verifiche

**Stato**: COMPLETATA (wrapper strutturale)

- [x] Identificare differenze NTC2008 vs NTC2018 (§4.1, §7)
- [x] Wrapper `src/methods/ntc2008/checks.py` su `src/methods/ec/ec2.py`
- [x] Aggiornare fattori amplificazione dinamica (NTC2008 §3.2 vs NTC2018 §3.2)
- [x] Combinazioni di carico NTC2008 (ψ_0, ψ_1, ψ_2 da Tab.2.5.I NTC2008)
- [x] Test funzione wrapper completati (`tests/test_ntc2008.py`)

### S.3 — EC2 flessione/taglio/torsione/SLE

**Stato**: COMPLETATA

- [x] Flessione semplice: equilibrio sezione, x neutro, M_Rd (§6.1)
- [x] Flessione con sforzo normale: dominio N-M per pressoflessione (§6.1)
- [x] Taglio senza armatura: V_Rd,c con fattore k (§6.2.2)
- [x] Taglio con armatura: V_Rd,s e V_Rd,max con angolo θ (§6.2.3)
- [x] Torsione: analogia sezione a parete sottile; verifica T_Rd,c e T_Rd,s (§6.3)
- [x] Interazione taglio-torsione (§6.3.2 formula combinata)
- [x] SLE fessurazione: check semplificato w_k (§7.3.4)
- [x] SLE deformazione: freccia con I_eff interpolato (§7.4.3)
- [x] Test base EC2 completati (`tests/test_ec_modules.py`)

### S.4 — EC3 acciaio: classi sezione, instabilità, connessioni

**Stato**: COMPLETATA

- [x] Classificazione sezione acciaio: rapporti c/t per ali e anima (§5.5 Tab.5.2)
- [x] Resistenza a flessione: M_Rd per classi 1-2 (W_pl) e 3 (W_el) (§6.2.5)
- [x] Resistenza a taglio: V_Rd = A_v·f_y/(√3·γ_M0) (§6.2.6)
- [x] Resistenza a compressione: N_Rd = A·f_y/γ_M0 (§6.2.4)
- [x] Instabilità flessionale: χ da curva di buckling (§6.3.1), λ = √(A·f_y/N_cr)
- [x] Instabilità flessotorsionale: χ_LT, M_b,Rd (§6.3.2)
- [x] Bullonature: resistenza a taglio Cat.A (§3.6.1 EC3-1-8)
- [x] Saldature a cordone d'angolo: F_w,Rd = a·f_vw,d (§4.5.3 EC3-1-8)
- [x] Test base EC3 completati (`tests/test_ec_modules.py`)

### S.5 — EC8 dettagli duttili e gerarchia resistenze

**Stato**: COMPLETATA

- [x] Calcolo duttilità richiesta μ_φ in funzione di q e T_1/T_C
- [x] Verifica μ_φ disponibile: μ_φ = ε_cu/ε_y · 1/(x/d) (sezione con confinamento)
- [x] Calcolo armatura confinamento (staffe): formula EC8 §5.4.3.2.2
- [x] Gerarchia resistenze nodo trave-pilastro: Σ M_Rc ≥ 1.3·Σ M_Rb
- [x] Taglio progetto trave da gerarchia: V_CD = (M_Rb,l + M_Rb,r)/L + V_G (§5.4.3.1.2)
- [x] Taglio progetto pilastro: V_CD = (M_Rc,top + M_Rc,bot)/H_cl (§5.4.3.2.1)
- [x] Nodi trave-pilastro: verifica compressione diagonale V_jhd ≤ η·f_cd·b_j·h_jc (§5.5.3.3)
- [x] Test base EC8 completati (`tests/test_ec_modules.py`)

### S.6 — CNR-DT 200 rinforzi FRP

**Stato**: COMPLETATA

- [x] Materiali FRP: CFRP (E_f=170 GPa, f_fu=2800 MPa), GFRP, AFRP
- [x] Fattori di riduzione: γ_f per tipo FRP; η_a per condizioni ambientali
- [x] Rinforzo a flessione con lamine: incremento ΔM_Rd, verifica ε_fd ≤ ε_de
- [x] Verifica delamination end: check di aderenza/bond
- [x] Rinforzo a taglio con tessuto: incremento ΔV_Rd per wrapping totale e parziale
- [x] Confinamento pilastri con FRP: incremento f_cc = f_c + k_1·f_l (Mander)
- [x] Test base FRP completati (`tests/test_frp.py`)

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/methods/dm92/__init__.py` | 10 | Export modulo DM92 |
| `src/methods/dm92/checks.py` | 300 | Verifiche TA + SL DM92 |
| `src/methods/ntc2008/__init__.py` | 10 | Export modulo NTC2008 |
| `src/methods/ntc2008/checks.py` | 200 | Wrapper EC2 con adattamenti NTC2008 |
| `src/methods/ec/__init__.py` | 15 | Export modulo EC |
| `src/methods/ec/ec2.py` | 160 | EC2: flessione, taglio, torsione, SLE semplificato |
| `src/methods/ec/ec3.py` | 150 | EC3: classi sezione, flessione, instabilità flessotorsionale |
| `src/methods/ec/ec3_connessioni.py` | 200 | EC3-1-8: bullonature, saldature |
| `src/methods/ec/ec8.py` | 100 | EC8: μ_φ, gerarchia nodo |
| `src/rinforzi/__init__.py` | 10 | Export modulo rinforzi |
| `src/rinforzi/frp_cnr_dt200.py` | 300 | CNR-DT 200: lamine FRP, delamination, confinamento |
| `tests/test_dm92.py` | 30 test | TA + SL DM92 |
| `tests/test_ntc2008.py` | 20 test | Wrapper NTC2008 |
| `tests/test_ec_modules.py` | 10 test | EC2+EC3+EC8 core |
| `tests/test_frp.py` | 15 test | FRP: M_Rd, V_Rd, delamination |

---

## Decisioni architetturali consolidate

| Decisione | Esito adottato |
| --- | --- |
| NTC2008: wrapper su EC2 o implementazione autonoma | Wrapper su EC2 (riuso formule, minore duplicazione) |
| EC3 connessioni: incluse in Fase S o separata | Incluse in Fase S tramite modulo dedicato `ec3_connessioni.py` |
| Catalogo materiali DM92 | Catalogo dedicato `data/materials/catalogo_dm92.json` |
| CNR-DT 200 | Riferimento operativo allineato a revisione R1/2013 semplificata |

---

## Limiti noti e punti di attenzione

| Tema | Stato attuale | Mitigazione/nota |
| --- | --- | --- |
| Formule semplificate | Alcuni check sono in forma semplificata per robustezza implementativa | Estendibili con varianti avanzate mantenendo stessa API |
| EC2 taglio con armatura | θ configurabile in range normativo, default conservativo | Documentare nel report il valore usato in ogni verifica |
| EC3 classificazione | Sensibile a parametri geometrici/sezionali | Validare input geometrici prima del calcolo |
| FRP proprietà meccaniche | Dipendono da prodotto/certificazione specifica | Prevedere override input e tracciamento fonte dati nel report |

---

## Validazione e qualità

| Ambito test | File | Esito |
| --- | --- | --- |
| Verifiche Fase S (DM92, NTC2008, EC, FRP) | `tests/test_dm92.py`, `tests/test_ntc2008.py`, `tests/test_ec_modules.py`, `tests/test_frp.py` | 52/52 PASS |
| Cataloghi materiali multi-norma (incluso DM92) | `tests/test_cataloghi_materiali.py` | 22/22 PASS |

Totale evidenze dirette su completamento fase: 74 test verdi mirati (52 verifiche + 22 cataloghi).

---

## Note di pianificazione

- La Fase S ha bassa priorità perché le verifiche NTC2018 (già implementate in fasi precedenti) coprono la maggior parte dei casi d'uso italiani correnti.
- EC2 e NTC2018 sono strutturalmente molto simili: la Fase S.3 deve riutilizzare il codice NTC2018 dove possibile, non duplicarlo.
- I rinforzi FRP (S.6) sono strettamente collegati alla Fase R (edifici esistenti): considerare di anticipare S.6 contestualmente a Fase R se richiesto.
- La Fase S deve garantire che ogni norma produca `SingleCheckResult` con `riferimento_normativo` completo per il confronto multinorma (Q.7).

## Storicizzazione

| Data | Sessione | Azione | Esito |
| --- | --- | --- | --- |
| 2026-03-12 | S1 | Implementazione DM92 + wrapper NTC2008 | 22 test verdi |
| 2026-03-12 | S2 | Implementazione EC2/EC3/EC8 core + integrazione NTC2008 | 32 test verdi |
| 2026-03-12 | S3 | Estensioni avanzate EC2/EC3/EC8 + EC3 connessioni + FRP base | test mirati aggiornati |
| 2026-03-12 | S4 | Chiusura checklist, consolidamento catalogo DM92, validazione cataloghi | 22 test cataloghi verdi |
