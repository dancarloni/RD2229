# 📘 RD2229 — Documentazione Centrale

Benvenuto! Questa è la **home page della documentazione** del progetto RD2229 (Calcolo Strutturale Edifici Esistenti).

**Ultimo aggiornamento**: 2026-03-29 | **Status**: Sprint A (Refactoring Documentazione)

---

## 🚀 INIZIO VELOCE

### Per sviluppatori
- 📖 Leggi [`CLAUDE.md`](/CLAUDE.md) — Convenzioni, unità misura, struttura moduli
- 🏗️ Vedi [`ARCHITECTURE.md`](ARCHITECTURE.md) — Decisioni architetturali locked/open
- 🧪 Esegui test: `python -m pytest tests/ -v`

### Per capire lo stato del progetto
- 📋 [`PIANO_LAVORO.md`](PIANO_LAVORO.md) — **SOURCE OF TRUTH** — fasi A→Y, test coverage, milestone
- 📊 [`progress/STATUS.md`](progress/STATUS.md) — Dashboard stato attuale

---

## 📚 SEZIONI DOCUMENTAZIONE

### 🎯 **Pianificazione & Roadmap**
- 📍 [`PIANO_LAVORO.md`](PIANO_LAVORO.md) — Piano di lavoro completo (fasi A-Y)
- 📁 [`planning/`](planning/) — Dettagli fasi
- 🗓️ [`PIANO_LAVORO_GUI.md`](PIANO_LAVORO_GUI.md) — Roadmap GUI

### 🏛️ **Architettura & Design**
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Decisioni architetturali
- [`specs/`](specs/) — Specifiche dettagliate
- [`ARCHITETTURA_GUI.md`](ARCHITETTURA_GUI.md) — Progettazione GUI Qt

### 🔧 **Implementazione**
- [`implementation/_theory/`](implementation/_theory/) — Teoria e formule
- [`implementation/norms/`](implementation/norms/) — Knowledge bases per norma
- [`specs/`](specs/) — Dettagli implementativi

### 🔄 **Pipeline & Processi**
- [`pipelines/README.md`](pipelines/README.md) — Indice pipeline (P00-P29)
- [`pipelines/MASTER_MATRIX.md`](pipelines/MASTER_MATRIX.md) — Orchestrazione

### 🔥 **Feature Specifiche**
- 📐 [`features/secondary_elements/`](features/secondary_elements/) — Elementi secondari
- 🧮 [`features/material_editor/`](features/material_editor/) — Material Editor
- 🔥 [`features/fire/`](features/fire/) — Fire engineering (L1-L3)

### 💾 **Stato & Progress**
- [`progress/STATUS.md`](progress/STATUS.md) — Dashboard attuale
- [`progress/`](progress/) — Rapporti verifica

### 🧠 **Memoria & Context**
- [`memory/`](memory/) — Session memory e codebase map

### 📖 **Archivio**
- [`archived/`](archived/) — File storici
- [`megaplan/`](megaplan/) — Archivio MEGAPLAN

---

## 🎯 BLOCKERS NOTI

| Blocker | Status |
|---------|--------|
| **Fase U** — Muratura LV3 | 🔴 BLOCCATO |
| **Formule DM96** — 3 TODO | 🟠 IN LAVORO |
| **Stub DM72/74** — Falsi | 🟠 IN LAVORO |
| **Unità misura** — Incoerenti | 🟠 IN LAVORO |

---

## 🔗 QUICK LINKS

**Gestione progetto**:
- [`CLAUDE.md`](/CLAUDE.md) — Convenzioni (LEGGI PRIMA)
- [`PIANO_LAVORO.md`](PIANO_LAVORO.md) — Source of truth
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Linee guida sviluppo

**Codice**:
- `src/core/` — Core modules
- `src/methods/` — Calcoli normativi
- `tests/` — Suite test pytest (~1293 test)

---

**Last updated**: 2026-03-29 | **Session**: Claude AI Plan mode
