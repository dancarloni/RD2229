# 📋 Planning & Fase — Indice Centrale

Questa directory contiene il **piano di lavoro dettagliato** per ogni fase del progetto RD2229 (A→Y, X1→X8, S1→S9).

**Ultimo aggiornamento**: 2026-03-29 | **Status**: Sprint A2 — Consolidamento planning

---

## 📑 STRUTTURA

```
planning/
├── README.md (questo file)
├── PIANO_LAVORO.md (⭐ SOURCE OF TRUTH — in root)
├── fase_A/ → piano_fase_A.md + audit_fase_A.md
├── fase_B/ → piano_fase_B.md + audit_fase_B.md
├── ...
├── fase_Y/ → piano_fase_Y.md + audit_fase_Y.md
├── extended_X/ → fase X1-X8 (dettagli implementativi)
└── secondary_S/ → fase S1-S9 (elementi secondari)
```

---

## 🎯 FASI PRINCIPALI (A-Y)

| Fase | Nome | Piano | Audit | Status |
|------|------|-------|-------|--------|
| A | Setup & Environment | [piano_fase_A.md](fase_A/piano_fase_A.md) | [audit_fase_A.md](fase_A/audit_fase_A.md) | ✅ |
| B | Core Library | [piano_fase_B.md](fase_B/piano_fase_B.md) | [audit_fase_B.md](fase_B/audit_fase_B.md) | ✅ |
| C | Material Repository | [piano_fase_C.md](fase_C/piano_fase_C.md) | [audit_fase_C.md](fase_C/audit_fase_C.md) | ✅ |
| D-F | Verifiche Base | [piano_fase_D→F.md](extended/...md) | Audit correlati | ✅ |
| G-O | Verifiche Avanzate | [piano_fase_G→O.md](extended/...md) | Audit correlati | 🟨 |
| P-Z | GUI & Integration | [piano_fase_P→Z.md](extended/...md) | Audit correlati | 🟨 |
| U | **Muratura LV3** | [piano_fase_U.md](fase_U/piano_fase_U.md) | [audit_fase_U.md](fase_U/audit_fase_U.md) | 🔴 BLOCKED |

---

## 🔧 FASI ESTESE (X1-X8, S1-S9)

### **Sottofasi X** (Extended — Implementativi dettagliati)
- **X1**: Tipologie input (sezioni, materiali, carichi)
- **X2**: Combinazioni di carico (SLU, SLE)
- **X3**: Verifiche SLU (flessione, taglio, torsione)
- **X4**: Verifiche SLE + Vibrazioni
- **X5**: Aperture & cerchiature
- **X6**: Report & Tracciabilità
- **X7**: Casi speciali
- **X8**: Optimizzazione & Refinement

### **Sottofasi S** (Secondary Elements — Elementi secondari NTC2018)
- **S1-S9**: Tramezzi, impianti, facciate, balconate, parapetti, scale, scalone, etc.

---

## 🔗 LINK PRINCIPALI

- ⭐ **[PIANO_LAVORO.md](../PIANO_LAVORO.md)** — SOURCE OF TRUTH (fase status, commit, changelog)
- 📊 **[progress/STATUS.md](../progress/STATUS.md)** — Dashboard attuale
- 🏗️ **[ARCHITECTURE.md](../ARCHITECTURE.md)** — Decisioni architetturali (locked/open)

---

## 📝 COME USARE QUESTA DIRECTORY

1. **Leggi PIANO_LAVORO.md** in root per overview stato
2. **Vai a fase_X/** per piano + audit dettagliato della fase
3. **Update piano dopo completamento**:
   - Modifica `piano_fase_X.md` con checkbox completed
   - Update PIANO_LAVORO.md con commit hash
   - Commit e push

---

## 🎯 MILESTONE PROSSIMI

- ✅ Sprint A1: Rimosso file deprecated
- ✅ Sprint A2.1: Entry point centrale (docs/index.md)
- 🟨 **Sprint A2.2 (IN PROGRESS)**: Consolidamento planning directory
  - Creato `docs/planning/README.md` (questo file)
  - In progress: Spostamento 98 file `piano_fase_*` e `audit_fase_*`
- 🟨 Sprint B: Bug fixes (formule DM96, stub DM72/74, unità misura)
- 🔴 Sprint C/U: Fase U (muratura LV3) + Test coverage

---

**Generated**: 2026-03-29 | **Maintainer**: Claude AI (Sonnet 4.6)
