# Piano di consolidamento — geometria, GUI, test e documentazione

Versione: 2026-02-14
Scopo: trascrivere e rendere eseguibile il piano di lavoro per l'unificazione dei moduli di geometria/graphics, l'aumento della copertura dei test e la redazione di documentazione collegata al codice.

## Obiettivi principali
- Consolidare le implementazioni duplicate (geometry, graphics, section_calculations) in moduli canonici.
- Documentare l'architettura e le API chiave con esempi eseguibili.
- Aumentare la copertura dei test (calcoli critici e API GUI headless).
- Rendere il piano recuperabile e collegato al codice tramite file in `docs/`.

## Strategia di lavoro (PR piccoli)
- PR 1 — Docs + audit (skeleton + piano): bassa rischiosità — subito.
- PR 2 — Tests per calcoli critici (regressione numerica): medio rischio.
- PR 3 — GUI tests + demo: medio rischio.
- PR 4 — Cleanup finale (rimozione backup/.bak): basso rischio.

> Ogni PR deve includere: descrizione, checklist (tests, docs, CHANGELOG), e riferimenti ai file interessati.

## Fasi (azione immediata → deliverable)
1. Audit & inventory
   - Deliverable: `docs/audit_report.md` (file inventario + gap list).
2. Analisi dei calcoli
   - Deliverable: unit tests di regressione + `docs/section-calculations.md`.
3. Analisi GUI & controller
   - Deliverable: `docs/graphics.md`, test headless (`FakeCanvas`) e demo script.
4. Trascrizione documentazione collegata
   - Deliverable: pagine `docs/geometry.md`, `docs/section-calculations.md`, `docs/graphics.md` e aggiornamento `mkdocs.yml`.
5. Test & CI hardening
   - Deliverable: CI verde (ruff / mypy / pytest), badge aggiornato.
6. Refactor / Cleanup
   - Deliverable: rimozione duplicati residui, commit pulito.
7. Post‑merge
   - Deliverable: aggiornamento `IMPLEMENTATION_SUMMARY.md`, rimozione backup `.bak` dopo approvazione.

## Criteri di accettazione per ogni PR
- Tutti i test passano (locale + CI).
- Documentazione aggiornata e linkabile.
- Nessuna regressione numerica su casi di riferimento.
- CHANGELOG aggiornato.

## Mappa file → pagine docs (iniziale)
- `src/core_calculus/core/geometry_model.py` → `docs/geometry.md`
- `src/core_calculus/section_calculations.py` → `docs/section-calculations.md`
- `apps/sections/section_graphics.py` → `docs/graphics.md`

## Checklist operativa (immediata)
- [x] Trascrivere il piano in `docs/consolidation-plan.md` (questo file).
- [x] Creare `docs/audit_report.md` con inventario iniziale.
- [ ] Aprire PR separati come da strategia.
- [ ] Implementare test mancanti e aggiornare documentazione.

## Prossimi passi (per Copilot)
1. Completare audit e generare report (file aggiunto).
2. Aggiungere skeleton delle pagine docs collegate.
3. Inserire unit test prioritari per `section_calculations`.
4. Aprire PR incrementali seguendo la strategia sopra.

---

Nota: il piano è tracciato e recuperabile in `docs/consolidation-plan.md`. Procedo con la creazione del report di audit e il primo commit sulla branch di lavoro.