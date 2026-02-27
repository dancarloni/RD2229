# AGENT EXECUTION CONTEXT

> Ultima esecuzione batch: 2026-02-26

## Contesto caricato

| File | Decisioni LOCKED rilevate | Conflitti/Rischi |
|------|--------------------------|-----------------|
| docs/MEGAPLAN/AGGREGAZIONE.md | Separazione Model/Engine/Persistence/UI; SQLite MVP; Trace obbligatorio; Nessun valore normativo inventato | Nessuno |
| docs/MEGAPLAN/AGGREGAZIONE_POST_AGENT.md | A/D/B completati; 510 pass, 0 fail in ambiente locale | Test count diverge in CI headless (479 pass, 9 skip) |
| docs/MEGAPLAN/2026-02-26-002_PLAN.md | Stream A→D→B→C→E; Strategia B | Ordine consigliato confermato |
| docs/specs/PLAN_NEXT_IMPLEMENTATION.md | Stream A/D/B: completati; E2 baseline avviato | C/E1 ancora aperti |
| docs/specs/BLOCKERS.md | Blocker 1/2: CHIUSI | Monitoraggio regressione continuo |
| pyproject.toml | src-layout, rd2229 package, setuptools | — |
| pytest.ini | pythonpath=src .; markers: gui, slow | — |

## Vincoli LOCKED

1. App offline mono-utente, un progetto alla volta.
2. Separazione architetturale `Model ≠ Engine ≠ Repository/Persistence ≠ UI`.
3. SQLite è lo storage primario MVP con schema versioning (`PRAGMA user_version`).
4. Trace obbligatorio in ogni risultato: `run_id`, `norm_references[]`, `method_id`, `assumptions`, `warnings`.
5. Plugin/discovery via `ModuleSpec` — estendere senza rompere API esistenti.
6. Nessun valore normativo inventato: usare `TODO(NTC/EC/RD)` espliciti.
7. Modulo incendio separato dal core strutturale.
8. Strategia B: 2 test rossi preesistenti accettati solo se documentati e non peggiorano il quadro.

## Decisioni OPEN

| ID | Descrizione | Best-judgment applicato |
|----|-------------|------------------------|
| OQ-001 | Priorità E1 vs E2 | E1 prima di E2 per compliance |
| OQ-002 | Selezione macro bandiera stream C | CA_SLU.VerifResistCA_SLU_TensNorm (alta freq, indipendente da Excel GUI) |
| OQ-003 | Livello validazione jsoncode | Minimo + warning ora, strict in iterazione successiva |

## Assunzioni

- La macro bandiera selezionata per stream C è `CA_SLU::VerifResistCA_SLU_TensNorm` (verifica SLU resistenza tensioni normali, CA generico).
- Il report MVP è JSON-first; HTML/PDF sono stream successivi.
- Tutti i TODO normativi presenti nel codice sono intenzionali e non errori.
