# Documentazione Teorica — Moduli RD2229

Questa directory contiene la **documentazione teorica dettagliata** per i moduli di calcolo strutturale di RD2229.

---

## Documenti disponibili

### 1. 📘 Muratura LV3 — Modello SVD e Accoppiamento Taglio-Flessione
**File**: [`muratura_lv3_macro_elemento.md`](./muratura_lv3_macro_elemento.md) (38 KB, 1012 righe)

**Contenuto**:
- Panoramica del modello e contesto normativo (LV1/LV2/LV3)
- Equazioni fondamentali accoppiamento σ-τ con diagonalizzazione SVD
- Parametri del modello (v₀, μ, f_d, E_m, G_m) per muratura storica italiana
- Quattro criteri di rottura: fessurazione diagonale (Turnšek-Čačovič), scorrimento (Mohr-Coulomb), pressoflessione, compressione eccentrica
- Algoritmo SVD iterativo con pseudocodice e controllo convergenza
- Esempio numerico step-by-step (maschio murario, δ=1 cm, σ₀=0.10 kg/cm²)
- Approfondimento: rotazione degli assi principali durante carico laterale
- Tabella comparativa tra NTC2018, EN 1996-1-1, ASCE 41-06
- Struttura moduli Python proposti e pseudo-interfaccia
- Cronologia implementazione (Planning Fase U)

**Stato**: ✅ RICERCA TEORICA COMPLETATA (2026-03-29)

**Prossimi step**: Implementazione codice (Fase U.6b), validazione benchmark ASCE 41

---

### 2. ⚡ Muratura LV3 — Quick Reference
**File**: [`MURATURA_LV3_SUMMARY.md`](./MURATURA_LV3_SUMMARY.md) (7.6 KB)

**Contenuto**:
- Equazioni fondamentali (un foglio)
- Parametri essenziali (tabella)
- Algoritmo SVD (pseudocodice compatto)
- Esempio numerico sintetico (δ=1 cm)
- Curva di capacità (pushover)
- Criteri di rottura (envelope)
- Fenomeno rotazione assi principali
- Parametri NTC2018 LC1/LC2/LC3
- Connessione al codice RD2229
- Benchmark ASCE 41-06
- Timeline implementazione

**Uso**: Consultazione rapida durante implementazione codice

---

### 3. 📋 DM96 — Formule Stato Limite Esercizio
**File**: [`dm96_formule_stato_limite_esercizio.md`](./dm96_formule_stato_limite_esercizio.md) (6.8 KB)

**Contenuto**:
- Formule e metodi per calcolo secondo DM 20/11/1996
- Stato limite di esercizio
- Interazione tra moduli

---

## Struttura della ricerca (2026-03-29)

### Fase 1: Ricerca Teorica ✅
- [x] Identificazione norme rilevanti (NTC2018, EN 1996-1-1, Circ. 7/2019, ASCE 41-06)
- [x] Estrazione formule fondamentali (σ₁, σ₂, Mohr-Coulomb, Turnšek-Čačovič)
- [x] Parametrizzazione per muratura storica italiana
- [x] Algoritmo SVD iterativo (pseudocodice)
- [x] Esempio numerico completo con validazione
- [x] Approfondimento fenomeni critici (rotazione assi)

### Fase 2: Preparazione Implementazione ✅
- [x] Tabella comparativa norme internazionali
- [x] Pseudo-interfaccia Python (classi, metodi)
- [x] Struttura moduli proposti
- [x] Unit test framework e benchmark ASCE 41-06

### Fase 3: Implementazione (⏳ In coda per U.6b)
- [ ] `src/methods/muratura/macro_elemento_lv3.py` (SVD iterativo)
- [ ] `src/methods/muratura/verifica_lv3.py` (demand-capacity)
- [ ] `src/methods/muratura/curve_capacita.py` (pushover)
- [ ] `tests/test_macro_elemento_lv3.py` (SVD, convergenza)
- [ ] Benchmark ASCE 41-06 Table 6-28

