# 🔥 FIRE — Analisi Strutturale a Caldo

Modulo completo per il calcolo strutturale con azione termica secondo:
- **NTC 2018** (Cap. 11 Fuoco)
- **EC2-1-2** (Design for fire exposure)
- **Livelli di analisi**: L1 (tabellare), L2 (semplificato), L3 (FEM avanzato)

## Struttura

```
fire/
├── README.md (questo file)
├── FIRE_MASTER.md (entry point principale)
├── FIRE_NORMATIVA_*.md (normativi EC e NTC)
├── FIRE_TEORIA_CALCOLO.md (fondamenti calcolo)
├── FIRE_INTEGRAZIONE_*.md (integrazione nel software)
├── l3_steps/ (9 file — analisi FEM multi-step)
├── benchmarks/ (8 file — casi studio e validazione)
├── solver/ (2 file — engine risolutivo)
└── tests/ (4 file — test e verifiche)
```

## File Principali

- **FIRE_MASTER.md** — Indice centrale, flussi di calcolo, milestone
- **FIRE_NORMATIVA_EC.md** — EN 1992-1-2 (European standard)
- **FIRE_NORMATIVA_NTC.md** — NTC 2018 Cap. 11
- **FIRE_TEORIA_CALCOLO.md** — Fondamenti termo-meccanici

## Sottodirectory

### `l3_steps/` — Analisi L3 Avanzata (FEM)
- Analisi termica 2D/3D
- Analisi meccanica accoppiata
- Modelli costitutivi non-lineari
- Procedure step-by-step

### `benchmarks/` — Validazione Numerica
- Case studio (pilastri, pareti, travi)
- Benchmark vs normativi
- Esempi parametrici (R60, R90, R120)
- Relazioni di calcolo tipo

### `solver/` — Engine Risolutivo
- Algoritmi SVD/iterativi
- Accoppiamento termo-meccanico
- Codice Python riferimento

### `tests/` — Test Suite
- Test pytest end-to-end
- Validazione vs norma
- Casi limite e singolarità

## Stato di Implementazione

- ✅ L1 (tabellare) — COMPLETO
- 🟨 L2 (semplificato) — PARZIALE
- 🟨 L3 (FEM) — IN SVILUPPO

**Ultimo aggiornamento**: 2026-03-29
