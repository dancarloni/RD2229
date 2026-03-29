# Piano Ristrutturazione MEGAPLAN — Sonnet 4.6 Completo

**Generato**: 2026-03-29 05:00 | **Modello**: Claude Sonnet 4.6 | **Scope**: 116 file → 90 file organizzati

---

## EXECUTIVE SUMMARY

**MEGAPLAN** attualmente:
- **116 file** in `/home/user/RD2229/docs/MEGAPLAN/`
- **28.991 linee** di testo
- **Disorganizzato per tema**: 4 mega-file (CHAT_PLAN 3750 linee, AGGREGAZIONE 3026, etc.) + 38 file FIRE + 12 PLAN + 9 KB + 9 GUI + etc.

**Proposta**: Ristrutturare in **8 sottodirectory tematiche** + 1 archived
- **fire/** — 38 file FIRE engineering (L1/L2/L3, FEM, benchmark, test, solver)
- **planning/** — 13 file PLAN (master, calcolo, GUI, incendio, KB)
- **norms/** — 10 file KB normativi (NTC2018, DM, RD2229)
- **gui/** — 9 file GUI (binding, navigazione, codice)
- **implementation/** — 15 file step implementativi
- **secondary_elements/** — 6 file elementi secondari
- **specs/** — 9 file specifiche tecniche
- **reports/** — 7 file template relazioni
- **archived/** — 11 file log/snapshot storici

**Risultato**: ~90 file organizzati + centralized INDEX.md

**Timeline**:
- Esecuzione: ~100 minuti (Haiku)
- Review Copilot: ~45 minuti
- **Total**: Sprint A2.3 completabile in 1 sessione

---

## FASE 1 — ANALISI CRITICA

### Classificazione File

#### Categoria A — Log AI (archiviare)
- `CHAT_PLAN.md` (3750 linee) — trascrizione Copilot
- `AGGREGAZIONE.md` (3026 linee) — trascrizione Copilot
- `AGGREGAZIONE_POST_AGENT.md` (221 linee)
- `2026-02-26-001_PROPOSTA_AGENT.md` (364 linee)
- `2026-02-26-002_PLAN.md` (799 linee)

#### Categoria B — Snapshot/Utility (archiviare)
- `tree_for_m365.md` (3809 linee) — dump directory obsoleto
- `tree_no_dot_cache.json`, `.txt` — snapshot
- `01_ISSUE42_3_SUB_ISSUES.md` — file vuoto

#### Categoria C — Attivi da consolidare
- **FIRE_*** (38 file) → fire/ + sottogruppi (l3_steps/, benchmarks/, solver/, tests/)
- **PLAN_*** (12 file) → planning/
- **KB_*** (9 file) → norms/
- **GUI_*** (9 file) → gui/
- **IMPLEMENTAZIONE_*** (7 file) → implementation/
- **SECONDARY_ELEMENTS_*** (2 file) → secondary_elements/
- **SPEC_*** (4 file) → specs/
- **RELAZIONE_***, **REPORT_BUILDER_*** (7 file) → reports/

---

## FASE 2 — STRUTTURA TARGET

```
docs/MEGAPLAN/
├── INDEX.md [NEW]
├── fire/
│   ├── README.md
│   ├── FIRE_MASTER.md
│   ├── FIRE_NORMATIVA_*.md
│   ├── FIRE_TEORIA_CALCOLO.md
│   ├── FIRE_INTEGRAZIONE_*.md
│   ├── l3_steps/ (9 file)
│   ├── benchmarks/ (8 file)
│   ├── solver/ (2 file)
│   └── tests/ (4 file)
├── planning/ (13 file + README)
├── norms/ (10 file + README)
├── gui/ (9 file + README)
├── implementation/ (15 file + README)
├── secondary_elements/ (6 file + README)
├── specs/ (9 file + README)
├── reports/ (7 file + README)
└── archived/ (11 file + README)
```

**Conteggio**: ~90 file attivi (riduzione da 116 a 90 con archiviazione 11 file storici)

---

## FASE 3 — FILE-TO-FILE MAPPING

### Spostamenti diretti (git mv)

```bash
# archived (priority 1 — mega-file)
git mv docs/MEGAPLAN/CHAT_PLAN.md docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/AGGREGAZIONE.md docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/planning/MEGAPLAN_NTC2018_EC_con_risposte.md docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/tree_for_m365.md docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/tree_no_dot_cache.* docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/2026-02-26-* docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/AGGREGAZIONE_POST_AGENT.md docs/MEGAPLAN/archived/
git mv docs/MEGAPLAN/01_ISSUE42_3_SUB_ISSUES.md docs/MEGAPLAN/archived/

# fire/ (priority 2 — 38 file)
git mv docs/MEGAPLAN/FIRE_MASTER.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_NORMATIVA_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_TEORIA_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_INTEGRAZIONE_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_CHECKLIST_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_GATE_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_CODEMODULE_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_ANALISI_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_NEXT_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_PROGRAMMA_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_PROMPT_*.md docs/MEGAPLAN/fire/
git mv docs/MEGAPLAN/FIRE_PROTOTIPO_*.md docs/MEGAPLAN/fire/

# fire/l3_steps/ (9 file)
git mv docs/MEGAPLAN/FIRE_L3_STEP*.md docs/MEGAPLAN/fire/l3_steps/
git mv docs/MEGAPLAN/FIRE_L3_COSTITUTIVE*.md docs/MEGAPLAN/fire/l3_steps/
git mv docs/MEGAPLAN/FIRE_L3_ANALISI*.md docs/MEGAPLAN/fire/l3_steps/

# fire/benchmarks/ (8 file)
git mv docs/MEGAPLAN/FIRE_BENCHMARK*.md docs/MEGAPLAN/fire/benchmarks/
git mv docs/MEGAPLAN/FIRE_CASE_STUDIO*.md docs/MEGAPLAN/fire/benchmarks/
git mv docs/MEGAPLAN/FIRE_ESEMPIO_*.md docs/MEGAPLAN/fire/benchmarks/
git mv docs/MEGAPLAN/FIRE_ESTENSIONE_*.md docs/MEGAPLAN/fire/benchmarks/
git mv docs/MEGAPLAN/FIRE_RELAZIONE_*.md docs/MEGAPLAN/fire/benchmarks/

# fire/solver/ (2 file)
git mv docs/MEGAPLAN/FIRE_SOLVER_*.md docs/MEGAPLAN/fire/solver/
git mv docs/MEGAPLAN/FIRE_L3_TEST_*.md docs/MEGAPLAN/fire/solver/

# fire/tests/ (4 file)
git mv docs/MEGAPLAN/FIRE_TEST*.md docs/MEGAPLAN/fire/tests/
git mv docs/MEGAPLAN/FIRE_TESTS_*.md docs/MEGAPLAN/fire/tests/
git mv docs/MEGAPLAN/FIRE_VERIFICA_*.md docs/MEGAPLAN/fire/tests/

# planning/ (13 file)
git mv docs/MEGAPLAN/planning/PLAN_*.md docs/MEGAPLAN/planning/
git mv docs/MEGAPLAN/planning/MEGAPLAN_NTC2018_MasterPlan.md docs/MEGAPLAN/planning/

# norms/ (10 file)
git mv docs/MEGAPLAN/norms/KB_*.md docs/MEGAPLAN/norms/
git mv docs/MEGAPLAN/VERIFICHE_RD2229.md docs/MEGAPLAN/norms/

# gui/ (9 file)
git mv docs/MEGAPLAN/GUI_*.md docs/MEGAPLAN/gui/

# implementation/ (15 file)
git mv docs/MEGAPLAN/IMPLEMENTAZIONE_*.md docs/MEGAPLAN/implementation/
git mv docs/MEGAPLAN/INTEGRAZIONE_*.md docs/MEGAPLAN/implementation/
git mv docs/MEGAPLAN/STEP2*.md docs/MEGAPLAN/implementation/
git mv docs/MEGAPLAN/END_STEP2*.md docs/MEGAPLAN/implementation/
git mv docs/MEGAPLAN/FASE2_*.md docs/MEGAPLAN/implementation/
git mv docs/MEGAPLAN/CodeModule_CONTRACT.md docs/MEGAPLAN/implementation/

# secondary_elements/ (6 file)
git mv docs/MEGAPLAN/SECONDARY_ELEMENTS_*.md docs/MEGAPLAN/secondary_elements/
git mv docs/MEGAPLAN/SPEC_SecondaryElementSpec.md docs/MEGAPLAN/secondary_elements/
git mv docs/MEGAPLAN/SPEC_RC_*.md docs/MEGAPLAN/secondary_elements/
git mv docs/MEGAPLAN/CONFIG_NTC2018_SECONDARY_ELEMENTS_*.md docs/MEGAPLAN/secondary_elements/

# specs/ (9 file)
git mv docs/MEGAPLAN/SPEC_NTC2018_*.md docs/MEGAPLAN/specs/
git mv docs/MEGAPLAN/NTC2018_SPECTRUM_*.md docs/MEGAPLAN/specs/
git mv docs/MEGAPLAN/planning/PLAN__NTC2018_EC_*.md docs/MEGAPLAN/specs/
git mv docs/MEGAPLAN/TEST_PLAN_*.md docs/MEGAPLAN/specs/
git mv docs/MEGAPLAN/VERIFICATION_*.md docs/MEGAPLAN/specs/
git mv docs/MEGAPLAN/verification_gap.md docs/MEGAPLAN/specs/

# reports/ (7 file)
git mv docs/MEGAPLAN/RELAZIONE_*.md docs/MEGAPLAN/reports/
git mv docs/MEGAPLAN/REPORT_BUILDER_*.md docs/MEGAPLAN/reports/
git mv docs/MEGAPLAN/APPLICATION_REPORT.md docs/MEGAPLAN/reports/
git mv docs/MEGAPLAN/MANIFEST_APPLICAZIONE.md docs/MEGAPLAN/reports/
```

### File da creare (NEW)

```bash
# Index e README per ogni sottodirectory (10 file)
docs/MEGAPLAN/INDEX.md
docs/MEGAPLAN/fire/README.md
docs/MEGAPLAN/planning/README.md
docs/MEGAPLAN/norms/README.md
docs/MEGAPLAN/gui/README.md
docs/MEGAPLAN/implementation/README.md
docs/MEGAPLAN/secondary_elements/README.md
docs/MEGAPLAN/specs/README.md
docs/MEGAPLAN/reports/README.md
docs/MEGAPLAN/archived/README.md
```

---

## FASE 4 — RISK ASSESSMENT

| Rischio | Probabilità | Mitigazione |
|---------|-------------|------------|
| **Broken links interni** | ALTA | Grep per `(FIRE_\|PLAN_\|KB_\|GUI_)` prima dello spostamento; aggiorna riferimenti |
| **AGGREGAZIONE.md contiene vincoli LOCKED** | MEDIA | Verificare che `docs/specs/SPEC_0*.md` copra i vincoli prima di archiviare |
| **Cross-repository references** | MEDIA | Grep `MEGAPLAN/` in `docs/` + `tests/` + `src/` prima di esecuzione |
| **Git history** | BASSA | Usare `git mv` per preservare; eseguire in singolo commit atomico |

---

## FASE 5 — DOMANDE APERTE (User Input Required)

**D1 — Target numerico**:
- Vuoi ~90 file (struttura tematica, consigliata)
- O ~50 file (merge aggressivo, richiede editing)?

**D2 — AGGREGAZIONE.md**:
- Vincoli "LOCKED" già migrati in `docs/specs/SPEC_0*.md`?
- OK per archiviare con sicurezza?

**D3 — PLAN__NTC2018_EC_Integrazoini.md** (866 linee):
- Documento attivo o superseded?
- Vuoi rinominarlo correggendo il typo?

**D4 — Strategia linking**:
- Aggiornare riferimenti a nuovi path?
- O creare redirect stub?

**D5 — docs/MEGAPLAN vs docs/megaplan**:
- Esiste `docs/megaplan/` (lowercase, vuota)
- Unificarle o mantenerle separate?

---

## FASE 6 — SEQUENZA ESECUZIONE (Sessione 2)

1. **Audit cross-reference** (10 min) — Grep per `MEGAPLAN/`
2. **mkdir + archived** (5 min) — Creare dir + spostare mega-file
3. **git mv FIRE_*** (15 min) — 38 file FIRE
4. **git mv altri** (20 min) — PLAN + KB + GUI + IMPL + SEC + SPEC + REPORT
5. **Crea INDEX.md + README.md** (30 min) — 10 file nuovi
6. **Verifica link + fix** (15 min) — Grep e aggiorna riferimenti
7. **Update docs/index.md** (5 min) — Link a MEGAPLAN/INDEX.md

**Total**: 100 minuti esecuzione + 45 minuti Copilot review

---

## CRITICAL FILES FOR VERIFICATION

- `/home/user/RD2229/docs/MEGAPLAN/AGGREGAZIONE.md` — Verificare vincoli LOCKED
- `/home/user/RD2229/docs/specs/SPEC_0*.md` — Confermare coverage vincoli
- `/home/user/RD2229/docs/index.md` — Aggiornare link post-ristrutturazione

---

**Documento**: Sprint A2.3 Planning | **Status**: Ready for Sessione 2
**Autore**: Sonnet 4.6 | **Data**: 2026-03-29