---

## Normatività e Riferimenti

### NTC2018 + Circolare 7/2019
- **§7.8** — Edifici esistenti in muratura (analisi sismica)
- **§7.8.2.2** — Resistenza pannelli murari (3 criteri)
- **§C8.7.1.3.1.1** — Parametri meccanici per LC1/LC2/LC3
- **Tab. 4.5.IV** — Resistenza compressione f_d
- **Tab. 4.5.III** — Moduli elastici E_m

### EN 1996-1-1 (Eurocode 6)
- **Cap. 3** — Proprietà materiali
- **Tab. 3.4** — Resistenza taglio caratteristica f_vk0
- **Tab. 3.6** — Moduli elastici per tipo muratura
- **Cap. 6** — Calcolo della resistenza (Mohr-Coulomb, stati biassiali)

### ASCE 41-06 (USA)
- **Cap. 6–7** — Macro-elementi, modelli non-lineari
- **Tab. 6-28** — Curve di capacità muratura (benchmark)
- **Metodologia** — Demand-capacity approach, fattori degradazione

---

## Come usare questa documentazione

### Per implementatori (fase U.6b/U.6c)
1. Leggere [`muratura_lv3_macro_elemento.md`](./muratura_lv3_macro_elemento.md) sezioni 2–5 (equazioni, algoritmo)
2. Fare riferimento a [`MURATURA_LV3_SUMMARY.md`](./MURATURA_LV3_SUMMARY.md) per pseudocodice compatto
3. Implementare SVD iterativo in `macro_elemento_lv3.py`
4. Validare su benchmark ASCE 41-06 (sezione 9 di Summary)

### Per reviewer/audit
1. Sezione 6 (esempio numerico) — validazione manuale step-by-step
2. Sezione 10 (tabella comparativa) — coerenza fra norme
3. Benchmark ASCE 41 — confronto con esterno

### Per documentazione/training
1. Iniziare con [`MURATURA_LV3_SUMMARY.md`](./MURATURA_LV3_SUMMARY.md) (5 minuti)
2. Approfondire con [`muratura_lv3_macro_elemento.md`](./muratura_lv3_macro_elemento.md) (30 minuti)
3. Consultare sezione 7bis per fenomeni non-lineari

---

## Cronologia versioni

| Data | Versione | Evento |
|------|----------|--------|
| 2026-03-29 | 1.0-BOZZA-TEORIA | Ricerca teorica completata, documenti creati |
| 2026-04-XX | 1.0-IMPLEMENTAZIONE | Codice Python implementato e testato (pendente U.6b) |
| 2026-05-XX | 1.0-VALIDATO | Benchmark ASCE 41-06 OK, pronti per produzione |

---

## Contatti e Note

**Autore**: RD2229 — Progetto Calcolo Strutturale Edifici Muratura
**Data creazione**: 2026-03-29
**Stato complessivo**: ✅ RICERCA TERMINATA — Pronto per codifica fase U.6b
**Ultimo aggiornamento**: 2026-03-29 (creazione e completamento docs)

---

## Links interni RD2229

- **Piano di lavoro**: [`/docs/PIANO_LAVORO.md`](/docs/PIANO_LAVORO.md) — stato avanzamento progetto
- **Fase U (Analisi sismica)**: [`/docs/planning/piano_fase_U.md`](/docs/planning/piano_fase_U.md)
- **Fase R (Edifici esistenti)**: [`/docs/planning/piano_fase_R.md`](/docs/planning/piano_fase_R.md)
- **Verifiche muratura (codice)**: [`/src/methods/muratura/verifiche.py`](/src/methods/muratura/verifiche.py)
- **Resistenza muratura (codice)**: [`/src/methods/muratura/resistenza.py`](/src/methods/muratura/resistenza.py)

---

**Fine documentazione teorica — Inizio implementazione**
