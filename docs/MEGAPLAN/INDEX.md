# 🗂️ MEGAPLAN — Indice Centrale

**Last Updated**: 2026-03-29 | **Total Files**: ~90 (reorganized from 116)

Questo è l'indice centrale della documentazione MEGAPLAN ristrutturata per tematiche.

---

## 📚 Tematiche Principali

### 🔥 [FIRE](fire/README.md) — Analisi Strutturale a Caldo
Modulo completo per analisi termica (L1, L2, L3).
- **Files**: 38 (fire/ + l3_steps/ + benchmarks/ + solver/ + tests/)
- **Status**: L1✅ L2🟨 L3🟨
- **Entry**: [FIRE_MASTER.md](fire/FIRE_MASTER.md)

### 📋 [PLANNING](planning/README.md) — Piano Operativo
Documentazione del piano di lavoro e roadmap progetto.
- **Files**: 13 (piani per fase)
- **Status**: ✅ Aggiornato
- **Entry**: [PLAN_MASTER.md](planning/PLAN_MASTER.md)

### 📚 [NORMS](norms/README.md) — Knowledge Base Normative
Archivio Knowledge Base per tutte le norme strutturali coperte.
- **Files**: 10 (RD2229, DM72-96, NTC2008-2018)
- **Status**: ✅ KB completa
- **Entry**: [KB_NTC2018.md](norms/KB_NTC2018.md)

### 🎨 [GUI](gui/README.md) — Interfaccia Utente
Documentazione Qt/PySide6 per GUI principale.
- **Files**: 9 (widget, binding, support)
- **Status**: 🟨 In sviluppo
- **Entry**: [GUI_MAIN_PY_NAVIGAZIONE.md](gui/GUI_MAIN_PY_NAVIGAZIONE.md)

### ⚙️ [IMPLEMENTATION](implementation/README.md) — Step Implementativi
Documentazione step-by-step implementazione.
- **Files**: 15 (workflow, step, integrazioni)
- **Status**: 🟨 In corso
- **Entry**: [CodeModule_CONTRACT.md](implementation/CodeModule_CONTRACT.md)

### 🏗️ [SECONDARY_ELEMENTS](secondary_elements/README.md) — Elementi Secondari
Documentazione per tramezzi, impianti, balconate, etc. (NTC 2018 Cap. 7.8).
- **Files**: 6 (spec, automation)
- **Status**: 🟨 Parziale
- **Entry**: [SECONDARY_ELEMENTS_MASTER.md](secondary_elements/SECONDARY_ELEMENTS_MASTER.md)

### 📋 [SPECS](specs/README.md) — Specifiche Tecniche
Specifiche tecniche, test plan, verifiche.
- **Files**: 9 (spec, test plan, spettri)
- **Status**: 🟨 In sviluppo
- **Entry**: [TEST_PLAN_NTC2018.md](specs/TEST_PLAN_NTC2018.md)

### 📄 [REPORTS](reports/README.md) — Template Relazioni
Template per relazioni tecniche e report builder.
- **Files**: 7 (template, builder, output)
- **Status**: 🟨 Integrazione
- **Entry**: [RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md](reports/RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md)

### 📦 [ARCHIVED](archived/README.md) — Archivio Storico
File storici, transcript, snapshot deprecated.
- **Files**: 11 (mega-files, log, snapshot)
- **Status**: 📦 Archiviato
- **Entry**: Vedi README per lista

---

## 🔗 Navigazione Veloce

| Sezione | File Principale | Status |
|---------|-----------------|--------|
| **FIRE L3 (Fuoco)** | [FIRE_MASTER.md](fire/FIRE_MASTER.md) | 🟨 |
| **NTC2018 (Norme)** | [KB_NTC2018.md](norms/KB_NTC2018.md) | ✅ |
| **GUI (Interfaccia)** | [GUI_MAIN_PY_NAVIGAZIONE.md](gui/GUI_MAIN_PY_NAVIGAZIONE.md) | 🟨 |
| **Planning** | [PLAN_MASTER.md](planning/PLAN_MASTER.md) | ✅ |
| **Test & Spec** | [TEST_PLAN_NTC2018.md](specs/TEST_PLAN_NTC2018.md) | 🟨 |
| **Report** | [RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md](reports/RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md) | 🟨 |
| **Archive** | [archived/README.md](archived/README.md) | 📦 |

---

## 📊 Statistiche

- **Totale file**: ~90 (ridotto da 116)
- **Subdirectory tematiche**: 9 (fire/, planning/, norms/, gui/, implementation/, secondary_elements/, specs/, reports/, archived/)
- **File README per tema**: 9 (completati in questa sessione)

## 🎯 Milestone Sprint A2.3

- ✅ Creazione 9 subdirectory
- ✅ Git mv 116 file in categorie tematiche
- ✅ Creazione 9 README.md (per tema)
- ✅ Creazione INDEX.md centrale
- ⏳ **NEXT**: Validare cross-link + aggiornare docs/index.md (Sprint A3-A4)

---

## 📖 Come Usare

1. **Navigazione iniziale**: Partire da questa INDEX.md
2. **Per tema specifico**: Cliccare link tema → leggi README.md
3. **Per file specifico**: Usare README.md per trovare file dentro tema
4. **Per ricerca**: `grep -r "keyword" docs/MEGAPLAN/`
5. **Per git history**: `git log --follow docs/MEGAPLAN/[tema]/[file]`

---

## 🔄 Relazione con docs/ Root

- **docs/index.md** → Entry point generale progetto (tutte le sezioni)
- **docs/PIANO_LAVORO.md** → SOURCE OF TRUTH (stato, changelog, decisioni)
- **docs/MEGAPLAN/INDEX.md** → Questo file (navigazione tematiche)
- **docs/planning/** → Consolidamento 98 file piano_fase (in root docs/, non MEGAPLAN/)

**Best practice**: Leggere PIANO_LAVORO.md → MEGAPLAN/INDEX.md → tema specifico → README.md → file dettagliato

---

**Autore**: Claude AI (Sonnet 4.6) | **Sessione**: 2026-03-29 | **Stato**: ✅ Completo
