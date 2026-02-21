SEI GitHub Copilot Chat in VS Code. MODALITÀ: PREMIUM ONE‑SHOT.
OBIETTIVO: implementare STEP2 in modo controllato, minimale e deterministico, rispettando:

invarianti norma_attiva
regola no‑mixing
contratti output (trace.run_id, norm_references[], decision_log)
CONTESTO VINCOLANTE (GIÀ CHIUSO):

Fase 1 completata (SPEC/PLAN).
Fase 2 (PLAN) completata e congelata.
Decisione architetturale VINCOLANTE: 2A‑1 (conservativa)
Source of truth modulo Secondary Elements = src/codes/secondary_elements/*
NON esiste e NON deve essere creato un albero parallelo methods/verification/secondary_elements/*
Automation aggiornata con addendum 2A‑1.
File docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md esiste ed è vincolante.
DIVIETI ASSOLUTI:

NON creare directory methods/verification/secondary_elements/
NON toccare file fuori dalla baseline congelata (vedi lista sotto)
NON introdurre formule normative o calcoli numerici
NON implementare modelli fisici o verifiche complete
NON fare refactor creativi o miglioramenti estetici
NON modificare la GUI: STEP2 non prevede alcun intervento GUI
NON introdurre print, logging temporanei o debug code non strutturale
FILE AUTORIZZATI (BASELINE CONGELATA) — SOLO QUESTI:
TOUCH:

src/codes/secondary_elements/models.py
src/codes/secondary_elements/checks.py
src/codes/secondary_elements/storage_adapter.py
verifications/secondary_elements/dispatcher.py
CREATE (stub/interfacce, nessun calcolo):

src/codes/secondary_elements/ta_models.py
src/codes/secondary_elements/drift_models.py
src/codes/secondary_elements/anchors_capacity.py
CONFIG:

config/calculation_codes/SECONDARY_ELEMENTS.jsoncode
ORDINE DI IMPLEMENTAZIONE (OBBLIGATORIO):
STEP2‑A — Configurazione normativa

Creare config/calculation_codes/SECONDARY_ELEMENTS.jsoncode
Dichiarare check id:
NS_SLU_InertialForce
NS_SLE_DriftCompatibility
Impostare policy:
drift_method_default = SHEAR_BUILDING_PROXY
allow_estimated_drift = true
block_if_influence_on_global_model = true
Assicurare che il loader carichi il file senza errori anche se i check sono placeholder
STEP2‑B — Dispatcher e routing

Aggiornare verifications/secondary_elements/dispatcher.py per:
leggere esclusivamente project_model.norma_attiva
instradare SLU/SLE
restituire VerificationResultItem anche PLACEHOLDER/NOT_IMPLEMENTED
Garantire sempre:
trace.run_id
norm_references[] (minimo: riferimento NTC2018, anche placeholder)
STEP2‑C — Modello dati (contrattuale)

Evolvere SecondaryElementInput → SecondaryElementSpec (additivo e compatibile)
Campi minimi obbligatori:
ta_model
drift.source
drift.method
soft_storey_factor
confidence
influence_on_global_model
Aggiungere solo validazioni strutturali minime (presenza/tipi) — nessun calcolo
STEP2‑D — Stub di dominio (nessun calcolo)
Creare file stub senza formule:

ta_models.py
drift_models.py (Metodo B dichiarato: shear-building proxy + soft_storey_factor; solo metadata/commenti)
anchors_capacity.py (ETA-first; capacità come input manuale dichiarativo)
STEP2‑E — Contratti di output e gating

Ogni check deve produrre:
trace.run_id
norm_references[] (ammessi placeholder purché NON vuoti)
decision_log (minimo: metodo Ta/drift + assunzioni + warning)
Implementare gating contrattuale:
influence_on_global_model = true → NOT_APPLICABLE
drift.source = ESTIMATED → warning obbligatorio + confidence = LOW
STEP2‑F — Test contrattuali minimi
Creare/aggiornare SOLO test contrattuali (senza casi numerici, senza fixture nuove non necessarie):

presenza trace.run_id
presenza norm_references[]
warning su drift stimato (ESTIMATED → LOW)
NOT_APPLICABLE su gating (influence_on_global_model)
CRITERI DI ACCETTAZIONE FINALI:

STEP2 implementato senza violare 2A‑1
test esistenti non rotti
test contrattuali nuovi verdi
nessun file fuori baseline toccato
CLAUSOLA DI ARRESTO:
Se qualunque punto entra in conflitto con:

docs/MEGAPLAN/FASE2_BASELINE_CONGELATA.md
docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md (addendum 2A‑1)
docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md
FERMATI immediatamente e non procedere.