
FASE 2 — Baseline congelata (PLAN‑ONLY)
Data: 2026‑02‑21
Stato: Fase 1 completata; Fase 2 in PLAN; lista file target confermata.


1) Decisioni vincolanti già assunte
1.1 Consolidamento 2A‑1 (conservativo) — VINCOLANTE

Source of truth del modulo “Secondary Elements” = src/codes/secondary_elements/*.
Nessuna creazione di albero parallelo methods/verification/secondary_elements/* in Fase 2 (anti‑doppioni).
1.2 Automation aggiornata (addendum 2A‑1) — VINCOLANTE

Il file docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md contiene l’addendum “0‑bis mapping 2A‑1” incollato dall’utente.


2) Lista finale FILE TARGET (congelata)


Questa lista è la baseline operativa per la Fase 2. Qualunque implementazione deve limitarsi a questi target (salvo future variazioni deliberate in PLAN).


2.1 TOUCH (adattare/estendere)

src/codes/secondary_elements/models.py
src/codes/secondary_elements/checks.py
src/codes/secondary_elements/storage_adapter.py
verifications/secondary_elements/dispatcher.py
2.2 CREATE (solo se necessari — stub/interfacce; sempre sotto src/codes/secondary_elements/)

src/codes/secondary_elements/ta_models.py (stub)
src/codes/secondary_elements/drift_models.py (stub; Metodo B drift proxy)
src/codes/secondary_elements/anchors_capacity.py (stub; ETA‑first manual)
2.3 CONFIG

config/calculation_codes/SECONDARY_ELEMENTS.jsoncode
2.4 DOC (obbligatorio prima dell’implementazione)

docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md


3) Contratti (Definition of Done) — Fase 2
3.1 Contratti output (sempre)

Ogni risultato del modulo Secondary Elements deve includere:trace.run_id
norm_references[]
decision_log minimo (metodo Ta/drift e assunzioni)
3.2 Gating drift (Metodo B)

Drift SLE: Metodo B (shear‑building proxy + soft_storey_factor) con confidence = LOW e warning obbligatorio.
Se influence_on_global_model = true → NOT_APPLICABLE per i modelli semplificati.


4) Premium‑Gate (1 credito) — prerequisiti
Prima di spendere 1 credito premium per iniziare implementazione:

docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md deve esistere (creato/incollato).
La decisione 2A‑1 deve essere già formalizzata (✅).
La lista file target deve essere congelata (✅).


5) Prossima azione (PLAN) immediata

Creare (in repo) il file:docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md
usando il testo già presente nel canvas “FASE2_PROMPT _ STEP2_INTEGRATION.md (PLAN‑ONLY)”.
